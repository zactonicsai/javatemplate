# Web Interface Guide

## Overview

The FastText Keyword Classifier comes with a beautiful, modern web interface built with Tailwind CSS. This guide shows you how to use all its features.

## Accessing the Interface

Once your Docker container is running, simply open your browser to:

```
http://localhost:8000
```

## Dashboard

The top of every page shows real-time statistics:

- **Keywords** - Number of trained keywords
- **Examples** - Total training examples
- **Model Status** - Whether model is trained
- **Predictions** - Number of predictions made

## Features by Tab

### 1. 🔍 Predict Keywords Tab (Default)

**Purpose**: Analyze documents to find matching keywords

**Left Panel - Upload Document:**
- **Drag & Drop**: Drag files directly into the drop zone
- **Browse Files**: Click "Browse Files" to select from your computer
- **Text Input**: Or paste text directly into the text area
- **Supported Formats**: .txt, .doc, .docx, .pdf

**Right Panel - Results:**
- **Document Preview**: Shows first 200 characters
- **Top 5 Keywords**: Displayed with:
  - Ranking (1-5)
  - Keyword name
  - Confidence score (percentage)
  - Visual progress bar
  - Color coding by rank

**How to Use:**
1. Upload a file or paste text
2. Click "Analyze Document"
3. View results instantly

### 2. 🎓 Train Model Tab

**Purpose**: Add training data and train the classification model

**Left Panel - Add Training Data:**

**Keyword Field**:
- Enter the category name (e.g., "technology", "sports", "finance")

**Example Sentences**:
- Enter one example per line
- Minimum 5-10 examples recommended
- More examples = better accuracy

**Example:**
```
Keyword: technology

Sentences:
The latest smartphone features AI capabilities
Cloud computing revolutionizes data storage
Machine learning improves automation
Software development uses modern frameworks
Cybersecurity protects digital infrastructure
```

**Add Examples Button**:
- Saves your training data
- Can add multiple keywords
- Data persists across restarts

**Right Panel - Build Model:**

**Training Information**:
- Shows recommended best practices
- Displays current statistics

**Training Stats**:
- Total Keywords
- Total Examples

**Train Model Now Button**:
- Builds the FastText model
- Shows progress bar
- Takes 5-30 seconds depending on data size
- Must train before predictions work

**Workflow:**
1. Add training data for each keyword
2. Add 5-10+ examples per keyword
3. Click "Train Model Now"
4. Wait for training to complete
5. Go to Predict tab to test

### 3. 🗂️ Manage Keywords Tab

**Purpose**: View and manage all trained keywords

**Features**:
- **Table View**: Shows all keywords with example counts
- **Refresh Button**: Reload the keyword list
- **Delete Button**: Remove individual keywords

**Table Columns**:
- **Keyword**: The category name
- **Examples**: Number of training sentences
- **Actions**: Delete button

**How to Use:**
- Click "Refresh" to update the list
- Click "Delete" to remove a keyword
- Confirm deletion when prompted
- After changes, retrain the model

## UI Features

### Design Elements

**Color Scheme**:
- Purple gradient for primary actions
- Color-coded confidence levels:
  - Rank 1: Purple
  - Rank 2: Blue
  - Rank 3: Green
  - Rank 4: Yellow
  - Rank 5: Red

**Animations**:
- Slide-in results
- Progress bar transitions
- Hover effects on cards
- Pulse animation on status indicator

**Notifications (Toasts)**:
- Success (green): Operations completed
- Error (red): Something went wrong
- Warning (yellow): User input needed
- Info (blue): General information
- Auto-dismiss after 4 seconds

### Responsive Design

The interface works on:
- Desktop (optimal experience)
- Tablet (responsive grid)
- Mobile (stacked layout)

## Tips for Best Results

### Training:

1. **Quantity**: Add at least 5-10 examples per keyword
2. **Quality**: Use clear, representative sentences
3. **Diversity**: Include different phrasings and contexts
4. **Balance**: Similar example counts for each keyword
5. **Clarity**: Avoid ambiguous sentences

### Prediction:

1. **Document Length**: Works best with 50-500 words
2. **Format**: Plain text gives best results
3. **Content**: Similar style to training examples
4. **Multiple Attempts**: Try different phrasings

### Model Management:

1. **Retrain After Changes**: Train model after adding/deleting keywords
2. **Regular Updates**: Add more examples over time
3. **Test Predictions**: Verify accuracy after training
4. **Backup Data**: Training data saved in `./data/`

## Troubleshooting

### "Model not trained" Error

**Solution**: 
1. Go to "Train Model" tab
2. Ensure you have training data
3. Click "Train Model Now"
4. Wait for completion

### Low Confidence Scores

**Solutions**:
- Add more training examples
- Use more diverse examples
- Ensure examples match prediction style
- Retrain the model

### Upload Not Working

**Check**:
- File is text-based (.txt, .doc, etc.)
- File is UTF-8 encoded
- File size is reasonable (<10MB)
- Browser allows file uploads

### Interface Not Loading

**Check**:
- Docker container is running
- Port 8000 is accessible
- Visit http://localhost:8000 (not https)
- Check browser console for errors

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Submit forms
- **Ctrl/Cmd + V**: Paste into text areas
- **Esc**: (Future) Close modals

## Browser Support

Tested and works on:
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

Requires JavaScript enabled.

## Advanced Usage

### Using Both UI and API

You can:
1. Add data via UI
2. Train via UI
3. Predict via API calls from your code
4. View results in UI

Training data and model are shared!

### Customization

To modify the UI:
1. Edit `index.html` 
2. Tailwind CSS classes control styling
3. JavaScript functions handle API calls
4. Rebuild Docker container

### Integration

The web interface is separate from the API:
- UI calls same endpoints as curl/scripts
- Can replace UI with your own
- API endpoints documented at `/docs`

## Getting Help

- Check the main [README.md](README.md) for API details
- See [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) for implementation
- Review [QUICKSTART.md](QUICKSTART.md) for setup
- Check Docker logs: `docker-compose logs`

## Summary

The web interface provides an intuitive way to:
- ✅ Upload and analyze documents
- ✅ Add training data visually
- ✅ Train models with one click
- ✅ View results with beautiful visualizations
- ✅ Manage keywords easily

No command line required - everything works in your browser!
