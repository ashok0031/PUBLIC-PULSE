import schedule
import time
import logging
from datetime import datetime, timedelta
from app.celery_app import celery
from app.services.news_fetcher import fetch_all_news_task, fetch_category_news_task
from app.services.search_index import SearchIndexService
from app.database import db
from app.models.news_article import NewsArticle

logger = logging.getLogger(__name__)

class BackgroundTaskScheduler:
    """Scheduler for running background tasks automatically"""
    
    def __init__(self):
        self.search_service = SearchIndexService()
        self.is_running = False
        
    def start(self):
        """Start the background task scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting background task scheduler...")
        self.is_running = True
        
        # Schedule tasks
        self._schedule_tasks()
        
        # Run the scheduler
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.stop()
    
    def stop(self):
        """Stop the background task scheduler"""
        logger.info("Stopping background task scheduler...")
        self.is_running = False
        schedule.clear()
    
    def _schedule_tasks(self):
        """Schedule all background tasks"""
        
        # News fetching tasks
        # Fetch all categories every 6 hours
        schedule.every(6).hours.do(self._fetch_all_news)
        
        # Fetch specific categories at different times to spread load
        schedule.every().day.at("09:00").do(self._fetch_category, "Government Schemes")
        schedule.every().day.at("10:00").do(self._fetch_category, "Private Companies")
        schedule.every().day.at("11:00").do(self._fetch_category, "Education")
        schedule.every().day.at("12:00").do(self._fetch_category, "Healthcare")
        schedule.every().day.at("13:00").do(self._fetch_category, "Sports")
        schedule.every().day.at("14:00").do(self._fetch_category, "Entertainment")
        schedule.every().day.at("15:00").do(self._fetch_category, "India")
        
        # Search index maintenance
        # Reindex all articles daily at 2 AM
        schedule.every().day.at("02:00").do(self._reindex_search)
        
        # Clean up expired articles weekly
        schedule.every().monday.at("03:00").do(self._cleanup_expired_articles)
        
        # Database maintenance
        # Optimize database weekly
        schedule.every().sunday.at("04:00").do(self._optimize_database)
        
        logger.info("Background tasks scheduled successfully")
    
    def _fetch_all_news(self):
        """Fetch news for all categories"""
        try:
            logger.info("Starting scheduled news fetch for all categories")
            task = fetch_all_news_task.delay()
            logger.info(f"News fetch task started: {task.id}")
        except Exception as e:
            logger.error(f"Error starting news fetch task: {e}")
    
    def _fetch_category(self, category: str):
        """Fetch news for a specific category"""
        try:
            logger.info(f"Starting scheduled news fetch for category: {category}")
            task = fetch_category_news_task.delay(category)
            logger.info(f"Category fetch task started for {category}: {task.id}")
        except Exception as e:
            logger.error(f"Error starting category fetch task for {category}: {e}")
    
    def _reindex_search(self):
        """Reindex all articles in search index"""
        try:
            logger.info("Starting scheduled search reindex")
            count = self.search_service.reindex_all()
            logger.info(f"Search reindex completed: {count} articles indexed")
        except Exception as e:
            logger.error(f"Error during search reindex: {e}")
    
    def _cleanup_expired_articles(self):
        """Clean up expired articles from database"""
        try:
            logger.info("Starting scheduled cleanup of expired articles")
            
            # Mark expired articles as expired
            expired_count = db.session.query(NewsArticle).filter(
                NewsArticle.cache_expires_at < datetime.utcnow()
            ).update({'is_expired': True})
            
            # Remove from search index
            expired_articles = NewsArticle.query.filter_by(is_expired=True).all()
            for article in expired_articles:
                self.search_service.delete_article(article.id)
            
            db.session.commit()
            logger.info(f"Cleanup completed: {expired_count} articles marked as expired")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            db.session.rollback()
    
    def _optimize_database(self):
        """Perform database optimization tasks"""
        try:
            logger.info("Starting scheduled database optimization")
            
            # Get database statistics
            total_articles = NewsArticle.query.count()
            active_articles = NewsArticle.query.filter_by(is_duplicate=False, is_expired=False).count()
            duplicate_articles = NewsArticle.query.filter_by(is_duplicate=True).count()
            expired_articles = NewsArticle.query.filter_by(is_expired=True).count()
            
            logger.info(f"Database stats - Total: {total_articles}, Active: {active_articles}, "
                       f"Duplicates: {duplicate_articles}, Expired: {expired_articles}")
            
            # Clean up old duplicate and expired articles (older than 30 days)
            month_ago = datetime.utcnow() - timedelta(days=30)
            old_duplicates = NewsArticle.query.filter(
                NewsArticle.is_duplicate == True,
                NewsArticle.created_at < month_ago
            ).count()
            
            old_expired = NewsArticle.query.filter(
                NewsArticle.is_expired == True,
                NewsArticle.created_at < month_ago
            ).count()
            
            logger.info(f"Found {old_duplicates} old duplicates and {old_expired} old expired articles")
            
        except Exception as e:
            logger.error(f"Error during database optimization: {e}")
    
    def get_schedule_info(self) -> dict:
        """Get information about scheduled tasks"""
        try:
            jobs = schedule.get_jobs()
            job_info = []
            
            for job in jobs:
                job_info.append({
                    'function': job.job_func.__name__,
                    'next_run': str(job.next_run),
                    'interval': str(job.interval),
                    'unit': job.unit
                })
            
            return {
                'scheduler_running': self.is_running,
                'total_jobs': len(jobs),
                'jobs': job_info
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule info: {e}")
            return {'error': str(e)}
    
    def run_task_now(self, task_name: str, **kwargs):
        """Run a specific task immediately"""
        try:
            if task_name == 'fetch_all_news':
                self._fetch_all_news()
            elif task_name == 'reindex_search':
                self._reindex_search()
            elif task_name == 'cleanup_expired':
                self._cleanup_expired_articles()
            elif task_name == 'optimize_database':
                self._optimize_database()
            elif task_name == 'fetch_category':
                category = kwargs.get('category', 'India')
                self._fetch_category(category)
            else:
                logger.error(f"Unknown task: {task_name}")
                return False
            
            logger.info(f"Task {task_name} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running task {task_name}: {e}")
            return False

# Global scheduler instance
scheduler = BackgroundTaskScheduler()

def start_scheduler():
    """Start the background scheduler in a separate thread"""
    import threading
    
    def run_scheduler():
        scheduler.start()
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler started in separate thread")
    
    return scheduler_thread
