# Food Classification Example

This directory contains sample training data and scripts to create a **food classification system** using FastText. The model can identify 10 different food categories from text descriptions.

## 📋 Food Categories

The training data includes **10 categories** with **15 examples each** (150 total examples):

1. **🍎 Fruits** - Apples, bananas, oranges, berries, tropical fruits
2. **🥦 Vegetables** - Broccoli, carrots, spinach, peppers, tomatoes
3. **🍗 Proteins** - Chicken, salmon, beef, eggs, beans, tofu
4. **🌾 Grains** - Rice, bread, quinoa, oats, pasta, cereal
5. **🧀 Dairy** - Milk, cheese, yogurt, butter, cream
6. **🍰 Desserts** - Cakes, cookies, ice cream, pies, pastries
7. **☕ Beverages** - Coffee, tea, juice, smoothies, water
8. **🍿 Snacks** - Chips, popcorn, pretzels, trail mix, bars
9. **🦞 Seafood** - Salmon, shrimp, tuna, lobster, crab
10. **🥫 Condiments** - Ketchup, mustard, mayo, sauces, dressings

## 🚀 Quick Start

### Method 1: Python Script (Recommended)

```bash
# Make sure the API is running
docker-compose up -d

# Run the loader script
python3 load_food_data.py
```

This script will:
- ✅ Upload all 150 training examples
- ✅ Train the model automatically
- ✅ Run 10 test predictions
- ✅ Show accuracy results

### Method 2: Web Interface

1. Start the API: `docker-compose up`
2. Open http://localhost:8000
3. Go to **Train Model** tab
4. Manually copy data from `food_training_data.json`
5. Click **Train Model Now**

### Method 3: Manual Upload

```bash
# Upload training data
curl -X POST http://localhost:8000/train/batch \
  -H "Content-Type: application/json" \
  -d @food_training_data.json

# Train the model
curl -X POST http://localhost:8000/train/build
```

## 📊 Training Data Structure

The `food_training_data.json` file contains:

```json
{
  "fruits": [
    "The fresh apple has a crisp texture and sweet taste",
    "Ripe bananas are perfect for smoothies and baking",
    ...
  ],
  "vegetables": [
    "Fresh broccoli florets are rich in vitamins and minerals",
    "Crispy carrots are crunchy and naturally sweet vegetables",
    ...
  ],
  ...
}
```

Each category has:
- **15 example sentences**
- **Varied descriptions** covering different foods in the category
- **Natural language** that describes the food

## 🧪 Testing the Model

### Using the Web Interface

1. Go to http://localhost:8000
2. Click **Predict Keywords** tab
3. Try these example texts:

**Fruits:**
```
A bowl of fresh strawberries with whipped cream
```

**Proteins:**
```
Grilled chicken breast seasoned with herbs and spices
```

**Desserts:**
```
Warm chocolate brownies with vanilla ice cream on top
```

**Beverages:**
```
A cup of hot coffee with milk and sugar
```

### Using the API

```bash
# Test with a fruit description
curl -X POST "http://localhost:8000/predict/text?text=Fresh orange juice for breakfast"

# Test with a protein description
curl -X POST "http://localhost:8000/predict/text?text=Grilled salmon with lemon butter sauce"

# Test with a dessert description
curl -X POST "http://localhost:8000/predict/text?text=Chocolate chip cookies fresh from the oven"
```

### Using Python

```python
import requests

text = "A fresh Caesar salad with parmesan cheese and croutons"

response = requests.post(
    "http://localhost:8000/predict/text",
    params={"text": text}
)

result = response.json()
print(f"Top category: {result['top_keywords'][0]['keyword']}")
print(f"Confidence: {result['top_keywords'][0]['confidence']:.2%}")
```

## 📈 Expected Results

After training, the model should achieve:
- **80-95%** accuracy on test samples
- **High confidence** (>70%) for clear descriptions
- **Lower confidence** for ambiguous items

### Example Predictions

| Description | Expected Category | Confidence |
|-------------|------------------|------------|
| "Fresh apple slices" | fruits | ~90% |
| "Grilled steak" | proteins | ~85% |
| "Hot coffee" | beverages | ~88% |
| "Chocolate cake" | desserts | ~92% |

## 🎯 Use Cases

This food classifier can be used for:

1. **Recipe Categorization** - Classify recipes by main ingredient type
2. **Menu Organization** - Automatically categorize menu items
3. **Dietary Tracking** - Identify food groups in meal descriptions
4. **Restaurant Reviews** - Extract food type mentions from reviews
5. **Shopping Lists** - Organize grocery lists by category
6. **Nutrition Apps** - Categorize foods for calorie tracking

## 📝 Sample Test Documents

### Test Document 1: Breakfast
```
I had scrambled eggs with crispy bacon, whole wheat toast with butter,
and fresh orange juice. The eggs were fluffy and the bacon was perfectly
cooked. A side of strawberries made it complete.
```

**Expected predictions**: proteins, grains, beverages, fruits

### Test Document 2: Lunch
```
For lunch I enjoyed a fresh garden salad with mixed greens, cherry tomatoes,
cucumbers, and ranch dressing. I also had a grilled chicken sandwich on
whole grain bread with swiss cheese.
```

**Expected predictions**: vegetables, proteins, grains, dairy, condiments

### Test Document 3: Dinner
```
Tonight's dinner featured pan-seared salmon with lemon butter, steamed
broccoli, and wild rice. For dessert, we had vanilla ice cream with
chocolate sauce.
```

**Expected predictions**: seafood, vegetables, grains, desserts, dairy

## 🔧 Customization

### Adding More Examples

To improve accuracy, add more examples to `food_training_data.json`:

```json
{
  "fruits": [
    "Existing examples...",
    "Your new example here",
    "Another new example"
  ]
}
```

Then re-run the loader:
```bash
python3 load_food_data.py
```

### Adding New Categories

Add a new category to the JSON:

```json
{
  "fruits": [...],
  "vegetables": [...],
  "your_new_category": [
    "Example 1 for new category",
    "Example 2 for new category",
    "Example 3 for new category",
    ...
  ]
}
```

### Merging Categories

To combine categories (e.g., merge fruits and vegetables):
1. Edit the JSON to combine examples
2. Reload the data
3. Retrain the model

## 📚 Tips for Best Results

1. **Quantity**: 10-20 examples per category is ideal
2. **Variety**: Include different foods within each category
3. **Natural Language**: Use realistic descriptions
4. **Avoid Overlap**: Keep categories distinct
5. **Test Often**: Try edge cases to find weaknesses
6. **Iterate**: Add examples for misclassified items

## 🐛 Troubleshooting

**Low accuracy?**
- Add more diverse examples
- Check for overlapping categories
- Ensure examples are representative

**Model not training?**
- Check that data uploaded successfully
- Verify JSON format is correct
- Look for error messages in API logs

**Predictions seem random?**
- Model may not be trained
- Check if categories have enough examples
- Verify the model file exists: `ls -la models/`

## 📦 Files Included

- `food_training_data.json` - 150 training examples across 10 categories
- `load_food_data.py` - Automated loader with testing
- `load_food_data.sh` - Simple shell script loader
- `FOOD_CLASSIFICATION.md` - This file

## 🎓 Learning Exercise

Try these challenges:

1. **Add a new category** (e.g., "spices", "herbs", "sauces")
2. **Test with recipes** from cooking websites
3. **Build a meal analyzer** that breaks down meals by category
4. **Create a restaurant menu classifier**
5. **Make a grocery list organizer**

## 📊 Performance Metrics

After running `load_food_data.py`, you'll see:

```
📊 Accuracy: 9/10 (90.0%)
🎉 Excellent! The model is working great!
```

Typical results:
- **Training time**: 10-20 seconds
- **Prediction time**: <100ms per text
- **Model size**: ~1-2 MB
- **Memory usage**: ~50-100 MB

## 🔗 Next Steps

1. **Web Interface**: http://localhost:8000
2. **API Docs**: http://localhost:8000/docs
3. **Try the model** with your own food descriptions
4. **Add more data** to improve accuracy
5. **Build an application** using the classifier

Happy classifying! 🍕🥗🍰
