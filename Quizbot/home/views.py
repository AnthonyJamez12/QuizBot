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


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Topic, QuizQuestion, AnswerOption, UserResponse
from .gpt4all_integration import generate_question, vector_db
from .utils import embed_text, load_metadata
#from .gpt4all_integration import evaluate_open_ended_response  # Import the evaluation function

dimension = 384  # Ensure the dimension matches the Sentence Transformer model you're using
vector_db = VectorDB(dimension=dimension)




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
        # For Open-Ended, use AI to evaluate the response
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
    Evaluates open-ended responses using GPT4All.
    """
    prompt = f"Evaluate the following response to the question '{question.text}': {response}"
    from .gpt4all_integration import evaluate_open_ended_response as evaluate_response
    evaluation = evaluate_response(question.text, response)
    return evaluation  # Adjust this logic based on the AI's response format


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


def quiz_screen(request, quiz_type, topic_id=None):
    # Set topic name based on quiz type and topic_id
    topic_text = "general knowledge in network security"
    topic = None

    # Check if the quiz is focused and fetch the specific topic
    if quiz_type == 'focused' and topic_id:
        topic = get_object_or_404(Topic, id=topic_id)
        topic_text = topic.name
        # Fetch questions filtered by the specific topic
        questions = list(QuizQuestion.objects.filter(topic=topic)[:5])  # Adjust limit as needed
    else:
        # General quiz: Fetch questions not associated with a specific topic
        questions = list(QuizQuestion.objects.filter(topic__isnull=True)[:5])  # Adjust limit as needed

    # Render the quiz screen with existing questions
    return render(request, 'html/quizScreen.html', {
        'questions': questions,
        'quiz_type': quiz_type,
        'topic': topic_text if topic else "General"
    })



from django.db.models import Q

def generate_and_save_question(topic, topic_text, question_type="MC"):
    print('question_type', question_type)
    if question_type == "MC":
        prompt = (
            f"Create a multiple choice quiz question on the topic: '{topic_text}'. "
            "Do not make a question about firewalls. "
            "Do not include the answer in the question. "
            "Include four options labeled A, B, C, and D, and specify the correct answer at the end. "
            "Format: 'Question: {question text} A) {option 1} B) {option 2} C) {option 3} D) {option 4} "
            "The correct answer is {correct option}.'"
        )
    elif question_type == "TF":
        prompt = (
            f"Create a single True/False question on the topic: '{topic_text}'. "
            "Provide the question text and the correct answer as either True or False. "
            "Only give one question in this format: 'Question: {question text} The correct answer is {True/False}'"
        )
    elif question_type == "OE":
        prompt = (
            f"Create an open-ended question on the topic: '{topic_text}'. "
            "Provide the question text without any answer options."
        )

    generated_text = generate_question(prompt)
    print('Generated text:', generated_text)
    question_text = ""
    options = []
    correct_option_letter = ""

    # Parse the generated question based on the type
    if question_type == "MC":
        try:
            question_text = generated_text.split("Question:")[1].split("A)")[0].strip()
            options = [
                ("A", generated_text.split("A)")[1].split("B)")[0].strip()),
                ("B", generated_text.split("B)")[1].split("C)")[0].strip()),
                ("C", generated_text.split("C)")[1].split("D)")[0].strip()),
                ("D", generated_text.split("D)")[1].split("The correct answer is")[0].strip()),
            ]
            correct_option_letter = generated_text.split("The correct answer is")[1].strip()[0]
        except IndexError as e:
            print(f"Error parsing generated MC question: {e}")
            question_text = "Unable to generate a valid question."
    elif question_type == "TF":
        try:
            question_text = generated_text.split("Question:")[1].split("The correct answer is")[0].strip()
            correct_answer = generated_text.split("The correct answer is")[1].strip().lower()
            print('correct_answer', correct_answer)
            options = [("True", correct_answer == "true"), ("False", correct_answer == "false")]
        except IndexError as e:
            print(f"Error parsing generated TF question: {e}")
            question_text = "Unable to generate a valid question."
    elif question_type == "OE":
        try:
            if "Here's your open-ended question:" in generated_text:
                question_text = generated_text.split("Here's your open-ended question:")[1].strip()
            elif "Question:" in generated_text:
                question_text = generated_text.split("Question:")[1].strip()
            else:
                question_text = generated_text.strip()
            if "Please provide your response" in question_text:
                question_text = question_text.split("Please provide your response")[0].strip()
        except IndexError as e:
            print(f"Error parsing generated OE question: {e}")
            question_text = "Unable to generate a valid question."

    # Check for duplicate questions
    if QuizQuestion.objects.filter(Q(text=question_text) & Q(topic=topic)).exists():
        print("Duplicate question detected. Generating a new question.")
        return generate_and_save_question(topic, topic_text, question_type)

    # Create the QuizQuestion instance
    new_question = QuizQuestion.objects.create(
        text=question_text,
        question_type=question_type,
        topic=topic
    )

    # Create AnswerOption instances for each option (if applicable)
    if question_type == "MC":
        for letter, option_text in options:
            is_correct = (letter == correct_option_letter)
            AnswerOption.objects.create(
                question=new_question,
                text=option_text,
                is_correct=is_correct
            )
    elif question_type == "TF":
        try:
            # Extract question text and clean correct answer
            question_text = generated_text.split("Question:")[1].split("The correct answer is")[0].strip()
            correct_answer = generated_text.split("The correct answer is")[1].strip(" '")

            # Normalize the case of the answer and remove any trailing period
            correct_answer = correct_answer.capitalize().rstrip('.')

            # Debug print statements
            print(f"Extracted question text: {question_text}")
            print("Cleaned correct answer for TF question:", correct_answer, "Spaces might be in correct answer")

            # Define the options with is_correct values set according to correct_answer
            options = [
                ("True", correct_answer == "True"),
                ("False", correct_answer == "False")
            ]

            # Confirm parsed information
            print(f"Options with is_correct values: {options}")

            # Create AnswerOption instances for True/False
            for option_text, is_correct in options:
                print(f"Creating AnswerOption - Text: {option_text}, Is Correct: {is_correct}")
                AnswerOption.objects.create(
                    question=new_question,
                    text=option_text,
                    is_correct=is_correct
                )

        except IndexError as e:
            print(f"Error parsing generated TF question: {e}")
            question_text = "Unable to generate a valid question."

    return new_question


def generate_question_view(request):
    question_type = request.POST.get("question_type")
    topic_text = "general knowledge in network security"  # Example topic, adjust as needed
    topic, _ = Topic.objects.get_or_create(name=topic_text)

    # Generate a question based on the requested type
    new_question = generate_and_save_question(topic, topic_text, question_type=question_type)

    # Prepare response data
    response_data = {
        'new_question': {
            'id': new_question.id,
            'text': new_question.text,
            'options': [
                {'id': option.id, 'text': option.text} for option in new_question.options.all()
            ] if question_type != "OE" else []  # Open-ended questions don't have options
        }
    }
    return JsonResponse(response_data)