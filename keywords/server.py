from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import fasttext
import os
import tempfile
import json
from pathlib import Path

app = FastAPI(title="FastText Keyword Classifier API")

# Paths
MODEL_PATH = "/app/models/keyword_model.bin"
TRAINING_DATA_PATH = "/app/data/training_data.json"
TEMP_TRAIN_FILE = "/app/data/train.txt"

# In-memory storage for training data
training_data: Dict[str, List[str]] = {}


class TrainingData(BaseModel):
    keyword: str
    sentences: List[str]


class PredictionResponse(BaseModel):
    top_keywords: List[Dict[str, float]]
    text_preview: str


@app.on_event("startup")
async def load_training_data():
    """Load existing training data on startup"""
    global training_data
    if os.path.exists(TRAINING_DATA_PATH):
        with open(TRAINING_DATA_PATH, 'r') as f:
            training_data = json.load(f)
        print(f"Loaded training data with {len(training_data)} keywords")


def save_training_data():
    """Save training data to disk"""
    with open(TRAINING_DATA_PATH, 'w') as f:
        json.dump(training_data, f, indent=2)


def create_fasttext_training_file():
    """Create FastText format training file from training data"""
    with open(TEMP_TRAIN_FILE, 'w', encoding='utf-8') as f:
        for keyword, sentences in training_data.items():
            # FastText format: __label__<label> <text>
            for sentence in sentences:
                # Clean the text
                clean_text = sentence.replace('\n', ' ').strip()
                if clean_text:
                    f.write(f"__label__{keyword} {clean_text}\n")


@app.get("/")
async def root():
    """API health check"""
    model_exists = os.path.exists(MODEL_PATH)
    return {
        "status": "running",
        "model_trained": model_exists,
        "keywords_count": len(training_data),
        "total_examples": sum(len(sentences) for sentences in training_data.values())
    }


@app.post("/train/add")
async def add_training_data(data: TrainingData):
    """Add or update training data for a keyword"""
    if not data.sentences:
        raise HTTPException(status_code=400, detail="At least one sentence is required")
    
    if data.keyword in training_data:
        # Append to existing sentences
        training_data[data.keyword].extend(data.sentences)
    else:
        # Create new keyword entry
        training_data[data.keyword] = data.sentences
    
    save_training_data()
    
    return {
        "message": f"Added {len(data.sentences)} examples for keyword '{data.keyword}'",
        "total_examples": len(training_data[data.keyword])
    }


@app.post("/train/batch")
async def add_batch_training_data(batch: List[TrainingData]):
    """Add multiple keywords with their training data at once"""
    added_count = 0
    
    for data in batch:
        if data.keyword in training_data:
            training_data[data.keyword].extend(data.sentences)
        else:
            training_data[data.keyword] = data.sentences
        added_count += len(data.sentences)
    
    save_training_data()
    
    return {
        "message": f"Added {added_count} examples across {len(batch)} keywords",
        "total_keywords": len(training_data)
    }


@app.post("/train/build")
async def train_model():
    """Train the FastText model with current training data"""
    if not training_data:
        raise HTTPException(status_code=400, detail="No training data available. Add data first.")
    
    try:
        # Create training file
        create_fasttext_training_file()
        
        # Count total examples
        total_examples = sum(len(sentences) for sentences in training_data.items())
        
        # Train the model
        model = fasttext.train_supervised(
            input=TEMP_TRAIN_FILE,
            epoch=25,
            lr=1.0,
            wordNgrams=2,
            dim=100,
            loss='softmax'
        )
        
        # Save the model
        model.save_model(MODEL_PATH)
        
        return {
            "message": "Model trained successfully",
            "keywords": list(training_data.keys()),
            "total_keywords": len(training_data),
            "total_examples": total_examples
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.get("/keywords")
async def list_keywords():
    """List all trained keywords with example counts"""
    return {
        "keywords": [
            {
                "keyword": keyword,
                "example_count": len(sentences)
            }
            for keyword, sentences in training_data.items()
        ]
    }


@app.delete("/keywords/{keyword}")
async def delete_keyword(keyword: str):
    """Delete a keyword and its training data"""
    if keyword not in training_data:
        raise HTTPException(status_code=404, detail=f"Keyword '{keyword}' not found")
    
    del training_data[keyword]
    save_training_data()
    
    return {"message": f"Deleted keyword '{keyword}'"}


@app.post("/predict", response_model=PredictionResponse)
async def predict_keywords(file: UploadFile = File(...)):
    """Upload a document and get top 5 matching keywords"""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=400, 
            detail="Model not trained yet. Train the model first using /train/build"
        )
    
    try:
        # Read the uploaded file
        content = await file.read()
        text = content.decode('utf-8')
        
        # Clean the text
        clean_text = text.replace('\n', ' ').strip()
        
        if not clean_text:
            raise HTTPException(status_code=400, detail="Empty document")
        
        # Load model and predict
        model = fasttext.load_model(MODEL_PATH)
        
        # Get top 5 predictions
        labels, probabilities = model.predict(clean_text, k=5)
        
        # Format results
        top_keywords = []
        for label, prob in zip(labels, probabilities):
            # Remove __label__ prefix
            keyword = label.replace('__label__', '')
            top_keywords.append({
                "keyword": keyword,
                "confidence": float(prob)
            })
        
        # Create preview of text (first 200 chars)
        preview = text[:200] + "..." if len(text) > 200 else text
        
        return PredictionResponse(
            top_keywords=top_keywords,
            text_preview=preview
        )
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/text")
async def predict_from_text(text: str):
    """Predict keywords from raw text instead of file upload"""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Train the model first using /train/build"
        )
    
    try:
        clean_text = text.replace('\n', ' ').strip()
        
        if not clean_text:
            raise HTTPException(status_code=400, detail="Empty text")
        
        # Load model and predict
        model = fasttext.load_model(MODEL_PATH)
        labels, probabilities = model.predict(clean_text, k=5)
        
        # Format results
        top_keywords = []
        for label, prob in zip(labels, probabilities):
            keyword = label.replace('__label__', '')
            top_keywords.append({
                "keyword": keyword,
                "confidence": float(prob)
            })
        
        preview = text[:200] + "..." if len(text) > 200 else text
        
        return {
            "top_keywords": top_keywords,
            "text_preview": preview
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
