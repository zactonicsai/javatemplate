# FastText Keyword Classification API

A Docker-based FastText API for training keyword classification models and predicting the top 5 matching keywords from uploaded documents.

## Features

- 🚀 FastText compiled from source for optimal performance
- 📝 REST API for training and prediction
- 🏷️ Train models with keywords and example sentences
- 📄 Upload documents to get top 5 matching keywords
- 💾 Persistent storage for training data and models
- 🔄 Easy model retraining with new data

## Quick Start

### 1. Build and Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### 2. Build and Run with Docker

```bash
docker build -t fasttext-api .
docker run -p 8000:8000 -v $(pwd)/models:/app/models -v $(pwd)/data:/app/data fasttext-api
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Usage Examples

### 1. Check API Status

```bash
curl http://localhost:8000/
```

### 2. Add Training Data

Add examples for a single keyword:

```bash
curl -X POST http://localhost:8000/train/add \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "technology",
    "sentences": [
      "The latest smartphone features advanced AI capabilities",
      "Cloud computing revolutionizes data storage",
      "Artificial intelligence is transforming industries"
    ]
  }'
```

### 3. Add Multiple Keywords (Batch)

```bash
curl -X POST http://localhost:8000/train/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "keyword": "sports",
      "sentences": [
        "The basketball team won the championship",
        "Football season starts next month",
        "Olympic athletes train year-round"
      ]
    },
    {
      "keyword": "finance",
      "sentences": [
        "Stock market reaches new highs",
        "Investment portfolio diversification is key",
        "Cryptocurrency prices fluctuate daily"
      ]
    },
    {
      "keyword": "health",
      "sentences": [
        "Regular exercise improves cardiovascular health",
        "Balanced diet essential for wellness",
        "Mental health awareness is increasing"
      ]
    }
  ]'
```

### 4. List All Keywords

```bash
curl http://localhost:8000/keywords
```

### 5. Train the Model

After adding training data, build the model:

```bash
curl -X POST http://localhost:8000/train/build
```

### 6. Predict from Text

```bash
curl -X POST "http://localhost:8000/predict/text?text=The+new+iPhone+has+incredible+processing+power"
```

### 7. Predict from File Upload

```bash
# Create a test document
echo "The stock market showed strong gains today as tech companies reported earnings." > test_doc.txt

# Upload and predict
curl -X POST http://localhost:8000/predict \
  -F "file=@test_doc.txt"
```

### 8. Delete a Keyword

```bash
curl -X DELETE http://localhost:8000/keywords/technology
```

## Response Examples

### Training Response

```json
{
  "message": "Added 3 examples for keyword 'technology'",
  "total_examples": 3
}
```

### Model Training Response

```json
{
  "message": "Model trained successfully",
  "keywords": ["technology", "sports", "finance", "health"],
  "total_keywords": 4,
  "total_examples": 12
}
```

### Prediction Response

```json
{
  "top_keywords": [
    {
      "keyword": "finance",
      "confidence": 0.92
    },
    {
      "keyword": "technology",
      "confidence": 0.65
    },
    {
      "keyword": "sports",
      "confidence": 0.15
    },
    {
      "keyword": "health",
      "confidence": 0.08
    }
  ],
  "text_preview": "The stock market showed strong gains today as tech companies reported earnings."
}
```

## Python Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# 1. Add training data
training_data = {
    "keyword": "technology",
    "sentences": [
        "The latest smartphone features advanced AI capabilities",
        "Cloud computing revolutionizes data storage"
    ]
}
response = requests.post(f"{base_url}/train/add", json=training_data)
print(response.json())

# 2. Train the model
response = requests.post(f"{base_url}/train/build")
print(response.json())

# 3. Predict from text
text = "Apple released a new MacBook with M3 chip"
response = requests.post(
    f"{base_url}/predict/text",
    params={"text": text}
)
print(response.json())

# 4. Predict from file
with open("document.txt", "rb") as f:
    response = requests.post(
        f"{base_url}/predict",
        files={"file": f}
    )
print(response.json())
```

## Data Persistence

Training data and models are persisted in the following locations:

- **Training Data**: `/app/data/training_data.json`
- **Trained Model**: `/app/models/keyword_model.bin`

These are mounted as Docker volumes, so your data persists across container restarts.

## Workflow

1. **Add Training Data**: Use `/train/add` or `/train/batch` to add keywords with example sentences
2. **Build Model**: Call `/train/build` to train the FastText model
3. **Predict**: Upload documents via `/predict` or text via `/predict/text` to get top 5 keywords
4. **Iterate**: Add more training data and retrain as needed

## Model Parameters

The FastText model is trained with these parameters:
- **Epochs**: 25
- **Learning Rate**: 1.0
- **Word N-grams**: 2
- **Dimensions**: 100
- **Loss**: Softmax

You can modify these in `server.py` in the `train_model()` function.

## Tips for Best Results

1. **More Examples**: Add at least 5-10 example sentences per keyword
2. **Diverse Examples**: Include varied sentence structures and contexts
3. **Quality Data**: Use clear, well-written examples that represent the keyword
4. **Regular Retraining**: Retrain the model after adding significant new data
5. **Balanced Data**: Try to have similar numbers of examples for each keyword

## Troubleshooting

**Model not trained error**: Make sure to call `/train/build` after adding training data

**Low confidence scores**: Add more diverse training examples for your keywords

**Empty predictions**: Ensure the uploaded document is UTF-8 encoded text

## License

This project uses FastText, which is under MIT license.
