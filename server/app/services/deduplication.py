import hashlib
import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple
import json
from app.models.news_article import NewsArticle
from app.database import db

class NewsDeduplicationService:
    """Smart service for deduplicating news articles using multiple strategies"""
    
    def __init__(self):
        self.similarity_threshold = 0.85  # Articles with 85%+ similarity are considered duplicates
        self.title_similarity_threshold = 0.80
        self.content_similarity_threshold = 0.75
    
    def find_duplicates(self, new_articles: List[Dict], existing_articles: List[NewsArticle] = None) -> List[Tuple[Dict, NewsArticle]]:
        """
        Find duplicate articles between new articles and existing ones
        
        Returns:
            List of tuples: (new_article, existing_duplicate)
        """
        if existing_articles is None:
            existing_articles = NewsArticle.query.filter_by(is_duplicate=False).all()
        
        duplicates = []
        
        for new_article in new_articles:
            for existing in existing_articles:
                if self._is_duplicate(new_article, existing):
                    duplicates.append((new_article, existing))
                    break
        
        return duplicates
    
    def _is_duplicate(self, new_article: Dict, existing: NewsArticle) -> bool:
        """Check if two articles are duplicates using multiple strategies"""
        
        # Strategy 1: Exact URL match
        if new_article.get('url') == existing.url:
            return True
        
        # Strategy 2: Content hash comparison
        new_hash = self._generate_content_hash(new_article)
        if new_hash == existing.content_hash:
            return True
        
        # Strategy 3: Title similarity (most reliable for news)
        title_similarity = self._calculate_title_similarity(
            new_article.get('title', ''), 
            existing.title
        )
        if title_similarity > self.title_similarity_threshold:
            return True
        
        # Strategy 4: Content similarity (if we have content)
        if new_article.get('description') and existing.description:
            content_similarity = self._calculate_content_similarity(
                new_article.get('description', ''),
                existing.description
            )
            if content_similarity > self.content_similarity_threshold:
                return True
        
        # Strategy 5: Source + published time proximity
        if self._is_same_source_same_time(new_article, existing):
            return True
        
        return False
    
    def _generate_content_hash(self, article: Dict) -> str:
        """Generate a hash for content similarity checking"""
        content_str = f"{article.get('title', '')}{article.get('description', '')}{article.get('source_name', '')}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        if not title1 or not title2:
            return 0.0
        
        # Clean titles for better comparison
        clean_title1 = self._clean_text(title1)
        clean_title2 = self._clean_text(title2)
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, clean_title1, clean_title2).ratio()
        
        # Boost similarity if they share key words
        word_similarity = self._calculate_word_overlap(clean_title1, clean_title2)
        
        # Combine both metrics
        final_similarity = (similarity * 0.7) + (word_similarity * 0.3)
        
        return final_similarity
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content pieces"""
        if not content1 or not content2:
            return 0.0
        
        # Clean content
        clean_content1 = self._clean_text(content1)
        clean_content2 = self._clean_text(content2)
        
        # Use SequenceMatcher
        similarity = SequenceMatcher(None, clean_content1, clean_content2).ratio()
        
        # Calculate word overlap
        word_similarity = self._calculate_word_overlap(clean_content1, clean_content2)
        
        # Combine metrics
        final_similarity = (similarity * 0.6) + (word_similarity * 0.4)
        
        return final_similarity
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better comparison"""
        if not text:
            return ""
        
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip().lower()
        
        return cleaned
    
    def _is_same_source_same_time(self, new_article: Dict, existing: NewsArticle) -> bool:
        """Check if articles are from same source and published around same time"""
        if not new_article.get('source_name') or not existing.source_name:
            return False
        
        if new_article.get('source_name') != existing.source_name:
            return False
        
        # Check if published within 1 hour of each other
        if new_article.get('publishedAt') and existing.published_at:
            try:
                from datetime import datetime
                new_time = self._parse_date(new_article.get('publishedAt'))
                if new_time and existing.published_at:
                    time_diff = abs((new_time - existing.published_at).total_seconds())
                    return time_diff < 3600  # 1 hour
            except:
                pass
        
        return False
    
    def _parse_date(self, date_str: str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        from datetime import datetime
        
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
    
    def mark_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Mark articles as duplicates and return only unique ones
        
        Returns:
            List of unique articles
        """
        unique_articles = []
        seen_hashes = set()
        
        for article in articles:
            content_hash = self._generate_content_hash(article)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_similar_articles(self, article: NewsArticle, limit: int = 5) -> List[NewsArticle]:
        """Find articles similar to the given article"""
        similar_articles = []
        
        # Get articles from same category and time period
        query = NewsArticle.query.filter(
            NewsArticle.id != article.id,
            NewsArticle.is_duplicate == False,
            NewsArticle.category == article.category
        )
        
        if article.published_at:
            from datetime import datetime, timedelta
            week_ago = article.published_at - timedelta(days=7)
            query = query.filter(NewsArticle.published_at >= week_ago)
        
        candidates = query.limit(20).all()
        
        # Calculate similarity scores
        scored_candidates = []
        for candidate in candidates:
            title_sim = self._calculate_title_similarity(article.title, candidate.title)
            content_sim = self._calculate_content_similarity(
                article.description or '', 
                candidate.description or ''
            )
            
            # Weighted score
            score = (title_sim * 0.6) + (content_sim * 0.4)
            scored_candidates.append((candidate, score))
        
        # Sort by score and return top results
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [article for article, score in scored_candidates[:limit] if score > 0.3]
