"""
Enhanced deduplication service with canonical key logic
"""
import re
from typing import List, Dict, Any, Optional
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class EnhancedDeduplicationService:
    """
    Enhanced deduplication with canonical keys and source ranking
    """
    
    # Source ranking (higher = more authoritative)
    SOURCE_RANKING = {
        'newsapi': 10,
        'newsdata': 9,
        'gnews': 8,
        'mediastack': 7,
        'currents': 6,
        'datagovin': 9,
        'omdb': 10,
        'tmdb': 9,
        'thesportsdb': 8,
        'api-football': 9,
        'football-data': 8,
        'wikipedia': 3,  # Lower rank - fallback only
    }
    
    def __init__(self):
        self.default_source_rank = 5
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        if not title:
            return ""
        
        # Convert to lowercase
        title = title.lower()
        
        # Remove special characters but keep spaces
        title = re.sub(r'[^a-z0-9\s]', '', title)
        
        # Collapse whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def generate_dedupe_key(self, item: Dict[str, Any]) -> str:
        """
        Generate canonical dedupe key for an item
        
        Format: normalized_title||entity_type||year||canonical_id
        """
        title = self.normalize_title(item.get('title', ''))
        entity_type = item.get('type', item.get('entity_type', 'unknown'))
        year = str(item.get('year', '')) if item.get('year') else ''
        canonical_id = str(item.get('id', item.get('imdb_id', item.get('tmdb_id', '')))) if item.get('id') or item.get('imdb_id') or item.get('tmdb_id') else ''
        
        # Build key
        key_parts = [title, entity_type, year, canonical_id]
        return '||'.join(key_parts)
    
    def dedupe_and_merge(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate items and merge metadata from multiple sources
        
        Args:
            items: List of items with at least: title, type, source, and optionally year, id, summary, image
        
        Returns:
            Deduplicated list with merged sources
        """
        by_key = OrderedDict()
        
        for item in items:
            dedupe_key = self.generate_dedupe_key(item)
            source = item.get('source', 'unknown')
            source_rank = self.SOURCE_RANKING.get(source.lower(), self.default_source_rank)
            
            if dedupe_key not in by_key:
                # New item - create copy with sources list
                merged_item = {
                    'title': item.get('title', ''),
                    'type': item.get('type', item.get('entity_type', 'unknown')),
                    'year': item.get('year'),
                    'id': item.get('id', item.get('imdb_id', item.get('tmdb_id'))),
                    'summary': item.get('summary', item.get('description', item.get('plot', ''))),
                    'image': item.get('image', item.get('image_url', item.get('poster', item.get('urlToImage', '')))),
                    'url': item.get('url', item.get('link', '')),
                    'source': source,  # Primary source (highest rank)
                    'sources': [source],  # All sources
                    'source_rank': source_rank,
                    'category_tags': item.get('category_tags', []),
                    'published_at': item.get('published_at', item.get('publishedAt')),
                    # Preserve other fields
                    **{k: v for k, v in item.items() if k not in [
                        'title', 'type', 'entity_type', 'year', 'id', 'imdb_id', 'tmdb_id',
                        'summary', 'description', 'plot', 'image', 'image_url', 'poster', 'urlToImage',
                        'url', 'link', 'source', 'category_tags', 'published_at', 'publishedAt'
                    ]}
                }
                by_key[dedupe_key] = merged_item
            else:
                # Existing item - merge sources and enrich metadata
                existing = by_key[dedupe_key]
                existing_source_rank = existing.get('source_rank', self.default_source_rank)
                
                # Add source to sources list if not already present
                if source not in existing['sources']:
                    existing['sources'].append(source)
                
                # If new source has higher rank, update primary source and metadata
                if source_rank > existing_source_rank:
                    existing['source'] = source
                    existing['source_rank'] = source_rank
                
                # Enrich metadata from higher-ranked sources
                # Keep better image if available
                if not existing.get('image') and item.get('image') or item.get('image_url') or item.get('poster'):
                    existing['image'] = item.get('image') or item.get('image_url') or item.get('poster')
                
                # Keep longer/more detailed summary
                new_summary = item.get('summary') or item.get('description') or item.get('plot', '')
                if len(new_summary) > len(existing.get('summary', '')):
                    existing['summary'] = new_summary
                
                # Merge category tags
                new_tags = item.get('category_tags', [])
                existing_tags = existing.get('category_tags', [])
                merged_tags = list(set(existing_tags + new_tags))
                existing['category_tags'] = merged_tags
        
        return list(by_key.values())
    
    def filter_by_category(self, items: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """
        Filter items by category using category_tags
        
        Args:
            items: List of items
            category: Category to filter by (case-insensitive)
        
        Returns:
            Filtered list
        """
        if not category:
            return items
        
        category_lower = category.lower()
        filtered = []
        
        for item in items:
            tags = item.get('category_tags', [])
            # Check if category matches any tag
            if any(category_lower in str(tag).lower() for tag in tags):
                filtered.append(item)
            # Also check type field
            elif category_lower in str(item.get('type', '')).lower():
                filtered.append(item)
        
        return filtered

# Global instance
enhanced_dedupe = EnhancedDeduplicationService()

