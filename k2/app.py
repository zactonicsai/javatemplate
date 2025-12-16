import os
import re
from flask import Flask, request, jsonify, render_template
from chromadb import Client, Settings
from sentence_transformers import SentenceTransformer

# --- Configuration ---
# Use a simple, fast Sentence Transformer model for embeddings
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
COLLECTION_NAME = "document_embeddings"

# Define the keywords for semantic search and verification.
# These will be embedded and used as queries against the document's content.
VERIFICATION_KEYWORDS = [
    "long-term financial investment strategy and capital gains",
    "analysis of software API documentation and server architecture",
    "detailed review of the contract clauses and legal regulations",
    "mortgage loan interest rates and associated debt",
    "cloud computing infrastructure and database optimization",
    "dispute litigation and jurisdiction rules",
    # Add more complex phrases/sentences here
]

# --- ChromaDB and Embedding Setup ---
# Initialize ChromaDB client (in-memory for this example)
chroma_client = Client(Settings(allow_reset=True))
collection = None
model = None

def initialize_embedding_model():
    """Loads the sentence transformer model and embeds the keywords."""
    global model, collection
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Create or reset the collection
    if collection is not None:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Embed the verification keywords into the collection for later use (as a query target)
    print("Embedding verification keywords...")
    keyword_embeddings = model.encode(VERIFICATION_KEYWORDS).tolist()
    collection.add(
        embeddings=keyword_embeddings,
        documents=VERIFICATION_KEYWORDS,
        ids=[f"keyword_{i}" for i in range(len(VERIFICATION_KEYWORDS))]
    )
    print("Initialization complete.")

# Initialize upon startup
initialize_embedding_model()


def process_document(document_text):
    """
    Splits document into sentences and embeds them into a *new, temporary* collection
    for searching purposes.
    """
    # Simple sentence splitting using regex (adjust for production use)
    # Splits by periods, exclamation marks, or question marks followed by a space
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', document_text.strip())
    
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return []

    print(f"Processing {len(sentences)} sentences...")
    
    # Since we are searching document context based on keywords, we will embed the keywords
    # and search against the document's embedded sentences.
    
    # Store sentence ID and original text
    sentence_data = []
    
    # Embed all document sentences
    sentence_embeddings = model.encode(sentences, show_progress_bar=False).tolist()
    
    # We use the existing 'collection' which now contains the keywords
    # We will search the keywords against the document's sentences.
    
    # --- Semantic Search ---
    # 1. Embed the verification keywords (already done in initialize_embedding_model)
    # 2. Query the document's sentences with the keyword embeddings

    # For this implementation, we will perform a similarity search where the 
    # **query is a KEYWORD** and the **database is the DOCUMENT SENTENCES**.

    all_document_data = {
        "embeddings": sentence_embeddings,
        "documents": sentences,
        "ids": [f"doc_sen_{i}" for i in range(len(sentences))]
    }
    
    return all_document_data

def find_semantic_matches(document_data, num_results=3, num_top_sentences=3):
    """
    Performs semantic search to find:
    1. Top N most relevant sentences in the document for *each* keyword.
    2. Top N most relevant keywords overall based on the document's context.
    
    For simplicity, we will search all keywords against all document sentences 
    and aggregate results.
    """
    
    # Create a temporary collection just for the current document's sentences
    doc_collection = chroma_client.get_or_create_collection(
        name="temp_document_collection",
        metadata={"hnsw:space": "cosine"}
    )
    doc_collection.add(**document_data)

    try:
        # Search document sentences for similarity to each VERIFICATION_KEYWORD
        results = doc_collection.query(
            query_texts=VERIFICATION_KEYWORDS,
            n_results=num_top_sentences, # Find top N sentences for each keyword
            include=['documents', 'distances']
        )
        
        # --- Process Results for Summary ---
        
        # 1. Aggregate Top Sentences Matched per Keyword
        keyword_matches = {}
        for i, keyword in enumerate(VERIFICATION_KEYWORDS):
            # Extract the matched sentences and their distance (lower is better)
            matched_sentences = results['documents'][i]
            distances = results['distances'][i]
            
            # Find the best match (lowest distance) for this keyword
            if matched_sentences and distances:
                best_match = (matched_sentences[0], distances[0])
                
                # Store all found sentences for this keyword
                keyword_matches[keyword] = {
                    "top_match_sentence": best_match[0],
                    "top_match_distance": best_match[1],
                    "all_matched_sentences": matched_sentences,
                    "all_distances": distances,
                }

        # 2. Determine Top 3 Overall Keywords
        # We find the overall best-matched sentence (lowest distance) across all keyword searches.
        # This is a proxy for the 'most relevant' keywords.
        
        overall_best_matches = []
        for keyword, data in keyword_matches.items():
            overall_best_matches.append({
                "keyword": keyword,
                "distance": data['top_match_distance'],
                "matched_sentence": data['top_match_sentence']
            })
            
        # Sort by distance (lowest distance = highest similarity)
        overall_best_matches.sort(key=lambda x: x['distance'])
        
        # Get the top N keywords
        top_keywords = overall_best_matches[:num_results]
        
        return {
            "top_keywords_overall": top_keywords,
            "keyword_details": keyword_matches
        }

    finally:
        # Clean up the temporary document collection
        chroma_client.delete_collection(name="temp_document_collection")


# --- Flask Application ---

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main HTML form."""
    return render_template('index.html', keywords=VERIFICATION_KEYWORDS)

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """Handles the document submission for semantic search."""
    
    # 1. Handle File Upload
    if 'document' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['document']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        # Read the file content (assuming text file like .txt, .md, etc.)
        try:
            document_text = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({"error": "Could not decode file content as UTF-8."}), 400
        
        if not document_text.strip():
            return jsonify({"error": "Document content is empty."}), 400
        
        # 2. Process Document and Search
        document_data = process_document(document_text)
        
        if not document_data['documents']:
             return jsonify({"error": "Could not split the document into sentences."}), 400
        
        # Perform semantic search
        semantic_results = find_semantic_matches(document_data, num_results=3, num_top_sentences=1)
        
        # 3. Compile Response
        response_summary = f"Analyzed document with {len(document_data['documents'])} sentences."
        
        return jsonify({
            "status": "success",
            "summary": response_summary,
            "top_keywords": semantic_results['top_keywords_overall'],
            "document_sentences": document_data['documents'],
            "keyword_details": semantic_results['keyword_details']
        })

if __name__ == '__main__':
    # Flask runs on 0.0.0.0:5000 inside the Docker container
    app.run(host='0.0.0.0', port=5000, debug=True)
