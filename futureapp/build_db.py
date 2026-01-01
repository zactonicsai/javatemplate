#!/usr/bin/env python3
"""
build_db.py - Code Snippet Database Builder

This script:
1. Loads code snippets from JSON files
2. Creates embeddings for searchable text (keywords + description)
3. Stores everything in ChromaDB for semantic retrieval

The key insight: We embed the SEARCH TEXT (keywords, descriptions),
not the code itself. This allows natural language queries to find
relevant code patterns.

Usage:
    python build_db.py
"""

import chromadb
import ollama
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


# =============================================================================
# CONFIGURATION
# =============================================================================

# Embedding model - must be pulled in Ollama first
EMBEDDING_MODEL = "nomic-embed-text"

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "code_snippets"

# Snippets directory
SNIPPETS_DIR = "./snippets"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CodeSnippet:
    """Represents a code snippet with all metadata."""
    id: str
    category: str
    subcategory: str
    keywords: List[str]
    description: str
    search_text: str
    language: str
    code: str
    dependencies: List[str]
    difficulty: str


# =============================================================================
# SNIPPET LOADING
# =============================================================================

def load_snippets_from_file(file_path: str) -> List[CodeSnippet]:
    """
    Load snippets from a JSON file.
    
    Expected JSON structure:
    {
        "metadata": { ... },
        "snippets": [
            {
                "id": "...",
                "category": "...",
                ...
            }
        ]
    }
    """
    print(f"📄 Loading: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    snippets = []
    for item in data.get('snippets', []):
        snippet = CodeSnippet(
            id=item['id'],
            category=item['category'],
            subcategory=item['subcategory'],
            keywords=item['keywords'],
            description=item['description'],
            search_text=item['search_text'],
            language=item['language'],
            code=item['code'],
            dependencies=item.get('dependencies', []),
            difficulty=item.get('difficulty', 'intermediate')
        )
        snippets.append(snippet)
    
    print(f"   Loaded {len(snippets)} snippets")
    return snippets


def load_all_snippets(snippets_dir: str) -> List[CodeSnippet]:
    """
    Load all snippets from JSON files in the snippets directory.
    """
    all_snippets = []
    snippets_path = Path(snippets_dir)
    
    if not snippets_path.exists():
        print(f"❌ Snippets directory not found: {snippets_dir}")
        return []
    
    for json_file in snippets_path.glob("*.json"):
        snippets = load_snippets_from_file(str(json_file))
        all_snippets.extend(snippets)
    
    return all_snippets


# =============================================================================
# EMBEDDING GENERATION
# =============================================================================

def create_search_embedding(snippet: CodeSnippet) -> List[float]:
    """
    Create embedding for a snippet's searchable content.
    
    We embed:
    - Keywords (primary search terms)
    - Description (natural language)
    - Category/subcategory (context)
    
    We do NOT embed the code itself because:
    - Code syntax doesn't match natural language queries
    - "Create a navbar" won't match "<nav class=..."
    - Keywords bridge user intent to code
    """
    # Combine searchable elements
    search_content = f"""
    {' '.join(snippet.keywords)}
    {snippet.description}
    {snippet.category} {snippet.subcategory}
    {snippet.search_text}
    """.strip()
    
    # Generate embedding via Ollama
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=search_content
    )
    
    return response['embedding']


def generate_all_embeddings(snippets: List[CodeSnippet]) -> List[List[float]]:
    """
    Generate embeddings for all snippets.
    """
    print(f"\n🔄 Generating embeddings for {len(snippets)} snippets...")
    
    embeddings = []
    for i, snippet in enumerate(snippets):
        embedding = create_search_embedding(snippet)
        embeddings.append(embedding)
        
        if (i + 1) % 5 == 0:
            print(f"   Processed {i + 1}/{len(snippets)}")
    
    print(f"✅ Generated all embeddings")
    print(f"   Embedding dimension: {len(embeddings[0])}")
    
    return embeddings


# =============================================================================
# CHROMADB STORAGE
# =============================================================================

def create_chromadb_client() -> chromadb.ClientAPI:
    """
    Initialize ChromaDB with persistent storage.
    """
    # Create directory if needed
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    print(f"💾 ChromaDB initialized at: {CHROMA_PERSIST_DIR}")
    
    return client


def store_snippets(
    client: chromadb.ClientAPI,
    snippets: List[CodeSnippet],
    embeddings: List[List[float]]
) -> chromadb.Collection:
    """
    Store snippets and embeddings in ChromaDB.
    
    Storage structure:
    - ID: snippet.id (unique identifier)
    - Embedding: vector for similarity search
    - Document: the actual code (stored for retrieval)
    - Metadata: keywords, category, description, etc.
    """
    # Delete existing collection if present
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"🗑️  Deleted existing collection: {COLLECTION_NAME}")
    except:
        pass
    
    # Create new collection with cosine similarity
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Prepare data for batch insert
    ids = []
    documents = []  # Store the actual code
    metadatas = []
    
    for snippet in snippets:
        ids.append(snippet.id)
        documents.append(snippet.code)  # Store code as document
        metadatas.append({
            "category": snippet.category,
            "subcategory": snippet.subcategory,
            "keywords": json.dumps(snippet.keywords),  # JSON for list
            "description": snippet.description,
            "search_text": snippet.search_text,
            "language": snippet.language,
            "dependencies": json.dumps(snippet.dependencies),
            "difficulty": snippet.difficulty
        })
    
    # Add all snippets to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"✅ Stored {len(snippets)} snippets in collection: {COLLECTION_NAME}")
    
    return collection


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_database(collection: chromadb.Collection) -> None:
    """
    Verify the database with some test queries.
    """
    print("\n" + "="*60)
    print("🔍 VERIFICATION QUERIES")
    print("="*60)
    
    test_queries = [
        "navigation menu bar header",
        "form input login authentication",
        "lexer parser arithmetic calculator",
        "json tokens parsing"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        for i, (doc_id, distance) in enumerate(zip(
            results['ids'][0], 
            results['distances'][0]
        )):
            similarity = 1 - distance
            metadata = results['metadatas'][0][i]
            print(f"   {i+1}. {doc_id} ({similarity:.2f}) - {metadata['description'][:50]}...")


def print_statistics(snippets: List[CodeSnippet]) -> None:
    """
    Print database statistics.
    """
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)
    
    # Count by category
    categories = {}
    for s in snippets:
        categories[s.category] = categories.get(s.category, 0) + 1
    
    print("\nSnippets by category:")
    for cat, count in sorted(categories.items()):
        print(f"   • {cat}: {count}")
    
    # Count by language
    languages = {}
    for s in snippets:
        languages[s.language] = languages.get(s.language, 0) + 1
    
    print("\nSnippets by language:")
    for lang, count in sorted(languages.items()):
        print(f"   • {lang}: {count}")
    
    # All keywords
    all_keywords = set()
    for s in snippets:
        all_keywords.update(s.keywords)
    
    print(f"\nTotal unique keywords: {len(all_keywords)}")
    print(f"Total snippets: {len(snippets)}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main entry point for building the code snippet database.
    """
    print("\n" + "="*60)
    print("🔧 CODE SNIPPET DATABASE BUILDER")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"   • Embedding model: {EMBEDDING_MODEL}")
    print(f"   • Storage: {CHROMA_PERSIST_DIR}")
    print(f"   • Collection: {COLLECTION_NAME}")
    
    # Step 1: Load all snippets
    print("\n" + "-"*40)
    print("STEP 1: Loading Snippets")
    print("-"*40)
    
    snippets = load_all_snippets(SNIPPETS_DIR)
    
    if not snippets:
        print("❌ No snippets found. Please add JSON files to the snippets/ directory.")
        return
    
    # Step 2: Generate embeddings
    print("\n" + "-"*40)
    print("STEP 2: Generating Embeddings")
    print("-"*40)
    
    try:
        embeddings = generate_all_embeddings(snippets)
    except Exception as e:
        print(f"\n❌ Error generating embeddings: {e}")
        print("\nTroubleshooting:")
        print("   1. Ensure Ollama is running: ollama serve")
        print(f"   2. Pull the model: ollama pull {EMBEDDING_MODEL}")
        return
    
    # Step 3: Store in ChromaDB
    print("\n" + "-"*40)
    print("STEP 3: Storing in ChromaDB")
    print("-"*40)
    
    client = create_chromadb_client()
    collection = store_snippets(client, snippets, embeddings)
    
    # Step 4: Verify and show stats
    print_statistics(snippets)
    verify_database(collection)
    
    print("\n" + "="*60)
    print("✨ DATABASE BUILD COMPLETE")
    print("="*60)
    print(f"\nNext steps:")
    print(f"   1. Run: python code_qa.py")
    print(f"   2. Ask coding questions!")


if __name__ == "__main__":
    main()
