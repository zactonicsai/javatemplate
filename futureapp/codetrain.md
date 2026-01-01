# Code Snippet Q&A System

A RAG (Retrieval Augmented Generation) system for generating code from natural language queries using ChromaDB and Ollama.

## Features

- 🔍 **Semantic Search**: Find code by meaning, not just keywords
- 🧩 **HTML/Tailwind Components**: Navigation, forms, cards, modals, etc.
- 🔧 **YACC/LEX Templates**: Lexers, parsers, AST builders
- 🤖 **RAG Generation**: LLM generates code based on retrieved examples

## Quick Start

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve &

# Pull required models
ollama pull nomic-embed-text    # For embeddings
ollama pull codellama           # For code generation

# Install Python dependencies
pip install -r requirements.txt
```

### Build & Run

```bash
# 1. Build the database
python build_db.py

# 2. Start the Q&A system
python code_qa.py
```

### Example Session

```
🎯 Your question: Create a responsive navbar with dropdown menu

🔍 Searching knowledge base...
📚 Found 3 relevant examples:
   • tw_navbar_dropdown (similarity: 0.91)
   • tw_navbar_basic (similarity: 0.87)
   • tw_sidebar_nav (similarity: 0.72)

🤖 Generating code with codellama...

============================================================
GENERATED CODE
============================================================
<nav class="bg-white shadow-lg">
  ...
</nav>
```

## Project Structure

```
code_qa_system/
├── tutorial.md              # Full documentation
├── build_db.py              # Database builder
├── code_qa.py               # Q&A system
├── requirements.txt         # Dependencies
├── snippets/                # Code snippet JSON files
│   ├── tailwind_components.json
│   └── yacc_lex_templates.json
└── chroma_db/               # ChromaDB storage (created)
```

## Adding Custom Snippets

Create a new JSON file in `snippets/`:

```json
{
  "metadata": { "name": "My Snippets" },
  "snippets": [
    {
      "id": "unique_id",
      "category": "category",
      "subcategory": "subcategory",
      "keywords": ["keyword1", "keyword2"],
      "description": "What this code does",
      "search_text": "keywords for semantic search",
      "language": "html",
      "code": "<div>Your code here</div>",
      "dependencies": [],
      "difficulty": "beginner"
    }
  ]
}
```

Then rebuild: `python build_db.py`

## How It Works

```
User Question
     │
     ▼
┌─────────────┐     ┌──────────────┐
│ Embed Query │────▶│  ChromaDB    │
└─────────────┘     │ Vector Search│
                    └──────┬───────┘
                           │
     ┌─────────────────────┘
     ▼
┌────────────────────────┐
│ Retrieved Examples:    │
│ • navbar_dropdown      │
│ • navbar_basic         │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Augmented Prompt:      │
│ Examples + Question    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Ollama LLM generates   │
│ new code using context │
└────────────────────────┘
```

## Command Line Options

```bash
# Interactive mode (default)
python code_qa.py

# Single query
python code_qa.py -q "Create a login form"

# Use different model
python code_qa.py -m deepseek-coder

# Retrieve more examples
python code_qa.py -k 5
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Run `ollama serve` first |
| "Model not found" | Run `ollama pull <model>` |
| "Database not found" | Run `python build_db.py` |
| Poor results | Lower similarity threshold in code_qa.py |

## License

MIT - See tutorial.md for full documentation.