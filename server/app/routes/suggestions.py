"""
Search suggestions/autocomplete endpoint
"""
import os
import logging
from flask import Blueprint, request, jsonify
from typing import List, Dict
from functools import lru_cache

from app.services.cache_service import cache_service
from app.database import db
from app.models.news_article import NewsArticle
from app.models.entity import Entity

logger = logging.getLogger(__name__)

suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/api/suggestions')

# In-memory cache for popular suggestions
_popular_entities = []
_popular_news_titles = []

def _load_popular_suggestions():
    """Load popular entities and news titles for suggestions"""
    global _popular_entities, _popular_news_titles
    
    try:
        # Load recent popular entities
        entities = Entity.query.order_by(Entity.id.desc()).limit(100).all()
        _popular_entities = [e.name for e in entities if e.name]
        
        # Load recent news titles
        news = NewsArticle.query.filter(
            NewsArticle.is_duplicate == False
        ).order_by(NewsArticle.published_at.desc()).limit(200).all()
        
        _popular_news_titles = [n.title for n in news if n.title]
        
        logger.info(f"Loaded {len(_popular_entities)} entities and {len(_popular_news_titles)} news titles for suggestions")
    except Exception as e:
        logger.error(f"Error loading popular suggestions: {e}")

# Load on module import
_load_popular_suggestions()

def _fuzzy_match(query: str, candidates: List[str], limit: int = 10) -> List[str]:
    """
    Simple fuzzy matching for suggestions
    Returns candidates that contain the query (case-insensitive)
    """
    query_lower = query.lower()
    matches = []
    
    for candidate in candidates:
        if query_lower in candidate.lower():
            matches.append(candidate)
            if len(matches) >= limit:
                break
    
    # Sort by position of match (earlier matches first)
    matches.sort(key=lambda x: x.lower().find(query_lower))
    
    return matches[:limit]

@suggestions_bp.route('/', methods=['GET'])
def get_suggestions():
    """
    Get search suggestions/autocomplete
    
    Query params:
        q: Search query (required)
        category: Optional category filter
        limit: Max number of suggestions (default: 10)
    """
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip().lower()
    limit = min(int(request.args.get('limit', 10)), 20)  # Max 20
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Check cache
    cache_key = f"suggestions:{query}:{category}:{limit}"
    cached = cache_service.get(cache_key)
    if cached:
        return jsonify(cached)
    
    suggestions = []
    
    # Search in popular entities
    entity_matches = _fuzzy_match(query, _popular_entities, limit=limit)
    for match in entity_matches:
        suggestions.append({
            'text': match,
            'type': 'entity',
            'category': 'company'
        })
    
    # Search in news titles
    news_matches = _fuzzy_match(query, _popular_news_titles, limit=limit)
    for match in news_matches:
        if match not in [s['text'] for s in suggestions]:
            suggestions.append({
                'text': match,
                'type': 'news',
                'category': 'news'
            })
    
    # Add common search terms if we have few results
    if len(suggestions) < limit:
        common_terms = [
            'India', 'Government', 'Sports', 'Entertainment', 'Business',
            'Technology', 'Finance', 'Healthcare', 'Education'
        ]
        for term in common_terms:
            if query.lower() in term.lower() and term not in [s['text'] for s in suggestions]:
                suggestions.append({
                    'text': term,
                    'type': 'category',
                    'category': term.lower()
                })
                if len(suggestions) >= limit:
                    break
    
    # Apply category filter if specified
    if category:
        suggestions = [s for s in suggestions if category in s.get('category', '').lower()]
    
    # Limit results
    suggestions = suggestions[:limit]
    
    # Cache for 5 minutes
    cache_service.set(cache_key, suggestions, ttl_seconds=300)
    
    return jsonify(suggestions)

@suggestions_bp.route('/refresh', methods=['POST'])
def refresh_suggestions():
    """Refresh the popular suggestions cache"""
    try:
        _load_popular_suggestions()
        return jsonify({'status': 'success', 'message': 'Suggestions refreshed'})
    except Exception as e:
        logger.error(f"Error refreshing suggestions: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

