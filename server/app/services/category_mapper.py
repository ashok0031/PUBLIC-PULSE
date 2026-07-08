"""
Comprehensive category mapping service
Maps various API categories to internal taxonomy
"""
import re
from typing import List, Dict, Set

class CategoryMapper:
    """
    Maps categories from different APIs to internal taxonomy
    """
    
    # Internal taxonomy
    INTERNAL_CATEGORIES = {
        'news': ['news', 'article', 'headline', 'breaking'],
        'sports': ['sports', 'sport', 'athletic', 'game', 'match', 'tournament'],
        'entertainment': ['entertainment', 'movie', 'film', 'cinema', 'tv', 'television', 'show', 'actor', 'actress'],
        'business': ['business', 'company', 'corporate', 'enterprise', 'industry', 'market', 'economy'],
        'technology': ['technology', 'tech', 'software', 'app', 'digital', 'internet', 'ai', 'artificial intelligence'],
        'politics': ['politics', 'government', 'policy', 'scheme', 'yojana', 'ministry', 'minister', 'political'],
        'finance': ['finance', 'financial', 'stock', 'market', 'investment', 'bank', 'trading', 'economy'],
        'healthcare': ['health', 'healthcare', 'medical', 'hospital', 'doctor', 'medicine', 'treatment'],
        'education': ['education', 'school', 'university', 'college', 'student', 'academic', 'learning'],
        'science': ['science', 'scientific', 'research', 'study', 'discovery', 'innovation'],
    }
    
    # API-specific category mappings
    API_CATEGORY_MAPPINGS = {
        'newsapi': {
            'business': ['business'],
            'entertainment': ['entertainment'],
            'general': ['news', 'politics'],
            'health': ['healthcare'],
            'science': ['science'],
            'sports': ['sports'],
            'technology': ['technology'],
        },
        'newsdata': {
            'business': ['business'],
            'entertainment': ['entertainment'],
            'politics': ['politics'],
            'health': ['healthcare'],
            'science': ['science'],
            'sports': ['sports'],
            'technology': ['technology'],
            'education': ['education'],
        },
        'gnews': {
            'business': ['business'],
            'entertainment': ['entertainment'],
            'health': ['healthcare'],
            'science': ['science'],
            'sports': ['sports'],
            'technology': ['technology'],
        },
    }
    
    def __init__(self):
        # Build reverse lookup for fast category inference
        self._keyword_to_categories = {}
        for category, keywords in self.INTERNAL_CATEGORIES.items():
            for keyword in keywords:
                if keyword not in self._keyword_to_categories:
                    self._keyword_to_categories[keyword] = []
                self._keyword_to_categories[keyword].append(category)
    
    def map_api_category(self, api_name: str, api_category: str) -> List[str]:
        """
        Map API-specific category to internal categories
        
        Args:
            api_name: Name of the API (e.g., 'newsapi', 'newsdata')
            api_category: Category from the API
        
        Returns:
            List of internal category names
        """
        if api_name.lower() in self.API_CATEGORY_MAPPINGS:
            mapping = self.API_CATEGORY_MAPPINGS[api_name.lower()]
            if api_category.lower() in mapping:
                return mapping[api_category.lower()]
        
        # Fallback: try to infer from category name
        return self.infer_categories(api_category)
    
    def infer_categories(self, text: str) -> List[str]:
        """
        Infer categories from text content
        
        Args:
            text: Text to analyze (title, description, etc.)
        
        Returns:
            List of inferred category names
        """
        if not text:
            return []
        
        text_lower = text.lower()
        matched_categories = set()
        
        # Check keyword matches
        for keyword, categories in self._keyword_to_categories.items():
            if keyword in text_lower:
                matched_categories.update(categories)
        
        # Special patterns
        patterns = {
            r'\b(cricket|football|soccer|hockey|basketball|tennis|olympic)\b': ['sports'],
            r'\b(movie|film|cinema|bollywood|hollywood|actor|actress)\b': ['entertainment'],
            r'\b(company|corporate|business|enterprise|industry)\b': ['business'],
            r'\b(government|policy|scheme|yojana|ministry|minister)\b': ['politics'],
            r'\b(stock|market|finance|investment|bank|trading)\b': ['finance'],
            r'\b(tech|software|app|digital|ai|artificial intelligence)\b': ['technology'],
            r'\b(health|medical|hospital|doctor|medicine)\b': ['healthcare'],
            r'\b(education|school|university|college|student)\b': ['education'],
            r'\b(science|research|study|discovery)\b': ['science'],
        }
        
        for pattern, categories in patterns.items():
            if re.search(pattern, text_lower):
                matched_categories.update(categories)
        
        return list(matched_categories) if matched_categories else ['news']
    
    def normalize_category(self, category: str) -> str:
        """
        Normalize category name to internal format
        
        Args:
            category: Category name to normalize
        
        Returns:
            Normalized category name
        """
        if not category:
            return 'news'
        
        category_lower = category.lower().strip()
        
        # Direct mapping
        for internal_cat, keywords in self.INTERNAL_CATEGORIES.items():
            if category_lower in keywords or category_lower == internal_cat:
                return internal_cat
        
        # Partial matches
        for internal_cat, keywords in self.INTERNAL_CATEGORIES.items():
            if any(kw in category_lower for kw in keywords):
                return internal_cat
        
        return category_lower

# Global instance
category_mapper = CategoryMapper()

