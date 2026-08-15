import os
import sqlite3
import logging
from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS so the static HTML can call the API even when opened directly as a file
CORS(app)

MAX_FEEDBACK_WORDS = 100

# Local SQLite database file for storing feedback
DB_PATH = os.environ.get('FEEDBACK_DB_PATH', os.path.join(os.path.dirname(__file__), 'feedback.db'))

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create the feedback table if it does not exist in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized: 'feedback' table checked/created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Run database initialization on startup
init_db()

@app.route('/')
def home():
    """Redirect to the Svelte-based landing page on the main WebUI server."""
    # 1. Check WEBUI_URL environment variable
    webui_url = os.environ.get('WEBUI_URL', '')
    
    # 2. Check CORS_ALLOW_ORIGIN if WEBUI_URL is not set
    if not webui_url:
        cors_origins = os.environ.get('CORS_ALLOW_ORIGIN', '')
        if cors_origins:
            # e.g., "http://localhost:5173;http://localhost:8080"
            origins = [o.strip() for o in cors_origins.split(';') if o.strip()]
            if origins:
                # Prefer the first one (dev server if present)
                webui_url = origins[0]
                
    # 3. Fallback based on debug / environment mode
    if not webui_url:
        env_mode = os.environ.get('ENV', 'dev')
        if app.debug or env_mode == 'dev':
            webui_url = "http://localhost:5173"
        else:
            webui_url = "http://localhost:8080"
            
    redirect_url = f"{webui_url.rstrip('/')}/landing"
    logger.info(f"Redirecting home route to: {redirect_url}")
    return redirect(redirect_url)

@app.route('/api/submit-feedback', methods=['POST'])
def submit_feedback():
    """Insert a new feedback comment into the feedback table."""
    data = request.get_json()
    if not data or 'email' not in data or 'comment' not in data:
        return jsonify({"error": "Email and comment are required"}), 400

    email = data['email'].strip()
    comment = data['comment'].strip()

    if not email:
        return jsonify({"error": "Email cannot be empty"}), 400

    if not comment:
        return jsonify({"error": "Comment cannot be empty"}), 400

    word_count = len(comment.split())
    if word_count > MAX_FEEDBACK_WORDS:
        return jsonify({"error": f"Feedback cannot exceed {MAX_FEEDBACK_WORDS} words"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO feedback (email, comment) VALUES (?, ?);',
            (email, comment)
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Feedback successfully saved for {email}")
        return jsonify({"success": True, "message": "Feedback submitted successfully"}), 200
    except Exception as e:
        logger.error(f"Database error during feedback submission: {e}")
        return jsonify({"error": f"Failed to submit feedback: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
