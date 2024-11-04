from django.shortcuts import render, get_object_or_404
from .models import Topic, QuizQuestion, AnswerOption, UserResponse
from django.http import JsonResponse
from .vector_db import VectorDB
from .gpt4all_integration import generate_question 
import numpy as np
from .gpt4all_integration import generate_question, vector_db
from .utils import embed_text, load_metadata


dimension = 384  # Ensure the dimension matches the Sentence Transformer model you're using
vector_db = VectorDB(dimension=dimension)


def main_menu_screen(request):
    """
    View for the main menu screen, allowing the user to choose between General Quiz and Focus Quiz.
    """
    return render(request, 'html/mainMenuScreen.html')  # You’ll need to create this template

def topic_menu_screen(request):
    """
    View for the topic menu screen, showing a list of topics for the Focus Quiz.
    """
    topics = Topic.objects.all()  # Retrieve all available topics
    return render(request, 'html/topicMenuScreen.html', {'topics': topics})  # Pass topics to the template



def quiz_screen(request, quiz_type, topic_id=None):
    # Set topic name based on quiz type and topic_id
    topic_text = "general knowledge in network security"
    topic = None
    if quiz_type == 'focused' and topic_id:
        topic = get_object_or_404(Topic, id=topic_id)
        topic_text = topic.name

    # Generate embedding for the topic
    query_embedding = embed_text(topic_text)
    print(f"Generated embedding for topic '{topic_text}': {query_embedding}")

    # Search vector DB for relevant content
    results, _ = vector_db.search(query_embedding, k=1)
    print(f"Vector DB search results for '{topic_text}': {results}")

    # Load content from metadata based on results, fallback if none found
    metadata = load_metadata()
    context_text = " ".join(
        metadata.get(str(result), {}).get('content', '') for result in results if result != -1
    ) or "Fundamental concepts in network security."

    # Generate a new quiz question with options
    prompt = (
        f"Create a multiple choice quiz question on the topic: '{topic_text}'. "
        "Include four options labeled A, B, C, and D, and specify the correct answer at the end. "
        "Format: 'Question: {question text} A) {option 1} B) {option 2} C) {option 3} D) {option 4} "
        "The correct answer is {correct option}.'"
    )
    generated_text = generate_question(prompt)
    print(f"Generated text: {generated_text}")

    # Parse the generated response to extract the question and options
    question_text = ""
    options = []
    correct_option_letter = ""

    try:
        # Extract question and options from the generated text
        question_text = generated_text.split("Question:")[1].split("A)")[0].strip()
        options = [
            ("A", generated_text.split("A)")[1].split("B)")[0].strip()),
            ("B", generated_text.split("B)")[1].split("C)")[0].strip()),
            ("C", generated_text.split("C)")[1].split("D)")[0].strip()),
            ("D", generated_text.split("D)")[1].split("The correct answer is")[0].strip()),
        ]
        correct_option_letter = generated_text.split("The correct answer is")[1].strip()[0]

    except IndexError as e:
        print(f"Error parsing generated question: {e}")
        question_text = "Unable to generate a valid question."

    # Create the QuizQuestion instance
    new_question = QuizQuestion.objects.create(
        text=question_text,
        question_type="MC",
        topic=topic
    )

    # Create AnswerOption instances for each option
    for letter, option_text in options:
        is_correct = (letter == correct_option_letter)
        AnswerOption.objects.create(
            question=new_question,
            text=option_text,
            is_correct=is_correct
        )

    # Display the new question on the quiz screen
    questions = [new_question]

    return render(request, 'html/quizScreen.html', {
        'questions': questions,
        'quiz_type': quiz_type,
        'topic': topic_text if topic else "General"
    })









def submit_answer(request):
    """
    Handles the answer submission and provides feedback to the user.
    This would be called via AJAX in the quiz screen template.
    """
    question_id = request.POST.get('question_id')
    selected_option_id = request.POST.get('selected_option_id')
    open_ended_response = request.POST.get('open_ended_response')

    question = get_object_or_404(QuizQuestion, id=question_id)

    # Handling Multiple Choice or True/False Questions
    if question.question_type in ['MC', 'TF']:
        selected_option = get_object_or_404(AnswerOption, id=selected_option_id)
        correct = selected_option.is_correct
    elif question.question_type == 'OE':
        # For Open-Ended, we would ideally use some logic or LLM-based evaluation here.
        correct = evaluate_open_ended_response(question, open_ended_response)
    else:
        return JsonResponse({'error': 'Invalid question type.'}, status=400)

    # Save the response
    UserResponse.objects.create(
        question=question,
        selected_option=selected_option if question.question_type in ['MC', 'TF'] else None,
        open_ended_response=open_ended_response,
        correct=correct,
        score=1 if correct else 0  # Adjust scoring logic as needed
    )

    feedback = "Correct!" if correct else "Incorrect. Try again!"
    return JsonResponse({'correct': correct, 'feedback': feedback})

def evaluate_open_ended_response(question, response):
    """
    Evaluates open-ended responses; this is a placeholder.
    You might integrate more complex logic here, such as LLM analysis.
    """
    keywords = ["example_keyword"]  # Replace with relevant keywords or LLM-based evaluation
    response_lower = response.lower()
    return "example_keyword" in response.lower()  # Simple keyword check for now


def topic_quiz(request, topic):
    """
    View for topic-specific quiz, finding relevant questions based on vector embeddings and generating
    additional questions using GPT4All.
    """
    # Generate embedding for the chosen topic
    query_embedding = embed_text(topic)

    # Search the vector database for similar embeddings
    results, distances = vector_db.search(query_embedding, k=5)  # Adjust 'k' as needed for the number of results

    # Retrieve content from the FAISS search results to construct context
    relevant_questions = QuizQuestion.objects.filter(id__in=results)
    context_text = " ".join([q.text for q in relevant_questions])

    # Generate a new question using GPT4All with context
    prompt = f"Create a quiz question on the topic: {topic}. Context: {context_text}"
    generated_question = generate_question(prompt)

    # Combine retrieved questions with the generated question
    all_questions = list(relevant_questions) + [generated_question]

    # Render the quiz screen with both retrieved and generated questions
    context = {
        'topic': topic,
        'questions': all_questions
    }
    return render(request, 'html/quizScreen.html', context)