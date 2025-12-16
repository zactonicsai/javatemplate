#!/usr/bin/env python3
"""
Load Food Training Data into FastText API

This script loads the sample food training data and trains the model.
Run this after starting the Docker container to quickly set up the food classifier.
"""

import requests
import json
import sys
import time

API_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_api():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/api")
        return response.status_code == 200
    except:
        return False

def load_training_data():
    """Load training data from JSON file"""
    try:
        with open('food_training_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: food_training_data.json not found!")
        print("   Make sure the file is in the current directory.")
        sys.exit(1)

def upload_training_data(data):
    """Upload all training data to the API"""
    print_header("Uploading Training Data")
    
    # Prepare batch data
    batch = []
    for keyword, sentences in data.items():
        batch.append({
            "keyword": keyword,
            "sentences": sentences
        })
    
    print(f"📦 Preparing to upload {len(batch)} food categories...")
    print(f"📊 Total examples: {sum(len(sentences) for sentences in data.values())}\n")
    
    # Display what we're uploading
    for keyword, sentences in data.items():
        print(f"  • {keyword:15s} - {len(sentences):2d} examples")
    
    print("\n🚀 Uploading to API...")
    
    try:
        response = requests.post(
            f"{API_URL}/train/batch",
            json=batch
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success! {result['message']}")
            return True
        else:
            print(f"\n❌ Upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ Error uploading data: {e}")
        return False

def train_model():
    """Train the FastText model"""
    print_header("Training Model")
    
    print("🔧 Starting model training...")
    print("⏳ This may take 10-30 seconds...\n")
    
    try:
        response = requests.post(f"{API_URL}/train/build")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Training successful!")
            print(f"\n📊 Training Results:")
            print(f"   • Keywords: {result['total_keywords']}")
            print(f"   • Examples: {result['total_examples']}")
            print(f"   • Categories: {', '.join(result['keywords'])}")
            return True
        else:
            print(f"❌ Training failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def test_predictions():
    """Test the model with sample food descriptions"""
    print_header("Testing Model with Sample Foods")
    
    test_samples = [
        {
            "description": "Fresh and juicy strawberries",
            "expected": "fruits"
        },
        {
            "description": "Grilled chicken breast with herbs",
            "expected": "proteins"
        },
        {
            "description": "Crispy french fries with ketchup",
            "expected": "snacks"
        },
        {
            "description": "Chocolate cake with vanilla frosting",
            "expected": "desserts"
        },
        {
            "description": "Fresh whole wheat bread",
            "expected": "grains"
        },
        {
            "description": "Steamed broccoli with butter",
            "expected": "vegetables"
        },
        {
            "description": "Cold milk in a glass",
            "expected": "dairy"
        },
        {
            "description": "Iced coffee with cream",
            "expected": "beverages"
        },
        {
            "description": "Grilled salmon with lemon",
            "expected": "seafood"
        },
        {
            "description": "Spicy mustard on a hot dog",
            "expected": "condiments"
        }
    ]
    
    print("🧪 Running predictions on 10 sample descriptions...\n")
    
    correct = 0
    total = len(test_samples)
    
    for i, sample in enumerate(test_samples, 1):
        try:
            response = requests.post(
                f"{API_URL}/predict/text",
                params={"text": sample["description"]}
            )
            
            if response.status_code == 200:
                result = response.json()
                top_prediction = result['top_keywords'][0]
                
                is_correct = top_prediction['keyword'] == sample['expected']
                if is_correct:
                    correct += 1
                
                status = "✅" if is_correct else "❌"
                confidence = top_prediction['confidence'] * 100
                
                print(f"{i:2d}. {status} '{sample['description']}'")
                print(f"    Predicted: {top_prediction['keyword']} ({confidence:.1f}%)")
                print(f"    Expected:  {sample['expected']}\n")
            else:
                print(f"{i}. ❌ Prediction failed for: {sample['description']}\n")
        except Exception as e:
            print(f"{i}. ❌ Error: {e}\n")
    
    accuracy = (correct / total) * 100
    print(f"\n📊 Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy >= 80:
        print("🎉 Excellent! The model is working great!")
    elif accuracy >= 60:
        print("👍 Good! The model is performing well.")
    else:
        print("⚠️  Consider adding more training examples for better accuracy.")

def main():
    print("\n🍎 FastText Food Classifier - Training Data Loader")
    print("="*70)
    
    # Check API
    print("\n🔍 Checking API connection...")
    if not check_api():
        print("❌ API is not running!")
        print("\n📝 Please start the API first:")
        print("   docker-compose up")
        sys.exit(1)
    print("✅ API is running\n")
    
    # Load data
    data = load_training_data()
    
    # Upload data
    if not upload_training_data(data):
        sys.exit(1)
    
    # Wait a moment
    time.sleep(1)
    
    # Train model
    if not train_model():
        sys.exit(1)
    
    # Wait for training to complete
    time.sleep(2)
    
    # Test predictions
    test_predictions()
    
    print_header("Setup Complete!")
    print("🎉 Your food classifier is ready to use!\n")
    print("💡 Next steps:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Go to the 'Predict Keywords' tab")
    print("   3. Try describing different foods!")
    print("\n📝 Example descriptions to try:")
    print("   • 'A bowl of fresh blueberries and yogurt'")
    print("   • 'Grilled steak with mashed potatoes'")
    print("   • 'Hot coffee with milk and sugar'")
    print("   • 'Chocolate ice cream with sprinkles'\n")

if __name__ == "__main__":
    main()
