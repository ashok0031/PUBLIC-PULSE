import os
import requests
import time
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

# Get API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini client if API key is valid
client = None
if GEMINI_API_KEY:
    try:
        import google.genai as genai
        from google.genai.errors import ClientError
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini AI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI client: {e}")
        client = None

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def check_ai_available():
    """Check if AI service is available"""
    if client:
        return True, None
    else:
        return False, "AI service is not available - check GEMINI_API_KEY"

def fallback_summarize(text):
    """Fallback summarization without external API"""
    words = text.split()
    if len(words) <= 20:
        return text
    
    # Simple extractive summarization
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text
    
    # Take first 2 sentences
    summary = '. '.join(sentences[:2]) + '.'
    return summary

def fallback_sentiment(text):
    """Fallback sentiment analysis"""
    positive_words = ['good', 'great', 'excellent', 'positive', 'happy', 'success', 'win', 'profit']
    negative_words = ['bad', 'terrible', 'negative', 'sad', 'loss', 'fail', 'crisis', 'problem']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

# Summarization endpoint
@ai_bp.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data is required'}), 400
            
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Try Gemini first
        if client:
            try:
                prompt = f"Summarize the following news article in 2-3 sentences:\n{text}"
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                summary = response.text.strip() if hasattr(response, 'text') else str(response)
                return jsonify({'summary': summary, 'source': 'gemini'})
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fall back to local processing
        
        # Use fallback
        summary = fallback_summarize(text)
        return jsonify({'summary': summary, 'source': 'fallback'})
        
    except Exception as e:
        logger.error(f"Unexpected error in summarize: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Sentiment analysis endpoint
@ai_bp.route('/sentiment', methods=['POST'])
def sentiment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data is required'}), 400
            
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Try Gemini first
        if client:
            try:
                prompt = f"Analyze the sentiment of this news article. Respond with only: positive, negative, or neutral.\n{text}"
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                sentiment_result = response.text.strip() if hasattr(response, 'text') else str(response)
                return jsonify({'sentiment': sentiment_result, 'source': 'gemini'})
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fall back to local processing
        
        # Use fallback
        sentiment_result = fallback_sentiment(text)
        return jsonify({'sentiment': sentiment_result, 'source': 'fallback'})
        
    except Exception as e:
        logger.error(f"Unexpected error in sentiment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Q&A endpoint
@ai_bp.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data is required'}), 400
            
        text = data.get('text')
        question = data.get('question')
        if not text or not question:
            return jsonify({'error': 'Text and question are required'}), 400
        
        # Try Gemini first
        if client:
            try:
                prompt = f"Given the following news article, answer the question.\nArticle: {text}\nQuestion: {question}"
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                answer = response.text.strip() if hasattr(response, 'text') else str(response)
                return jsonify({'answer': answer, 'source': 'gemini'})
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fall back to local processing
        
        # Use fallback - simple keyword matching
        text_lower = text.lower()
        question_lower = question.lower()
        
        if any(word in text_lower for word in question_lower.split()):
            answer = "Based on the article, the information you're asking about appears to be mentioned."
        else:
            answer = "The article doesn't seem to contain specific information about your question."
        
        return jsonify({'answer': answer, 'source': 'fallback'})
        
    except Exception as e:
        logger.error(f"Unexpected error in ask: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@ai_bp.route('/health', methods=['GET'])
def health():
    available, error_msg = check_ai_available()
    return jsonify({
        'status': 'healthy',
        'ai_available': available,
        'gemini_available': client is not None,
        'fallback_available': True,
        'message': 'AI service is working' if available else error_msg
    }) 