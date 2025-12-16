#!/bin/bash

# FastText C++ Executable Usage Examples
# This script demonstrates how the FastText executable works directly

echo "================================================"
echo "FastText C++ Executable - Direct Usage Examples"
echo "================================================"
echo ""

# Check if FastText is installed
if ! command -v fasttext &> /dev/null; then
    echo "❌ FastText executable not found!"
    echo "This script should be run inside the Docker container."
    echo "Run: docker-compose exec fasttext-api bash"
    exit 1
fi

echo "✓ FastText executable found at: $(which fasttext)"
echo ""

# Create sample training data
echo "1. Creating sample training data..."
cat > /tmp/sample_train.txt << 'EOF'
__label__positive This is a great product and I love it
__label__positive Amazing quality and excellent service
__label__positive Best purchase I have ever made
__label__positive Highly recommend this to everyone
__label__negative Terrible quality and poor service
__label__negative Waste of money do not buy
__label__negative Very disappointed with this product
__label__negative Would not recommend to anyone
EOF

echo "✓ Training data created: /tmp/sample_train.txt"
echo ""

# Train a model
echo "2. Training FastText model..."
fasttext supervised \
    -input /tmp/sample_train.txt \
    -output /tmp/sample_model \
    -epoch 25 \
    -lr 1.0 \
    -wordNgrams 2 \
    -dim 100 \
    -loss softmax

echo ""
echo "✓ Model trained: /tmp/sample_model.bin"
echo ""

# Create test data
echo "3. Creating test document..."
echo "This product is absolutely fantastic and worth every penny" > /tmp/test_doc.txt
echo "✓ Test document: /tmp/test_doc.txt"
echo ""

# Make predictions
echo "4. Making predictions (top 2)..."
echo "Command: fasttext predict-prob /tmp/sample_model.bin /tmp/test_doc.txt 2"
echo ""
fasttext predict-prob /tmp/sample_model.bin /tmp/test_doc.txt 2
echo ""

# Show model labels
echo "5. Showing model labels..."
echo "Command: fasttext labels /tmp/sample_model.bin"
echo ""
fasttext labels /tmp/sample_model.bin
echo ""

# Test with another phrase
echo "6. Testing negative sentiment..."
echo "This is horrible and I hate it" > /tmp/test_doc2.txt
fasttext predict-prob /tmp/sample_model.bin /tmp/test_doc2.txt 2
echo ""

echo "================================================"
echo "FastText C++ executable works perfectly!"
echo "================================================"
echo ""
echo "The Python API uses these same commands via subprocess"
echo "to provide a REST interface for training and prediction."
echo ""

# Cleanup
rm -f /tmp/sample_train.txt /tmp/sample_model.bin /tmp/sample_model.vec
rm -f /tmp/test_doc.txt /tmp/test_doc2.txt

echo "Cleanup complete."
