from app.database import db
from datetime import datetime
import json

class SearchAccuracy(db.Model):
    __tablename__ = 'search_accuracy'
    
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(500), nullable=False, index=True)
    search_category = db.Column(db.String(100), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Accuracy metrics
    accuracy_rating = db.Column(db.Float, nullable=False)  # 1-5 scale
    relevance_score = db.Column(db.Float, nullable=True)  # 0-1 scale
    completeness_score = db.Column(db.Float, nullable=True)  # 0-1 scale
    freshness_score = db.Column(db.Float, nullable=True)  # 0-1 scale
    
    # Search result details
    results_count = db.Column(db.Integer, default=0)
    clicked_results = db.Column(db.JSON, nullable=True)  # Array of clicked result IDs
    time_spent = db.Column(db.Integer, nullable=True)  # Time spent on search in seconds
    
    # Feedback
    user_feedback = db.Column(db.Text, nullable=True)
    was_helpful = db.Column(db.Boolean, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('search_accuracies', lazy=True))
    
    def __repr__(self):
        return f'<SearchAccuracy {self.search_query[:30]}... - {self.accuracy_rating}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'search_query': self.search_query,
            'search_category': self.search_category,
            'user_id': self.user_id,
            'accuracy_rating': self.accuracy_rating,
            'relevance_score': self.relevance_score,
            'completeness_score': self.completeness_score,
            'freshness_score': self.freshness_score,
            'results_count': self.results_count,
            'clicked_results': json.loads(self.clicked_results) if self.clicked_results else [],
            'time_spent': self.time_spent,
            'user_feedback': self.user_feedback,
            'was_helpful': self.was_helpful,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_accuracy_stats(days=30):
        """Get accuracy statistics for the last N days"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stats = db.session.query(
            db.func.avg(SearchAccuracy.accuracy_rating).label('avg_accuracy'),
            db.func.count(SearchAccuracy.id).label('total_searches'),
            db.func.avg(SearchAccuracy.relevance_score).label('avg_relevance'),
            db.func.avg(SearchAccuracy.completeness_score).label('avg_completeness'),
            db.func.avg(SearchAccuracy.freshness_score).label('avg_freshness')
        ).filter(SearchAccuracy.created_at >= cutoff_date).first()
        
        return {
            'avg_accuracy': round(stats.avg_accuracy or 0, 2),
            'total_searches': stats.total_searches or 0,
            'avg_relevance': round(stats.avg_relevance or 0, 2),
            'avg_completeness': round(stats.avg_completeness or 0, 2),
            'avg_freshness': round(stats.avg_freshness or 0, 2)
        }
    
    @staticmethod
    def get_accuracy_trends(days=30):
        """Get daily accuracy trends for graphing"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily averages
        daily_stats = db.session.query(
            db.func.date(SearchAccuracy.created_at).label('date'),
            db.func.avg(SearchAccuracy.accuracy_rating).label('avg_accuracy'),
            db.func.count(SearchAccuracy.id).label('search_count')
        ).filter(
            SearchAccuracy.created_at >= cutoff_date
        ).group_by(
            db.func.date(SearchAccuracy.created_at)
        ).order_by('date').all()
        
        return [
            {
                'date': stat.date.isoformat(),
                'avg_accuracy': round(stat.avg_accuracy or 0, 2),
                'search_count': stat.search_count or 0
            }
            for stat in daily_stats
        ]
