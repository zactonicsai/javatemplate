# Technical Notes: FastText C++ Executable Implementation

## Overview

This implementation uses the **native FastText C++ executable** compiled from source, rather than the Python bindings (`import fasttext`).

## Architecture Comparison

### Python Bindings Approach (Not Used)
```python
import fasttext

# Training
model = fasttext.train_supervised(
    input='train.txt',
    epoch=25,
    lr=1.0
)
model.save_model('model.bin')

# Prediction
model = fasttext.load_model('model.bin')
labels, probs = model.predict(text, k=5)
```

### C++ Executable Approach (Current Implementation)
```python
import subprocess

# Training
subprocess.run([
    'fasttext', 'supervised',
    '-input', 'train.txt',
    '-output', 'model',
    '-epoch', '25',
    '-lr', '1.0'
])

# Prediction
result = subprocess.run([
    'fasttext', 'predict-prob',
    'model.bin',
    'input.txt',
    '5'
], capture_output=True, text=True)

# Parse output
predictions = parse_fasttext_output(result.stdout)
```

## Benefits of C++ Executable Approach

1. **No Python Binding Dependencies**
   - Avoids potential version conflicts
   - Simpler Docker build process
   - No need for Cython compilation

2. **Direct Access to C++ Implementation**
   - Uses the official FastText C++ code directly
   - Consistent with FastText documentation
   - Access to all command-line features

3. **Better Resource Management**
   - No Python GIL overhead for prediction
   - C++ memory management
   - Potentially better performance for large models

4. **Easier Debugging**
   - Standard output/error from executable
   - Can test commands directly in shell
   - Clear separation between API and ML code

## Implementation Details

### File Structure

```
/app/
├── server.py              # FastAPI server
├── models/
│   └── keyword_model.bin  # Trained model
├── data/
│   └── training_data.json # Training data storage
└── temp/                  # Temporary files for prediction
```

### Training Workflow

1. **User adds training data** via `/train/add` or `/train/batch`
   - Data stored in JSON format in memory and disk
   
2. **User triggers training** via `/train/build`
   - Server creates FastText format file: `__label__keyword text`
   - Calls: `fasttext supervised -input train.txt -output model ...`
   - FastText creates `model.bin` automatically

3. **Model ready for predictions**

### Prediction Workflow

1. **User uploads document** via `/predict`
   - Text written to temporary file
   
2. **Call FastText executable**
   - `fasttext predict-prob model.bin input.txt 5`
   - Returns: `__label__keyword1 prob1 __label__keyword2 prob2 ...`

3. **Parse output**
   - Extract labels and probabilities
   - Format as JSON response

4. **Cleanup**
   - Remove temporary files

## FastText Executable Commands

The Docker image includes the `fasttext` executable with these key commands:

### Training
```bash
fasttext supervised -input train.txt -output model [options]

Options:
  -epoch N          Number of epochs (default: 5)
  -lr FLOAT         Learning rate (default: 0.1)
  -dim N            Size of word vectors (default: 100)
  -wordNgrams N     Max word n-gram length (default: 1)
  -loss TYPE        Loss function: softmax, hs, ns (default: softmax)
```

### Prediction
```bash
# Single prediction
fasttext predict model.bin test.txt

# Top-k predictions with probabilities
fasttext predict-prob model.bin test.txt k

# Output format: __label__label1 prob1 __label__label2 prob2 ...
```

### Model Inspection
```bash
# List all labels in model
fasttext labels model.bin

# Get word vectors
fasttext print-word-vectors model.bin
```

## Error Handling

### Common Issues

1. **Empty predictions**
   - Check if model is trained
   - Verify input text is not empty
   - Ensure model has labels

2. **Training failures**
   - Verify training data format
   - Check for empty sentences
   - Ensure unique labels exist

3. **Subprocess errors**
   - FastText executable not found (check Docker build)
   - Permission issues (check file paths)
   - Memory issues (large models)

### Subprocess Error Handling

```python
try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True  # Raises CalledProcessError on non-zero exit
    )
except subprocess.CalledProcessError as e:
    # e.stderr contains error message from fasttext
    raise HTTPException(500, f"FastText failed: {e.stderr}")
```

## Performance Considerations

### Training
- FastText is very fast (typically seconds)
- Training time scales with:
  - Number of examples
  - Number of epochs
  - Dimension size
  - Word n-gram size

### Prediction
- Prediction is extremely fast (milliseconds)
- Temporary file I/O adds minimal overhead
- Consider caching for repeated predictions on same text

### Optimization Tips

1. **Adjust hyperparameters** based on your data size:
   - Fewer epochs for large datasets
   - Higher learning rate for quick convergence
   - Larger dimensions for complex classification

2. **Preprocessing**
   - Remove unnecessary whitespace
   - Normalize text (lowercase, remove special chars)
   - Use consistent tokenization

3. **Model size**
   - Smaller dimensions = smaller models
   - Fewer word n-grams = faster training
   - Consider accuracy vs size tradeoff

## Testing

### Manual Testing with Shell

```bash
# Enter Docker container
docker-compose exec fasttext-api bash

# Run demo script
./demo_fasttext_executable.sh

# Or test manually
echo "This is a test" > test.txt
fasttext predict-prob /app/models/keyword_model.bin test.txt 5
```

### API Testing

```bash
# Use the test script
python3 test_api.py

# Or manual curl commands
curl -X POST http://localhost:8000/train/build
curl -X POST http://localhost:8000/predict/text?text="test document"
```

## Future Enhancements

Potential improvements:

1. **Batch prediction** - Process multiple documents at once
2. **Model versioning** - Keep multiple model versions
3. **A/B testing** - Compare different model configurations
4. **Metrics** - Track prediction latency and accuracy
5. **Preprocessing pipeline** - Text normalization options
6. **Auto-retraining** - Trigger retraining on schedule
7. **Model export** - Download trained models
8. **Fine-tuning** - Incremental training on new data

## References

- [FastText Official Documentation](https://fasttext.cc/)
- [FastText GitHub Repository](https://github.com/facebookresearch/fastText)
- [FastText Paper](https://arxiv.org/abs/1607.01759)
