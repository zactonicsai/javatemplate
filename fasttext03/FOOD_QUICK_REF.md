# 🍎 Food Classifier - Quick Reference

## One-Command Setup

```bash
# 1. Start the API
docker-compose up -d

# 2. Load food data & train
python3 load_food_data.py

# 3. Open browser
# Visit: http://localhost:8000
```

## 📊 What You Get

```
✅ 10 Food Categories
   • Fruits       • Vegetables   • Proteins
   • Grains       • Dairy        • Desserts
   • Beverages    • Snacks       • Seafood
   • Condiments

✅ 150 Training Examples (15 per category)

✅ Pre-made Test Documents
   • breakfast.txt
   • lunch_salad.txt
   • dinner_seafood.txt
   • dessert_party.txt
   • coffee_shop_drinks.txt
   • movie_snacks.txt
   • grocery_shopping.txt
```

## 🎯 Quick Test

### Via Web Interface
1. Go to http://localhost:8000
2. Click "Predict Keywords"
3. Drag & drop `test_documents/breakfast.txt`
4. See results!

### Via API
```bash
curl -X POST "http://localhost:8000/predict/text?text=Fresh orange juice and scrambled eggs"
```

### Via Python
```python
import requests

text = "Grilled chicken with broccoli and rice"
response = requests.post(
    "http://localhost:8000/predict/text",
    params={"text": text}
)
print(response.json()['top_keywords'][0])
# Output: {'keyword': 'proteins', 'confidence': 0.87}
```

## 📝 Try These Examples

| Text Input | Expected Top Category |
|------------|----------------------|
| "Fresh apple slices with peanut butter" | fruits |
| "Steamed broccoli and carrots" | vegetables |
| "Grilled salmon with herbs" | seafood |
| "Hot coffee with cream" | beverages |
| "Chocolate ice cream cone" | desserts |
| "Popcorn with butter" | snacks |
| "Whole wheat bread toast" | grains |
| "Cheddar cheese slices" | dairy |
| "Ketchup and mustard" | condiments |
| "Chicken breast with seasoning" | proteins |

## 🎨 Web Interface Features

```
┌─────────────────────────────────────────┐
│  🔍 Predict Keywords                    │
├─────────────────────────────────────────┤
│  • Drag & drop files                    │
│  • Paste text directly                  │
│  • See top 5 matches                    │
│  • Confidence percentages               │
│  • Color-coded rankings                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🎓 Train Model                         │
├─────────────────────────────────────────┤
│  • Add new food examples                │
│  • Batch upload                         │
│  • One-click training                   │
│  • Progress tracking                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🗂️ Manage Keywords                     │
├─────────────────────────────────────────┤
│  • View all categories                  │
│  • Example counts                       │
│  • Delete categories                    │
│  • Refresh list                         │
└─────────────────────────────────────────┘
```

## ⚡ Common Use Cases

1. **Recipe Classifier**
   - Upload recipe → Get main ingredient type
   
2. **Menu Organizer**
   - Input menu item → Auto-categorize

3. **Diet Tracker**
   - Log meals → Track food groups

4. **Restaurant Reviews**
   - Analyze reviews → Extract food mentions

5. **Grocery Helper**
   - Shopping list → Organize by section

## 🔧 Customization

### Add More Examples
```python
# Edit food_training_data.json
{
  "fruits": [
    "existing examples...",
    "New example: Fresh pineapple chunks",
    "New example: Ripe avocados"
  ]
}

# Reload
python3 load_food_data.py
```

### Add New Category
```python
{
  "existing_categories": [...],
  "spices": [
    "Black pepper adds sharp flavor",
    "Cinnamon is sweet and warm",
    "Garlic powder enhances savory dishes"
  ]
}
```

## 📈 Performance

```
Training Time:    10-20 seconds
Prediction Time:  <100ms
Accuracy:         80-95%
Model Size:       1-2 MB
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| API not responding | `docker-compose up` |
| Model not trained | Run `python3 load_food_data.py` |
| Low accuracy | Add more varied examples |
| Wrong predictions | Check training data quality |

## 📚 File Guide

```
food_training_data.json    → Training data (150 examples)
load_food_data.py         → Auto-loader script
FOOD_CLASSIFICATION.md    → Complete documentation
test_documents/           → 7 sample test files
```

## 🎓 Next Steps

1. ✅ Load the data
2. ✅ Train the model  
3. ✅ Test with samples
4. 🔄 Add your own examples
5. 🚀 Build an app with it!

---

**Need Help?**
- Main README: `README.md`
- Food Guide: `FOOD_CLASSIFICATION.md`
- Web UI Guide: `WEB_INTERFACE_GUIDE.md`
- API Docs: http://localhost:8000/docs
