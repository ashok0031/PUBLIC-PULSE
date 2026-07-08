import React, { useState, useEffect, useCallback } from 'react';
import { SkeletonLoader } from './SkeletonLoader';

const OptimizedNews = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [category, setCategory] = useState('India');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState('published_at');
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [filters, setFilters] = useState({});

  // Fetch categories on component mount
  useEffect(() => {
    fetchCategories();
    fetchSources();
  }, []);

  // Fetch news when dependencies change
  useEffect(() => {
    fetchNews();
  }, [category, searchQuery, currentPage, sortBy, filters]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/v2/news/categories');
      const data = await response.json();
      if (data.success) {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchSources = async () => {
    try {
      const response = await fetch('/api/v2/news/sources');
      const data = await response.json();
      if (data.success) {
        setSources(data.sources);
      }
    } catch (error) {
      console.error('Error fetching sources:', error);
    }
  };

  const fetchNews = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        category: category,
        page: currentPage,
        per_page: 20,
        sort: sortBy,
        ...(searchQuery && { q: searchQuery }),
        ...(filters.source && { source: filters.source }),
        ...(filters.bias && { bias: filters.bias })
      });

      const response = await fetch(`/api/v2/news/?${params}`);
      const data = await response.json();

      if (data.success) {
        setNews(data.data);
        setTotalPages(data.pagination.total_pages);
      } else {
        setError(data.error || 'Failed to fetch news');
      }
    } catch (error) {
      setError('Network error occurred');
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  }, [category, searchQuery, currentPage, sortBy, filters]);

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchNews();
  };

  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);
    setCurrentPage(1);
    setSearchQuery('');
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setCurrentPage(1);
  };

  const getBiasColor = (biasScore) => {
    if (biasScore < -0.3) return 'text-blue-600';
    if (biasScore > 0.3) return 'text-red-600';
    return 'text-green-600';
  };

  const getBiasLabel = (biasScore) => {
    if (biasScore < -0.3) return 'Left-leaning';
    if (biasScore > 0.3) return 'Right-leaning';
    return 'Neutral';
  };

  const getReliabilityColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading && news.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <SkeletonLoader key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Public Pulse News
        </h1>
        <p className="text-gray-600">
          Stay informed with aggregated news from multiple sources, featuring AI-powered analysis and bias transparency.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search for news, schemes, or topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Search
            </button>
          </div>
        </form>

        {/* Category Tabs */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat.slug}
                onClick={() => handleCategoryChange(cat.name)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  category === cat.name
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.name} ({cat.count})
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Source Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source
            </label>
            <select
              value={filters.source || ''}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Sources</option>
              {sources.map((source) => (
                <option key={source.name} value={source.name}>
                  {source.name} ({source.article_count})
                </option>
              ))}
            </select>
          </div>

          {/* Bias Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bias
            </label>
            <select
              value={filters.bias || ''}
              onChange={(e) => handleFilterChange('bias', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Perspectives</option>
              <option value="left">Left-leaning</option>
              <option value="neutral">Neutral</option>
              <option value="right">Right-leaning</option>
            </select>
          </div>

          {/* Sort Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => handleSortChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="published_at">Latest</option>
              <option value="created_at">Added Recently</option>
              <option value="source_reliability">Most Reliable</option>
              <option value="ai_sentiment">AI Sentiment</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* News Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {news.map((article) => (
          <article
            key={article.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Article Image */}
            {article.image_url && (
              <div className="aspect-video overflow-hidden">
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/400x225?text=No+Image';
                  }}
                />
              </div>
            )}

            {/* Article Content */}
            <div className="p-6">
              {/* Source and Bias Info */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-600">
                    {article.source_name}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${getReliabilityColor(article.source_reliability)}`}>
                    {Math.round(article.source_reliability * 100)}% reliable
                  </span>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full bg-gray-100 ${getBiasColor(article.source_bias_score)}`}>
                  {getBiasLabel(article.source_bias_score)}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 transition-colors"
                >
                  {article.title}
                </a>
              </h3>

              {/* Description */}
              {article.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {article.description}
                </p>
              )}

              {/* AI Analysis */}
              {article.ai_summary && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <h4 className="text-sm font-medium text-blue-800 mb-1">AI Summary</h4>
                  <p className="text-sm text-blue-700 line-clamp-2">
                    {article.ai_summary}
                  </p>
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  {article.published_at
                    ? new Date(article.published_at).toLocaleDateString()
                    : 'Recently added'}
                </span>
                <span className="capitalize">{article.category}</span>
              </div>

              {/* Keywords */}
              {article.ai_keywords && article.ai_keywords.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {article.ai_keywords.slice(0, 3).map((keyword, index) => (
                    <span
                      key={index}
                      className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </article>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex justify-center">
          <nav className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {[...Array(totalPages)].map((_, i) => {
              const page = i + 1;
              if (
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 2 && page <= currentPage + 2)
              ) {
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                );
              } else if (
                page === currentPage - 3 ||
                page === currentPage + 3
              ) {
                return <span key={page} className="px-3 py-2 text-gray-500">...</span>;
              }
              return null;
            })}
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </nav>
        </div>
      )}

      {/* Loading State for Pagination */}
      {loading && news.length > 0 && (
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            Loading more articles...
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizedNews;


