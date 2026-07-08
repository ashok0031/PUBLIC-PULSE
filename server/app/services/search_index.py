import os
import json
from typing import List, Dict, Optional
from meilisearch import Client
from app.models.news_article import NewsArticle
from app.database import db
import logging

logger = logging.getLogger(__name__)

class SearchIndexService:
    """Service for managing search indexing with Meilisearch"""
    
    def __init__(self):
        self.meili_url = os.getenv('MEILISEARCH_URL', 'http://localhost:7700')
        self.meili_key = os.getenv('MEILISEARCH_MASTER_KEY', 'masterKey')
        
        try:
            self.client = Client(self.meili_url, self.meili_key)
            self.index_name = 'news_articles'
            self._setup_index()
        except Exception as e:
            logger.error(f"Failed to initialize Meilisearch client: {e}")
            self.client = None
    
    def _setup_index(self):
        """Setup the search index with proper configuration"""
        if not self.client:
            return
        
        try:
            # Create index if it doesn't exist
            try:
                self.client.create_index(self.index_name, {'primaryKey': 'id'})
                logger.info(f"Created search index: {self.index_name}")
            except Exception:
                # Index already exists
                pass
            
            # Configure searchable attributes
            self.client.index(self.index_name).update_searchable_attributes([
                'title',
                'description',
                'content',
                'source_name',
                'category',
                'ai_keywords'
            ])
            
            # Configure filterable attributes
            self.client.index(self.index_name).update_filterable_attributes([
                'category',
                'source_name',
                'language',
                'country',
                'published_at',
                'source_bias_score',
                'source_reliability'
            ])
            
            # Configure sortable attributes
            self.client.index(self.index_name).update_sortable_attributes([
                'published_at',
                'created_at',
                'source_reliability',
                'ai_sentiment'
            ])
            
            # Configure ranking rules for better relevance
            self.client.index(self.index_name).update_ranking_rules([
                'words',
                'typo',
                'proximity',
                'attribute',
                'sort',
                'exactness'
            ])
            
            logger.info(f"Search index {self.index_name} configured successfully")
            
        except Exception as e:
            logger.error(f"Error setting up search index: {e}")
    
    def index_article(self, article: NewsArticle) -> bool:
        """Index a single article"""
        if not self.client:
            return False
        
        try:
            # Prepare document for indexing
            doc = {
                'id': article.id,
                'title': article.title,
                'description': article.description or '',
                'content': article.content or '',
                'url': article.url,
                'image_url': article.image_url or '',
                'source_name': article.source_name,
                'source_bias_score': article.source_bias_score,
                'source_reliability': article.source_reliability,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'category': article.category,
                'language': article.language,
                'country': article.country,
                'ai_summary': article.ai_summary or '',
                'ai_sentiment': article.ai_sentiment,
                'ai_keywords': article.ai_keywords or '[]',
                'ai_bias_analysis': article.ai_bias_analysis or '',
                'created_at': article.created_at.isoformat(),
                'updated_at': article.updated_at.isoformat(),
                'is_expired': article.is_expired
            }
            
            # Add to search index
            self.client.index(self.index_name).add_documents([doc])
            logger.debug(f"Indexed article: {article.title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing article {article.id}: {e}")
            return False
    
    def index_multiple_articles(self, articles: List[NewsArticle]) -> int:
        """Index multiple articles at once"""
        if not self.client:
            return 0
        
        try:
            docs = []
            for article in articles:
                doc = {
                    'id': article.id,
                    'title': article.title,
                    'description': article.description or '',
                    'content': article.content or '',
                    'url': article.url,
                    'image_url': article.image_url or '',
                    'source_name': article.source_name,
                    'source_bias_score': article.source_bias_score,
                    'source_reliability': article.source_reliability,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'category': article.category,
                    'language': article.language,
                    'country': article.country,
                    'ai_summary': article.ai_summary or '',
                    'ai_sentiment': article.ai_sentiment,
                    'ai_keywords': article.ai_keywords or '[]',
                    'ai_bias_analysis': article.ai_bias_analysis or '',
                    'created_at': article.created_at.isoformat(),
                    'updated_at': article.updated_at.isoformat(),
                    'is_expired': article.is_expired
                }
                docs.append(doc)
            
            if docs:
                self.client.index(self.index_name).add_documents(docs)
                logger.info(f"Indexed {len(docs)} articles")
                return len(docs)
            
        except Exception as e:
            logger.error(f"Error indexing multiple articles: {e}")
        
        return 0
    
    def search_articles(self, query: str, filters: Dict = None, 
                       sort_by: str = None, page: int = 1, per_page: int = 20) -> Dict:
        """Search articles using Meilisearch"""
        if not self.client:
            return self._fallback_search(query, filters, sort_by, page, per_page)
        
        try:
            search_params = {
                'q': query,
                'offset': (page - 1) * per_page,
                'limit': per_page
            }
            
            # Add filters
            if filters:
                filter_strings = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        filter_strings.append(f"{key} IN {value}")
                    elif isinstance(value, dict):
                        # Handle range filters
                        if 'min' in value or 'max' in value:
                            range_filters = []
                            if 'min' in value:
                                range_filters.append(f"{key} >= {value['min']}")
                            if 'max' in value:
                                range_filters.append(f"{key} <= {value['max']}")
                            filter_strings.extend(range_filters)
                    else:
                        filter_strings.append(f"{key} = {value}")
                
                if filter_strings:
                    search_params['filter'] = ' AND '.join(filter_strings)
            
            # Add sorting
            if sort_by:
                search_params['sort'] = [sort_by]
            
            # Perform search
            results = self.client.index(self.index_name).search(query, search_params)
            
            # Process results
            articles = []
            for hit in results.get('hits', []):
                try:
                    # Parse AI keywords back to list
                    ai_keywords = json.loads(hit.get('ai_keywords', '[]'))
                    hit['ai_keywords'] = ai_keywords
                    articles.append(hit)
                except:
                    hit['ai_keywords'] = []
                    articles.append(hit)
            
            return {
                'articles': articles,
                'total': results.get('estimatedTotalHits', 0),
                'page': page,
                'per_page': per_page,
                'total_pages': (results.get('estimatedTotalHits', 0) + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return self._fallback_search(query, filters, sort_by, page, per_page)
    
    def _fallback_search(self, query: str, filters: Dict = None, 
                        sort_by: str = None, page: int = 1, per_page: int = 20) -> Dict:
        """Fallback search using database when Meilisearch is unavailable"""
        try:
            # Build database query
            db_query = NewsArticle.query.filter_by(is_duplicate=False)
            
            # Add text search
            if query:
                db_query = db_query.filter(
                    db.or_(
                        NewsArticle.title.ilike(f'%{query}%'),
                        NewsArticle.description.ilike(f'%{query}%'),
                        NewsArticle.content.ilike(f'%{query}%')
                    )
                )
            
            # Add filters
            if filters:
                if 'category' in filters:
                    db_query = db_query.filter(NewsArticle.category == filters['category'])
                if 'source_name' in filters:
                    db_query = db_query.filter(NewsArticle.source_name == filters['source_name'])
                if 'language' in filters:
                    db_query = db_query.filter(NewsArticle.language == filters['language'])
                if 'country' in filters:
                    db_query = db_query.filter(NewsArticle.country == filters['country'])
            
            # Add sorting
            if sort_by == 'published_at':
                db_query = db_query.order_by(NewsArticle.published_at.desc())
            elif sort_by == 'created_at':
                db_query = db_query.order_by(NewsArticle.created_at.desc())
            elif sort_by == 'source_reliability':
                db_query = db_query.order_by(NewsArticle.source_reliability.desc())
            else:
                db_query = db_query.order_by(NewsArticle.created_at.desc())
            
            # Get total count
            total = db_query.count()
            
            # Pagination
            articles = db_query.offset((page - 1) * per_page).limit(per_page).all()
            
            # Convert to dict format
            article_dicts = []
            for article in articles:
                article_dict = article.to_dict()
                article_dicts.append(article_dict)
            
            return {
                'articles': article_dicts,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return {
                'articles': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }
    
    def reindex_all(self) -> int:
        """Reindex all articles in the database"""
        if not self.client:
            return 0
        
        try:
            # Clear existing index
            self.client.index(self.index_name).delete_all_documents()
            logger.info("Cleared existing search index")
            
            # Get all articles
            articles = NewsArticle.query.filter_by(is_duplicate=False).all()
            
            # Index them
            count = self.index_multiple_articles(articles)
            logger.info(f"Reindexed {count} articles")
            
            return count
            
        except Exception as e:
            logger.error(f"Error reindexing all articles: {e}")
            return 0
    
    def delete_article(self, article_id: int) -> bool:
        """Remove an article from the search index"""
        if not self.client:
            return False
        
        try:
            self.client.index(self.index_name).delete_document(article_id)
            logger.debug(f"Deleted article {article_id} from search index")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting article {article_id} from search index: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the search index"""
        if not self.client:
            return {'error': 'Search index not available'}
        
        try:
            stats = self.client.index(self.index_name).get_stats()
            return {
                'total_documents': stats.get('numberOfDocuments', 0),
                'index_size': stats.get('databaseSize', 0),
                'last_update': stats.get('updatedAt', ''),
                'is_indexing': stats.get('isIndexing', False)
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {'error': str(e)}
    
    def suggest_queries(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial query"""
        if not self.client or len(partial_query) < 2:
            return []
        
        try:
            # Search for suggestions
            results = self.client.index(self.index_name).search(
                partial_query, 
                {'limit': limit, 'attributesToRetrieve': ['title']}
            )
            
            suggestions = []
            for hit in results.get('hits', []):
                title = hit.get('title', '')
                if title and partial_query.lower() in title.lower():
                    suggestions.append(title)
            
            return list(set(suggestions))[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
