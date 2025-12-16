from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
import io

# PDF processing
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Alternative PDF library (pdfplumber is often better for complex PDFs)
try:
    import pdfplumber
    PDFPLUMBER_SUPPORT = True
except ImportError:
    PDFPLUMBER_SUPPORT = False

app = FastAPI(title="FastText Keyword Classifier API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Paths
MODEL_PATH = "/app/models/keyword_model.bin"
TRAINING_DATA_PATH = "/app/data/training_data.json"
TEMP_DIR = "/app/temp"
FASTTEXT_BIN = "/usr/local/bin/fasttext"
STATIC_DIR = "/app/static"

# In-memory storage for training data
training_data: Dict[str, List[str]] = {}


class TrainingData(BaseModel):
    keyword: str
    sentences: List[str]


class TextInput(BaseModel):
    text: str


class KeywordPrediction(BaseModel):
    keyword: str
    confidence: float


class PredictionResponse(BaseModel):
    top_keywords: List[KeywordPrediction]
    text_preview: str
    source_type: Optional[str] = "text"
    page_count: Optional[int] = None


def extract_text_from_pdf_pypdf2(file_content: bytes) -> tuple[str, int]:
    """Extract text from PDF using PyPDF2"""
    text_parts = []
    page_count = 0
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        page_count = len(pdf_reader.pages)
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        return '\n'.join(text_parts), page_count
    except Exception as e:
        raise ValueError(f"PyPDF2 extraction failed: {str(e)}")


def extract_text_from_pdf_pdfplumber(file_content: bytes) -> tuple[str, int]:
    """Extract text from PDF using pdfplumber (better for complex layouts)"""
    text_parts = []
    page_count = 0
    
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            page_count = len(pdf.pages)
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts), page_count
    except Exception as e:
        raise ValueError(f"pdfplumber extraction failed: {str(e)}")


def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    """
    Extract text from PDF using available libraries.
    Tries pdfplumber first (better quality), falls back to PyPDF2.
    Returns tuple of (extracted_text, page_count)
    """
    if not PDF_SUPPORT and not PDFPLUMBER_SUPPORT:
        raise HTTPException(
            status_code=500,
            detail="PDF support not available. Install PyPDF2 or pdfplumber: pip install PyPDF2 pdfplumber"
        )
    
    # Try pdfplumber first (generally better text extraction)
    if PDFPLUMBER_SUPPORT:
        try:
            return extract_text_from_pdf_pdfplumber(file_content)
        except ValueError:
            # Fall back to PyPDF2 if pdfplumber fails
            if PDF_SUPPORT:
                return extract_text_from_pdf_pypdf2(file_content)
            raise
    
    # Use PyPDF2 if pdfplumber not available
    if PDF_SUPPORT:
        return extract_text_from_pdf_pypdf2(file_content)
    
    raise HTTPException(status_code=500, detail="No PDF library available")


def is_pdf_file(filename: str, content: bytes) -> bool:
    """Check if file is a PDF based on filename or magic bytes"""
    # Check filename extension
    if filename and filename.lower().endswith('.pdf'):
        return True
    
    # Check PDF magic bytes (PDF files start with %PDF-)
    if content and content[:5] == b'%PDF-':
        return True
    
    return False


@app.on_event("startup")
async def load_training_data():
    """Load existing training data on startup"""
    global training_data
    if os.path.exists(TRAINING_DATA_PATH):
        with open(TRAINING_DATA_PATH, 'r') as f:
            training_data = json.load(f)
        print(f"Loaded training data with {len(training_data)} keywords")
    
    # Ensure temp directory exists
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Ensure static directory exists
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    # Log PDF support status
    print(f"PDF Support - PyPDF2: {PDF_SUPPORT}, pdfplumber: {PDFPLUMBER_SUPPORT}")


@app.get("/", include_in_schema=False)
async def serve_web_interface():
    """Serve the web interface"""
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        # Return API info if no web interface
        return await root_api()


@app.get("/api")
async def root_api():
    """API health check"""
    model_exists = os.path.exists(MODEL_PATH)
    
    # Check FastText version
    try:
        result = subprocess.run(
            [FASTTEXT_BIN, "--help"],
            capture_output=True,
            text=True
        )
        fasttext_available = result.returncode == 0
    except:
        fasttext_available = False
    
    return {
        "status": "running",
        "fasttext_available": fasttext_available,
        "model_trained": model_exists,
        "keywords_count": len(training_data),
        "total_examples": sum(len(sentences) for sentences in training_data.values()),
        "pdf_support": {
            "available": PDF_SUPPORT or PDFPLUMBER_SUPPORT,
            "pypdf2": PDF_SUPPORT,
            "pdfplumber": PDFPLUMBER_SUPPORT
        }
    }


def save_training_data():
    """Save training data to disk"""
    with open(TRAINING_DATA_PATH, 'w') as f:
        json.dump(training_data, f, indent=2)


def create_fasttext_training_file(filepath: str):
    """Create FastText format training file from training data"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for keyword, sentences in training_data.items():
            # FastText format: __label__<label> <text>
            for sentence in sentences:
                # Clean the text - remove newlines and extra spaces
                clean_text = ' '.join(sentence.replace('\n', ' ').split())
                if clean_text:
                    f.write(f"__label__{keyword} {clean_text}\n")


def run_fasttext_command(args: List[str], input_text: str = None) -> subprocess.CompletedProcess:
    """Run FastText executable with given arguments"""
    try:
        cmd = [FASTTEXT_BIN] + args
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"FastText command failed: {e.stderr}"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="FastText executable not found"
        )


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
    """Train the FastText model with current training data using C++ executable"""
    if not training_data:
        raise HTTPException(status_code=400, detail="No training data available. Add data first.")
    
    # Create temporary training file
    train_file = os.path.join(TEMP_DIR, "train.txt")
    
    try:
        # Create training file
        create_fasttext_training_file(train_file)
        
        # Count total examples
        total_examples = sum(len(sentences) for sentences in training_data.values())
        
        # Train the model using FastText C++ executable
        # Command: fasttext supervised -input train.txt -output model
        model_prefix = os.path.join("/app/models", "keyword_model")
        
        args = [
            "supervised",
            "-input", train_file,
            "-output", model_prefix,
            "-epoch", "25",
            "-lr", "1.0",
            "-wordNgrams", "2",
            "-dim", "100",
            "-loss", "softmax"
        ]
        
        result = run_fasttext_command(args)
        
        # FastText creates model_prefix.bin automatically
        # Ensure it exists
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=500,
                detail="Model file not created after training"
            )
        
        return {
            "message": "Model trained successfully",
            "keywords": list(training_data.keys()),
            "total_keywords": len(training_data),
            "total_examples": total_examples
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
    finally:
        # Clean up temporary training file
        if os.path.exists(train_file):
            os.remove(train_file)


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


def predict_with_fasttext(text: str, k: int = 5) -> List[Dict[str, any]]:
    """Use FastText C++ executable to predict keywords"""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Train the model first using /train/build"
        )
    
    # Create temporary file for input text
    temp_input = os.path.join(TEMP_DIR, f"input_{os.getpid()}.txt")
    
    try:
        # Write text to temporary file
        with open(temp_input, 'w', encoding='utf-8') as f:
            # Clean the text
            clean_text = ' '.join(text.replace('\n', ' ').split())
            f.write(clean_text)
        
        # Run prediction: fasttext predict-prob model.bin input.txt k
        args = [
            "predict-prob",
            MODEL_PATH,
            temp_input,
            str(k)
        ]
        
        result = run_fasttext_command(args)
        
        # Parse output
        # Format: __label__keyword1 probability1 __label__keyword2 probability2 ...
        predictions = []
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            parts = line.strip().split()
            # Process pairs of (label, probability)
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    label = parts[i].replace('__label__', '')
                    try:
                        prob = float(parts[i + 1])
                        predictions.append({
                            "keyword": label,
                            "confidence": prob
                        })
                    except ValueError:
                        continue
        
        # Return top k predictions
        return predictions[:k]
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_input):
            os.remove(temp_input)


@app.post("/predict", response_model=PredictionResponse)
async def predict_keywords(file: UploadFile = File(...)):
    """
    Upload a document (text or PDF) and get top 5 matching keywords.
    
    Supported formats:
    - Text files (.txt, etc.) - UTF-8 encoded
    - PDF files (.pdf)
    """
    try:
        # Read the uploaded file
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Check if it's a PDF file
        if is_pdf_file(file.filename, content):
            # Extract text from PDF
            text, page_count = extract_text_from_pdf(content)
            source_type = "pdf"
            
            if not text.strip():
                raise HTTPException(
                    status_code=400, 
                    detail="Could not extract text from PDF. The PDF might be image-based or encrypted."
                )
        else:
            # Treat as text file
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        text = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail="Could not decode file. Ensure it's UTF-8 encoded text or a valid PDF."
                    )
            source_type = "text"
            page_count = None
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty document")
        
        # Get predictions
        top_keywords = predict_with_fasttext(text, k=5)
        
        # Create preview of text (first 200 chars)
        preview = text[:200] + "..." if len(text) > 200 else text
        
        return PredictionResponse(
            top_keywords=top_keywords,
            text_preview=preview,
            source_type=source_type,
            page_count=page_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/text")
async def predict_from_text(data: TextInput):
    """Predict keywords from raw text instead of file upload"""
    try:
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Empty text")
        
        # Get predictions
        top_keywords = predict_with_fasttext(data.text, k=5)
        
        # Create preview
        preview = data.text[:200] + "..." if len(data.text) > 200 else data.text
        
        return {
            "top_keywords": top_keywords,
            "text_preview": preview,
            "source_type": "text"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/pdf/extract")
async def extract_pdf_text(file: UploadFile = File(...)):
    """
    Extract text from a PDF file without prediction.
    Useful for previewing PDF content before classification.
    """
    try:
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if not is_pdf_file(file.filename, content):
            raise HTTPException(status_code=400, detail="File is not a valid PDF")
        
        text, page_count = extract_text_from_pdf(content)
        
        return {
            "filename": file.filename,
            "page_count": page_count,
            "character_count": len(text),
            "word_count": len(text.split()),
            "text": text,
            "preview": text[:500] + "..." if len(text) > 500 else text
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Get information about the trained model"""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=404, detail="No model found")
    
    # Get model file size
    model_size = os.path.getsize(MODEL_PATH)
    
    # Get model labels using FastText
    try:
        args = ["labels", MODEL_PATH]
        result = run_fasttext_command(args)
        
        labels = [
            line.replace('__label__', '').strip()
            for line in result.stdout.strip().split('\n')
            if line.strip()
        ]
        
        return {
            "model_path": MODEL_PATH,
            "model_size_bytes": model_size,
            "model_size_mb": round(model_size / (1024 * 1024), 2),
            "labels": labels,
            "label_count": len(labels)
        }
    except Exception as e:
        return {
            "model_path": MODEL_PATH,
            "model_size_bytes": model_size,
            "model_size_mb": round(model_size / (1024 * 1024), 2),
            "error": str(e)
        }


@app.get("/pdf/status")
async def pdf_status():
    """Check PDF processing capabilities"""
    return {
        "pdf_support_available": PDF_SUPPORT or PDFPLUMBER_SUPPORT,
        "libraries": {
            "pypdf2": {
                "installed": PDF_SUPPORT,
                "description": "Basic PDF text extraction"
            },
            "pdfplumber": {
                "installed": PDFPLUMBER_SUPPORT,
                "description": "Advanced PDF text extraction with better layout handling"
            }
        },
        "recommendation": "pdfplumber" if PDFPLUMBER_SUPPORT else ("pypdf2" if PDF_SUPPORT else "Install PyPDF2 or pdfplumber")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)