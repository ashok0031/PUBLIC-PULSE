from app.database import db
from datetime import datetime, timedelta
import hashlib
import json

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core article data
    title = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    url = db.Column(db.String(1000), unique=True, nullable=False, index=True)
    image_url = db.Column(db.String(1000))
    
    # Source information
    source_name = db.Column(db.String(200), nullable=False, index=True)
    source_id = db.Column(db.String(100))
    source_bias_score = db.Column(db.Float, default=0.0)  # -1 to 1 (left to right)
    source_reliability = db.Column(db.Float, default=0.5)  # 0 to 1
    
    # Metadata
    published_at = db.Column(db.DateTime, index=True)
    category = db.Column(db.String(100), index=True)
    language = db.Column(db.String(10), default='en')
    country = db.Column(db.String(10), default='in')
    
    # Processing flags
    is_processed = db.Column(db.Boolean, default=False)
    is_duplicate = db.Column(db.Boolean, default=False)
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey('news_articles.id'))
    
    # Caching & freshness
    last_fetched = db.Column(db.DateTime, default=datetime.utcnow)
    cache_expires_at = db.Column(db.DateTime)
    
    # AI processing results
    ai_summary = db.Column(db.Text)
    ai_sentiment = db.Column(db.Float)  # -1 to 1
    ai_keywords = db.Column(db.Text)  # JSON array of keywords
    ai_bias_analysis = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Commented out until Rating/Review models are properly set up
    # ratings = db.relationship('Rating', backref='article', lazy='dynamic')
    # reviews = db.relationship('Review', backref='article', lazy='dynamic')
    
    def __repr__(self):
        return f'<NewsArticle {self.title[:50]}...>'
    
    @property
    def is_expired(self):
        """Check if the cached article has expired"""
        if not self.cache_expires_at:
            return False
        return datetime.utcnow() > self.cache_expires_at
    
    @property
    def content_hash(self):
        """Generate a hash for content similarity checking"""
        content_str = f"{self.title}{self.description}{self.source_name}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'source_name': self.source_name,
            'source_bias_score': self.source_bias_score,
            'source_reliability': self.source_reliability,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category,
            'language': self.language,
            'country': self.country,
            'ai_summary': self.ai_summary,
            'ai_sentiment': self.ai_sentiment,
            'ai_keywords': json.loads(self.ai_keywords) if self.ai_keywords else [],
            'ai_bias_analysis': self.ai_bias_analysis,
            'last_updated': self.updated_at.isoformat(),
            'is_expired': self.is_expired
        }
    
    def update_from_api(self, api_data, source_name):
        """Update article data from API response"""
        self.title = api_data.get('title', self.title)
        self.description = api_data.get('description', self.description)
        self.content = api_data.get('content', self.content)
        self.url = api_data.get('url', self.url)
        self.image_url = api_data.get('image_url') or api_data.get('urlToImage', self.image_url)
        self.source_name = source_name
        self.published_at = self._parse_date(api_data.get('publishedAt'))
        self.last_fetched = datetime.utcnow()
        self.cache_expires_at = datetime.utcnow() + timedelta(hours=24)  # Cache for 24 hours
    
    def _parse_date(self, date_str):
        """Parse various date formats from APIs"""
        if not date_str:
            return None
        
        # Common date formats from news APIs
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

class NewsSource(db.Model):
    __tablename__ = 'news_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    api_key = db.Column(db.String(100))
    base_url = db.Column(db.String(500))
    
    # Rate limiting info
    rate_limit_per_hour = db.Column(db.Integer, default=100)
    rate_limit_per_day = db.Column(db.Integer, default=1000)
    current_hourly_usage = db.Column(db.Integer, default=0)
    current_daily_usage = db.Column(db.Integer, default=0)
    last_reset_hour = db.Column(db.DateTime, default=datetime.utcnow)
    last_reset_day = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Source metadata
    bias_score = db.Column(db.Float, default=0.0)  # -1 to 1
    reliability_score = db.Column(db.Float, default=0.5)  # 0 to 1
    categories = db.Column(db.Text)  # JSON array
    countries = db.Column(db.Text)  # JSON array
    languages = db.Column(db.Text)  # JSON array
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewsSource {self.name}>'
    
    def can_make_request(self):
        """Check if we can make a request without hitting rate limits"""
        now = datetime.utcnow()
        
        # Reset hourly counter if needed
        if (now - self.last_reset_hour).total_seconds() > 3600:
            self.current_hourly_usage = 0
            self.last_reset_hour = now
        
        # Reset daily counter if needed
        if (now - self.last_reset_day).total_seconds() > 86400:
            self.current_daily_usage = 0
            self.last_reset_day = now
        
        return (self.current_hourly_usage < self.rate_limit_per_hour and 
                self.current_daily_usage < self.rate_limit_per_day)
    
    def record_request(self):
        """Record that a request was made"""
        self.current_hourly_usage += 1
        self.current_daily_usage += 1
        self.last_used = datetime.utcnow()
