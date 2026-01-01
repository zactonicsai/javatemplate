# ChromaDB + Ollama Embedding Tutorial
## Building a Semantic Keyword Matcher for Food & Cooking Documents

---

## Table of Contents
1. [Understanding Embeddings](#understanding-embeddings)
2. [Architecture Overview](#architecture-overview)
3. [Setup & Installation](#setup--installation)
4. [File 1: Document Reader & Embedding Creator](#file-1-document-reader--embedding-creator)
5. [File 2: Semantic Keyword Matcher](#file-2-semantic-keyword-matcher)
6. [How It All Works Together](#how-it-all-works-together)
7. [Running the Tutorial](#running-the-tutorial)

---

## Understanding Embeddings

### What Are Embeddings?

Embeddings are numerical representations of text that capture semantic meaning. Think of them as coordinates in a high-dimensional space where similar concepts are located near each other.

```
Traditional Search:          Embedding-Based Search:
"frying" → exact match       "frying" → [0.23, -0.45, 0.87, ...]
                                          ↓
                             Similar to "sautéing", "pan-cooking"
```

### How Embeddings Work

1. **Tokenization**: Text is broken into tokens (words or subwords)
2. **Neural Network Processing**: Tokens pass through transformer layers
3. **Vector Output**: A fixed-size array of floating-point numbers (e.g., 384 or 768 dimensions)
4. **Similarity Measurement**: Vectors are compared using cosine similarity or Euclidean distance

### Why Embeddings Matter for Our Use Case

| Traditional Keyword Matching | Semantic Embedding Matching |
|------------------------------|------------------------------|
| "grill" only matches "grill" | "grill" matches "BBQ", "charbroil", "flame-cook" |
| Misses synonyms | Understands meaning |
| Exact string required | Conceptual similarity |

### Cosine Similarity Explained

```
                    A · B
cos(θ) = ─────────────────────
         ||A|| × ||B||

Where:
- A · B = dot product of vectors
- ||A|| = magnitude of vector A
- Result: -1 (opposite) to 1 (identical)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐
│   Document   │────▶│   Ollama     │────▶│     ChromaDB         │
│   (Text)     │     │  Embedding   │     │   Vector Database    │
│              │     │    Model     │     │                      │
└──────────────┘     └──────────────┘     └──────────────────────┘
                            │                       │
                            ▼                       ▼
                    ┌──────────────┐     ┌──────────────────────┐
                    │   Keyword    │     │   Semantic Query     │
                    │   Embeddings │────▶│   & Matching         │
                    └──────────────┘     └──────────────────────┘
```

### Components

1. **Ollama**: Local LLM server that provides embedding models
2. **ChromaDB**: Open-source vector database for storing and querying embeddings
3. **File 1 (embedding_reader.py)**: Reads documents, chunks text, creates embeddings
4. **File 2 (keyword_matcher.py)**: Matches predefined keywords to document chunks

---

## Setup & Installation

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Pull an embedding model (in a new terminal)
ollama pull nomic-embed-text
# Alternative: ollama pull mxbai-embed-large
```

### Step 2: Install Python Dependencies

```bash
pip install chromadb ollama
```

### Step 3: Verify Installation

```python
# Quick test
import chromadb
import ollama

# Test Ollama connection
response = ollama.embeddings(model='nomic-embed-text', prompt='test')
print(f"Embedding dimension: {len(response['embedding'])}")

# Test ChromaDB
client = chromadb.Client()
print("ChromaDB initialized successfully!")
```

---

## File 1: Document Reader & Embedding Creator

**Purpose**: Read documents, split into meaningful chunks, generate embeddings, store in ChromaDB.

### Key Concepts in embedding_reader.py

```python
# 1. CHUNKING STRATEGY
# Why chunk? Long documents exceed model context limits
# Goal: Preserve semantic coherence while respecting size limits

def chunk_document(text, chunk_size=500, overlap=50):
    """
    chunk_size: Target characters per chunk
    overlap: Characters shared between chunks (prevents cutting sentences)
    """
```

### Sentence-Based vs. Fixed-Size Chunking

```
Fixed-Size Chunking:              Sentence-Based Chunking:
├─────────────────┤               ├─── Sentence 1 ───┤
│ "The chef prep  │               │ "The chef prepared│
├─────────────────┤               │  the ingredients."│
│ ared the ingred │               ├─── Sentence 2 ───┤
├─────────────────┤               │ "He heated oil in│
│ ients. He heate │               │  the pan."       │
└─────────────────┘               └──────────────────┘

✗ Breaks mid-word/sentence        ✓ Preserves meaning
```

### Metadata Storage

Each chunk is stored with metadata for later retrieval:

```python
{
    "id": "doc1_chunk_3",
    "text": "Sauté the onions until translucent...",
    "embedding": [0.23, -0.45, 0.87, ...],  # 768 dimensions
    "metadata": {
        "source": "cooking_guide.txt",
        "chunk_index": 3,
        "paragraph": "Preparation Steps"
    }
}
```

---

## File 2: Semantic Keyword Matcher

**Purpose**: Take predefined cooking keywords, find document chunks that semantically match.

### The Keyword Matching Process

```
┌─────────────────┐
│ KNOWN KEYWORDS  │
│ ─────────────── │
│ • grilling      │
│ • baking        │
│ • fermentation  │
│ • knife skills  │
└────────┬────────┘
         │
         ▼ Create embeddings for each keyword
┌─────────────────┐
│ KEYWORD VECTORS │
│ ─────────────── │
│ grilling → [...]│
│ baking → [...]  │
└────────┬────────┘
         │
         ▼ Query ChromaDB for similar chunks
┌─────────────────────────────────────┐
│ MATCHES                             │
│ ─────────────────────────────────── │
│ "grilling" matches:                 │
│   • "Place steaks on hot grill..."  │
│   • "BBQ requires indirect heat..." │
│ "baking" matches:                   │
│   • "Preheat oven to 350°F..."      │
└─────────────────────────────────────┘
```

### Similarity Threshold

```python
# Only accept matches above threshold
SIMILARITY_THRESHOLD = 0.7  # Range: 0-1

# ChromaDB returns distance (lower = more similar)
# Convert: similarity = 1 - distance

if similarity >= SIMILARITY_THRESHOLD:
    # Accept match
```

---

## How It All Works Together

### Complete Data Flow

```
STEP 1: Document Ingestion (embedding_reader.py)
──────────────────────────────────────────────
sample_cooking_doc.txt
        │
        ▼
┌───────────────────────────────────────────┐
│ "Grilling is a dry heat cooking method   │
│ that uses direct heat from below. The    │
│ Maillard reaction creates..."            │
└───────────────────────────────────────────┘
        │
        ▼ Chunk into paragraphs/sentences
┌─────────────┬─────────────┬─────────────┐
│  Chunk 1    │  Chunk 2    │  Chunk 3    │
│ "Grilling..."│ "Maillard..."│ "Baking..." │
└─────────────┴─────────────┴─────────────┘
        │
        ▼ Generate embeddings via Ollama
┌─────────────┬─────────────┬─────────────┐
│ [0.2, -0.4] │ [0.5, 0.1]  │ [-0.3, 0.8] │
└─────────────┴─────────────┴─────────────┘
        │
        ▼ Store in ChromaDB
┌─────────────────────────────────────────────┐
│ ChromaDB Collection: "cooking_documents"    │
│ ┌─────────┬───────────────┬───────────────┐ │
│ │   ID    │   Embedding   │   Metadata    │ │
│ ├─────────┼───────────────┼───────────────┤ │
│ │ chunk_1 │ [0.2, -0.4...]│ {source:...}  │ │
│ │ chunk_2 │ [0.5, 0.1...] │ {source:...}  │ │
│ └─────────┴───────────────┴───────────────┘ │
└─────────────────────────────────────────────┘


STEP 2: Keyword Matching (keyword_matcher.py)
──────────────────────────────────────────────
Known Keywords: ["grilling", "baking", "fermentation", ...]
        │
        ▼ Embed each keyword
"grilling" → [0.21, -0.38, ...]
        │
        ▼ Query ChromaDB (cosine similarity search)
┌─────────────────────────────────────────────┐
│ Query: Find chunks similar to "grilling"   │
│                                             │
│ Results:                                    │
│   1. chunk_1 (similarity: 0.92) ✓          │
│   2. chunk_5 (similarity: 0.78) ✓          │
│   3. chunk_3 (similarity: 0.45) ✗          │
└─────────────────────────────────────────────┘
        │
        ▼ Output
┌─────────────────────────────────────────────┐
│ KEYWORD: grilling                           │
│ MATCHED CHUNKS:                             │
│   • "Grilling is a dry heat cooking..."    │
│   • "Direct flame cooking techniques..."    │
└─────────────────────────────────────────────┘
```

---

## Running the Tutorial

### Quick Start

```bash
# 1. Ensure Ollama is running
ollama serve &

# 2. Run the embedding reader first
python embedding_reader.py

# 3. Run the keyword matcher
python keyword_matcher.py
```

### Expected Output

```
=== Embedding Reader ===
Loading document: sample_cooking_doc.txt
Created 12 chunks from document
Generating embeddings... Done!
Stored 12 embeddings in ChromaDB

=== Keyword Matcher ===
Analyzing keywords against document...

KEYWORD: grilling
├── Match: "Grilling involves cooking food over direct heat..." (0.91)
└── Match: "BBQ and grilling share similar techniques..." (0.84)

KEYWORD: baking
├── Match: "Baking uses enclosed heat in an oven..." (0.89)
└── Match: "Bread making requires precise temperature..." (0.76)
...
```

---

## Advanced Concepts

### Embedding Model Comparison

| Model | Dimensions | Speed | Quality | Best For |
|-------|------------|-------|---------|----------|
| nomic-embed-text | 768 | Fast | Good | General purpose |
| mxbai-embed-large | 1024 | Medium | Better | Higher accuracy |
| all-minilm | 384 | Fastest | Basic | Quick prototyping |

### Performance Tips

1. **Batch Embedding**: Process multiple texts at once
2. **Persistent Storage**: Use `chromadb.PersistentClient()` for disk storage
3. **Index Optimization**: ChromaDB auto-optimizes, but consider HNSW params for large datasets

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Ensure `ollama serve` is running |
| Slow embeddings | Use smaller model or batch processing |
| Poor matches | Lower threshold or use better model |
| Memory issues | Use persistent ChromaDB storage |

---

## Summary

This tutorial demonstrated:

1. **Embeddings** convert text to numerical vectors capturing meaning
2. **ChromaDB** efficiently stores and queries these vectors
3. **Ollama** provides local embedding generation
4. **Semantic matching** finds conceptually similar content, not just exact matches
5. **Two-file architecture** separates concerns: ingestion vs. querying

The power of this approach: searching for "grilling" can find content about "BBQ", "charbroiling", or "flame-cooking" even if those exact words aren't in your keyword list!