from flask import Blueprint, request, jsonify
from app.database import db
from app.models.review import Review
from app.models.user import User
from app.models.entity import Entity

import os
import requests
from collections import defaultdict
from flask import current_app

from app.utils.sentiment import analyze_sentiment  # You will need to implement this util

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

review_bp = Blueprint('review', __name__, url_prefix='/api/reviews')

# Simple in-memory cache for recent queries (2 min)
_agg_cache = {}
_CACHE_TTL = 300  # seconds (5 minutes)

def get_cached_aggregate(key):
    entry = _agg_cache.get(key)
    if entry and time.time() - entry['ts'] < _CACHE_TTL:
        return entry['data']
    return None

def set_cached_aggregate(key, data):
    _agg_cache[key] = {'data': data, 'ts': time.time()}

@review_bp.route('/<int:entity_id>', methods=['GET'])
def get_reviews(entity_id):
    reviews = Review.query.filter_by(entity_id=entity_id).all()
    return jsonify([{
        'id': r.id,
        'user_id': r.user_id,
        'text': r.text,
        'sentiment': r.sentiment,
        'rating': r.rating,
        'timestamp': r.timestamp.isoformat()
    } for r in reviews])

@review_bp.route('/<int:entity_id>', methods=['POST'])
def post_review(entity_id):
    data = request.get_json()
    user_id = data.get('user_id')
    text = data.get('text')
    sentiment = data.get('sentiment')
    rating = data.get('rating')

    if not user_id or not text:
        return jsonify({'error': 'Missing required fields'}), 400

    if not User.query.get(user_id) or not Entity.query.get(entity_id):
        return jsonify({'error': 'Invalid user or entity'}), 404

    review = Review(user_id=user_id, entity_id=entity_id, text=text, sentiment=sentiment, rating=rating)
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review posted successfully'}), 201 

@review_bp.route('/aggregate', methods=['GET'])
def aggregate_reviews():
    start_time = time.time()
    query = request.args.get('query')
    category = request.args.get('category')
    language = request.args.get('language')
    debug_mode = request.args.get('debug') == '1'
    debug_info = {}
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    cache_key = f'{query}|{category}|{language}'
    cached = get_cached_aggregate(cache_key)
    if cached and not debug_mode:
        return jsonify(cached)

    reviews = []
    ratings = []
    source_counts = defaultdict(int)

    # --- User Reviews (DB) ---
    entity = Entity.query.filter(Entity.name.ilike(f"%{query}%")).first()
    if entity:
        user_reviews = Review.query.filter_by(entity_id=entity.id).all()
        for r in user_reviews:
            reviews.append({
                'text': r.text,
                'sentiment': r.sentiment,
                'rating': r.rating,
                'source': 'User',
                'source_url': None
            })
            if r.rating:
                ratings.append(r.rating)
            source_counts['User'] += 1

    def fetch_youtube():
        t0 = time.time()
        try:
            yt_key = os.getenv('YOUTUBE_API_KEY')
            yt_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}+review&type=video&maxResults=20&key={yt_key}'  # maxResults can be up to 50
            print(f"[YouTube] Fetching for query: {query}")
            yt_resp = requests.get(yt_url, timeout=5)
            out = []
            if yt_resp.status_code == 200:
                yt_data = yt_resp.json()
                for item in yt_data.get('items', []):
                    video_id = item['id']['videoId']
                    title = item['snippet']['title']
                    desc = item['snippet']['description']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    transcript = title + '. ' + desc
                    sentiment = analyze_sentiment(transcript)
                    rating = extract_rating(transcript)
                    if rating is None:
                        rating = sentiment_to_rating(sentiment)
                    out.append({
                        'text': transcript,
                        'sentiment': sentiment,
                        'rating': rating,
                        'source': 'YouTube',
                        'source_url': video_url
                    })
            print(f"YouTube fetch took {time.time() - t0:.2f}s, results: {len(out)}")
            if debug_mode:
                debug_info['youtube'] = {'results': len(out), 'error': None}
            return out
        except Exception as e:
            print(f'YouTube fetch error: {e}')
            print(f"YouTube fetch failed after {time.time() - t0:.2f}s")
            if debug_mode:
                debug_info['youtube'] = {'results': 0, 'error': str(e)}
            return []
    def fetch_reddit():
        t0 = time.time()
        try:
            reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
            if not reddit_client_id or not reddit_secret:
                print('[Reddit] Missing credentials')
                if debug_mode:
                    debug_info['reddit'] = {'results': 0, 'error': 'Missing credentials'}
                return []
            print(f"[Reddit] Fetching for query: {query}")
            reddit_auth = requests.auth.HTTPBasicAuth(reddit_client_id, reddit_secret)
            reddit_headers = {'User-Agent': 'PublicPulse/0.1'}
            reddit_data = {'grant_type': 'client_credentials'}
            reddit_token_resp = requests.post('https://www.reddit.com/api/v1/access_token', auth=reddit_auth, data=reddit_data, headers=reddit_headers, timeout=5)
            out = []
            if reddit_token_resp.status_code == 200:
                reddit_token = reddit_token_resp.json()['access_token']
                reddit_headers['Authorization'] = f'bearer {reddit_token}'
                reddit_search_url = f'https://oauth.reddit.com/search?q={query}&limit=20&sort=relevance&type=link'  # Reddit limit can be up to 100
                reddit_search_resp = requests.get(reddit_search_url, headers=reddit_headers, timeout=5)
                if reddit_search_resp.status_code == 200:
                    for post in reddit_search_resp.json().get('data', {}).get('children', []):
                        post_data = post['data']
                        text = post_data.get('title', '') + '. ' + post_data.get('selftext', '')
                        sentiment = analyze_sentiment(text)
                        rating = extract_rating(text)
                        if rating is None:
                            rating = sentiment_to_rating(sentiment)
                        out.append({
                            'text': text,
                            'sentiment': sentiment,
                            'rating': rating,
                            'source': 'Reddit',
                            'source_url': 'https://reddit.com' + post_data.get('permalink', '')
                        })
            print(f"Reddit fetch took {time.time() - t0:.2f}s, results: {len(out)}")
            if debug_mode:
                debug_info['reddit'] = {'results': len(out), 'error': None}
            return out
        except Exception as e:
            print(f'Reddit fetch error: {e}')
            print(f"Reddit fetch failed after {time.time() - t0:.2f}s")
            if debug_mode:
                debug_info['reddit'] = {'results': 0, 'error': str(e)}
            return []
    def fetch_twitter():
        t0 = time.time()
        try:
            twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
            if not twitter_bearer:
                print('[Twitter] Missing credentials')
                if debug_mode:
                    debug_info['twitter'] = {'results': 0, 'error': 'Missing credentials'}
                return []
            print(f"[Twitter] Fetching for query: {query}")
            twitter_headers = {'Authorization': f'Bearer {twitter_bearer}'}
            twitter_url = f'https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=20&tweet.fields=text,author_id'  # Twitter max_results can be up to 100
            twitter_resp = requests.get(twitter_url, headers=twitter_headers, timeout=5)
            out = []
            if twitter_resp.status_code == 200:
                for tweet in twitter_resp.json().get('data', []):
                    text = tweet.get('text', '')
                    sentiment = analyze_sentiment(text)
                    rating = extract_rating(text)
                    if rating is None:
                        rating = sentiment_to_rating(sentiment)
                    out.append({
                        'text': text,
                        'sentiment': sentiment,
                        'rating': rating,
                        'source': 'Twitter',
                        'source_url': f'https://twitter.com/i/web/status/{tweet["id"]}'
                    })
            print(f"Twitter fetch took {time.time() - t0:.2f}s, results: {len(out)}")
            if debug_mode:
                debug_info['twitter'] = {'results': len(out), 'error': None}
            return out
        except Exception as e:
            print(f'Twitter fetch error: {e}')
            print(f"Twitter fetch failed after {time.time() - t0:.2f}s")
            if debug_mode:
                debug_info['twitter'] = {'results': 0, 'error': str(e)}
            return []
    def fetch_news():
        t0 = time.time()
        try:
            cat = (category or '').lower()
            if cat == 'sports':
                return []
            from app.routes.search import fetch_newsapi_news, fetch_newsdata_io, fetch_gnews_news, fetch_mediastack_news, fetch_currents_news
            news = []
            news += fetch_newsapi_news(query)
            news += fetch_newsdata_io(query)
            news += fetch_gnews_news(query)
            news += fetch_mediastack_news(query)
            news += fetch_currents_news(query)
            seen_news = set()
            out = []
            for item in news:
                url = item.get('url') or item.get('link')
                if url and url in seen_news:
                    continue
                seen_news.add(url)
                text = (item.get('title') or '') + '. ' + (item.get('description') or '')
                sentiment = analyze_sentiment(text)
                rating = extract_rating(text)
                if rating is None:
                    rating = sentiment_to_rating(sentiment)
                source = item.get('source')
                if isinstance(source, dict):
                    source = source.get('name') or source.get('id') or 'News'
                if not isinstance(source, str):
                    source = str(source) if source else 'News'
                out.append({
                    'text': text,
                    'sentiment': sentiment,
                    'rating': rating,
                    'source': source,
                    'source_url': url
                })
            print(f"News fetch took {time.time() - t0:.2f}s, results: {len(out)}")
            if debug_mode:
                debug_info['news'] = {'results': len(out), 'error': None}
            return out
        except Exception as e:
            print(f'News fetch error: {e}')
            print(f"News fetch failed after {time.time() - t0:.2f}s")
            if debug_mode:
                debug_info['news'] = {'results': 0, 'error': str(e)}
            return []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_youtube): 'YouTube',
            executor.submit(fetch_reddit): 'Reddit',
            executor.submit(fetch_twitter): 'Twitter',
            executor.submit(fetch_news): 'News',
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                for r in result:
                    reviews.append(r)
                    ratings.append(r['rating'])
                    source_counts[r['source']] += 1
            except Exception:
                continue
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else (3.0 if reviews else None)
    classified = {'positive': [], 'neutral': [], 'negative': []}
    for r in reviews:
        classified[r['sentiment']].append(r)
    result = {
        'public_pulse_rating': avg_rating,
        'review_count': len(reviews),
        'source_counts': source_counts,
        'classified_reviews': classified,
        'all_reviews': reviews
    }
    set_cached_aggregate(cache_key, result)
    print(f"/aggregate endpoint total time: {time.time() - start_time:.2f}s")
    if debug_mode:
        result['debug'] = debug_info
    return jsonify(result)

@review_bp.route('/submit', methods=['POST'])
def submit_user_review():
    data = request.get_json()
    entity_name = data.get('entity_name')
    user_id = data.get('user_id')
    text = data.get('text')
    rating = data.get('rating')
    if not entity_name or not user_id or not text:
        return jsonify({'error': 'Missing required fields'}), 400
    # Find or create entity
    entity = Entity.query.filter(Entity.name.ilike(entity_name)).first()
    if not entity:
        entity = Entity(name=entity_name, type='unknown')
        db.session.add(entity)
        db.session.commit()
    # Analyze sentiment
    sentiment = analyze_sentiment(text)
    review = Review(user_id=user_id, entity_id=entity.id, text=text, sentiment=sentiment, rating=rating)
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review submitted successfully'}), 201

# --- Helper functions ---
def extract_rating(text):
    # Look for patterns like "4/5", "8 out of 10", "rated 3 stars", etc.
    import re
    patterns = [
        r'(\d+(?:\.\d+)?)[ ]*/[ ]*(10|5)',
        r'(\d+(?:\.\d+)?)[ ]*out of[ ]*(10|5)',
        r'rated[ ]*(\d+(?:\.\d+)?)[ ]*stars?'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            score = float(m.group(1))
            base = float(m.group(2)) if m.lastindex > 1 else 5.0
            return round(5.0 * score / base, 2)
    return None

def sentiment_to_rating(sentiment):
    return {'positive': 4.5, 'neutral': 3.0, 'negative': 2.0}.get(sentiment, 3.0) 