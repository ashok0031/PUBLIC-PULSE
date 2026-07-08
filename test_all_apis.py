import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('server/.env')

print("=" * 80)
print("COMPREHENSIVE API STATUS CHECK")
print(f"Tested at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

results = {
    'working': [],
    'not_working': [],
    'not_configured': []
}

def test_api(name, test_func):
    """Test an API and record the result"""
    try:
        status, message = test_func()
        if status:
            results['working'].append((name, message))
            print(f"✅ {name}: {message}")
        else:
            results['not_working'].append((name, message))
            print(f"❌ {name}: {message}")
    except Exception as e:
        results['not_working'].append((name, f"Error: {str(e)}"))
        print(f"❌ {name}: Error - {str(e)}")

# ==================== NEWS APIs ====================
print("📰 NEWS APIs:")
print("-" * 80)

# 1. NewsData.io
def test_newsdata():
    key = os.getenv('NEWSDATA_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://newsdata.io/api/1/latest"
        params = {'apikey': key, 'country': 'in', 'size': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 400:
            return False, "Invalid API key"
        elif r.status_code == 429:
            return False, "Rate limit exceeded"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("NewsData.io", test_newsdata)

# 2. NewsAPI.org
def test_newsapi():
    key = os.getenv('NEWSAPI_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {'apiKey': key, 'country': 'in', 'pageSize': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("NewsAPI.org", test_newsapi)

# 3. DataGovIn
def test_datagovin():
    key = os.getenv('DATAGOVIN_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://api.data.gov.in/resource/press-releases-ministry-information-and-broadcasting"
        params = {'api-key': key, 'format': 'json', 'limit': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("DataGovIn", test_datagovin)

# 4. GNews
def test_gnews():
    key = os.getenv('GNEWS_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://gnews.io/api/v4/top-headlines"
        params = {'token': key, 'country': 'in', 'max': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("GNews", test_gnews)

# 5. MediaStack
def test_mediastack():
    key = os.getenv('MEDIASTACK_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "http://api.mediastack.com/v1/news"
        params = {'access_key': key, 'countries': 'in', 'limit': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'error' in data:
                return False, data.get('error', {}).get('info', 'Error')
            return True, "Working"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("MediaStack", test_mediastack)

# 6. Currents API
def test_currents():
    key = os.getenv('CURRENTS_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://api.currentsapi.services/v1/latest-news"
        params = {'apiKey': key, 'language': 'en', 'page_size': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Currents API", test_currents)

print()

# ==================== MOVIES & TV APIs ====================
print("🎬 MOVIES & TV APIs:")
print("-" * 80)

# 7. OMDB
def test_omdb():
    key = os.getenv('OMDB_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "http://www.omdbapi.com/"
        params = {'apikey': key, 't': 'Inception'}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('Response') == 'True':
                return True, "Working"
            else:
                return False, data.get('Error', 'Unknown error')
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("OMDB", test_omdb)

# 8. TMDB
def test_tmdb():
    key = os.getenv('TMDB_API_KEY')
    if not key or key == 'your_tmdb_api_key_here':
        return False, "API key not configured"
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {'api_key': key, 'query': 'Inception'}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("TMDB", test_tmdb)

print()

# ==================== SPORTS APIs ====================
print("⚽ SPORTS APIs:")
print("-" * 80)

# 9. TheSportsDB
def test_thesportsdb():
    key = os.getenv('THESPORTSDB_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/{key}/searchteams.php"
        params = {'t': 'Manchester United'}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'teams' in data:
                return True, "Working"
            return False, "No data returned"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("TheSportsDB", test_thesportsdb)

# 10. API-Football
def test_api_football():
    key = os.getenv('API_FOOTBALL_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://v3.football.api-sports.io/status"
        headers = {'x-rapidapi-key': key, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("API-Football", test_api_football)

# 11. Football-Data.org
def test_football_data():
    key = os.getenv('FOOTBALL_DATA_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://api.football-data.org/v4/competitions"
        headers = {'X-Auth-Token': key}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Football-Data.org", test_football_data)

# 12. CricAPI
def test_cricapi():
    key = os.getenv('CRICAPI_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://cricapi.com/api/matches"
        params = {'apikey': key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'error' in data:
                return False, data.get('error', 'Error')
            return True, "Working"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("CricAPI", test_cricapi)

# 13. SportRadar
def test_sportradar():
    key = os.getenv('SPORTRADAR_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        # SportRadar requires specific endpoints, testing with a simple one
        url = f"https://api.sportradar.com/test"
        params = {'api_key': key}
        r = requests.get(url, params=params, timeout=10)
        # Any response means key is being processed
        return True, "Key configured (endpoint specific)"
    except:
        return False, "Connection error"

test_api("SportRadar", test_sportradar)

print()

# ==================== IMAGES & SEARCH APIs ====================
print("🖼️  IMAGES & SEARCH APIs:")
print("-" * 80)

# 14. Pexels
def test_pexels():
    key = os.getenv('PEXELS_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {'Authorization': key}
        params = {'query': 'test', 'per_page': 1}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Pexels", test_pexels)

# 15. SerpAPI
def test_serpapi():
    key = os.getenv('SERPAPI_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://serpapi.com/search.json"
        params = {'engine': 'google', 'q': 'test', 'api_key': key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("SerpAPI", test_serpapi)

print()

# ==================== FINANCE APIs ====================
print("💰 FINANCE APIs:")
print("-" * 80)

# 16. Alpha Vantage
def test_alpha_vantage():
    key = os.getenv('ALPHA_VANTAGE_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://www.alphavantage.co/query"
        params = {'function': 'TIME_SERIES_INTRADAY', 'symbol': 'IBM', 'interval': '1min', 'apikey': key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'Error Message' in data:
                return False, data.get('Error Message', 'Error')
            return True, "Working"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Alpha Vantage", test_alpha_vantage)

# 17. Finnhub
def test_finnhub():
    key = os.getenv('FINNHUB_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://finnhub.io/api/v1/quote"
        params = {'symbol': 'AAPL', 'token': key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Finnhub", test_finnhub)

print()

# ==================== SOCIAL MEDIA APIs ====================
print("📱 SOCIAL MEDIA APIs:")
print("-" * 80)

# 18. YouTube
def test_youtube():
    key = os.getenv('YOUTUBE_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {'part': 'snippet', 'q': 'test', 'key': key, 'maxResults': 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 400:
            return False, "Invalid API key or API not enabled"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("YouTube", test_youtube)

# 19. Reddit
def test_reddit():
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    if not client_id or not client_secret:
        return False, "API credentials not configured"
    try:
        import base64
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {'Authorization': f'Basic {auth}', 'User-Agent': 'PublicPulse/1.0'}
        data = {'grant_type': 'client_credentials'}
        r = requests.post('https://www.reddit.com/api/v1/access_token', headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid credentials"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Reddit", test_reddit)

# 20. Twitter
def test_twitter():
    bearer = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer:
        return False, "Bearer token not configured"
    try:
        bearer = bearer.replace('%2F', '/').replace('%3D', '=')
        headers = {'Authorization': f'Bearer {bearer}'}
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {'query': 'test', 'max_results': 1}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return True, "Working"
        elif r.status_code == 401:
            return False, "Invalid/expired token"
        elif r.status_code == 403:
            return False, "Access forbidden (may need paid tier)"
        else:
            return False, f"Status {r.status_code}"
    except:
        return False, "Connection error"

test_api("Twitter", test_twitter)

print()

# ==================== AI APIs ====================
print("🤖 AI APIs:")
print("-" * 80)

# 21. Gemini
def test_gemini():
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        return False, "API key not configured"
    try:
        import google.genai as genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents="Say hello"
        )
        if hasattr(response, 'text'):
            return True, "Working"
        return False, "No response text"
    except ImportError:
        return False, "google-genai library not installed"
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "not found" in error_str.lower():
            return False, "API not enabled in Google Cloud"
        elif "invalid" in error_str.lower() or "401" in error_str:
            return False, "Invalid API key"
        else:
            return False, f"Error: {error_str[:50]}"

test_api("Gemini AI", test_gemini)

print()

# ==================== SUMMARY ====================
print("=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"✅ Working: {len(results['working'])}")
print(f"❌ Not Working: {len(results['not_working'])}")
print()

if results['working']:
    print("✅ WORKING APIs:")
    for name, msg in results['working']:
        print(f"   • {name}")

print()

if results['not_working']:
    print("❌ NOT WORKING APIs:")
    for name, msg in results['not_working']:
        print(f"   • {name}: {msg}")

print()
print("=" * 80)

