#!/usr/bin/env python3
"""
Simple News Fetcher - Directly fetch and store news
"""

import sys
import os
import requests
from pathlib import Path
from datetime import datetime

# Add server directory to Python path
server_path = Path(__file__).parent / 'server'
sys.path.insert(0, str(server_path))

def fetch_news_directly():
    """Fetch news directly from APIs and store in database"""
    print("🚀 Starting direct news fetch...")
    
    try:
        from app import create_app
        from app.models.news_article import NewsArticle
        from app.database import db
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            stored_count = 0
            
            # Fetch from NewsData.io
            print("📰 Fetching from NewsData.io...")
            newsdata_key = os.getenv('NEWSDATA_API_KEY')
            if newsdata_key:
                try:
                    url = f"https://newsdata.io/api/1/latest?apikey={newsdata_key}&country=in&language=en"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('results', [])
                        print(f"   Found {len(articles)} articles")
                        
                        for article in articles[:10]:  # Limit to 10
                            try:
                                # Check if article already exists
                                existing = db.session.query(NewsArticle).filter_by(
                                    url=article.get('link', '')
                                ).first()
                                
                                if not existing and article.get('link'):
                                    news_article = NewsArticle(
                                        title=article.get('title', 'No Title'),
                                        description=article.get('description', ''),
                                        url=article.get('link', ''),
                                        image_url=article.get('image_url', ''),
                                        source_name='NewsData.io',
                                        category='India',
                                        published_at=datetime.utcnow(),
                                        cache_expires_at=datetime.utcnow()
                                    )
                                    db.session.add(news_article)
                                    stored_count += 1
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error storing article: {e}")
                                continue
                                
                except Exception as e:
                    print(f"   ❌ Error fetching from NewsData.io: {e}")
            
            # Fetch from GNews
            print("📰 Fetching from GNews...")
            gnews_key = os.getenv('GNEWS_API_KEY')
            if gnews_key:
                try:
                    url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&apikey={gnews_key}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('articles', [])
                        print(f"   Found {len(articles)} articles")
                        
                        for article in articles[:10]:  # Limit to 10
                            try:
                                # Check if article already exists
                                existing = db.session.query(NewsArticle).filter_by(
                                    url=article.get('url', '')
                                ).first()
                                
                                if not existing and article.get('url'):
                                    news_article = NewsArticle(
                                        title=article.get('title', 'No Title'),
                                        description=article.get('description', ''),
                                        url=article.get('url', ''),
                                        image_url=article.get('image', ''),
                                        source_name='GNews',
                                        category='India',
                                        published_at=datetime.utcnow(),
                                        cache_expires_at=datetime.utcnow()
                                    )
                                    db.session.add(news_article)
                                    stored_count += 1
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error storing article: {e}")
                                continue
                                
                except Exception as e:
                    print(f"   ❌ Error fetching from GNews: {e}")
            
            # Commit to database
            db.session.commit()
            
            print(f"✅ Successfully stored {stored_count} new articles")
            
            # Check total articles in database
            total_articles = db.session.query(NewsArticle).count()
            print(f"📊 Total articles in database: {total_articles}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fetch_news_directly()
    if success:
        print("\n🎉 News fetch completed successfully!")
        print("🌐 Refresh your browser to see the news articles!")
    else:
        print("\n❌ News fetch failed. Check the errors above.")
