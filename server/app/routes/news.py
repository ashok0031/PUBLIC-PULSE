import os
import requests
from flask import Blueprint, request, jsonify, current_app

news_bp = Blueprint('news', __name__, url_prefix='/api/news')

NEWS_DATA_KEY = os.getenv('NEWSDATA_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_API_KEY')
DATAGOVIN_KEY = os.getenv('DATAGOVIN_API_KEY')

# Map your app's categories to NewsAPI.org and NewsData.io allowed values
CATEGORY_MAP = {
    'Government Schemes': {'newsapi': 'general', 'newsdata': 'politics'},
    'Private Companies': {'newsapi': 'business', 'newsdata': 'business'},
    'Education': {'newsapi': 'education', 'newsdata': 'education'},
    'Healthcare': {'newsapi': 'health', 'newsdata': 'health'},
    'Sports': {'newsapi': 'sports', 'newsdata': 'sports'},
    'Entertainment': {'newsapi': 'entertainment', 'newsdata': 'entertainment'},
    'India': {'newsapi': 'general', 'newsdata': 'top'},
}

# NewsData.io allowed: 'business', 'entertainment', 'environment', 'food', 'health', 'politics', 'science', 'sports', 'technology', 'top', 'tourism', 'world', 'education'
# NewsAPI.org allowed: 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'

def normalize_news_item(item):
    """Normalize news item to consistent format"""
    if not item or not isinstance(item, dict):
        return None
    
    # Handle source field (can be string or dict)
    source = item.get('source') or item.get('source_name') or item.get('sourceName') or 'Unknown'
    if isinstance(source, dict):
        source = source.get('name', source.get('id', 'Unknown'))
    if not source or source == '':
        source = 'Unknown'
    
    # Handle different API formats
    normalized = {
        'title': item.get('title') or item.get('headline') or '',
        'description': item.get('description') or item.get('content') or item.get('summary') or item.get('extract') or '',
        'url': item.get('url') or item.get('link') or item.get('webUrl') or '',
        'image': item.get('image') or item.get('image_url') or item.get('urlToImage') or item.get('imageUrl') or '',
        'source': str(source),
        'source_name': str(source),  # Also include for compatibility
        'publishedAt': item.get('publishedAt') or item.get('published_at') or item.get('pubDate') or item.get('published_date') or '',
    }
    
    # Ensure we have at least a title or description
    if not normalized['title'] and not normalized['description']:
        return None
    
    return normalized

def fetch_newsdata_io(category):
    url = 'https://newsdata.io/api/1/latest'
    mapped = CATEGORY_MAP.get(category, {})
    newsdata_cat = mapped.get('newsdata')
    params = {
        'apikey': NEWS_DATA_KEY,
        'country': 'in',
        'language': 'en',
        'size': 20  # Increased to ensure we get enough articles
    }
    if newsdata_cat:
        params['category'] = newsdata_cat
    else:
        params['q'] = category or 'India'
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f'newsdata.io HTTP error: {resp.status_code}')
            return []
        data = resp.json()
        results = data.get('results', [])
        # Normalize results
        normalized = []
        for item in results:
            norm = normalize_news_item(item)
            if norm:
                normalized.append(norm)
        return normalized
    except Exception as e:
        print('newsdata.io error:', e)
        return []

def fetch_newsapi_org(category):
    url = 'https://newsapi.org/v2/top-headlines'
    mapped = CATEGORY_MAP.get(category, {})
    newsapi_cat = mapped.get('newsapi')
    params = {
        'apiKey': NEWSAPI_KEY,
        'country': 'in',
        'language': 'en',
        'pageSize': 20  # Increased to ensure we get enough articles
    }
    if newsapi_cat:
        params['category'] = newsapi_cat
    else:
        params['q'] = category or 'India'
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f'newsapi.org HTTP error: {resp.status_code}')
            return []
        data = resp.json()
        articles = data.get('articles', [])
        # Normalize results
        normalized = []
        for item in articles:
            norm = normalize_news_item(item)
            if norm:
                normalized.append(norm)
        return normalized
    except Exception as e:
        print('newsapi.org error:', e)
        return []

def fetch_datagovin():
    url = 'https://api.data.gov.in/resource/press-releases-ministry-information-and-broadcasting'
    params = {
        'api-key': DATAGOVIN_KEY,
        'format': 'json',
        'limit': 10  # Reverted to original limit
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data.get('records', [])
    except Exception as e:
        print('data.gov.in error:', e)
        return []

def fetch_knowivate_latest():
    url = "https://news.knowivate.com/api/latest"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Return up to 30 articles for Knowivate, normalized
            items = data.get('news', [])[:30]
            normalized = []
            for item in items:
                norm = normalize_news_item(item)
                if norm:
                    normalized.append(norm)
            return normalized
        return []
    except Exception as e:
        print('knowivate latest error:', e)
        return []

def fetch_knowivate_local():
    url = "https://news.knowivate.com/api/local"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Return up to 30 articles for Knowivate, normalized
            items = data.get('news', [])[:30]
            normalized = []
            for item in items:
                norm = normalize_news_item(item)
                if norm:
                    normalized.append(norm)
            return normalized
        return []
    except Exception as e:
        print('knowivate local error:', e)
        return []

def dedupe_news(news):
    """Deduplicate news items by URL"""
    seen = set()
    deduped = []
    for item in news:
        if not item:
            continue
        try:
            normalized = normalize_news_item(item)
            if not normalized:
                continue
            url = normalized.get('url')
            if url and url not in seen:
                deduped.append(normalized)
                seen.add(url)
        except Exception as e:
            print(f'Error normalizing news item: {e}')
            continue
    return deduped

@news_bp.route('/', methods=['GET'])
def get_news():
    try:
        category = request.args.get('category', 'India')
        results = []
        # Try each source independently, always append
        newsdata_results = []
        newsapi_results = []
        datagovin_results = []
        gnews_results = []
        mediastack_results = []
        currents_results = []
        knowivate_latest_results = []
        knowivate_local_results = []
        
        # Fetch main APIs with error handling
        try:
            if NEWS_DATA_KEY:
                newsdata_results = fetch_newsdata_io(category)
                print(f'NewsData.io: {len(newsdata_results)} articles')
        except Exception as e:
            print(f'NewsData.io error: {e}')
            newsdata_results = []
        
        try:
            if NEWSAPI_KEY:
                newsapi_results = fetch_newsapi_org(category)
                print(f'NewsAPI.org: {len(newsapi_results)} articles')
        except Exception as e:
            print(f'NewsAPI.org error: {e}')
            newsapi_results = []
        
        try:
            if DATAGOVIN_KEY and category.lower() in ['government schemes', 'government', 'schemes', 'policy', 'policies']:
                datagovin_results = fetch_datagovin()
                print(f'DataGovIn: {len(datagovin_results)} articles')
        except Exception as e:
            print(f'DataGovIn error: {e}')
            datagovin_results = []
        
        try:
            from app.routes.search import fetch_gnews_news, fetch_mediastack_news, fetch_currents_news
            gnews_results = fetch_gnews_news(category)
            print(f'GNews: {len(gnews_results)} articles')
            mediastack_results = fetch_mediastack_news(category)
            print(f'MediaStack: {len(mediastack_results)} articles')
            currents_results = fetch_currents_news(category)
            print(f'Currents: {len(currents_results)} articles')
        except Exception as e:
            print('Optional news sources error:', e)
            import traceback
            traceback.print_exc()
            gnews_results = []
            mediastack_results = []
            currents_results = []
        
        try:
            knowivate_latest_results = fetch_knowivate_latest()
            knowivate_local_results = fetch_knowivate_local()
            print(f'Knowivate latest: {len(knowivate_latest_results)} articles')
            print(f'Knowivate local: {len(knowivate_local_results)} articles')
        except Exception as e:
            print(f'Knowivate error: {e}')
            knowivate_latest_results = []
            knowivate_local_results = []
        
        # Combine all results
        main_apis = newsdata_results + newsapi_results + datagovin_results + gnews_results + mediastack_results + currents_results
        knowivate_apis = knowivate_latest_results + knowivate_local_results
        all_news = main_apis + knowivate_apis
        
        # Normalize and dedupe
        all_news = dedupe_news(all_news)
        
        max_cards = 50
        min_cards = 20  # Changed from 30 to 20 as requested
        main_count = int(max_cards * 0.65)
        
        # Prioritize main APIs first
        prioritized = main_apis[:main_count] + knowivate_apis
        prioritized = dedupe_news(prioritized)
        
        # Fill with Knowivate if less than min_cards
        if len(prioritized) < min_cards:
            for n in knowivate_apis:
                if n not in prioritized:
                    normalized = normalize_news_item(n)
                    if normalized:
                        prioritized.append(normalized)
                if len(prioritized) >= min_cards:
                    break
        
        # If still not enough, fill with any other news
        if len(prioritized) < min_cards:
            for n in all_news:
                if n not in prioritized:
                    prioritized.append(n)
                if len(prioritized) >= min_cards:
                    break
        
        # Final slice
        prioritized = prioritized[:max_cards]
        print(f'Total articles returned to frontend after prioritization (min {min_cards}): {len(prioritized)}')
        
        # Ensure we return at least some results even if less than min_cards
        if len(prioritized) == 0:
            # Return empty array with message
            return jsonify([])
        
        return jsonify(prioritized)
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        print(f'Error in get_news: {error_msg}')
        # Return empty array instead of error to prevent frontend crash
        return jsonify([]), 200 