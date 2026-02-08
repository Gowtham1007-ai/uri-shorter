"""
Flask Backend for URL Shortener - React Frontend
"""
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import sqlite3
import hashlib
import random
import string
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React

# Database setup
def get_db():
    conn = sqlite3.connect('urls.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_code():
    """Generate 6-character short code"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

# Initialize database
init_db()

# API Routes
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Shorten a URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url']
    
    # Simple validation
    if not original_url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL. Must start with http:// or https://'}), 400
    
    # Generate unique short code
    short_code = generate_short_code()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Ensure unique code
    for _ in range(5):
        try:
            cursor.execute(
                'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
                (short_code, original_url)
            )
            conn.commit()
            break
        except sqlite3.IntegrityError:
            short_code = generate_short_code()
    
    conn.close()
    
    short_url = f"{request.host_url}{short_code}"
    
    return jsonify({
        'success': True,
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url
    })

@app.route('/api/urls', methods=['GET'])
def get_all_urls():
    """Get all shortened URLs"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM urls ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    urls = []
    for row in rows:
        urls.append({
            'id': row['id'],
            'short_code': row['short_code'],
            'original_url': row['original_url'],
            'clicks': row['clicks'],
            'created_at': row['created_at'],
            'short_url': f"{request.host_url}{row['short_code']}"
        })
    
    return jsonify(urls)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total_urls FROM urls')
    total_urls = cursor.fetchone()['total_urls']
    
    cursor.execute('SELECT SUM(clicks) as total_clicks FROM urls')
    total_clicks = cursor.fetchone()['total_clicks'] or 0
    
    conn.close()
    
    return jsonify({
        'total_urls': total_urls,
        'total_clicks': total_clicks
    })

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to original URL (for short links)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT original_url FROM urls WHERE short_code = ?',
        (short_code,)
    )
    row = cursor.fetchone()
    
    if row:
        # Update click count
        cursor.execute(
            'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?',
            (short_code,)
        )
        conn.commit()
        conn.close()
        return redirect(row['original_url'])
    
    conn.close()
    return jsonify({'error': 'URL not found'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'URL Shortener API'})

if __name__ == '__main__':
    print("🚀 Flask Backend Running...")
    print("🌐 API Base URL: http://localhost:5000")
    print("📊 API Endpoints:")
    print("   POST /api/shorten  - Shorten URL")
    print("   GET  /api/urls     - Get all URLs")
    print("   GET  /api/stats    - Get statistics")
    print("   GET  /:code        - Redirect to URL")
    print("\n⚛️  React frontend should run on: http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=5000)