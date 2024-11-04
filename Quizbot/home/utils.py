import os
import json
from sentence_transformers import SentenceTransformer
from .vector_db import VectorDB
import numpy as np
from PyPDF2 import PdfReader

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
PROCESSED_META_FILE = os.path.join(DATA_DIR, 'processed_metadata.json')

# Initialize the SentenceTransformer model and VectorDB
model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # Ensure this matches the model output dimension
vector_db = VectorDB(dimension=dimension)

def load_metadata():
    """Load processed metadata from the JSON file."""
    if os.path.exists(PROCESSED_META_FILE):
        with open(PROCESSED_META_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_metadata(metadata):
    """Save processed metadata to the JSON file."""
    with open(PROCESSED_META_FILE, 'w') as file:
        json.dump(metadata, file, indent=4)

def pdf_to_text(file_path):
    """Convert PDF to text."""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def embed_text(text):
    """Convert text to embeddings."""
    return model.encode(text, convert_to_numpy=True)

def process_all_pdfs():
    """Process and embed new or modified PDFs, then save embeddings in FAISS."""
    metadata = load_metadata()

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.pdf'):
            file_path = os.path.join(DATA_DIR, filename)
            last_modified = os.path.getmtime(file_path)

            # Check if the file is new or modified
            if filename not in metadata or metadata[filename]['last_modified'] < last_modified:
                print(f"Processing and embedding: {filename}")
                
                # Extract text from PDF
                text = pdf_to_text(file_path)
                if not text.strip():
                    print(f"No text extracted from {filename}. Skipping...")
                    continue

                # Embed text
                embedding = embed_text(text)
                print(f"Embedding for {filename}: {embedding[:10]}... (shape: {embedding.shape})")

                # Generate a unique integer ID for each filename
                file_id = abs(hash(filename)) % (10 ** 8)
                print(f"Generated file ID for {filename}: {file_id}")

                # Add embedding to FAISS index with the generated integer ID
                vector_db.add([embedding], ids=[file_id])

                # Update metadata with last modified time and file ID
                metadata[filename] = {
                    'last_modified': last_modified,
                    'file_id': file_id,
                    'content': text[:200],  # Save snippet for reference
                }

    # Save metadata and FAISS index
    save_metadata(metadata)
    print("Metadata saved.")
    vector_db.save_index()
    print("FAISS index saved.")
    print("Total embeddings in index:", vector_db.index.ntotal)
