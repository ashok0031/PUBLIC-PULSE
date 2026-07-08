"""
Source confidence scoring service
Calculates confidence scores based on multiple factors
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """
    Calculates confidence scores for search results
    """
    
    # Source reliability scores (0-1)
    SOURCE_RELIABILITY = {
        'newsapi': 0.9,
        'newsdata': 0.85,
        'gnews': 0.8,
        'mediastack': 0.75,
        'currents': 0.75,
        'datagovin': 0.95,  # Government sources are highly reliable
        'omdb': 0.9,
        'tmdb': 0.9,
        'thesportsdb': 0.8,
        'api-football': 0.85,
        'football-data': 0.85,
        'cricapi': 0.8,
        'wikipedia': 0.7,  # Lower because it's fallback
        'pexels': 0.8,
        'serpapi': 0.75,
    }
    
    def __init__(self):
        self.default_reliability = 0.5
    
    def calculate_confidence(self, item: Dict) -> float:
        """
        Calculate confidence score for an item
        
        Factors considered:
        1. Source reliability
        2. Number of sources reporting the same item
        3. Completeness of metadata
        4. Recency (for news)
        
        Args:
            item: Item dictionary with source, sources, etc.
        
        Returns:
            Confidence score (0-1)
        """
        score = 0.0
        
        # Factor 1: Source reliability (40% weight)
        sources = item.get('sources', [item.get('source', 'unknown')])
        if isinstance(sources, str):
            sources = [sources]
        
        source_scores = []
        for source in sources:
            reliability = self.SOURCE_RELIABILITY.get(source.lower(), self.default_reliability)
            source_scores.append(reliability)
        
        avg_source_reliability = sum(source_scores) / len(source_scores) if source_scores else self.default_reliability
        score += avg_source_reliability * 0.4
        
        # Factor 2: Multiple sources (30% weight)
        source_count = len(set(sources))
        if source_count > 1:
            # Multiple sources increase confidence
            multi_source_boost = min(0.3, (source_count - 1) * 0.1)
            score += multi_source_boost
        else:
            score += 0.0
        
        # Factor 3: Metadata completeness (20% weight)
        completeness = self._calculate_completeness(item)
        score += completeness * 0.2
        
        # Factor 4: Recency (10% weight) - only for news
        if item.get('type', '').lower() in ['news', 'article']:
            recency_score = self._calculate_recency_score(item)
            score += recency_score * 0.1
        else:
            score += 0.1  # Full score for non-news items
        
        # Cap at 1.0
        return min(1.0, score)
    
    def _calculate_completeness(self, item: Dict) -> float:
        """Calculate how complete the item's metadata is"""
        required_fields = ['title', 'summary', 'url']
        optional_fields = ['image', 'published_at', 'source', 'category_tags']
        
        score = 0.0
        
        # Required fields (60% of completeness)
        required_count = sum(1 for field in required_fields if item.get(field))
        score += (required_count / len(required_fields)) * 0.6
        
        # Optional fields (40% of completeness)
        optional_count = sum(1 for field in optional_fields if item.get(field))
        score += (optional_count / len(optional_fields)) * 0.4
        
        return score
    
    def _calculate_recency_score(self, item: Dict) -> float:
        """Calculate recency score for news items"""
        from datetime import datetime, timedelta
        
        published_at = item.get('published_at') or item.get('publishedAt')
        if not published_at:
            return 0.5  # Neutral if no date
        
        try:
            if isinstance(published_at, str):
                # Try to parse various date formats
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        published_at = datetime.strptime(published_at, fmt)
                        break
                    except:
                        continue
            
            if isinstance(published_at, datetime):
                now = datetime.utcnow()
                age = now - published_at
                
                # Score based on age
                if age < timedelta(hours=1):
                    return 1.0  # Very recent
                elif age < timedelta(hours=6):
                    return 0.9
                elif age < timedelta(days=1):
                    return 0.8
                elif age < timedelta(days=3):
                    return 0.6
                elif age < timedelta(days=7):
                    return 0.4
                else:
                    return 0.2  # Old news
        except:
            pass
        
        return 0.5  # Default if parsing fails
    
    def add_confidence_scores(self, items: List[Dict]) -> List[Dict]:
        """
        Add confidence scores to a list of items
        
        Args:
            items: List of item dictionaries
        
        Returns:
            List with confidence scores added
        """
        for item in items:
            item['confidence_score'] = self.calculate_confidence(item)
            item['confidence_level'] = self._get_confidence_level(item['confidence_score'])
        
        # Sort by confidence (highest first)
        items.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        return items
    
    def _get_confidence_level(self, score: float) -> str:
        """Get human-readable confidence level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'

# Global instance
confidence_scorer = ConfidenceScorer()

