# Code Snippet Q&A System with ChromaDB + Ollama
## Retrieval Augmented Generation (RAG) for Code

---

## Table of Contents
1. [System Overview](#system-overview)
2. [How RAG Works for Code](#how-rag-works-for-code)
3. [Architecture](#architecture)
4. [Setup & Installation](#setup--installation)
5. [Code Snippet Database Structure](#code-snippet-database-structure)
6. [Building the Knowledge Base](#building-the-knowledge-base)
7. [Query & Generation System](#query--generation-system)
8. [Running the System](#running-the-system)

---

## System Overview

This system answers coding questions by:
1. **Retrieving** relevant code snippets from ChromaDB based on semantic similarity
2. **Augmenting** the prompt with retrieved examples
3. **Generating** new code using Ollama with context from similar examples

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CODE Q&A SYSTEM FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

User Question: "Create a responsive navbar with dropdown"
         │
         ▼
┌─────────────────┐     ┌──────────────────────────────────────────┐
│ Embed Question  │────▶│ ChromaDB: Find similar code snippets     │
└─────────────────┘     └──────────────────────────────────────────┘
                                          │
                                          ▼
                        ┌──────────────────────────────────────────┐
                        │ Retrieved Snippets:                      │
                        │  • navbar-basic.html (0.89 similarity)   │
                        │  • dropdown-menu.html (0.85 similarity)  │
                        │  • responsive-header.html (0.78 sim)     │
                        └──────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ AUGMENTED PROMPT TO OLLAMA:                                         │
│ ─────────────────────────────────────────────────────────────────── │
│ Based on these examples:                                            │
│ [Retrieved code snippets inserted here]                             │
│                                                                     │
│ Generate: A responsive navbar with dropdown                         │
└─────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OLLAMA GENERATES NEW CODE                                           │
│ Using patterns from retrieved examples                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## How RAG Works for Code

### Traditional LLM vs RAG Approach

```
TRADITIONAL LLM:                         RAG APPROACH:
┌─────────────┐                         ┌─────────────┐
│   Question  │                         │   Question  │
└──────┬──────┘                         └──────┬──────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                         ┌─────────────────┐
│    LLM      │                         │ Vector Search   │
│ (training   │                         │ (your codebase) │
│  knowledge) │                         └────────┬────────┘
└──────┬──────┘                                  │
       │                                         ▼
       │                                ┌─────────────────┐
       │                                │ Retrieved Code  │
       │                                │ + Question      │
       │                                └────────┬────────┘
       │                                         │
       │                                         ▼
       │                                ┌─────────────────┐
       │                                │      LLM        │
       │                                └────────┬────────┘
       ▼                                         ▼
┌─────────────┐                         ┌─────────────────┐
│ Generic     │                         │ Contextual      │
│ Response    │                         │ Response        │
└─────────────┘                         └─────────────────┘

✗ May hallucinate                       ✓ Grounded in real code
✗ No custom patterns                    ✓ Uses your patterns
✗ Outdated knowledge                    ✓ Current codebase
```

### Why RAG for Code Generation?

| Benefit | Explanation |
|---------|-------------|
| **Consistency** | Generated code follows your existing patterns |
| **Accuracy** | Reduces hallucination with real examples |
| **Customization** | Uses your specific libraries/frameworks |
| **Updatable** | Add new snippets without retraining |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────┐
                    │     CODE SNIPPETS           │
                    │  ───────────────────────    │
                    │  • HTML/Tailwind examples   │
                    │  • YACC/LEX templates       │
                    │  • Component patterns       │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                        INDEXER (build_db.py)                       │
│  ─────────────────────────────────────────────────────────────────│
│  1. Load snippet files (JSON format)                              │
│  2. Extract: code, keywords, description, category                │
│  3. Create embeddings for searchable text                         │
│  4. Store in ChromaDB with metadata                               │
└───────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                          CHROMADB                                  │
│  ─────────────────────────────────────────────────────────────────│
│  Collection: "code_snippets"                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ID          │ Embedding      │ Document      │ Metadata      │ │
│  ├─────────────┼────────────────┼───────────────┼───────────────┤ │
│  │ navbar_001  │ [0.2, -0.4...] │ <nav>...</nav>│ {category:    │ │
│  │             │                │               │  "tailwind",  │ │
│  │             │                │               │  keywords:    │ │
│  │             │                │               │  ["navbar"]}  │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                     QUERY SYSTEM (code_qa.py)                      │
│  ─────────────────────────────────────────────────────────────────│
│  1. User asks coding question                                      │
│  2. Embed question, search ChromaDB                                │
│  3. Retrieve top-k relevant snippets                               │
│  4. Build augmented prompt with examples                           │
│  5. Send to Ollama for generation                                  │
│  6. Return generated code                                          │
└───────────────────────────────────────────────────────────────────┘
```

---

## Setup & Installation

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve &

# Pull required models
ollama pull nomic-embed-text    # For embeddings
ollama pull codellama           # For code generation
# OR
ollama pull deepseek-coder      # Alternative code model
```

### Step 2: Install Python Dependencies

```bash
pip install chromadb ollama
```

### Step 3: Verify Setup

```python
import ollama

# Test embedding
emb = ollama.embeddings(model='nomic-embed-text', prompt='navbar')
print(f"Embedding dims: {len(emb['embedding'])}")

# Test generation
resp = ollama.chat(model='codellama', messages=[
    {'role': 'user', 'content': 'Write hello world in HTML'}
])
print(resp['message']['content'])
```

---

## Code Snippet Database Structure

### Snippet JSON Format

Each snippet is stored with rich metadata for better retrieval:

```json
{
  "id": "tailwind_navbar_001",
  "category": "tailwind",
  "subcategory": "navigation",
  "keywords": ["navbar", "navigation", "header", "menu", "responsive"],
  "description": "Responsive navigation bar with mobile hamburger menu",
  "search_text": "navbar navigation header menu responsive mobile hamburger",
  "code": "<nav class=\"bg-gray-800\">...</nav>",
  "language": "html",
  "dependencies": ["tailwindcss"],
  "difficulty": "beginner"
}
```

### Search Text Strategy

The `search_text` field combines multiple elements for better matching:

```
search_text = keywords + description + category + subcategory

Example:
"navbar navigation header responsive tailwind component mobile menu dropdown"
```

This is what gets embedded and searched, not the code itself.

---

## Embedding Strategy

### What Gets Embedded?

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMBEDDING STRATEGY                            │
└─────────────────────────────────────────────────────────────────┘

NOT Embedded (stored as metadata):     EMBEDDED (searchable):
┌─────────────────────────────────┐   ┌─────────────────────────┐
│ • Actual code                   │   │ • Keywords              │
│ • Language identifier           │   │ • Description           │
│ • Dependencies                  │   │ • Category names        │
│ • Difficulty level              │   │ • Semantic search text  │
└─────────────────────────────────┘   └─────────────────────────┘

WHY?
─────
• Code syntax doesn't match natural language queries
• "Create a navbar" should match navbar snippets
• Keywords bridge user intent to code solutions
```

### Similarity Matching

```
User Query: "I need a dropdown menu for navigation"
                    │
                    ▼ Embed query
            [0.23, -0.45, 0.12, ...]
                    │
                    ▼ Cosine similarity search
┌─────────────────────────────────────────────────────────────┐
│ Top Matches:                                                 │
│                                                              │
│ 1. "dropdown menu navigation select options" (sim: 0.91)    │
│    → Returns: dropdown_menu.html                             │
│                                                              │
│ 2. "navbar navigation header menu" (sim: 0.84)              │
│    → Returns: navbar_basic.html                              │
│                                                              │
│ 3. "accordion expandable menu" (sim: 0.72)                  │
│    → Returns: accordion.html                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## RAG Prompt Construction

### Building the Augmented Prompt

```python
def build_rag_prompt(question: str, retrieved_snippets: list) -> str:
    """
    Construct prompt with retrieved code examples.
    """
    prompt = """You are a code generation assistant. 
Use the following code examples as reference patterns.

### REFERENCE CODE EXAMPLES:
"""
    
    for snippet in retrieved_snippets:
        prompt += f"""
--- Example: {snippet['description']} ---
Category: {snippet['category']}
Keywords: {', '.join(snippet['keywords'])}

```{snippet['language']}
{snippet['code']}
```
"""
    
    prompt += f"""
### USER REQUEST:
{question}

### INSTRUCTIONS:
1. Use patterns from the examples above
2. Adapt the code to match the user's specific request
3. Use the same styling conventions (Tailwind classes, etc.)
4. Provide complete, working code

### GENERATED CODE:
"""
    return prompt
```

---

## File Structure

```
code_qa_system/
├── README.md                    # Quick start guide
├── tutorial.md                  # This documentation
├── requirements.txt             # Python dependencies
├── snippets/                    # Code snippet database
│   ├── tailwind_components.json # HTML/Tailwind snippets
│   └── yacc_lex_templates.json  # YACC/LEX snippets
├── build_db.py                  # Indexes snippets into ChromaDB
├── code_qa.py                   # Q&A system with RAG
└── chroma_db/                   # ChromaDB storage (created)
```

---

## Running the System

### Quick Start

```bash
# 1. Ensure Ollama is running
ollama serve &

# 2. Build the ChromaDB database
python build_db.py

# 3. Run interactive Q&A
python code_qa.py

# 4. Ask questions!
> Create a card component with image and title
> Write a lexer for arithmetic expressions
> Build a responsive footer with social links
```

### Example Session

```
═══════════════════════════════════════════════════════════════
🔧 CODE SNIPPET Q&A SYSTEM
═══════════════════════════════════════════════════════════════

Enter your coding question (or 'quit' to exit):
> Create a hero section with centered text and gradient background

🔍 Searching knowledge base...
📚 Found 3 relevant examples:
   • hero_section_basic (similarity: 0.91)
   • gradient_background (similarity: 0.87)
   • centered_content (similarity: 0.82)

🤖 Generating code with Ollama...

═══════════════════════════════════════════════════════════════
GENERATED CODE:
═══════════════════════════════════════════════════════════════

<section class="min-h-screen bg-gradient-to-r from-purple-500 
                to-pink-500 flex items-center justify-center">
  <div class="text-center text-white px-4">
    <h1 class="text-5xl font-bold mb-4">Welcome to Our Site</h1>
    <p class="text-xl mb-8">Discover amazing things with us</p>
    <button class="bg-white text-purple-600 px-8 py-3 
                   rounded-full font-semibold hover:bg-gray-100">
      Get Started
    </button>
  </div>
</section>

═══════════════════════════════════════════════════════════════
```

---

## Advanced: YACC/LEX Integration

The system also includes YACC/LEX templates for parser generation:

```
Query: "Create a lexer for JSON tokens"

Retrieved Examples:
  • basic_lexer.l - Token patterns
  • string_handling.l - Quoted strings
  • number_patterns.l - Numeric literals

Generated:
  Complete .l file with JSON token definitions
```

See `yacc_lex_templates.json` for available templates.

---

## Summary

This RAG-based code Q&A system:

1. **Stores** code snippets with semantic keywords in ChromaDB
2. **Retrieves** relevant examples using embedding similarity
3. **Augments** prompts with real code patterns
4. **Generates** new code following your conventions

The result: More accurate, consistent, and contextual code generation than vanilla LLM prompting.