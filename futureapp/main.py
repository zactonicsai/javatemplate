# Quick test
import chromadb
import ollama

# Test Ollama connection
response = ollama.embeddings(model='nomic-embed-text', prompt='test')
print(f"Embedding dimension: {len(response['embedding'])}")

# Test ChromaDB
client = chromadb.Client()
print("ChromaDB initialized successfully!")