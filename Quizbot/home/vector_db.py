import faiss
import numpy as np

class VectorDB:
    def __init__(self, dimension):
        # Wrap IndexFlatL2 with IndexIDMap to enable custom IDs
        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(dimension))

    def add(self, embeddings, ids):
        """Add embeddings with custom IDs to the index."""
        embeddings = np.array(embeddings).astype('float32')
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)  # Ensure 2D shape
        ids = np.array(ids).astype('int64')
        
        if len(ids) != len(embeddings):
            raise ValueError("Length of `ids` must match the number of `embeddings`.")

        self.index.add_with_ids(embeddings, ids)
        print(f"Added {len(ids)} embeddings to the index.")
        print(f"Total embeddings in index: {self.index.ntotal}")  # Debug: Check index size

    def search(self, query_embedding, k=5):
        """Search the index for the k nearest neighbors."""
        query_embedding = np.array([query_embedding]).astype('float32')
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, k)
        print(f"Search results: indices={indices}, distances={distances}")  # Debug: Show search results
        return indices[0], distances[0]

    def save_index(self, file_path="vector_index.bin"):
        """Save the index to a file."""
        faiss.write_index(self.index, file_path)
        print(f"Index saved to {file_path}")  # Debug: Confirm save

    def load_index(self, file_path="vector_index.bin"):
        """Load an index from a file."""
        self.index = faiss.read_index(file_path)
        print(f"Index loaded from {file_path}")  # Debug: Confirm load
