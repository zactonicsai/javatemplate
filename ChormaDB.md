# Understanding Embeddings & Building a ChromaDB Knowledge Base
## A Step-by-Step Tutorial Using Cooking Methods, Foods & Healthy Choices

---

## Table of Contents

1. [What Are Embeddings?](#1-what-are-embeddings)
2. [How Embeddings Relate to AI & GPTs](#2-how-embeddings-relate-to-ai--gpts)
3. [Why Use a Vector Database Like ChromaDB?](#3-why-use-a-vector-database-like-chromadb)
4. [Environment Setup](#4-environment-setup)
5. [Step-by-Step Implementation](#5-step-by-step-implementation)
6. [Complete Working Example](#6-complete-working-example)
7. [Advanced: Adding Keywords & Metadata](#7-advanced-adding-keywords--metadata)
8. [Querying Your Knowledge Base](#8-querying-your-knowledge-base)

---

## 1. What Are Embeddings?

### The Core Concept

**Embeddings** are numerical representations of text (or other data) as vectors—lists of numbers that capture the *meaning* and *semantic relationships* of words, sentences, or documents.

Think of it this way: imagine you could plot every word, sentence, or document on a giant map where similar concepts are physically close together. That's essentially what embeddings do, but in a high-dimensional space (typically 384 to 1536 dimensions).

### A Simple Analogy

Imagine organizing a cookbook:
- "Grilling" and "BBQ" would be placed close together (similar cooking methods)
- "Steaming vegetables" and "healthy cooking" would be neighbors
- "Deep frying" would be far from "low-fat cooking"

Embeddings create this same kind of organization, but mathematically.

### What Does an Embedding Look Like?

```
Text: "Grilling is a healthy cooking method"

Embedding (simplified): [0.23, -0.45, 0.87, 0.12, -0.33, 0.56, ...]
                        (typically 384-1536 numbers)
```

Each number represents some learned feature about the text's meaning.

---

## 2. How Embeddings Relate to AI & GPTs

### The Connection

Large Language Models (LLMs) like GPT use embeddings as a fundamental building block:

```
┌─────────────────────────────────────────────────────────────────┐
│                    How GPT Uses Embeddings                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query: "What's a healthy way to cook chicken?"            │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────┐                    │
│  │  1. TOKENIZATION                        │                    │
│  │     Break text into tokens              │                    │
│  └─────────────────────────────────────────┘                    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────┐                    │
│  │  2. EMBEDDING LAYER                     │                    │
│  │     Convert tokens → vectors            │                    │
│  │     Each word becomes numbers           │                    │
│  └─────────────────────────────────────────┘                    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────┐                    │
│  │  3. TRANSFORMER LAYERS                  │                    │
│  │     Process relationships between       │                    │
│  │     all embeddings using attention      │                    │
│  └─────────────────────────────────────────┘                    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────┐                    │
│  │  4. OUTPUT GENERATION                   │                    │
│  │     Generate response based on          │                    │
│  │     learned patterns                    │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Retrieval-Augmented Generation (RAG)

This is where YOUR embeddings become powerful. RAG combines:

1. **Your embedded documents** (stored in ChromaDB)
2. **A user's question** (also converted to an embedding)
3. **An LLM** (like GPT or Claude) to generate answers

```
┌────────────────────────────────────────────────────────────────┐
│                      RAG Architecture                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   User Question ──────► Embed Query ──────┐                    │
│                                           │                    │
│                                           ▼                    │
│                              ┌─────────────────────┐           │
│                              │    ChromaDB         │           │
│                              │  Vector Database    │           │
│                              │                     │           │
│   Your Documents ──────►     │  [0.2, 0.5, ...]   │           │
│   (embedded)                 │  [0.8, 0.1, ...]   │           │
│                              │  [0.3, 0.7, ...]   │           │
│                              └─────────────────────┘           │
│                                           │                    │
│                                           ▼                    │
│                              Find Most Similar                 │
│                                           │                    │
│                                           ▼                    │
│                              ┌─────────────────────┐           │
│   Relevant Context ◄─────────│  Top 3-5 Results   │           │
│                              └─────────────────────┘           │
│          │                                                     │
│          ▼                                                     │
│   ┌─────────────────────────────────────────────┐              │
│   │  LLM (GPT/Claude)                           │              │
│   │  "Based on this context, answer..."         │              │
│   └─────────────────────────────────────────────┘              │
│          │                                                     │
│          ▼                                                     │
│   Generated Answer with Source Attribution                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Why Use a Vector Database Like ChromaDB?

### The Problem with Traditional Search

Traditional keyword search:
- Query: "healthy cooking" 
- ❌ Misses: "nutritious meal preparation" (same meaning, different words)
- ❌ Misses: "steaming vegetables" (healthy method, not mentioned directly)

### The Embedding Solution

Semantic search with embeddings:
- Query: "healthy cooking"
- ✅ Finds: "nutritious meal preparation" (similar meaning = similar vectors)
- ✅ Finds: "steaming vegetables" (related healthy concept)

### Why ChromaDB?

| Feature | Benefit |
|---------|---------|
| **Open Source** | Free to use, modify, and deploy |
| **Embedded or Client-Server** | Run locally or scale to production |
| **Built-in Embedding** | Can auto-generate embeddings |
| **Metadata Filtering** | Filter by keywords, categories, dates |
| **Simple API** | Easy to learn and implement |

---

## 4. Environment Setup

### Step 4.1: Install Required Packages

```bash
# Create a project directory
mkdir cooking_knowledge_base
cd cooking_knowledge_base

# Install ChromaDB and sentence-transformers
pip install chromadb sentence-transformers
```

### Step 4.2: Verify Installation

```python
# test_setup.py
import chromadb
from sentence_transformers import SentenceTransformer

print("ChromaDB version:", chromadb.__version__)
print("Setup successful!")
```

---

## 5. Step-by-Step Implementation

### Step 5.1: Understanding Our Data Structure

We'll organize our cooking knowledge like this:

```
Documents (the text content)
    │
    ├── Cooking Methods
    │   ├── "Grilling involves cooking food over direct heat..."
    │   ├── "Steaming is a gentle cooking method..."
    │   └── "Sautéing uses a small amount of oil..."
    │
    ├── Food Types
    │   ├── "Leafy greens include spinach, kale..."
    │   ├── "Lean proteins such as chicken breast..."
    │   └── "Whole grains like quinoa and brown rice..."
    │
    └── Healthy Choices
        ├── "To reduce sodium, use herbs and spices..."
        ├── "Portion control is essential for..."
        └── "Combining proteins with fiber helps..."

Metadata (keywords and categories for each document)
    │
    └── {"category": "cooking_method", 
         "keywords": ["grilling", "healthy", "outdoor"],
         "health_rating": "good"}
```

### Step 5.2: Initialize ChromaDB

```python
import chromadb
from chromadb.config import Settings

# Option 1: In-memory (for testing)
client = chromadb.Client()

# Option 2: Persistent storage (recommended for production)
client = chromadb.PersistentClient(path="./cooking_db")

# Create a collection for our cooking knowledge
collection = client.create_collection(
    name="cooking_knowledge",
    metadata={"description": "Cooking methods, foods, and healthy choices"}
)
```

### Step 5.3: Prepare Your Documents

```python
# Our cooking knowledge documents
documents = [
    # Cooking Methods
    {
        "id": "method_001",
        "text": "Grilling is a healthy cooking method that uses direct heat to cook food quickly. It allows fat to drip away from meat, reducing overall fat content. Best for lean proteins like chicken breast, fish, and vegetables. Grilling at high temperatures creates a flavorful char while keeping the inside moist.",
        "metadata": {
            "category": "cooking_method",
            "method_type": "dry_heat",
            "keywords": "grilling, bbq, outdoor cooking, char, direct heat",
            "health_rating": "healthy",
            "best_for": "proteins, vegetables"
        }
    },
    {
        "id": "method_002", 
        "text": "Steaming is one of the healthiest cooking methods available. Food is cooked by surrounding it with steam, preserving nutrients, color, and texture. No added fats are required. Ideal for vegetables, fish, dumplings, and delicate foods. Steaming retains up to 90% of water-soluble vitamins.",
        "metadata": {
            "category": "cooking_method",
            "method_type": "moist_heat",
            "keywords": "steaming, healthy, nutrient preservation, no oil, gentle cooking",
            "health_rating": "very_healthy",
            "best_for": "vegetables, fish, dumplings"
        }
    },
    {
        "id": "method_003",
        "text": "Sautéing involves cooking food quickly in a small amount of oil or butter over medium-high heat. The food is kept moving in the pan. This method works well for tender vegetables, thin cuts of meat, and creating flavorful bases for sauces. Use healthy oils like olive oil for better nutrition.",
        "metadata": {
            "category": "cooking_method",
            "method_type": "dry_heat",
            "keywords": "sautéing, quick cooking, stir fry, pan cooking, olive oil",
            "health_rating": "moderate",
            "best_for": "vegetables, thin meats"
        }
    },
    {
        "id": "method_004",
        "text": "Deep frying submerges food completely in hot oil, typically between 350-375°F. While it creates crispy, flavorful results, it significantly increases calorie and fat content. Foods absorb oil during cooking. This method should be used sparingly for health-conscious eating.",
        "metadata": {
            "category": "cooking_method",
            "method_type": "dry_heat",
            "keywords": "deep frying, oil, crispy, high calorie, indulgent",
            "health_rating": "unhealthy",
            "best_for": "occasional treats"
        }
    },
    {
        "id": "method_005",
        "text": "Roasting uses dry heat in an oven to cook food evenly on all sides. It's excellent for developing complex flavors through caramelization and the Maillard reaction. Roasting works well for vegetables, whole chickens, and large cuts of meat. Minimal oil is needed.",
        "metadata": {
            "category": "cooking_method",
            "method_type": "dry_heat",
            "keywords": "roasting, oven, caramelization, maillard reaction, whole foods",
            "health_rating": "healthy",
            "best_for": "vegetables, whole meats"
        }
    },
    
    # Food Types
    {
        "id": "food_001",
        "text": "Leafy green vegetables like spinach, kale, Swiss chard, and arugula are nutritional powerhouses. They're rich in vitamins A, C, K, and folate. Low in calories but high in fiber, they support digestive health and provide antioxidants that may reduce inflammation and chronic disease risk.",
        "metadata": {
            "category": "food_type",
            "food_group": "vegetables",
            "keywords": "leafy greens, spinach, kale, vitamins, antioxidants, fiber",
            "health_rating": "very_healthy",
            "nutrients": "vitamins A, C, K, folate, fiber"
        }
    },
    {
        "id": "food_002",
        "text": "Lean proteins include chicken breast, turkey, fish, tofu, and legumes. These provide essential amino acids for muscle building and repair without excessive saturated fat. Fish like salmon and mackerel also provide omega-3 fatty acids beneficial for heart and brain health.",
        "metadata": {
            "category": "food_type",
            "food_group": "proteins",
            "keywords": "lean protein, chicken, fish, tofu, omega-3, muscle building",
            "health_rating": "very_healthy",
            "nutrients": "protein, omega-3, amino acids"
        }
    },
    {
        "id": "food_003",
        "text": "Whole grains such as quinoa, brown rice, oats, and whole wheat provide complex carbohydrates, fiber, and essential nutrients. Unlike refined grains, they retain the bran and germ, offering B vitamins, iron, and magnesium. They provide sustained energy and help maintain stable blood sugar levels.",
        "metadata": {
            "category": "food_type",
            "food_group": "grains",
            "keywords": "whole grains, quinoa, brown rice, oats, fiber, complex carbs",
            "health_rating": "healthy",
            "nutrients": "fiber, B vitamins, iron, magnesium"
        }
    },
    {
        "id": "food_004",
        "text": "Processed foods often contain high levels of sodium, added sugars, unhealthy fats, and artificial preservatives. Examples include chips, frozen dinners, sugary cereals, and fast food. Regular consumption is linked to obesity, heart disease, and type 2 diabetes. Reading labels helps identify hidden unhealthy ingredients.",
        "metadata": {
            "category": "food_type",
            "food_group": "processed",
            "keywords": "processed food, junk food, sodium, sugar, preservatives, unhealthy",
            "health_rating": "unhealthy",
            "concerns": "sodium, sugar, artificial ingredients"
        }
    },
    
    # Healthy Eating Choices
    {
        "id": "health_001",
        "text": "Reducing sodium intake is crucial for heart health. Instead of salt, use herbs like basil, oregano, and thyme, or spices like cumin, turmeric, and paprika. Citrus juice, vinegar, and garlic also add flavor without sodium. Aim for less than 2,300mg of sodium per day.",
        "metadata": {
            "category": "healthy_choice",
            "topic": "sodium_reduction",
            "keywords": "low sodium, herbs, spices, heart health, blood pressure",
            "health_rating": "very_healthy",
            "goal": "reduce sodium"
        }
    },
    {
        "id": "health_002",
        "text": "Portion control is essential for maintaining a healthy weight. Use smaller plates, measure servings, and avoid eating directly from packages. A serving of protein should be about the size of your palm, carbs the size of your fist, and fats the size of your thumb.",
        "metadata": {
            "category": "healthy_choice",
            "topic": "portion_control",
            "keywords": "portion size, weight management, serving size, mindful eating",
            "health_rating": "healthy",
            "goal": "weight management"
        }
    },
    {
        "id": "health_003",
        "text": "The Mediterranean diet emphasizes olive oil, fish, whole grains, legumes, fruits, and vegetables while limiting red meat and processed foods. Studies show it reduces risk of heart disease, stroke, and cognitive decline. It's not just a diet but a sustainable lifestyle approach to eating.",
        "metadata": {
            "category": "healthy_choice",
            "topic": "diet_pattern",
            "keywords": "mediterranean diet, olive oil, heart health, longevity, whole foods",
            "health_rating": "very_healthy",
            "goal": "overall health"
        }
    },
    {
        "id": "health_004",
        "text": "Meal prepping on weekends saves time and promotes healthier eating throughout the week. Prepare grains, wash and chop vegetables, and cook proteins in batches. Store in portioned containers. This reduces reliance on fast food and makes healthy choices convenient.",
        "metadata": {
            "category": "healthy_choice",
            "topic": "meal_preparation",
            "keywords": "meal prep, batch cooking, time saving, planning, convenience",
            "health_rating": "healthy",
            "goal": "consistency"
        }
    },
    {
        "id": "health_005",
        "text": "Combining protein with fiber at each meal helps maintain stable blood sugar and promotes satiety. For example, pair grilled chicken with roasted vegetables, or add beans to a whole grain salad. This combination slows digestion and provides sustained energy without blood sugar spikes.",
        "metadata": {
            "category": "healthy_choice",
            "topic": "nutrient_pairing",
            "keywords": "protein fiber combo, blood sugar, satiety, balanced meals, energy",
            "health_rating": "very_healthy",
            "goal": "balanced nutrition"
        }
    }
]
```

### Step 5.4: Add Documents to ChromaDB

```python
# Extract the components ChromaDB needs
ids = [doc["id"] for doc in documents]
texts = [doc["text"] for doc in documents]
metadatas = [doc["metadata"] for doc in documents]

# Add to collection
# ChromaDB will automatically generate embeddings using its default model
collection.add(
    ids=ids,
    documents=texts,
    metadatas=metadatas
)

print(f"Added {len(documents)} documents to the collection")
```

---

## 6. Complete Working Example

Here's a complete, runnable script:

```python
#!/usr/bin/env python3
"""
Cooking Knowledge Base with ChromaDB
=====================================
A complete example of building a semantic search system
for cooking methods, foods, and healthy eating choices.
"""

import chromadb
from chromadb.config import Settings

def create_cooking_knowledge_base():
    """Initialize ChromaDB and create the cooking collection."""
    
    # Use persistent storage
    client = chromadb.PersistentClient(path="./cooking_db")
    
    # Delete existing collection if it exists (for fresh start)
    try:
        client.delete_collection("cooking_knowledge")
    except:
        pass
    
    # Create collection
    collection = client.create_collection(
        name="cooking_knowledge",
        metadata={"description": "Cooking methods, foods, and healthy choices"}
    )
    
    return client, collection

def add_cooking_documents(collection):
    """Add all cooking documents to the collection."""
    
    # [Include all documents from Step 5.3 here]
    documents = [
        # Cooking Methods
        {
            "id": "method_001",
            "text": "Grilling is a healthy cooking method that uses direct heat to cook food quickly. It allows fat to drip away from meat, reducing overall fat content. Best for lean proteins like chicken breast, fish, and vegetables.",
            "metadata": {
                "category": "cooking_method",
                "method_type": "dry_heat",
                "keywords": "grilling, bbq, outdoor cooking, char, direct heat",
                "health_rating": "healthy",
                "best_for": "proteins, vegetables"
            }
        },
        {
            "id": "method_002", 
            "text": "Steaming is one of the healthiest cooking methods available. Food is cooked by surrounding it with steam, preserving nutrients, color, and texture. No added fats are required. Ideal for vegetables, fish, dumplings, and delicate foods.",
            "metadata": {
                "category": "cooking_method",
                "method_type": "moist_heat",
                "keywords": "steaming, healthy, nutrient preservation, no oil",
                "health_rating": "very_healthy",
                "best_for": "vegetables, fish, dumplings"
            }
        },
        {
            "id": "method_003",
            "text": "Deep frying submerges food completely in hot oil. While it creates crispy results, it significantly increases calorie and fat content. This method should be used sparingly for health-conscious eating.",
            "metadata": {
                "category": "cooking_method",
                "method_type": "dry_heat",
                "keywords": "deep frying, oil, crispy, high calorie",
                "health_rating": "unhealthy",
                "best_for": "occasional treats"
            }
        },
        # Food Types
        {
            "id": "food_001",
            "text": "Leafy green vegetables like spinach, kale, and Swiss chard are nutritional powerhouses. They're rich in vitamins A, C, K, and folate. Low in calories but high in fiber.",
            "metadata": {
                "category": "food_type",
                "food_group": "vegetables",
                "keywords": "leafy greens, spinach, kale, vitamins, fiber",
                "health_rating": "very_healthy"
            }
        },
        {
            "id": "food_002",
            "text": "Lean proteins include chicken breast, turkey, fish, tofu, and legumes. Fish like salmon provides omega-3 fatty acids beneficial for heart and brain health.",
            "metadata": {
                "category": "food_type",
                "food_group": "proteins",
                "keywords": "lean protein, chicken, fish, omega-3",
                "health_rating": "very_healthy"
            }
        },
        {
            "id": "food_003",
            "text": "Whole grains such as quinoa, brown rice, and oats provide complex carbohydrates and fiber. They provide sustained energy and help maintain stable blood sugar levels.",
            "metadata": {
                "category": "food_type",
                "food_group": "grains",
                "keywords": "whole grains, quinoa, fiber, complex carbs",
                "health_rating": "healthy"
            }
        },
        # Healthy Choices
        {
            "id": "health_001",
            "text": "The Mediterranean diet emphasizes olive oil, fish, whole grains, legumes, fruits, and vegetables. Studies show it reduces risk of heart disease and promotes longevity.",
            "metadata": {
                "category": "healthy_choice",
                "topic": "diet_pattern",
                "keywords": "mediterranean diet, olive oil, heart health",
                "health_rating": "very_healthy"
            }
        },
        {
            "id": "health_002",
            "text": "Combining protein with fiber at each meal helps maintain stable blood sugar and promotes satiety. Pair grilled chicken with roasted vegetables for a balanced meal.",
            "metadata": {
                "category": "healthy_choice",
                "topic": "nutrient_pairing",
                "keywords": "protein fiber, blood sugar, balanced meals",
                "health_rating": "very_healthy"
            }
        },
        {
            "id": "health_003",
            "text": "Reducing sodium intake is crucial for heart health. Use herbs and spices instead of salt. Basil, oregano, cumin, and turmeric add flavor without sodium.",
            "metadata": {
                "category": "healthy_choice",
                "topic": "sodium_reduction",
                "keywords": "low sodium, herbs, spices, heart health",
                "health_rating": "very_healthy"
            }
        }
    ]
    
    # Add to collection
    collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["text"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )
    
    return len(documents)

def semantic_search(collection, query, n_results=3):
    """Perform semantic search on the collection."""
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

def filtered_search(collection, query, category=None, health_rating=None, n_results=3):
    """Search with metadata filters."""
    
    where_filter = {}
    if category:
        where_filter["category"] = category
    if health_rating:
        where_filter["health_rating"] = health_rating
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter if where_filter else None,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

def print_results(results, query):
    """Pretty print search results."""
    
    print(f"\n{'='*60}")
    print(f"Query: \"{query}\"")
    print('='*60)
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = 1 - distance  # Convert distance to similarity
        print(f"\n--- Result {i+1} (Similarity: {similarity:.2%}) ---")
        print(f"Category: {metadata.get('category', 'N/A')}")
        print(f"Health Rating: {metadata.get('health_rating', 'N/A')}")
        print(f"Keywords: {metadata.get('keywords', 'N/A')}")
        print(f"\nContent: {doc[:200]}...")

# Main execution
if __name__ == "__main__":
    print("Initializing Cooking Knowledge Base...")
    client, collection = create_cooking_knowledge_base()
    
    print("Adding documents...")
    count = add_cooking_documents(collection)
    print(f"Added {count} documents\n")
    
    # Example searches
    print("\n" + "="*60)
    print("EXAMPLE SEARCHES")
    print("="*60)
    
    # Search 1: General health query
    results = semantic_search(collection, "healthy ways to cook chicken")
    print_results(results, "healthy ways to cook chicken")
    
    # Search 2: Nutrition query
    results = semantic_search(collection, "foods high in vitamins and fiber")
    print_results(results, "foods high in vitamins and fiber")
    
    # Search 3: Filtered search - only cooking methods
    results = filtered_search(
        collection, 
        "low fat cooking",
        category="cooking_method"
    )
    print_results(results, "low fat cooking (cooking methods only)")
    
    # Search 4: Filtered by health rating
    results = filtered_search(
        collection,
        "how to eat better",
        health_rating="very_healthy"
    )
    print_results(results, "how to eat better (very healthy items only)")
```

---

## 7. Advanced: Adding Keywords & Metadata

### Sentence-Level Keyword Tagging

For more granular search, you can tag specific sentences:

```python
def create_sentence_level_embeddings(collection):
    """Add documents with sentence-level keyword tagging."""
    
    sentence_documents = [
        {
            "id": "sent_001",
            "text": "Grilling allows fat to drip away from meat.",
            "metadata": {
                "parent_doc": "method_001",
                "sentence_keywords": "grilling, fat reduction, meat",
                "topic": "health_benefit",
                "cooking_method": "grilling"
            }
        },
        {
            "id": "sent_002",
            "text": "Steaming retains up to 90% of water-soluble vitamins.",
            "metadata": {
                "parent_doc": "method_002",
                "sentence_keywords": "steaming, vitamins, nutrient retention",
                "topic": "nutrition",
                "cooking_method": "steaming"
            }
        },
        {
            "id": "sent_003",
            "text": "Salmon provides omega-3 fatty acids beneficial for heart and brain.",
            "metadata": {
                "parent_doc": "food_002",
                "sentence_keywords": "salmon, omega-3, heart health, brain health",
                "topic": "nutrition",
                "food_type": "fish"
            }
        },
        {
            "id": "sent_004",
            "text": "Use herbs and spices instead of salt to reduce sodium.",
            "metadata": {
                "parent_doc": "health_001",
                "sentence_keywords": "herbs, spices, low sodium, salt alternative",
                "topic": "sodium_reduction",
                "health_goal": "heart_health"
            }
        }
    ]
    
    collection.add(
        ids=[doc["id"] for doc in sentence_documents],
        documents=[doc["text"] for doc in sentence_documents],
        metadatas=[doc["metadata"] for doc in sentence_documents]
    )

### Using Custom Embedding Models

```python
from sentence_transformers import SentenceTransformer

# Use a specific model for better domain performance
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings manually
texts = ["Grilling is healthy", "Steaming preserves nutrients"]
embeddings = model.encode(texts).tolist()

# Add with pre-computed embeddings
collection.add(
    ids=["custom_001", "custom_002"],
    embeddings=embeddings,
    documents=texts,
    metadatas=[{"source": "custom"}, {"source": "custom"}]
)
```

---

## 8. Querying Your Knowledge Base

### Basic Semantic Search

```python
# Find similar documents based on meaning
results = collection.query(
    query_texts=["What's the best way to cook vegetables without losing nutrients?"],
    n_results=5
)
```

### Filtered Search

```python
# Search only within a specific category
results = collection.query(
    query_texts=["healthy protein options"],
    n_results=3,
    where={"category": "food_type"}
)

# Search with multiple conditions
results = collection.query(
    query_texts=["cooking methods"],
    n_results=3,
    where={
        "$and": [
            {"category": "cooking_method"},
            {"health_rating": {"$in": ["healthy", "very_healthy"]}}
        ]
    }
)
```

### Keyword + Semantic Search

```python
# Combine semantic search with keyword filtering
results = collection.query(
    query_texts=["heart healthy eating"],
    n_results=5,
    where_document={"$contains": "omega-3"}  # Must contain this keyword
)
```

### Integration with an LLM (RAG Pattern)

```python
def ask_cooking_question(collection, question, llm_client):
    """Use retrieved context to answer questions with an LLM."""
    
    # Get relevant documents
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    # Build context from results
    context = "\n\n".join(results['documents'][0])
    
    # Create prompt for LLM
    prompt = f"""Based on the following information about cooking and nutrition:

{context}

Please answer this question: {question}

Provide a helpful, accurate answer based only on the information provided."""

    # Send to your LLM (example with generic API)
    response = llm_client.generate(prompt)
    
    return response, results  # Return both answer and sources

# Example usage:
# answer, sources = ask_cooking_question(
#     collection, 
#     "What's the healthiest way to cook fish?",
#     my_llm_client
# )
```

---

## Summary

### What You've Learned

1. **Embeddings** convert text into numerical vectors that capture meaning
2. **Similar meanings = similar vectors** (close together in vector space)
3. **ChromaDB** stores and searches these vectors efficiently
4. **Metadata** allows filtering and categorization
5. **RAG** combines retrieval with LLMs for informed answers

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Semantic Understanding** | Find relevant info even with different wording |
| **Scalability** | Handle thousands of documents efficiently |
| **Flexibility** | Filter by category, rating, keywords |
| **LLM Integration** | Provide context for better AI responses |
