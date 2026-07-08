import os
import requests
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

# Helper: Wikipedia summary
def fetch_wikipedia_summary(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    headers = {
        'User-Agent': 'PublicPulse/1.0 (https://github.com/yourusername/public-pulse; contact@example.com)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Check if it's a valid page (not an error)
            if data.get('type') != 'https://mediawiki.org/wiki/HyperSwitch/errors/not_found':
                return data
        elif resp.status_code == 404:
            # Try URL encoding
            from urllib.parse import quote
            encoded_title = quote(title.replace(' ', '_'))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('type') != 'https://mediawiki.org/wiki/HyperSwitch/errors/not_found':
                    return data
    except Exception as e:
        print(f"Wikipedia fetch error for '{title}': {e}")
    return None

def fetch_wikipedia_movie_variants(query):
    # Try several title variants for movies
    variants = [
        query,
        query.replace('movie', '').strip(),
        query.replace('film', '').strip(),
        f"{query} (film)",
        f"{query} (movie)",
        f"{query.title()} (film)",
        f"{query.title()} (movie)",
        query.title(),
    ]
    seen = set()
    for v in variants:
        v = v.strip()
        if not v or v in seen:
            continue
        seen.add(v)
        wiki = fetch_wikipedia_summary(v)
        if wiki and wiki.get('extract'):
            return wiki
    return None

# Helper: OMDb movie info
def fetch_omdb_movie(title):
    key = os.getenv('OMDB_API_KEY')
    url = f"https://www.omdbapi.com/?apikey={key}&t={title}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('Response') == 'True':
            return data
    return None

# Helper: TMDB movie info (fallback/alternative)
def fetch_tmdb_movie(title):
	key = os.getenv('TMDB_API_KEY')
	if not key:
		return None
	try:
		url = f"https://api.themoviedb.org/3/search/movie?api_key={key}&query={title}"
		resp = requests.get(url, timeout=6)
		if resp.status_code == 200:
			results = resp.json().get('results', [])
			if results:
				movie = results[0]
				poster = movie.get('poster_path')
				return {
					'Title': movie.get('title'),
					'Plot': movie.get('overview'),
					'Poster': f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
					'ReleaseDate': movie.get('release_date'),
					'VoteAverage': movie.get('vote_average')
				}
	except Exception:
		return None
	return None

# Helper: TVMaze show info (no key required)
def fetch_tvmaze_show(title):
	try:
		url = f"https://api.tvmaze.com/singlesearch/shows?q={title}"
		resp = requests.get(url, timeout=6)
		if resp.status_code == 200:
			data = resp.json()
			image = (data.get('image') or {}).get('medium')
			return {
				'Title': data.get('name'),
				'Plot': data.get('summary'),
				'Poster': image,
				'Premiered': data.get('premiered')
			}
	except Exception:
		return None
	return None

# Helper: TheSportsDB team search
def fetch_sports_team(name):
    key = os.getenv('THESPORTSDB_API_KEY')
    url = f"https://www.thesportsdb.com/api/v1/json/{key}/searchteams.php?t={name}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('teams'):
            return data['teams'][0]
    return None

# Helper: API-Football team search (API-Sports)
def fetch_api_football_team(name):
	api_key = os.getenv('API_FOOTBALL_KEY')
	if not api_key:
		return None
	try:
		url = f"https://v3.football.api-sports.io/teams?search={name}"
		headers = {"x-apisports-key": api_key}
		resp = requests.get(url, headers=headers, timeout=6)
		if resp.status_code == 200:
			data = resp.json().get('response', [])
			return data[0] if data else None
	except Exception:
		return None
	return None

# Helper: Football-Data.org recent matches containing query in team names
def fetch_football_data_matches(query):
	api_key = os.getenv('FOOTBALL_DATA_API_KEY')
	if not api_key:
		return []
	try:
		date_to = datetime.utcnow().date()
		date_from = date_to - timedelta(days=7)
		url = f"https://api.football-data.org/v4/matches?dateFrom={date_from}&dateTo={date_to}"
		headers = {"X-Auth-Token": api_key}
		resp = requests.get(url, headers=headers, timeout=6)
		if resp.status_code == 200:
			matches = []
			for m in resp.json().get('matches', []):
				teams = f"{m.get('homeTeam', {}).get('name','')} vs {m.get('awayTeam', {}).get('name','')}"
				if query.lower() in teams.lower():
					matches.append({
						'utcDate': m.get('utcDate'),
						'status': m.get('status'),
						'competition': (m.get('competition') or {}).get('name'),
						'teams': teams
					})
			return matches
	except Exception:
		return []
	return []

# Helper: CricAPI recent matches (simple filter)
def fetch_cricapi_matches(query):
	api_key = os.getenv('CRICAPI_KEY')
	if not api_key:
		return []
	try:
		url = f"https://cricapi.com/api/matches?apikey={api_key}"
		resp = requests.get(url, timeout=8)
		if resp.status_code == 200:
			out = []
			for m in resp.json().get('matches', []):
				title = f"{m.get('team-1','')} vs {m.get('team-2','')}"
				if query.lower() in title.lower():
					out.append({'title': title, 'type': m.get('type'), 'date': m.get('date')})
			return out
	except Exception:
		return []
	return []

# Helper: Pexels images
def fetch_pexels_images(query):
	api_key = os.getenv('PEXELS_API_KEY')
	if not api_key:
		return []
	try:
		headers = {"Authorization": api_key}
		url = f"https://api.pexels.com/v1/search?query={query}&per_page=10"
		resp = requests.get(url, headers=headers, timeout=6)
		if resp.status_code == 200:
			photos = resp.json().get('photos', [])
			return [
				{
					'url': p.get('url'),
					'image': (p.get('src') or {}).get('medium') or (p.get('src') or {}).get('original'),
					'photographer': p.get('photographer')
				}
				for p in photos
			]
	except Exception:
		return []
	return []

# Helper: SerpAPI web results
def fetch_serpapi_results(query):
	api_key = os.getenv('SERPAPI_KEY')
	if not api_key:
		return []
	try:
		url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}"
		resp = requests.get(url, timeout=8)
		if resp.status_code == 200:
			return [
				{
					'title': r.get('title'),
					'url': r.get('link'),
					'snippet': r.get('snippet')
				}
				for r in resp.json().get('organic_results', [])
			][:10]
	except Exception:
		return []
	return []

# Helper: News search (NewsAPI.org)
def fetch_newsapi_news(query):
    key = os.getenv('NEWSAPI_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={key}&language=en&pageSize=10"  # Reverted to 10
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('articles', [])
    return []

def filter_news_by_movie(news, movie_name):
    filtered = []
    movie_name_lower = movie_name.lower()
    for item in news:
        title = (item.get('title') or '').lower()
        desc = (item.get('description') or '').lower()
        if movie_name_lower in title or movie_name_lower in desc:
            filtered.append(item)
    return filtered

def is_disambiguation(wiki):
    extract = (wiki.get('extract') or '').lower()
    return 'may refer to' in extract or wiki.get('type') == 'disambiguation'

def is_sports_related(wiki):
    extract = (wiki.get('extract') or '').lower()
    keywords = ['team', 'club', 'league', 'cricket', 'football', 'soccer', 'hockey', 'basketball', 'sports', 'athlete', 'olympic', 'tournament', 'match', 'stadium']
    return any(word in extract for word in keywords)

def is_entertainment_related(wiki):
    extract = (wiki.get('extract') or '').lower()
    keywords = ['film', 'movie', 'cinema', 'actor', 'actress', 'director', 'producer', 'entertainment', 'bollywood', 'hollywood', 'tollywood', 'kollywood', 'theatre', 'screenplay']
    return any(word in extract for word in keywords)

def is_company_related(wiki):
    extract = (wiki.get('extract') or '').lower()
    keywords = ['company', 'corporation', 'limited', 'ltd', 'inc', 'pvt', 'enterprise', 'business', 'firm', 'organization', 'industry', 'multinational']
    return any(word in extract for word in keywords)

def is_gov_scheme_related(wiki):
    extract = (wiki.get('extract') or '').lower()
    keywords = ['scheme', 'government', 'policy', 'initiative', 'programme', 'plan', 'ministry', 'welfare', 'yojana']
    return any(word in extract for word in keywords)

def is_finance_related(wiki):
    extract = (wiki.get('extract') or '').lower()
    keywords = ['finance', 'stock', 'market', 'exchange', 'investment', 'bank', 'trading', 'equity', 'share', 'nasdaq', 'nyse', 'bse', 'nse', 'mutual fund', 'ipo', 'dividend', 'portfolio', 'securities', 'fintech']
    return any(word in extract for word in keywords)

def fetch_alpha_vantage_news(query):
    key = os.getenv('ALPHA_VANTAGE_KEY')
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={query}&apikey={key}'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['title'],
                'url': item['url'],
                'image': item.get('banner_image'),
                'source': item.get('source'),
                'publishedAt': item.get('time_published'),
                'description': item.get('summary')
            }
            for item in data.get('feed', [])
        ]
    return []

def fetch_finnhub_news(query):
    key = os.getenv('FINNHUB_API_KEY')
    url = f'https://finnhub.io/api/v1/news?category=general&token={key}'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['headline'],
                'url': item['url'],
                'image': item.get('image'),
                'source': item.get('source'),
                'publishedAt': item.get('datetime'),
                'description': item.get('summary')
            }
            for item in data
        ]
    return []

def fetch_newsdata_io(query):
    key = os.getenv('NEWSDATA_API_KEY')
    url = f'https://newsdata.io/api/1/news?apikey={key}&q={query}&language=en'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['title'],
                'url': item['link'],
                'image': item.get('image_url'),
                'source': item.get('source_id'),
                'publishedAt': item.get('pubDate'),
                'description': item.get('description')
            }
            for item in data.get('results', [])
        ]
    return []

def dedupe_news(news):
    seen = set()
    deduped = []
    for item in news:
        url = item.get('url')
        if url and url not in seen:
            deduped.append(item)
            seen.add(url)
    return deduped

def filter_news_by_category(news, category_keywords):
    filtered = []
    for item in news:
        text = ((item.get('title') or '') + ' ' + (item.get('description') or '')).lower()
        if any(word in text for word in category_keywords):
            filtered.append(item)
    return filtered

def fetch_gnews_news(query):
    key = os.getenv('GNEWS_API_KEY')
    url = f'https://gnews.io/api/v4/search?q={query}&token={key}&lang=en'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['title'],
                'url': item['url'],
                'image': item.get('image'),
                'source': item.get('source', {}).get('name'),
                'publishedAt': item.get('publishedAt'),
                'description': item.get('description')
            }
            for item in data.get('articles', [])
        ]
    return []

def fetch_mediastack_news(query):
    key = os.getenv('MEDIASTACK_API_KEY')
    url = f'http://api.mediastack.com/v1/news?access_key={key}&keywords={query}&languages=en'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['title'],
                'url': item['url'],
                'image': item.get('image'),
                'source': item.get('source'),
                'publishedAt': item.get('published_at'),
                'description': item.get('description')
            }
            for item in data.get('data', [])
        ]
    return []

def fetch_currents_news(query):
    key = os.getenv('CURRENTS_API_KEY')
    url = f'https://api.currentsapi.services/v1/search?apiKey={key}&keywords={query}&language=en'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return [
            {
                'title': item['title'],
                'url': item['url'],
                'image': item.get('image'),
                'source': item.get('source'),
                'publishedAt': item.get('published'),
                'description': item.get('description')
            }
            for item in data.get('news', [])
        ]
    return []

def fetch_knowivate_latest():
    url = "https://news.knowivate.com/api/latest"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Format to match other news sources
            return [
                {
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'image': item.get('image'),
                    'source': 'Knowivate',
                    'publishedAt': item.get('publishedAt'),
                    'description': item.get('description')
                }
                for item in data.get('articles', [])
            ]
    except Exception as e:
        print('Knowivate latest error:', e)
    return []

def fetch_knowivate_local():
    url = "https://news.knowivate.com/api/local"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [
                {
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'image': item.get('image'),
                    'source': 'Knowivate',
                    'publishedAt': item.get('publishedAt'),
                    'description': item.get('description')
                }
                for item in data.get('articles', [])
            ]
    except Exception as e:
        print('Knowivate local error:', e)
    return []

@search_bp.route('/unified', methods=['GET'])
def unified_search():
    """
    New unified search endpoint with improved deduplication and fallback logic
    Supports pagination and confidence scoring
    """
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(50, max(1, int(request.args.get('per_page', 20))))  # Max 50 per page
    
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    
    try:
        from app.services.unified_search_service import unified_search
        results = unified_search.search(
            query, 
            category if category else None,
            page=page,
            per_page=per_page
        )
        # Log the response structure for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Unified search for '{query}': companies={len(results.get('companies', []))}, movies={len(results.get('movies', []))}, sports={len(results.get('sports', []))}")
        return jsonify(results)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in unified search: {e}", exc_info=True)
        # Fallback to old search
        return universal_search()

@search_bp.route('/', methods=['GET'])
def universal_search():
    query = request.args.get('query')
    category = request.args.get('category')
    results = {}
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    
    # Category-specific logic
    cat = (category or '').lower()
    
    # Always try Wikipedia first as fallback for expired API keys
    wiki_fallback = fetch_wikipedia_summary(query)
    
    # Company/entity info
    if not category or cat in ['company', 'private companies']:
        wiki = fetch_wikipedia_summary(query)
        if wiki and not (category and is_disambiguation(wiki)) and (not category or is_company_related(wiki)):
            results['company'] = wiki
        elif wiki_fallback and not is_disambiguation(wiki_fallback):
            # Use Wikipedia as fallback for company searches
            results['company'] = wiki_fallback
    # Movie info
    movie_name = query
    movie_cast = ''
    if not category or cat in ['movie', 'entertainment']:
        movie = fetch_omdb_movie(query)
        if movie and (movie.get('Plot') or movie.get('Poster') or movie.get('Actors')):
            results['movie'] = movie
            movie_name = movie.get('Title', query)
            movie_cast = movie.get('Actors', '')
        else:
            # Try TMDB and TVMaze fallbacks
            tmdb = fetch_tmdb_movie(query)
            if tmdb:
                results['movie_alt'] = tmdb
                movie_name = tmdb.get('Title', query)
            tvm = fetch_tvmaze_show(query)
            if tvm and 'movie_alt' not in results:
                results['movie_alt'] = tvm
            wiki = fetch_wikipedia_movie_variants(query)
            if wiki and not (category and is_disambiguation(wiki)) and is_entertainment_related(wiki):
                results['movie'] = wiki
                movie_name = wiki.get('title', query)
            elif wiki_fallback and not is_disambiguation(wiki_fallback):
                # Use Wikipedia as fallback for movie searches
                results['movie'] = wiki_fallback
                movie_name = wiki_fallback.get('title', query)
    # Sports info
    if not category or cat == 'sports':
        team = fetch_sports_team(query)
        if team:
            results['sports'] = team
        else:
            wiki = fetch_wikipedia_summary(query)
            if wiki and not (category and is_disambiguation(wiki)) and is_sports_related(wiki):
                results['sports'] = wiki
            elif wiki_fallback and not is_disambiguation(wiki_fallback):
                # Use Wikipedia as fallback for sports searches
                results['sports'] = wiki_fallback
        # Additional sports sources
        api_football = fetch_api_football_team(query)
        if api_football:
            results['sports_alt'] = {'api_football_team': api_football}
        fd_matches = fetch_football_data_matches(query)
        if fd_matches:
            results.setdefault('sports_alt', {})['football_data_matches'] = fd_matches
        cricket = fetch_cricapi_matches(query)
        if cricket:
            results.setdefault('sports_alt', {})['cricket_matches'] = cricket
    # Government Schemes
    if cat in ['government schemes', 'government', 'schemes', 'policy', 'policies']:
        wiki = fetch_wikipedia_summary(query)
        if wiki and not is_disambiguation(wiki) and is_gov_scheme_related(wiki):
            results['gov_scheme'] = wiki
        elif wiki_fallback and not is_disambiguation(wiki_fallback):
            # Use Wikipedia as fallback for government scheme searches
            results['gov_scheme'] = wiki_fallback
    # Finance & Markets
    if cat in ['finance & markets', 'finance', 'markets', 'stock', 'stocks', 'market']:
        # Wikipedia fallback (strict)
        wiki = fetch_wikipedia_summary(query)
        if wiki and not is_disambiguation(wiki) and is_finance_related(wiki):
            results['finance'] = wiki
        elif wiki_fallback and not is_disambiguation(wiki_fallback):
            # Use Wikipedia as fallback for finance searches
            results['finance'] = wiki_fallback
    # Always fetch and merge news from all sources, then dedupe
    news = []
    news += fetch_newsapi_news(query)
    news += fetch_newsdata_io(query)
    news += fetch_gnews_news(query)
    news += fetch_mediastack_news(query)
    news += fetch_currents_news(query)
    # Add Knowivate sources
    news += fetch_knowivate_latest()
    news += fetch_knowivate_local()
    # Add finance-specific news sources for finance category
    if cat in ['finance & markets', 'finance', 'markets', 'stock', 'stocks', 'market']:
        news += fetch_alpha_vantage_news(query)
        news += fetch_finnhub_news(query)
    # Dedupe all news
    news = dedupe_news(news)
    # Category-specific filtering
    if cat == 'entertainment':
        news = filter_news_by_category(news, ['film', 'movie', 'cinema', 'actor', 'actress', 'bollywood', 'hollywood', 'tollywood', 'kollywood'])
    elif cat == 'sports':
        news = filter_news_by_category(news, ['team', 'club', 'league', 'cricket', 'football', 'soccer', 'hockey', 'basketball', 'sports', 'athlete', 'olympic', 'tournament', 'match', 'stadium'])
    elif cat in ['company', 'private companies']:
        news = filter_news_by_category(news, ['company', 'corporation', 'limited', 'ltd', 'inc', 'pvt', 'enterprise', 'business', 'firm', 'organization', 'industry', 'multinational'])
    elif cat in ['government schemes', 'government', 'schemes', 'policy', 'policies']:
        news = filter_news_by_category(news, ['scheme', 'government', 'policy', 'initiative', 'programme', 'plan', 'ministry', 'welfare', 'yojana'])
    elif cat in ['finance & markets', 'finance', 'markets', 'stock', 'stocks', 'market']:
        news = filter_news_by_category(news, ['finance', 'stock', 'market', 'exchange', 'investment', 'bank', 'trading', 'equity', 'share', 'nasdaq', 'nyse', 'bse', 'nse', 'mutual fund', 'ipo', 'dividend', 'portfolio', 'securities', 'fintech'])
    if news:
        results['news'] = news
    # Images (Pexels)
    images = fetch_pexels_images(query)
    if images:
        results['images'] = images
    # Web results (SerpAPI)
    web = fetch_serpapi_results(query)
    if web:
        results['web'] = web
    # If no relevant results, try Wikipedia as final fallback
    if not results:
        if wiki_fallback and not is_disambiguation(wiki_fallback):
            # Use Wikipedia as final fallback for any search
            results['wikipedia'] = wiki_fallback
            return jsonify(results)
        else:
            return jsonify({'error': f'No results found in the {category or "selected"} category. Please try a different search term or check if your API keys are valid.'}), 200
    return jsonify(results)

@search_bp.route('/wikipedia', methods=['GET'])
def wikipedia_search():
    """Wikipedia-only search endpoint as fallback when APIs are down"""
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    
    # Try Wikipedia search
    wiki_result = fetch_wikipedia_summary(query)
    if wiki_result and not is_disambiguation(wiki_result):
        return jsonify({
            'wikipedia': wiki_result,
            'source': 'Wikipedia Fallback',
            'message': 'Using Wikipedia as fallback due to API issues'
        })
    
    # Try Wikipedia movie variants for entertainment searches
    wiki_movie = fetch_wikipedia_movie_variants(query)
    if wiki_movie and not is_disambiguation(wiki_movie):
        return jsonify({
            'wikipedia': wiki_movie,
            'source': 'Wikipedia Fallback',
            'message': 'Using Wikipedia as fallback due to API issues'
        })
    
    return jsonify({'error': 'No Wikipedia results found for this query'}), 404 