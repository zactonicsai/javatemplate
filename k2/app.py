from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Define the keywords for classification/verification
# You would load these from a file/database in a real-world application.
VERIFICATION_KEYWORDS = {
    "finance": ["money", "loan", "investment", "capital", "stock", "interest"],
    "technology": ["software", "api", "database", "cloud", "algorithm", "server"],
    "legal": ["contract", "clause", "litigation", "attorney", "jurisdiction", "regulation"],
}

def verify_keywords(text):
    """
    Analyzes the text and identifies found keywords and their associated categories.
    """
    text_lower = text.lower()
    results = {}
    
    for category, keywords in VERIFICATION_KEYWORDS.items():
        found_keywords = [
            keyword for keyword in keywords if keyword in text_lower
        ]
        if found_keywords:
            results[category] = {
                "count": len(found_keywords),
                "keywords": found_keywords
            }
            
    return results

@app.route('/')
def index():
    """Serves the main HTML form."""
    # Pass the keywords to the template for display
    return render_template('index.html', keywords=VERIFICATION_KEYWORDS)

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """Handles the text submission and returns the verification results."""
    # Handle both form data (from HTML) and JSON data (from other APIs)
    data = request.form or request.get_json()
    document_text = data.get('document_text', '')
    
    if not document_text:
        return jsonify({"error": "No document text provided"}), 400
    
    verification_results = verify_keywords(document_text)
    
    return jsonify({
        "status": "success",
        "results": verification_results,
        "summary": f"Found {sum(v['count'] for v in verification_results.values())} keywords across {len(verification_results)} categories."
    })

if __name__ == '__main.':
    """Runs the Flask application."""
    # In production, use a WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=5000)
