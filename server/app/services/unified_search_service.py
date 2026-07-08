"""
Unified search service with proper fallback logic
"""
import os
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from app.services.enhanced_deduplication import enhanced_dedupe
from app.services.cache_service import cache_service
from app.services.category_mapper import category_mapper
from app.services.confidence_scorer import confidence_scorer

logger = logging.getLogger(__name__)

class UnifiedSearchService:
    """
    Unified search service that aggregates results from multiple APIs
    with proper fallback logic (Wikipedia only when no API results)
    """
    
    def __init__(self):
        self.max_workers = 5  # Parallel API calls
        self.timeout = 10
    
    def search(self, query: str, category: Optional[str] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Perform unified search across all APIs
        
        Args:
            query: Search query
            category: Optional category filter
            page: Page number (1-indexed)
            per_page: Results per page
        
        Returns:
            Dictionary with results by type, pagination info, and confidence scores
        """
        # Check cache first (cache key includes pagination for first page only)
        cache_key = f"search:{query}:{category or 'all'}"
        cached_result = None
        if page == 1:
            cached_result = cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: {query}")
                # Apply pagination to cached results
                return self._paginate_results(cached_result, page, per_page)
        
        results = {
            'query': query,
            'category': category,
            'news': [],
            'movies': [],
            'sports': [],
            'companies': [],
            'gov_schemes': [],
            'finance': [],
            'images': [],
            'web': [],
            'total_results': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0
        }
        
        # Fetch from all APIs in parallel
        all_items = []
        
        # News APIs
        news_items = self._fetch_news_apis(query, category)
        all_items.extend(news_items)
        
        # Movies/TV APIs
        if not category or category.lower() in ['movie', 'entertainment', 'tv']:
            movie_items = self._fetch_movie_apis(query)
            all_items.extend(movie_items)
        
        # Sports APIs
        if not category or category.lower() == 'sports':
            sports_items = self._fetch_sports_apis(query)
            all_items.extend(sports_items)
        
        # Company APIs
        if not category or category.lower() in ['company', 'private companies', 'companies']:
            company_items = self._fetch_company_apis(query)
            all_items.extend(company_items)
        
        # Government Schemes
        if not category or category.lower() in ['government schemes', 'government', 'schemes', 'policy', 'policies']:
            gov_items = self._fetch_gov_scheme_apis(query)
            all_items.extend(gov_items)
        
        # Images
        image_items = self._fetch_image_apis(query)
        all_items.extend(image_items)
        
        # Web search
        web_items = self._fetch_web_apis(query)
        all_items.extend(web_items)
        
        # Deduplicate and merge
        deduped_items = enhanced_dedupe.dedupe_and_merge(all_items)
        
        # Add confidence scores
        deduped_items = confidence_scorer.add_confidence_scores(deduped_items)
        
        # Apply category filter if specified
        if category:
            deduped_items = enhanced_dedupe.filter_by_category(deduped_items, category)
        
        # Organize by type
        for item in deduped_items:
            item_type = item.get('type', 'unknown').lower()
            if 'news' in item_type or 'article' in item_type:
                results['news'].append(item)
            elif 'movie' in item_type or 'film' in item_type or 'tv' in item_type:
                results['movies'].append(item)
            elif 'sport' in item_type or 'team' in item_type:
                results['sports'].append(item)
            elif 'company' in item_type or 'business' in item_type:
                results['companies'].append(item)
            elif 'gov' in item_type or 'scheme' in item_type or 'policy' in item_type:
                results['gov_schemes'] = results.get('gov_schemes', [])
                results['gov_schemes'].append(item)
            elif 'finance' in item_type or 'market' in item_type or 'stock' in item_type:
                results['finance'] = results.get('finance', [])
                results['finance'].append(item)
            elif 'image' in item_type:
                results['images'].append(item)
            else:
                # Check if web result might be a company based on title/description
                title_lower = (item.get('title', '') or '').lower()
                desc_lower = (item.get('description', '') or item.get('summary', '') or '').lower()
                if any(keyword in title_lower or keyword in desc_lower for keyword in ['company', 'corporation', 'ltd', 'inc', 'pvt', 'enterprise', 'business']):
                    results['companies'].append(item)
                else:
                    results['web'].append(item)
        
        # Use Wikipedia fallback if we have NO entity cards (even if news exists)
        has_entities = bool(results.get('movies') or results.get('sports') or results.get('companies') or 
                           results.get('gov_schemes') or results.get('finance'))
        
        # If no entity cards found, try Wikipedia fallback
        if not has_entities:
            logger.info(f"No entity cards found for '{query}' (has_entities={has_entities}), using Wikipedia fallback")
            wiki_results = self._fetch_wikipedia_fallback(query, category)
            logger.info(f"Wikipedia fallback returned {len(wiki_results)} items for '{query}'")
            if wiki_results:
                # Add Wikipedia results - try to categorize them
                for item in wiki_results:
                    # Try to infer the type from the query and content
                    query_lower = query.lower()
                    title_lower = (item.get('title', '') or '').lower()
                    summary_lower = (item.get('summary', '') or '').lower()
                    
                    # Check if it's a movie FIRST (most specific)
                    is_movie = (
                        any(kw in query_lower for kw in ['movie', 'film', 'cinema']) or
                        '(film)' in title_lower or '(movie)' in title_lower or
                        any(kw in summary_lower[:500] for kw in ['directed by', 'starring', 'cast', 'film', 'movie', 'cinema', 'director', 'produced by'])
                    )
                    
                    # Check if it's a sports team (check for team-specific keywords)
                    is_sports = (
                        any(kw in query_lower for kw in ['team', 'club', 'cricket', 'football', 'soccer', 'sports', 'indians', 'kings', 'royals', 'super', 'united', 'city']) or
                        any(kw in title_lower for kw in ['team', 'club', 'fc', 'united', 'city', 'cricket', 'football']) or
                        any(kw in summary_lower[:500] for kw in ['cricket team', 'football team', 'sports team', 'club', 'league', 'championship', 'match', 'player', 'stadium', 'ipl', 'premier league'])
                    )
                    
                    # Check if it's a company (check for business keywords)
                    is_company = (
                        any(kw in query_lower for kw in ['company', 'corp', 'ltd', 'inc', 'pvt', 'enterprise', 'business', 'group', 'corporation']) or
                        any(kw in title_lower for kw in ['company', 'corporation', 'ltd', 'inc', 'pvt', 'enterprise', 'group', 'industries']) or
                        any(kw in summary_lower[:500] for kw in ['company', 'corporation', 'business', 'founded', 'headquarters', 'revenue', 'ceo', 'manufacturing', 'automotive', 'technology company'])
                    )
                    
                    # Check if it's a government scheme
                    is_gov_scheme = (
                        any(kw in query_lower for kw in ['scheme', 'yojana', 'policy', 'programme', 'initiative']) or
                        any(kw in title_lower for kw in ['scheme', 'yojana', 'policy', 'programme', 'initiative']) or
                        any(kw in summary_lower[:500] for kw in ['government', 'ministry', 'scheme', 'policy', 'programme', 'initiative', 'launched'])
                    )
                    
                    # Categorize and add to appropriate array (order matters!)
                    if is_movie:
                        item['type'] = 'movie'
                        item['category_tags'] = ['movie', 'entertainment']
                        results['movies'].append(item)
                        logger.info(f"Categorized '{query}' as MOVIE")
                    elif is_sports:
                        item['type'] = 'sports'
                        item['category_tags'] = ['sports']
                        results['sports'].append(item)
                        logger.info(f"Categorized '{query}' as SPORTS")
                    elif is_gov_scheme:
                        item['type'] = 'gov_scheme'
                        item['category_tags'] = ['government', 'scheme']
                        results['gov_schemes'] = results.get('gov_schemes', [])
                        results['gov_schemes'].append(item)
                        logger.info(f"Categorized '{query}' as GOV_SCHEME")
                    elif is_company:
                        item['type'] = 'company'
                        item['category_tags'] = ['company', 'business']
                        results['companies'].append(item)
                        logger.info(f"Categorized '{query}' as COMPANY")
                    else:
                        # Default to company if we can't determine (most common case)
                        item['type'] = 'company'
                        item['category_tags'] = ['company', 'business']
                        results['companies'].append(item)
                        logger.info(f"Categorized '{query}' as COMPANY (default)")
        
        # Calculate totals
        all_results = (results['news'] + results['movies'] + results['sports'] + 
                      results['companies'] + results.get('gov_schemes', []) + 
                      results.get('finance', []) + results['images'] + results['web'])
        results['total_results'] = len(all_results)
        results['total_pages'] = (results['total_results'] + per_page - 1) // per_page if results['total_results'] > 0 else 0
        
        # Cache full results (first page only) for 2 minutes
        if page == 1:
            cache_service.set(cache_key, results, ttl_seconds=120)
        
        # Apply pagination
        return self._paginate_results(results, page, per_page)
    
    def _paginate_results(self, results: Dict[str, Any], page: int, per_page: int) -> Dict[str, Any]:
        """Apply pagination to results"""
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get all results in a flat list (sorted by confidence)
        all_results = []
        for result_type in ['news', 'movies', 'sports', 'companies', 'gov_schemes', 'finance', 'images', 'web']:
            all_results.extend(results.get(result_type, []))
        
        # Sort by confidence score
        all_results.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        # Paginate
        paginated_results = all_results[start_idx:end_idx]
        
        # Reorganize by type
        paginated_by_type = {
            'news': [],
            'movies': [],
            'sports': [],
            'companies': [],
            'gov_schemes': [],
            'finance': [],
            'images': [],
            'web': []
        }
        
        for item in paginated_results:
            item_type = item.get('type', 'unknown').lower()
            if 'news' in item_type or 'article' in item_type:
                paginated_by_type['news'].append(item)
            elif 'movie' in item_type or 'film' in item_type or 'tv' in item_type:
                paginated_by_type['movies'].append(item)
            elif 'sport' in item_type or 'team' in item_type:
                paginated_by_type['sports'].append(item)
            elif 'company' in item_type or 'business' in item_type:
                paginated_by_type['companies'].append(item)
            elif 'gov' in item_type or 'scheme' in item_type or 'policy' in item_type:
                paginated_by_type['gov_schemes'].append(item)
            elif 'finance' in item_type or 'market' in item_type or 'stock' in item_type:
                paginated_by_type['finance'].append(item)
            elif 'image' in item_type:
                paginated_by_type['images'].append(item)
            else:
                paginated_by_type['web'].append(item)
        
        # Update results with paginated data
        results.update(paginated_by_type)
        results['page'] = page
        results['per_page'] = per_page
        results['total_results'] = len(all_results)
        results['total_pages'] = (len(all_results) + per_page - 1) // per_page if len(all_results) > 0 else 0
        results['has_next'] = end_idx < len(all_results)
        results['has_prev'] = page > 1
        
        return results
    
    def _fetch_news_apis(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Fetch from news APIs"""
        items = []
        
        # Import news fetching functions
        try:
            from app.routes.search import (
                fetch_newsapi_news, fetch_newsdata_io, fetch_gnews_news,
                fetch_mediastack_news, fetch_currents_news
            )
            
            # Fetch in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(fetch_newsapi_news, query): 'newsapi',
                    executor.submit(fetch_newsdata_io, query): 'newsdata',
                    executor.submit(fetch_gnews_news, query): 'gnews',
                    executor.submit(fetch_mediastack_news, query): 'mediastack',
                    executor.submit(fetch_currents_news, query): 'currents',
                }
                
                for future in as_completed(futures):
                    source = futures[future]
                    try:
                        news_items = future.result(timeout=self.timeout)
                        for item in news_items:
                            item['source'] = source
                            item['type'] = 'news'
                            # Use category mapper for better category inference
                            item['category_tags'] = category_mapper.infer_categories(
                                f"{item.get('title', '')} {item.get('description', '')}"
                            )
                            if category:
                                item['category_tags'].append(category.lower())
                        items.extend(news_items)
                    except Exception as e:
                        logger.error(f"Error fetching from {source}: {e}")
        except Exception as e:
            logger.error(f"Error in news API fetch: {e}")
        
        return items
    
    def _fetch_movie_apis(self, query: str) -> List[Dict]:
        """Fetch from movie/TV APIs"""
        items = []
        
        try:
            from app.routes.search import fetch_omdb_movie, fetch_tmdb_movie, fetch_tvmaze_show
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(fetch_omdb_movie, query): 'omdb',
                    executor.submit(fetch_tmdb_movie, query): 'tmdb',
                    executor.submit(fetch_tvmaze_show, query): 'tvmaze',
                }
                
                for future in as_completed(futures):
                    source = futures[future]
                    try:
                        movie = future.result(timeout=self.timeout)
                        if movie:
                            movie['source'] = source
                            movie['type'] = 'movie'
                            movie['category_tags'] = ['entertainment', 'movies']
                            items.append(movie)
                    except Exception as e:
                        logger.error(f"Error fetching from {source}: {e}")
        except Exception as e:
            logger.error(f"Error in movie API fetch: {e}")
        
        return items
    
    def _fetch_sports_apis(self, query: str) -> List[Dict]:
        """Fetch from sports APIs"""
        items = []
        
        try:
            from app.routes.search import (
                fetch_sports_team, fetch_api_football_team,
                fetch_football_data_matches, fetch_cricapi_matches
            )
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(fetch_sports_team, query): 'thesportsdb',
                    executor.submit(fetch_api_football_team, query): 'api-football',
                    executor.submit(fetch_football_data_matches, query): 'football-data',
                    executor.submit(fetch_cricapi_matches, query): 'cricapi',
                }
                
                for future in as_completed(futures):
                    source = futures[future]
                    try:
                        result = future.result(timeout=self.timeout)
                        if result:
                            if isinstance(result, list):
                                for item in result:
                                    item['source'] = source
                                    item['type'] = 'sports'
                                    item['category_tags'] = ['sports']
                                    items.append(item)
                            else:
                                result['source'] = source
                                result['type'] = 'sports'
                                result['category_tags'] = ['sports']
                                items.append(result)
                    except Exception as e:
                        logger.error(f"Error fetching from {source}: {e}")
        except Exception as e:
            logger.error(f"Error in sports API fetch: {e}")
        
        return items
    
    def _fetch_company_apis(self, query: str) -> List[Dict]:
        """Fetch company information from Wikipedia"""
        items = []
        try:
            from app.routes.search import fetch_wikipedia_summary, is_company_related, is_disambiguation
            wiki = fetch_wikipedia_summary(query)
            if wiki and not is_disambiguation(wiki):
                # Be more lenient - if it has extract and title, include it as potential company
                # The frontend will filter if needed
                extract = wiki.get('extract', '') or ''
                title = wiki.get('title', query) or query
                
                # Check if it's company-related OR if query contains company keywords
                query_lower = query.lower()
                title_lower = title.lower()
                extract_lower = extract.lower()
                
                is_company = (
                    is_company_related(wiki) or
                    any(kw in query_lower for kw in ['company', 'corp', 'ltd', 'inc', 'pvt', 'enterprise', 'business']) or
                    any(kw in title_lower for kw in ['company', 'corporation', 'ltd', 'inc', 'pvt', 'enterprise']) or
                    any(kw in extract_lower[:500] for kw in ['company', 'corporation', 'business', 'founded', 'headquarters', 'revenue'])
                )
                
                if is_company or not extract:  # Include if company-related or if no extract (might be a stub)
                    item = {
                        'title': title,
                        'summary': extract,
                        'description': extract,
                        'image': wiki.get('thumbnail', {}).get('source') if wiki.get('thumbnail') else None,
                        'url': wiki.get('content_urls', {}).get('desktop', {}).get('page') if wiki.get('content_urls') else None,
                        'wiki': wiki.get('content_urls', {}).get('desktop', {}).get('page') if wiki.get('content_urls') else None,
                        'source': 'wikipedia',
                        'type': 'company',
                        'category_tags': ['company', 'business']
                    }
                    items.append(item)
        except Exception as e:
            logger.error(f"Error fetching company info: {e}")
        return items
    
    def _fetch_gov_scheme_apis(self, query: str) -> List[Dict]:
        """Fetch government scheme information from Wikipedia"""
        items = []
        try:
            from app.routes.search import fetch_wikipedia_summary, is_gov_scheme_related, is_disambiguation
            wiki = fetch_wikipedia_summary(query)
            if wiki and not is_disambiguation(wiki) and is_gov_scheme_related(wiki):
                item = {
                    'title': wiki.get('title', query),
                    'summary': wiki.get('extract', ''),
                    'description': wiki.get('extract', ''),
                    'image': wiki.get('thumbnail', {}).get('source') if wiki.get('thumbnail') else None,
                    'url': wiki.get('content_urls', {}).get('desktop', {}).get('page') if wiki.get('content_urls') else None,
                    'wiki': wiki.get('content_urls', {}).get('desktop', {}).get('page') if wiki.get('content_urls') else None,
                    'source': 'wikipedia',
                    'type': 'gov_scheme',
                    'category_tags': ['government', 'scheme', 'policy']
                }
                items.append(item)
        except Exception as e:
            logger.error(f"Error fetching gov scheme info: {e}")
        return items
    
    def _fetch_image_apis(self, query: str) -> List[Dict]:
        """Fetch images"""
        items = []
        
        try:
            from app.routes.search import fetch_pexels_images
            images = fetch_pexels_images(query)
            if images:
                for img in images:
                    img['source'] = 'pexels'
                    img['type'] = 'image'
                    img['category_tags'] = []
                items.extend(images)
        except Exception as e:
            logger.error(f"Error fetching images: {e}")
        
        return items
    
    def _fetch_web_apis(self, query: str) -> List[Dict]:
        """Fetch web search results"""
        items = []
        
        try:
            from app.routes.search import fetch_serpapi_results
            web_results = fetch_serpapi_results(query)
            if web_results:
                for result in web_results:
                    result['source'] = 'serpapi'
                    result['type'] = 'web'
                    result['category_tags'] = []
                items.extend(web_results)
        except Exception as e:
            logger.error(f"Error fetching web results: {e}")
        
        return items
    
    def _fetch_wikipedia_fallback(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Fetch from Wikipedia as fallback only"""
        items = []
        
        try:
            from app.routes.search import fetch_wikipedia_summary, is_disambiguation
            
            logger.info(f"Fetching Wikipedia fallback for: {query}")
            wiki = fetch_wikipedia_summary(query)
            
            if not wiki:
                logger.warning(f"Wikipedia returned None for: {query}")
                return items
            
            if not wiki.get('extract'):
                logger.warning(f"Wikipedia has no extract for: {query}")
                return items
            
            if is_disambiguation(wiki):
                logger.warning(f"Wikipedia result is disambiguation for: {query}")
                return items
            
            logger.info(f"Wikipedia found for {query}: {wiki.get('title', 'N/A')}")
            wiki_item = {
                'title': wiki.get('title', query),
                'summary': wiki.get('extract', ''),
                'description': wiki.get('extract', ''),
                'image': wiki.get('thumbnail', {}).get('source', '') if wiki.get('thumbnail') else None,
                'url': wiki.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'wiki': wiki.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'source': 'wikipedia',
                'type': 'wikipedia',  # Will be re-categorized in the calling function
                'category_tags': [category] if category else []
            }
            items.append(wiki_item)
            logger.info(f"Wikipedia fallback item created: {wiki_item.get('title')}")
        except Exception as e:
            logger.error(f"Error fetching Wikipedia: {e}", exc_info=True)
        
        return items
    
    def _infer_category_tags(self, item: Dict, category: Optional[str] = None) -> List[str]:
        """Infer category tags from item content (using category mapper)"""
        text = f"{item.get('title', '')} {item.get('description', '')}"
        tags = category_mapper.infer_categories(text)
        
        if category:
            normalized = category_mapper.normalize_category(category)
            if normalized not in tags:
                tags.append(normalized)
        
        return list(set(tags))

# Global instance
unified_search = UnifiedSearchService()

