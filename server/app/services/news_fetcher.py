import os
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.news_article import NewsArticle, NewsSource
from app.services.deduplication import NewsDeduplicationService
from app.database import db
from app.celery_app import celery
import logging

logger = logging.getLogger(__name__)

class NewsFetcherService:
    """Service for fetching news from multiple APIs with rate limiting and caching"""
    
    def __init__(self):
        self.deduplication_service = NewsDeduplicationService()
        self.api_keys = {
            'newsdata': os.getenv('NEWSDATA_API_KEY'),
            'newsapi': os.getenv('NEWSAPI_API_KEY'),
            'datagovin': os.getenv('DATAGOVIN_API_KEY'),
            'gnews': os.getenv('GNEWS_API_KEY'),
            'mediastack': os.getenv('MEDIASTACK_API_KEY')
        }
        
        # Initialize news sources
        self._init_news_sources()
    
    def _init_news_sources(self):
        """Initialize news sources in database if they don't exist"""
        sources = [
            {
                'name': 'NewsData.io',
                'api_key': self.api_keys['newsdata'],
                'base_url': 'https://newsdata.io/api/1/latest',
                'rate_limit_per_hour': 100,
                'rate_limit_per_day': 1000,
                'bias_score': 0.0,
                'reliability_score': 0.8
            },
            {
                'name': 'NewsAPI.org',
                'api_key': self.api_keys['newsapi'],
                'base_url': 'https://newsapi.org/v2/top-headlines',
                'rate_limit_per_hour': 100,
                'rate_limit_per_day': 1000,
                'bias_score': 0.0,
                'reliability_score': 0.8
            },
            {
                'name': 'DataGovIn',
                'api_key': self.api_keys['datagovin'],
                'base_url': 'https://api.data.gov.in/resource',
                'rate_limit_per_hour': 1000,
                'rate_limit_per_day': 10000,
                'bias_score': 0.0,
                'reliability_score': 0.9
            },
            {
                'name': 'GNews',
                'api_key': self.api_keys['gnews'],
                'base_url': 'https://gnews.io/api/v4',
                'rate_limit_per_hour': 100,
                'rate_limit_per_day': 1000,
                'bias_score': 0.0,
                'reliability_score': 0.7
            },
            {
                'name': 'MediaStack',
                'api_key': self.api_keys['mediastack'],
                'base_url': 'http://api.mediastack.com/v1',
                'rate_limit_per_hour': 500,
                'rate_limit_per_day': 5000,
                'bias_score': 0.0,
                'reliability_score': 0.7
            }
        ]
        
        for source_data in sources:
            if source_data['api_key']:
                existing = NewsSource.query.filter_by(name=source_data['name']).first()
                if not existing:
                    source = NewsSource(**source_data)
                    db.session.add(source)
        
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error initializing news sources: {e}")
            db.session.rollback()
    
    def fetch_all_categories(self) -> Dict[str, int]:
        """Fetch news for all categories and return counts"""
        categories = [
            'Government Schemes', 'Private Companies', 'Education', 
            'Healthcare', 'Sports', 'Entertainment', 'India'
        ]
        
        results = {}
        for category in categories:
            try:
                count = self.fetch_category_news(category)
                results[category] = count
                logger.info(f"Fetched {count} articles for category: {category}")
                
                # Stagger requests to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error fetching category {category}: {e}")
                results[category] = 0
        
        return results
    
    def fetch_category_news(self, category: str) -> int:
        """Fetch news for a specific category"""
        articles = []
        
        # Try each API source
        sources = [
            ('newsdata', self._fetch_newsdata),
            ('newsapi', self._fetch_newsapi),
            ('gnews', self._fetch_gnews),
            ('mediastack', self._fetch_mediastack)
        ]
        
        for source_name, fetch_func in sources:
            try:
                if self._can_fetch_from_source(source_name):
                    source_articles = fetch_func(category)
                    if source_articles:
                        articles.extend(source_articles)
                        self._record_api_request(source_name)
                        logger.info(f"Fetched {len(source_articles)} articles from {source_name}")
                else:
                    logger.warning(f"Rate limit reached for {source_name}")
                    
            except Exception as e:
                logger.error(f"Error fetching from {source_name}: {e}")
        
        # Special handling for government schemes
        if category.lower() in ['government schemes', 'government', 'schemes']:
            try:
                if self._can_fetch_from_source('datagovin'):
                    gov_articles = self._fetch_datagovin()
                    if gov_articles:
                        articles.extend(gov_articles)
                        self._record_api_request('datagovin')
                        logger.info(f"Fetched {len(gov_articles)} government articles")
            except Exception as e:
                logger.error(f"Error fetching government data: {e}")
        
        # Deduplicate and store articles
        if articles:
            unique_articles = self.deduplication_service.mark_duplicates(articles)
            stored_count = self._store_articles(unique_articles, category)
            return stored_count
        
        return 0
    
    def _can_fetch_from_source(self, source_name: str) -> bool:
        """Check if we can make a request to the source"""
        source = NewsSource.query.filter_by(name=source_name).first()
        if not source:
            return False
        
        return source.can_make_request()
    
    def _record_api_request(self, source_name: str):
        """Record that an API request was made"""
        source = NewsSource.query.filter_by(name=source_name).first()
        if source:
            source.record_request()
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Error recording API request: {e}")
                db.session.rollback()
    
    def _fetch_newsdata(self, category: str) -> List[Dict]:
        """Fetch from NewsData.io"""
        if not self.api_keys['newsdata']:
            return []
        
        url = 'https://newsdata.io/api/1/latest'
        params = {
            'apikey': self.api_keys['newsdata'],
            'country': 'in',
            'language': 'en',
            'size': 20
        }
        
        # Map categories
        category_mapping = {
            'Government Schemes': 'politics',
            'Private Companies': 'business',
            'Education': 'education',
            'Healthcare': 'health',
            'Sports': 'sports',
            'Entertainment': 'entertainment',
            'India': 'top'
        }
        
        mapped_category = category_mapping.get(category, 'top')
        if mapped_category != 'top':
            params['category'] = mapped_category
        else:
            params['q'] = category
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('results', [])
                return self._normalize_newsdata_articles(articles, category)
        except Exception as e:
            logger.error(f"NewsData.io error: {e}")
        
        return []
    
    def _fetch_newsapi(self, category: str) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        if not self.api_keys['newsapi']:
            return []
        
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'apiKey': self.api_keys['newsapi'],
            'country': 'in',
            'language': 'en',
            'pageSize': 20
        }
        
        # Map categories
        category_mapping = {
            'Government Schemes': 'general',
            'Private Companies': 'business',
            'Education': 'general',
            'Healthcare': 'health',
            'Sports': 'sports',
            'Entertainment': 'entertainment',
            'India': 'general'
        }
        
        mapped_category = category_mapping.get(category, 'general')
        if mapped_category != 'general':
            params['category'] = mapped_category
        else:
            params['q'] = category
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                return self._normalize_newsapi_articles(articles, category)
        except Exception as e:
            logger.error(f"NewsAPI.org error: {e}")
        
        return []
    
    def _fetch_gnews(self, category: str) -> List[Dict]:
        """Fetch from GNews"""
        if not self.api_keys['gnews']:
            return []
        
        url = 'https://gnews.io/api/v4/top-headlines'
        params = {
            'token': self.api_keys['gnews'],
            'country': 'in',
            'lang': 'en',
            'max': 20
        }
        
        # GNews doesn't have category filtering, so we use search
        if category != 'India':
            params['q'] = category
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                return self._normalize_gnews_articles(articles, category)
        except Exception as e:
            logger.error(f"GNews error: {e}")
        
        return []
    
    def _fetch_mediastack(self, category: str) -> List[Dict]:
        """Fetch from MediaStack"""
        if not self.api_keys['mediastack']:
            return []
        
        url = 'http://api.mediastack.com/v1/news'
        params = {
            'access_key': self.api_keys['mediastack'],
            'countries': 'in',
            'languages': 'en',
            'limit': 20
        }
        
        if category != 'India':
            params['keywords'] = category
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                return self._normalize_mediastack_articles(articles, category)
        except Exception as e:
            logger.error(f"MediaStack error: {e}")
        
        return []
    
    def _fetch_datagovin(self) -> List[Dict]:
        """Fetch government data from DataGovIn"""
        if not self.api_keys['datagovin']:
            return []
        
        url = 'https://api.data.gov.in/resource/press-releases-ministry-information-and-broadcasting'
        params = {
            'api-key': self.api_keys['datagovin'],
            'format': 'json',
            'limit': 20
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                return self._normalize_datagovin_articles(records)
        except Exception as e:
            logger.error(f"DataGovIn error: {e}")
        
        return []
    
    def _normalize_newsdata_articles(self, articles: List[Dict], category: str) -> List[Dict]:
        """Normalize NewsData.io articles to standard format"""
        normalized = []
        for article in articles:
            normalized.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('link', ''),
                'image_url': article.get('image_url', ''),
                'source_name': article.get('source_id', 'NewsData.io'),
                'publishedAt': article.get('pubDate', ''),
                'category': category
            })
        return normalized
    
    def _normalize_newsapi_articles(self, articles: List[Dict], category: str) -> List[Dict]:
        """Normalize NewsAPI.org articles to standard format"""
        normalized = []
        for article in articles:
            normalized.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'source_name': article.get('source', {}).get('name', 'NewsAPI.org'),
                'publishedAt': article.get('publishedAt', ''),
                'category': category
            })
        return normalized
    
    def _normalize_gnews_articles(self, articles: List[Dict], category: str) -> List[Dict]:
        """Normalize GNews articles to standard format"""
        normalized = []
        for article in articles:
            normalized.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'image_url': article.get('image', ''),
                'source_name': article.get('source', {}).get('name', 'GNews'),
                'publishedAt': article.get('publishedAt', ''),
                'category': category
            })
        return normalized
    
    def _normalize_mediastack_articles(self, articles: List[Dict], category: str) -> List[Dict]:
        """Normalize MediaStack articles to standard format"""
        normalized = []
        for article in articles:
            normalized.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'image_url': article.get('image', ''),
                'source_name': article.get('source', 'MediaStack'),
                'publishedAt': article.get('published_at', ''),
                'category': category
            })
        return normalized
    
    def _normalize_datagovin_articles(self, records: List[Dict]) -> List[Dict]:
        """Normalize DataGovIn articles to standard format"""
        normalized = []
        for record in records:
            normalized.append({
                'title': record.get('title', ''),
                'description': record.get('description', ''),
                'url': record.get('url', ''),
                'image_url': '',
                'source_name': 'DataGovIn',
                'publishedAt': record.get('published_date', ''),
                'category': 'Government Schemes'
            })
        return normalized
    
    def _store_articles(self, articles: List[Dict], category: str) -> int:
        """Store articles in database"""
        stored_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = NewsArticle.query.filter_by(url=article_data['url']).first()
                
                if existing:
                    # Update existing article
                    existing.update_from_api(article_data, article_data['source_name'])
                    existing.category = category
                    stored_count += 1
                else:
                    # Create new article
                    new_article = NewsArticle(
                        title=article_data['title'],
                        description=article_data['description'],
                        url=article_data['url'],
                        image_url=article_data['image_url'],
                        source_name=article_data['source_name'],
                        published_at=NewsArticle._parse_date(article_data['publishedAt']),
                        category=category,
                        cache_expires_at=datetime.utcnow() + timedelta(hours=24)
                    )
                    db.session.add(new_article)
                    stored_count += 1
                    
            except Exception as e:
                logger.error(f"Error storing article {article_data.get('title', 'Unknown')}: {e}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"Successfully stored {stored_count} articles for category: {category}")
        except Exception as e:
            logger.error(f"Error committing articles to database: {e}")
            db.session.rollback()
            stored_count = 0
        
        return stored_count

# Celery tasks
@celery.task
def fetch_all_news_task():
    """Celery task to fetch all news categories"""
    try:
        fetcher = NewsFetcherService()
        results = fetcher.fetch_all_categories()
        logger.info(f"Background news fetch completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Background news fetch failed: {e}")
        return {}

@celery.task
def fetch_category_news_task(category: str):
    """Celery task to fetch news for a specific category"""
    try:
        fetcher = NewsFetcherService()
        count = fetcher.fetch_category_news(category)
        logger.info(f"Background fetch for {category} completed: {count} articles")
        return count
    except Exception as e:
        logger.error(f"Background fetch for {category} failed: {e}")
        return 0
