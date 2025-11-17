#!/usr/bin/env python
# coding: utf-8

"""
Web Interface for LaReQA Multilingual Question Answering System
================================================================

This module provides a Flask-based web interface for the multilingual QA system.
Users can interact with the system through a web browser with a clean, modern UI.

Features:
- Ask questions through a web form
- View results with similarity scores
- Add new Q&A pairs to the knowledge base
- View knowledge base statistics
- Responsive design for mobile and desktop
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from multilingual_qa_system import MultilingualQASystem
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lareqa-multilingual-qa-secret-key-2024'

# Initialize the QA system globally
qa_system = MultilingualQASystem()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Handle question submission and return results.
    
    Returns:
        JSON response with search results
    """
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Please enter a question'}), 400
    
    # Get top results
    results = qa_system.search_answers(question, top_k=5)
    
    # Filter out results with zero similarity
    results = [r for r in results if r['similarity_score'] > 0]
    
    if not results:
        return jsonify({
            'question': question,
            'results': [],
            'message': 'No relevant answers found. Try a different question or add new knowledge to the system.'
        })
    
    return jsonify({
        'question': question,
        'results': results,
        'message': f'Found {len(results)} relevant answer(s)'
    })

@app.route('/add', methods=['POST'])
def add_knowledge():
    """
    Add a new Q&A pair to the knowledge base.
    
    Returns:
        JSON response with success or error message
    """
    data = request.get_json()
    
    language = data.get('language', '').strip()
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    category = data.get('category', 'General').strip()
    
    # Validate inputs
    if not all([language, question, answer]):
        return jsonify({'error': 'All fields (language, question, answer) are required'}), 400
    
    if language not in qa_system.supported_languages:
        return jsonify({'error': f'Unsupported language. Supported: {", ".join(qa_system.supported_languages)}'}), 400
    
    # Add to knowledge base
    qa_system.add_to_knowledge_base(language, question, answer, category)
    
    # Save to file
    qa_system.save_knowledge_base('web_knowledge_base.json')
    
    return jsonify({
        'success': True,
        'message': 'Q&A pair added successfully!'
    })

@app.route('/stats')
def get_stats():
    """
    Get knowledge base statistics.
    
    Returns:
        JSON response with statistics
    """
    stats = qa_system.get_statistics()
    return jsonify(stats)

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*80)
    print("  LaReQA MULTILINGUAL QA SYSTEM - WEB INTERFACE")
    print("="*80)
    print("\n🌐 Starting web server...")
    print("📍 Access the interface at: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop the server")
    print("\n⚠️  Note: For production deployment, use a WSGI server like Gunicorn")
    print("="*80 + "\n")
    
    # Use debug mode only for development
    # Set debug=False for production deployment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
