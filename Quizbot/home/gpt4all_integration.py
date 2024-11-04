# gpt4all_integration.py
from gpt4all import GPT4All
from .vector_db import VectorDB
from .utils import embed_text

# Initialize the vector database
dimension = 384  # Ensure this matches your Sentence Transformer model's output dimension
vector_db = VectorDB(dimension=dimension)  # Create the vector database instance

# Load the GPT4All model
gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="D:/GPT4AllModels")  # Replace with your GPT4All model name

# Function to generate questions with GPT4All
def generate_question(prompt):
    """
    Generates a question based on a prompt using GPT4All.
    """
    response = gpt4all_model.generate(prompt)
    return response

def create_quiz_question_from_topic(topic):
    """
    Creates quiz questions for a specified topic using embeddings and GPT4All.
    """
    # Embed the topic to retrieve relevant content
    query_embedding = embed_text(topic)

    # Search the vector database for similar embeddings
    results, _ = vector_db.search(query_embedding, k=5)

    # Construct text from the retrieved embeddings for context
    context_text = " ".join(results)

    # Generate a question based on the context
    prompt = f"Create a quiz question on the topic: {topic}. Context: {context_text}"
    question = generate_question(prompt)

    return question
