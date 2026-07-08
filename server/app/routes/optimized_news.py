from flask import Blueprint, request, jsonify, current_app
from app.models.news_article import NewsArticle
from app.services.search_index import SearchIndexService
from app.services.news_fetcher import NewsFetcherService
from app.database import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

optimized_news_bp = Blueprint('optimized_news', __name__, url_prefix='/api/v2/news')

@optimized_news_bp.route('/', methods=['GET'])
def get_news():
    """Get news from database with optional search and filtering"""
    try:
        # Get query parameters
        category = request.args.get('category', 'India')
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)  # Max 50 per page
        sort_by = request.args.get('sort', 'published_at')
        
        # Build filters
        filters = {}
        if category and category != 'India':
            filters['category'] = category
        
        # Use search service if query provided, otherwise get from database
        if query:
            search_service = SearchIndexService()
            results = search_service.search_articles(
                query=query,
                filters=filters,
                sort_by=sort_by,
                page=page,
                per_page=per_page
            )
        else:
            # Get from database directly
            results = _get_news_from_db(category, filters, sort_by, page, per_page)
        
        # Add metadata
        response = {
            'success': True,
            'data': results['articles'],
            'pagination': {
                'page': results['page'],
                'per_page': results['per_page'],
                'total': results['total'],
                'total_pages': results['total_pages']
            },
            'filters': {
                'category': category,
                'query': query,
                'sort_by': sort_by
            },
            'cache_info': {
                'source': 'database',
                'last_updated': datetime.utcnow().isoformat()
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch news',
            'message': str(e)
        }), 500

@optimized_news_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get available news categories with article counts"""
    try:
        categories = db.session.query(
            NewsArticle.category,
            db.func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.is_duplicate == False,
            NewsArticle.is_expired == False
        ).group_by(NewsArticle.category).all()
        
        category_data = [
            {
                'name': cat.category,
                'count': cat.count,
                'slug': cat.category.lower().replace(' ', '-')
            }
            for cat in categories
        ]
        
        return jsonify({
            'success': True,
            'categories': category_data
        })
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch categories'
        }), 500

@optimized_news_bp.route('/sources', methods=['GET'])
def get_sources():
    """Get available news sources with metadata"""
    try:
        sources = db.session.query(
            NewsArticle.source_name,
            db.func.count(NewsArticle.id).label('count'),
            db.func.avg(NewsArticle.source_reliability).label('avg_reliability'),
            db.func.avg(NewsArticle.source_bias_score).label('avg_bias')
        ).filter(
            NewsArticle.is_duplicate == False,
            NewsArticle.is_expired == False
        ).group_by(NewsArticle.source_name).all()
        
        source_data = [
            {
                'name': source.source_name,
                'article_count': source.count,
                'reliability_score': round(float(source.avg_reliability or 0.5), 2),
                'bias_score': round(float(source.avg_bias or 0.0), 2),
                'bias_label': _get_bias_label(source.avg_bias or 0.0)
            }
            for source in sources
        ]
        
        return jsonify({
            'success': True,
            'sources': source_data
        })
        
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch sources'
        }), 500

@optimized_news_bp.route('/trending', methods=['GET'])
def get_trending():
    """Get trending articles based on recent activity"""
    try:
        # Get articles from last 7 days, ordered by creation time
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        trending = NewsArticle.query.filter(
            NewsArticle.is_duplicate == False,
            NewsArticle.is_expired == False,
            NewsArticle.created_at >= week_ago
        ).order_by(NewsArticle.created_at.desc()).limit(10).all()
        
        trending_data = [article.to_dict() for article in trending]
        
        return jsonify({
            'success': True,
            'trending': trending_data,
            'period': '7 days'
        })
        
    except Exception as e:
        logger.error(f"Error getting trending news: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch trending news'
        }), 500

@optimized_news_bp.route('/refresh', methods=['POST'])
def refresh_news():
    """Manually trigger news refresh (admin function)"""
    try:
        # Check if user is admin (you can add proper auth here)
        # For now, we'll allow it but add rate limiting
        
        # Trigger background refresh
        from app.services.news_fetcher import fetch_all_news_task
        task = fetch_all_news_task.delay()
        
        return jsonify({
            'success': True,
            'message': 'News refresh started in background',
            'task_id': task.id
        })
        
    except Exception as e:
        logger.error(f"Error starting news refresh: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to start news refresh'
        }), 500

@optimized_news_bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions based on partial query"""
    try:
        query = request.args.get('q', '')
        limit = min(int(request.args.get('limit', 5)), 10)
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        search_service = SearchIndexService()
        suggestions = search_service.suggest_queries(query, limit)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get suggestions'
        }), 500

@optimized_news_bp.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        article = NewsArticle.query.get_or_404(article_id)
        
        # Get similar articles
        from app.services.deduplication import NewsDeduplicationService
        dedup_service = NewsDeduplicationService()
        similar_articles = dedup_service.get_similar_articles(article, limit=5)
        
        article_data = article.to_dict()
        article_data['similar_articles'] = [
            {
                'id': similar.id,
                'title': similar.title,
                'url': similar.url,
                'source_name': similar.source_name
            }
            for similar in similar_articles
        ]
        
        return jsonify({
            'success': True,
            'article': article_data
        })
        
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch article'
        }), 500

def _get_news_from_db(category, filters, sort_by, page, per_page):
    """Get news from database with filtering and pagination"""
    query = NewsArticle.query.filter_by(is_duplicate=False, is_expired=False)
    
    # Apply category filter
    if category and category != 'India':
        query = query.filter(NewsArticle.category == category)
    
    # Apply sorting
    if sort_by == 'published_at':
        query = query.order_by(NewsArticle.published_at.desc().nullslast())
    elif sort_by == 'created_at':
        query = query.order_by(NewsArticle.created_at.desc())
    elif sort_by == 'source_reliability':
        query = query.order_by(NewsArticle.source_reliability.desc())
    elif sort_by == 'ai_sentiment':
        query = query.order_by(NewsArticle.ai_sentiment.desc().nullslast())
    else:
        query = query.order_by(NewsArticle.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    articles = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Convert to dict format
    article_dicts = [article.to_dict() for article in articles]
    
    return {
        'articles': article_dicts,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

def _get_bias_label(bias_score):
    """Convert bias score to human-readable label"""
    if bias_score < -0.3:
        return 'Left-leaning'
    elif bias_score > 0.3:
        return 'Right-leaning'
    else:
        return 'Neutral'
