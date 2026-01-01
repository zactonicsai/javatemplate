#!/usr/bin/env python3
"""
code_qa.py - Code Snippet Q&A System with RAG

This system uses Retrieval Augmented Generation (RAG) to:
1. Accept natural language coding questions
2. Search ChromaDB for semantically similar code snippets
3. Build an augmented prompt with retrieved examples
4. Use Ollama to generate new code based on the examples

The key innovation: Retrieved code examples provide context that
makes the LLM's output more accurate and consistent with your patterns.

Usage:
    python code_qa.py                    # Interactive mode
    python code_qa.py --query "..."      # Single query mode
"""

import chromadb
import ollama
import json
import argparse
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# =============================================================================
# CONFIGURATION
# =============================================================================

# Models
EMBEDDING_MODEL = "nomic-embed-text"
GENERATION_MODEL = "codellama"  # or "deepseek-coder", "mistral", etc.

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "code_snippets"

# Retrieval settings
TOP_K_RESULTS = 3          # Number of examples to retrieve
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity (0-1)

# Generation settings
MAX_TOKENS = 2048
TEMPERATURE = 0.7


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class RetrievedSnippet:
    """A code snippet retrieved from the database."""
    id: str
    code: str
    description: str
    keywords: List[str]
    category: str
    language: str
    similarity: float


@dataclass
class GenerationResult:
    """Result of code generation."""
    query: str
    retrieved_snippets: List[RetrievedSnippet]
    generated_code: str
    model_used: str


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def connect_to_database() -> chromadb.Collection:
    """
    Connect to the ChromaDB collection.
    """
    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"📚 Connected to database: {collection.count()} snippets available")
        return collection
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nPlease run 'python build_db.py' first to create the database.")
        sys.exit(1)


# =============================================================================
# RETRIEVAL
# =============================================================================

def retrieve_similar_snippets(
    collection: chromadb.Collection,
    query: str,
    n_results: int = TOP_K_RESULTS
) -> List[RetrievedSnippet]:
    """
    Retrieve code snippets similar to the query.
    
    Process:
    1. Query text is embedded by ChromaDB
    2. Cosine similarity search finds nearest neighbors
    3. Results are filtered by threshold
    4. Snippets are parsed and returned
    """
    # Query the collection
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    snippets = []
    
    for i in range(len(results['ids'][0])):
        distance = results['distances'][0][i]
        similarity = 1 - distance  # Convert distance to similarity
        
        # Skip low-similarity results
        if similarity < SIMILARITY_THRESHOLD:
            continue
        
        metadata = results['metadatas'][0][i]
        
        snippet = RetrievedSnippet(
            id=results['ids'][0][i],
            code=results['documents'][0][i],
            description=metadata['description'],
            keywords=json.loads(metadata['keywords']),
            category=metadata['category'],
            language=metadata['language'],
            similarity=similarity
        )
        snippets.append(snippet)
    
    return snippets


# =============================================================================
# PROMPT BUILDING
# =============================================================================

def build_rag_prompt(query: str, snippets: List[RetrievedSnippet]) -> str:
    """
    Build an augmented prompt with retrieved code examples.
    
    This is the core of RAG: we provide the LLM with relevant
    examples from our codebase so it can:
    1. Follow our coding patterns
    2. Use correct syntax and libraries
    3. Generate more accurate code
    """
    prompt = """You are an expert code generation assistant. Your task is to generate 
high-quality code based on the user's request and the reference examples provided.

### REFERENCE CODE EXAMPLES

The following code snippets are from our codebase. Use them as patterns and references:

"""
    
    for i, snippet in enumerate(snippets, 1):
        prompt += f"""
---
**Example {i}: {snippet.description}**
- Category: {snippet.category}
- Keywords: {', '.join(snippet.keywords)}
- Language: {snippet.language}

```{snippet.language}
{snippet.code}
```
"""
    
    prompt += f"""
---

### USER REQUEST

{query}

### INSTRUCTIONS

1. Generate complete, working code that addresses the user's request
2. Follow the patterns and styling conventions from the reference examples
3. Use the same technologies/libraries shown in the examples (e.g., Tailwind CSS classes)
4. Make the code production-ready with proper structure
5. If the examples use HTML with Tailwind, continue that pattern
6. If the examples use Lex/YACC patterns, follow those conventions

### GENERATED CODE

"""
    
    return prompt


def build_simple_prompt(query: str) -> str:
    """
    Build a simple prompt when no examples are found.
    """
    return f"""You are an expert code generation assistant.

Generate complete, working code for the following request:

{query}

Provide clean, well-structured code with comments where helpful.
"""


# =============================================================================
# CODE GENERATION
# =============================================================================

def generate_code(prompt: str) -> str:
    """
    Generate code using Ollama.
    """
    try:
        response = ollama.chat(
            model=GENERATION_MODEL,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': TEMPERATURE,
                'num_predict': MAX_TOKENS
            }
        )
        
        return response['message']['content']
    
    except Exception as e:
        return f"Error generating code: {e}\n\nMake sure Ollama is running and {GENERATION_MODEL} is available."


def process_query(
    collection: chromadb.Collection,
    query: str
) -> GenerationResult:
    """
    Process a coding question and generate code.
    
    Full RAG pipeline:
    1. Retrieve similar snippets
    2. Build augmented prompt
    3. Generate code
    4. Return result
    """
    # Step 1: Retrieve
    print("🔍 Searching knowledge base...")
    snippets = retrieve_similar_snippets(collection, query)
    
    if snippets:
        print(f"📚 Found {len(snippets)} relevant examples:")
        for s in snippets:
            print(f"   • {s.id} (similarity: {s.similarity:.2f})")
    else:
        print("⚠️  No similar examples found, generating without context")
    
    # Step 2: Build prompt
    if snippets:
        prompt = build_rag_prompt(query, snippets)
    else:
        prompt = build_simple_prompt(query)
    
    # Step 3: Generate
    print(f"\n🤖 Generating code with {GENERATION_MODEL}...")
    generated_code = generate_code(prompt)
    
    return GenerationResult(
        query=query,
        retrieved_snippets=snippets,
        generated_code=generated_code,
        model_used=GENERATION_MODEL
    )


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def print_result(result: GenerationResult) -> None:
    """
    Print the generation result in a nice format.
    """
    print("\n" + "="*60)
    print("GENERATED CODE")
    print("="*60)
    print(result.generated_code)
    print("="*60)


def print_welcome() -> None:
    """
    Print welcome message.
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           CODE SNIPPET Q&A SYSTEM (RAG)                      ║
╠══════════════════════════════════════════════════════════════╣
║  Ask coding questions in natural language.                   ║
║  Examples:                                                   ║
║    • Create a responsive navbar with dropdown                ║
║    • Build a login form with Tailwind                        ║
║    • Write a lexer for arithmetic expressions                ║
║    • Create a hero section with gradient background          ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    • Type 'quit' or 'exit' to leave                          ║
║    • Type 'help' for more examples                           ║
║    • Type 'stats' to see database info                       ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_help() -> None:
    """
    Print help with example queries.
    """
    print("""
📝 EXAMPLE QUERIES:

HTML/Tailwind Components:
  • "Create a card with image and title"
  • "Build a responsive navigation bar"
  • "Make a contact form with validation styling"
  • "Create a pricing table with 3 tiers"
  • "Build a modal dialog popup"
  • "Create a sidebar navigation for dashboard"
  • "Make alert messages for success/error/warning"

YACC/LEX Parsers:
  • "Write a lexer for JSON tokens"
  • "Create a calculator parser"
  • "Build an AST for arithmetic expressions"
  • "Write a lexer that handles strings with escapes"
  • "Create a lexer for HTML tags"
  • "Write a parser for simple programming language"

Tips:
  • Be specific about what you want
  • Mention technologies (Tailwind, Lex, YACC)
  • Describe the visual result for UI components
""")


def print_stats(collection: chromadb.Collection) -> None:
    """
    Print database statistics.
    """
    count = collection.count()
    
    # Get sample to analyze categories
    sample = collection.peek(limit=count)
    
    categories = {}
    languages = {}
    
    for meta in sample['metadatas']:
        cat = meta['category']
        lang = meta['language']
        categories[cat] = categories.get(cat, 0) + 1
        languages[lang] = languages.get(lang, 0) + 1
    
    print(f"""
📊 DATABASE STATISTICS

Total snippets: {count}

By category:""")
    for cat, cnt in sorted(categories.items()):
        print(f"   • {cat}: {cnt}")
    
    print("\nBy language:")
    for lang, cnt in sorted(languages.items()):
        print(f"   • {lang}: {cnt}")


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_mode(collection: chromadb.Collection) -> None:
    """
    Run the interactive Q&A loop.
    """
    print_welcome()
    
    while True:
        try:
            # Get user input
            print("\n" + "-"*60)
            query = input("🎯 Your question: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'stats':
                print_stats(collection)
                continue
            
            # Process the query
            result = process_query(collection, query)
            print_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description="Code Snippet Q&A System with RAG"
    )
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Single query mode (non-interactive)'
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        default=GENERATION_MODEL,
        help=f'Generation model (default: {GENERATION_MODEL})'
    )
    parser.add_argument(
        '--top-k', '-k',
        type=int,
        default=TOP_K_RESULTS,
        help=f'Number of examples to retrieve (default: {TOP_K_RESULTS})'
    )
    
    args = parser.parse_args()
    
    # Update globals from args
    global GENERATION_MODEL, TOP_K_RESULTS
    GENERATION_MODEL = args.model
    TOP_K_RESULTS = args.top_k
    
    # Connect to database
    collection = connect_to_database()
    
    if args.query:
        # Single query mode
        result = process_query(collection, args.query)
        print_result(result)
    else:
        # Interactive mode
        interactive_mode(collection)


if __name__ == "__main__":
    main()
