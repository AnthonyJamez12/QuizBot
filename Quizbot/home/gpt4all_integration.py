# FILE: home/gpt4all_integration.py

from gpt4all import GPT4All
from .vector_db import VectorDB
from .utils import embed_text

# Initialize the vector database
dimension = 384  # Ensure this matches your Sentence Transformer model's output dimension
vector_db = VectorDB(dimension=dimension)  # Create the vector database instance

# Load the GPT4All model
gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="D:/GPT4AllModels")

# If the library supports setting the device, set it here
# Example: gpt4all_model.set_device(device)

# Function to generate questions with GPT4All
def generate_question(prompt):
    response = gpt4all_model.generate(prompt)
    return response

# Function to evaluate open-ended responses using GPT4All
def evaluate_open_ended_response(question, response):
    """
    Evaluates open-ended responses using GPT4All.
    """
    prompt = f"Evaluate the following response to the question '{question}'. The answer that was given is {response}. Return one word only: either correct or incorrect."
    try:
        evaluation = gpt4all_model.generate(prompt)
        return "correct" in evaluation # Adjust this logic based on the AI's response format
    except Exception as e:
        print(f"Error evaluating response: {e}")
        return False