# Quick Start Guide

Get the FastText Keyword Classifier running in 3 minutes!

## Prerequisites

- Docker and Docker Compose installed
- 2GB free disk space
- Port 8000 available

## 1. Start the Service

```bash
# Clone or navigate to the project directory
cd /path/to/fasttext-classifier

# Build and start
docker-compose up --build
```

Wait for the build to complete (first time ~2-3 minutes). You'll see:
```
fasttext-api_1  | INFO:     Application startup complete.
fasttext-api_1  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 2. Open the Web Interface

**Simply open your browser and go to:** http://localhost:8000

You'll see a beautiful interface with:
- 📊 **Dashboard** - Real-time statistics
- 🔍 **Predict Keywords** - Upload documents or paste text
- 🎓 **Train Model** - Add training data and train
- 🗂️ **Manage Keywords** - View and delete keywords

### Using the Web Interface:

1. **Click the "Train Model" tab**
2. **Add some example data:**
   - Keyword: `technology`
   - Sentences: 
     ```
     The smartphone features AI capabilities
     Cloud computing is expanding rapidly
     Software development uses modern tools
     ```
3. **Click "Add Examples"**
4. **Click "Train Model Now"**
5. **Go to "Predict Keywords" tab**
6. **Paste some text or upload a file**
7. **Click "Analyze Document"**
8. **See your results!**

## 3. Or Use the API / Test Script

## 3. Or Use the API / Test Script

If you prefer command-line testing, run:

```bash
python3 test_api.py
```

This will:
- ✓ Add sample training data (5 categories)
- ✓ Train the model
- ✓ Make test predictions
- ✓ Show results with confidence scores

## 4. API Usage (Optional)

If you want to use curl or code instead of the web interface:

### Add training data:

```bash
curl -X POST http://localhost:8000/train/add \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "music",
    "sentences": [
      "The concert was amazing with great performances",
      "New album released by popular artist",
      "Music festival attracts thousands of fans"
    ]
  }'
```

### Train the model:

```bash
curl -X POST http://localhost:8000/train/build
```

### Test with your text:

```bash
curl -X POST "http://localhost:8000/predict/text?text=The band performed live last night"
```

## 5. Interactive API Documentation

Open in your browser: **http://localhost:8000/docs**

You can:
- Test all endpoints interactively
- Upload files for prediction
- See request/response schemas
- Try different queries

## Common Commands

```bash
# Check status
curl http://localhost:8000/

# List keywords
curl http://localhost:8000/keywords

# Get model info
curl http://localhost:8000/model/info

# Stop the service
docker-compose down

# View logs
docker-compose logs -f
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) for implementation details
- Run [demo_fasttext_executable.sh](demo_fasttext_executable.sh) to see FastText C++ in action

## Troubleshooting

**Port 8000 already in use?**
```bash
# Edit docker-compose.yml, change ports to:
ports:
  - "8080:8000"  # Now use localhost:8080
```

**Container won't start?**
```bash
# Check logs
docker-compose logs fasttext-api

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**API returns "Model not trained"?**
```bash
# Make sure you trained the model
curl -X POST http://localhost:8000/train/build
```

## Example Python Client

```python
import requests

# Add training data
data = {
    "keyword": "cooking",
    "sentences": [
        "Recipe for delicious chocolate cake",
        "How to cook perfect pasta",
        "Baking tips for beginners"
    ]
}
requests.post("http://localhost:8000/train/add", json=data)

# Train
requests.post("http://localhost:8000/train/build")

# Predict
text = "Best way to bake a cake at home"
response = requests.post(
    "http://localhost:8000/predict/text",
    params={"text": text}
)
print(response.json())
```

## Data Persistence

Your training data and models are saved in:
- `./data/training_data.json`
- `./models/keyword_model.bin`

These persist even when you stop/restart the container!

---

**Ready to classify!** 🚀

For questions or issues, check the full [README.md](README.md)
