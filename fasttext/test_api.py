#!/usr/bin/env python3
"""
Test script for FastText Keyword Classification API
Demonstrates the complete workflow: add data, train, predict
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_api():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except:
        return False

def add_sample_data():
    """Add sample training data"""
    print_section("Adding Sample Training Data")
    
    # Sample training data for different categories
    training_batch = [
        {
            "keyword": "technology",
            "sentences": [
                "The new smartphone features cutting-edge AI technology",
                "Cloud computing services are expanding rapidly",
                "Machine learning algorithms improve pattern recognition",
                "Software development requires programming expertise",
                "Cybersecurity protects digital infrastructure",
                "The latest processors offer unprecedented computing power",
                "Virtual reality creates immersive digital experiences"
            ]
        },
        {
            "keyword": "sports",
            "sentences": [
                "The basketball team won the championship game",
                "Football players train intensively during off-season",
                "Olympic athletes compete at the highest level",
                "Tennis matches can last for several hours",
                "Soccer is the most popular sport worldwide",
                "Baseball season begins in early spring",
                "Marathon runners push their physical limits"
            ]
        },
        {
            "keyword": "finance",
            "sentences": [
                "Stock market indices reached record highs today",
                "Investment portfolios require careful diversification",
                "Cryptocurrency markets show high volatility",
                "Central banks adjust interest rates quarterly",
                "Corporate earnings exceeded analyst expectations",
                "Real estate investments provide stable returns",
                "Bond yields reflect economic conditions"
            ]
        },
        {
            "keyword": "health",
            "sentences": [
                "Regular exercise improves cardiovascular health",
                "Balanced nutrition is essential for wellness",
                "Mental health awareness campaigns are expanding",
                "Medical research advances treatment options",
                "Preventive care reduces healthcare costs",
                "Sleep quality affects overall wellbeing",
                "Vaccines protect against infectious diseases"
            ]
        },
        {
            "keyword": "environment",
            "sentences": [
                "Climate change impacts global weather patterns",
                "Renewable energy sources reduce carbon emissions",
                "Recycling programs help conserve natural resources",
                "Deforestation threatens biodiversity",
                "Ocean pollution affects marine ecosystems",
                "Sustainable agriculture practices protect soil health",
                "Wildlife conservation efforts preserve endangered species"
            ]
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/train/batch",
        json=training_batch
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result['message']}")
        print(f"  Total keywords: {result['total_keywords']}")
    else:
        print(f"✗ Failed to add training data: {response.text}")
        return False
    
    return True

def train_model():
    """Train the FastText model"""
    print_section("Training Model")
    print("Training in progress... this may take a moment")
    
    response = requests.post(f"{BASE_URL}/train/build")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result['message']}")
        print(f"  Keywords: {', '.join(result['keywords'])}")
        print(f"  Total examples: {result['total_examples']}")
    else:
        print(f"✗ Training failed: {response.text}")
        return False
    
    return True

def test_predictions():
    """Test predictions with sample documents"""
    print_section("Testing Predictions")
    
    test_documents = [
        {
            "name": "Tech Article",
            "text": "Apple unveiled its latest iPhone featuring an advanced neural engine for artificial intelligence tasks. The new device includes improved camera sensors and enhanced processing capabilities for machine learning applications."
        },
        {
            "name": "Sports News",
            "text": "The Lakers secured their playoff position with a thrilling victory last night. LeBron James scored 35 points while the team demonstrated excellent defensive strategies throughout the game."
        },
        {
            "name": "Financial Report",
            "text": "Major stock indices showed mixed results today as investors analyzed quarterly earnings reports from tech companies. The Federal Reserve's recent interest rate decision continues to influence market sentiment."
        },
        {
            "name": "Health Article",
            "text": "New research highlights the importance of regular physical activity for maintaining mental health. Studies show that even moderate exercise can significantly reduce stress and improve cognitive function."
        },
        {
            "name": "Environmental News",
            "text": "Scientists warn that rising global temperatures are accelerating ice sheet melting in Antarctica. The environmental impact could lead to significant sea level changes affecting coastal communities worldwide."
        }
    ]
    
    for doc in test_documents:
        print(f"\n📄 Document: {doc['name']}")
        print(f"   Text: {doc['text'][:80]}...")
        
        response = requests.post(
            f"{BASE_URL}/predict/text",
            params={"text": doc["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Top Keywords:")
            for i, kw in enumerate(result['top_keywords'], 1):
                confidence_bar = "█" * int(kw['confidence'] * 20)
                print(f"      {i}. {kw['keyword']:15s} {confidence_bar} {kw['confidence']:.2%}")
        else:
            print(f"   ✗ Prediction failed: {response.text}")

def list_keywords():
    """List all trained keywords"""
    print_section("Current Keywords")
    
    response = requests.get(f"{BASE_URL}/keywords")
    
    if response.status_code == 200:
        result = response.json()
        for kw_info in result['keywords']:
            print(f"  • {kw_info['keyword']:15s} ({kw_info['example_count']} examples)")
    else:
        print(f"✗ Failed to retrieve keywords: {response.text}")

def main():
    print("\n🚀 FastText Keyword Classification API - Test Script")
    print("="*60)
    
    # Check if API is running
    print("\nChecking API status...", end=" ")
    if not check_api():
        print("✗ FAILED")
        print("\n❌ API is not running. Please start it with:")
        print("   docker-compose up")
        sys.exit(1)
    print("✓ OK")
    
    # Run workflow
    if not add_sample_data():
        sys.exit(1)
    
    list_keywords()
    
    if not train_model():
        sys.exit(1)
    
    # Wait a moment for model to be ready
    time.sleep(1)
    
    test_predictions()
    
    print_section("Test Complete!")
    print("\n✓ All tests passed successfully!")
    print("\nYou can now:")
    print("  1. Add more training data: POST /train/add")
    print("  2. Upload documents: POST /predict")
    print("  3. View API docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()
