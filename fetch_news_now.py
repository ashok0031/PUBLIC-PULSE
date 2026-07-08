#!/usr/bin/env python3
"""
Manual News Fetcher - Fetch news and store in database immediately
"""

import sys
import os
from pathlib import Path

# Add server directory to Python path
server_path = Path(__file__).parent / 'server'
sys.path.insert(0, str(server_path))

def fetch_and_store_news():
    """Fetch news from APIs and store in database"""
    print("🚀 Starting manual news fetch...")
    
    try:
        from app import create_app
        from app.services.news_fetcher import NewsFetcherService
        from app.database import db
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Initialize news fetcher
            fetcher = NewsFetcherService()
            
            print("📰 Fetching news from all sources...")
            
            # Fetch news from all categories
            categories = ['India', 'Government Schemes', 'Private Companies', 'Education', 'Healthcare', 'Sports', 'Entertainment']
            all_articles = []
            
            for category in categories:
                print(f"📰 Fetching {category} news...")
                articles = fetcher.fetch_category_news(category)
                print(f"   Found {articles} articles")
                all_articles.extend(articles)
            
            articles = all_articles
            
            print(f"✅ Fetched {len(articles)} articles")
            
            # Store articles in database
            stored_count = 0
            for article_data in articles:
                try:
                    # Check if article already exists
                    existing = db.session.query(fetcher.NewsArticle).filter_by(
                        url=article_data['url']
                    ).first()
                    
                    if not existing:
                        article = fetcher.NewsArticle(**article_data)
                        db.session.add(article)
                        stored_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Error storing article: {e}")
                    continue
            
            # Commit to database
            db.session.commit()
            
            print(f"✅ Successfully stored {stored_count} new articles")
            
            # Check total articles in database
            total_articles = db.session.query(fetcher.NewsArticle).count()
            print(f"📊 Total articles in database: {total_articles}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = fetch_and_store_news()
    if success:
        print("\n🎉 News fetch completed successfully!")
        print("🌐 Refresh your browser to see the news articles!")
    else:
        print("\n❌ News fetch failed. Check the errors above.")
