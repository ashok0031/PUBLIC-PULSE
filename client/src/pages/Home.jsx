import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { fetchNews, universalSearch, unifiedSearch, getSuggestions, fetchAggregatedReviews, summarizeNews, analyzeSentiment, askAI, fetchWikipediaFallback } from '../services/api';
import { useNavigate, useLocation } from 'react-router-dom';
import { SkeletonCard as Skeleton } from '../components/SkeletonLoader';

function getVideoUrl(item) {
  // Try to find a video URL in known fields
  const videoFields = ['video', 'video_url', 'videoUrl', 'media', 'media_url'];
  for (const field of videoFields) {
    if (item[field] && typeof item[field] === 'string') return item[field];
  }
  // Fallback: if the main link is a YouTube or Vimeo video
  const url = item.link || item.url || item.reference_link;
  if (typeof url === 'string' && (url.includes('youtube.com') || url.includes('youtu.be') || url.includes('vimeo.com') || url.match(/\.mp4($|\?)/))) {
    return url;
  }
  return null;
}

function getYouTubeEmbed(url) {
  // Convert YouTube URL to embed
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)/);
  if (match) return `https://www.youtube.com/embed/${match[1]}`;
  return null;
}

function getVimeoEmbed(url) {
  const match = url.match(/vimeo\.com\/(\d+)/);
  if (match) return `https://player.vimeo.com/video/${match[1]}`;
  return null;
}

function ConfidenceBadge({ score, level }) {
  if (!score) return null;
  
  const getColor = () => {
    if (level === 'high') return 'bg-green-100 text-green-800';
    if (level === 'medium') return 'bg-yellow-100 text-yellow-800';
    if (level === 'low') return 'bg-orange-100 text-orange-800';
    return 'bg-gray-100 text-gray-800';
  };
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getColor()}`}>
      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
      {Math.round(score * 100)}% {level}
    </span>
  );
}

function NewsCard({ item, onSelect }) {
  const articleUrl = item.link || item.url || item.reference_link;
  const imageUrl = item.image || item.image_url || item.urlToImage || "";
  const hasImage = Boolean(imageUrl);
  const videoUrl = getVideoUrl(item);
  const youTubeEmbed = videoUrl && getYouTubeEmbed(videoUrl);
  const vimeoEmbed = videoUrl && getVimeoEmbed(videoUrl);
  const isMp4 = videoUrl && videoUrl.endsWith('.mp4');

  // Carousel logic
  const slides = [];
  if (videoUrl) {
    slides.push({ type: 'video', videoUrl, youTubeEmbed, vimeoEmbed, isMp4 });
  }
  if (hasImage) {
    slides.push({ type: 'image', imageUrl });
  }
  const [currentSlide, setCurrentSlide] = useState(0);
  // Auto-slide every 4s
  useEffect(() => {
    if (slides.length <= 1) return;
    const timer = setTimeout(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 4000);
    return () => clearTimeout(timer);
  }, [currentSlide, slides.length]);
  const goTo = (idx) => setCurrentSlide(idx);
  const prev = (e) => { e.stopPropagation(); setCurrentSlide((currentSlide - 1 + slides.length) % slides.length); };
  const next = (e) => { e.stopPropagation(); setCurrentSlide((currentSlide + 1) % slides.length); };

  // Helper to safely render source
  const getSourceString = (source) => {
    if (!source) return '';
    if (typeof source === 'string') return source;
    if (typeof source === 'object') return source.name || source.id || JSON.stringify(source);
    return String(source);
  };
  const isValidUrl = typeof articleUrl === 'string' && articleUrl.trim() !== '';
  return (
    <div className="flex flex-col md:flex-row bg-white rounded-lg shadow mb-6 overflow-hidden hover:shadow-lg transition border-2 border-transparent hover:border-blue-400 cursor-pointer" onClick={() => onSelect(item)}>
      <div className="flex-shrink-0 w-full md:w-64 h-48 md:h-auto bg-gray-100 flex items-center justify-center relative group" style={{ minWidth: '16rem', maxWidth: '16rem' }}>
        {slides.length > 0 && (
          <div className="w-full h-full relative">
            {/* Slide content */}
            {slides[currentSlide].type === 'video' ? (
              slides[currentSlide].youTubeEmbed ? (
                <iframe
                  src={slides[currentSlide].youTubeEmbed}
                  title="YouTube video"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="w-full h-full"
                  style={{ minHeight: '100%', minWidth: '100%', border: 0 }}
                />
              ) : slides[currentSlide].vimeoEmbed ? (
                <iframe
                  src={slides[currentSlide].vimeoEmbed}
                  title="Vimeo video"
                  allow="autoplay; fullscreen; picture-in-picture"
                  allowFullScreen
                  className="w-full h-full"
                  style={{ minHeight: '100%', minWidth: '100%', border: 0 }}
                />
              ) : slides[currentSlide].isMp4 ? (
                <video controls className="w-full h-full object-cover">
                  <source src={slides[currentSlide].videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              ) : null
            ) : (
              <img
                src={slides[currentSlide].imageUrl}
                alt={item.title}
                className="object-cover w-full h-full"
                onError={e => (e.target.style.display = 'none')}
              />
            )}
            {/* Carousel controls */}
            {slides.length > 1 && (
              <>
                <button onClick={prev} className="absolute left-2 top-1/2 -translate-y-1/2 bg-white bg-opacity-70 rounded-full p-1 shadow hover:bg-opacity-100 z-10">
                  <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
                </button>
                <button onClick={next} className="absolute right-2 top-1/2 -translate-y-1/2 bg-white bg-opacity-70 rounded-full p-1 shadow hover:bg-opacity-100 z-10">
                  <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
                </button>
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1 z-10">
                  {slides.map((_, idx) => (
                    <button key={idx} onClick={e => { e.stopPropagation(); goTo(idx); }} className={`w-2 h-2 rounded-full ${idx === currentSlide ? 'bg-blue-600' : 'bg-gray-300'}`}></button>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
        {slides.length === 0 && (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a4 4 0 004 4h10a4 4 0 004-4V7a4 4 0 00-4-4H7a4 4 0 00-4 4z" /></svg>
            <span>No Image/Video</span>
          </div>
        )}
      </div>
      <div className="flex flex-col p-4 flex-1 justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-xl line-clamp-2 flex-1">{item.title}</h2>
            {item.confidence_score && (
              <ConfidenceBadge score={item.confidence_score} level={item.confidence_level} />
            )}
          </div>
          <div className="text-gray-600 text-base mb-2">
            {getSourceString(item.source)}
            {item.sources && item.sources.length > 1 && (
              <span className="text-xs text-gray-500 ml-2">
                (Also from: {item.sources.filter(s => s !== item.source).join(', ')})
              </span>
            )}
          </div>
          <div className="text-gray-700 mb-4 text-base line-clamp-4">{item.description || item.content || ''}</div>
        </div>
        <div>
          {isValidUrl && (
            <a
              href={articleUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded text-base hover:bg-blue-700 transition"
            >
              Read More
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function EntityCard({ card, rating, onRatingClick, onMouseEnter, search, category, navigate }) {
  // Safety check for card and title
  if (!card || !card.title) {
    return null;
  }
  
  // Ensure cardTitle is a string
  const cardTitle = String(card.title || '').trim();
  if (!cardTitle) {
    return null;
  }
  const entityPath = `/entity/${encodeURIComponent(cardTitle.replace(/\s+/g, '-').toLowerCase())}`;
  
  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-center justify-between mb-6" onClick={() => navigate(entityPath, { state: { search, category } })} onMouseEnter={onMouseEnter} style={{ cursor: 'pointer' }}>
      <div className="flex items-center">
        {card.image ? (
          <img src={card.image} alt="card" className="w-20 h-20 rounded mr-4" />
        ) : (
          <div className="w-20 h-20 bg-gray-200 flex items-center justify-center rounded mr-4 text-gray-400">No Image</div>
        )}
        <div>
          <div className="font-semibold text-lg">{cardTitle}</div>
          <div className="text-gray-700 mb-2">{card.description || ''}</div>
          {card.actors && <div className="text-gray-600">Cast: {card.actors}</div>}
          {card.imdbID && <a href={`https://www.imdb.com/title/${card.imdbID}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">IMDb</a>}
          {card.wiki && <a href={card.wiki} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-4">Wikipedia</a>}
        </div>
      </div>
      <div className="flex flex-col items-end min-w-[120px] cursor-pointer" onClick={(e) => { e.stopPropagation(); onRatingClick(); }} title="See all reviews and rating">
        <span className="font-bold text-base text-blue-700">PP Rating</span>
        <span className="text-2xl font-bold text-blue-700 flex items-center">
          {rating !== undefined && rating !== null && rating !== 'N/A' ? (typeof rating === 'number' ? rating.toFixed(1) : String(rating)) : 'N/A'} 
          <svg className="w-6 h-6 ml-1 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.967a1 1 0 00.95.69h4.18c.969 0 1.371 1.24.588 1.81l-3.388 2.46a1 1 0 00-.364 1.118l1.287 3.966c.3.922-.755 1.688-1.54 1.118l-3.388-2.46a1 1 0 00-1.175 0l-3.388 2.46c-.784.57-1.838-.196-1.54-1.118l1.287-3.966a1 1 0 00-.364-1.118l-3.388-2.46c-.783-.57-.38-1.81.588-1.81h4.18a1 1 0 00.95-.69l1.286-3.967z" /></svg>
        </span>
      </div>
    </div>
  );
}

function UniversalSearchResults({ results, navigate, loading, setSelectedNews, search, category, suggestions = [], onSearchChange, onSearch }) {
  function getMovieImage(movie) {
    if (movie.Poster && movie.Poster !== 'N/A') return movie.Poster;
    if (movie.thumbnail && movie.thumbnail.source) return movie.thumbnail.source;
    return null;
  }
  // Memoize cards array
  const cards = useMemo(() => {
    let arr = [];
    
    // Handle unified search results format (movies, companies, sports arrays)
    if (results?.movies && Array.isArray(results.movies)) {
      results.movies.forEach(movie => {
        const title = String(movie.title || movie.Title || '').trim();
        if (title) {
          arr.push({
            type: 'movie',
            title: title,
            description: movie.summary || movie.Plot || movie.extract || movie.description || '',
            image: movie.image || movie.Poster || getMovieImage(movie),
            actors: movie.actors || movie.Actors,
            imdbID: movie.id || movie.imdbID,
            wiki: movie.url || movie.wiki || movie.content_urls?.desktop?.page,
          });
        }
      });
    }
    
    if (results?.companies && Array.isArray(results.companies)) {
      results.companies.forEach(company => {
        const title = String(company.title || company.name || '').trim();
        if (title) {
          arr.push({
            type: 'company',
            title: title,
            description: company.summary || company.extract || company.description || '',
            image: company.image || company.thumbnail?.source || company.thumbnail,
            wiki: company.url || company.wiki || company.content_urls?.desktop?.page,
            url: company.url || company.link,
          });
        }
      });
    }
    
    if (results?.sports && Array.isArray(results.sports)) {
      results.sports.forEach(sport => {
        const title = String(sport.title || sport.strTeam || sport.name || sport.team || '').trim();
        if (title) {
          arr.push({
            type: 'sports',
            title: title,
            description: sport.summary || sport.strDescriptionEN?.slice(0, 200) || sport.extract?.slice(0, 200) || sport.description || '',
            image: sport.image || sport.strTeamBadge || sport.thumbnail?.source || sport.logo,
            website: sport.website || sport.strWebsite,
            wiki: sport.url || sport.wiki || sport.content_urls?.desktop?.page,
          });
        }
      });
    }
    
    // Handle old format (single objects)
    if (results?.movie && !Array.isArray(results.movie)) {
      const title = String(results.movie.Title || results.movie.title || '').trim();
      if (title) {
        arr.push({
          type: 'movie',
          title: title,
          description: results.movie.Plot || results.movie.extract || results.movie.summary || '',
          image: getMovieImage(results.movie),
          actors: results.movie.Actors,
          imdbID: results.movie.imdbID,
          wiki: results.movie.content_urls?.desktop?.page,
        });
      }
    }
    if (results?.company && !Array.isArray(results.company)) {
      const title = String(results.company.title || '').trim();
      if (title) {
        arr.push({
          type: 'company',
          title: title,
          description: results.company.extract || results.company.summary || '',
          image: results.company.thumbnail?.source,
          wiki: results.company.content_urls?.desktop?.page,
        });
      }
    }
    if (results?.sports && !Array.isArray(results.sports)) {
      const title = String(results.sports.strTeam || results.sports.title || '').trim();
      if (title) {
        arr.push({
          type: 'sports',
          title: title,
          description: results.sports.strDescriptionEN?.slice(0, 200) || results.sports.extract?.slice(0, 200) || '',
          image: results.sports.strTeamBadge || results.sports.thumbnail?.source,
          website: results.sports.strWebsite,
          wiki: results.sports.content_urls?.desktop?.page,
        });
      }
    }
    // Handle gov_schemes array from unified search
    if (results?.gov_schemes && Array.isArray(results.gov_schemes)) {
      results.gov_schemes.forEach(scheme => {
        const title = String(scheme.title || '').trim();
        if (title) {
          arr.push({
            type: 'gov_scheme',
            title: title,
            description: scheme.summary || scheme.extract || scheme.description || '',
            image: scheme.image || scheme.thumbnail?.source,
            wiki: scheme.url || scheme.wiki || scheme.content_urls?.desktop?.page,
          });
        }
      });
    }
    // Handle old format (single object)
    if (results?.gov_scheme && !Array.isArray(results.gov_scheme)) {
      const title = String(results.gov_scheme.title || '').trim();
      if (title) {
        arr.push({
          type: 'gov_scheme',
          title: title,
          description: results.gov_scheme.extract || results.gov_scheme.summary || '',
          image: results.gov_scheme.thumbnail?.source,
          wiki: results.gov_scheme.content_urls?.desktop?.page,
        });
      }
    }
    if (results?.finance) {
      const title = String(results.finance.title || '').trim();
      if (title) {
        arr.push({
          type: 'finance',
          title: title,
          description: results.finance.extract || results.finance.summary || '',
          image: results.finance.thumbnail?.source,
          wiki: results.finance.content_urls?.desktop?.page,
        });
      }
    }
    // Handle web results that might be companies
    if (results?.web && Array.isArray(results.web)) {
      results.web.forEach(webItem => {
        const title = String(webItem.title || webItem.name || '').trim();
        if (title) {
          // Check if it looks like a company
          const titleLower = title.toLowerCase();
          const descLower = (webItem.description || webItem.summary || '').toLowerCase();
          const isCompanyLike = (
            titleLower.includes('company') || titleLower.includes('corp') || 
            titleLower.includes('ltd') || titleLower.includes('inc') ||
            descLower.includes('company') || descLower.includes('corporation') ||
            descLower.includes('business') || descLower.includes('founded')
          );
          
          if (isCompanyLike) {
            arr.push({
              type: 'company',
              title: title,
              description: webItem.description || webItem.summary || '',
              image: webItem.image || webItem.thumbnail?.source,
              url: webItem.url || webItem.link,
              source: webItem.source || 'web',
            });
          }
        }
      });
    }
    
    // Handle Wikipedia fallback results
    if (results?.wikipedia) {
      const title = String(results.wikipedia.title || '').trim();
      if (title) {
        arr.push({
          type: 'wikipedia',
          title: title,
          description: results.wikipedia.extract || results.wikipedia.summary || '',
          image: results.wikipedia.thumbnail?.source,
          wiki: results.wikipedia.content_urls?.desktop?.page,
          source: 'Wikipedia Fallback',
          fallback: true
        });
      }
    }
    // Deduplicate by title+description and filter out invalid cards
    const seen = new Set();
    return arr.filter(card => {
      // Filter out cards without title
      if (!card || !card.title) {
        return false;
      }
      const key = (card.title || '') + '|' + (card.description || '');
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [results]);

  const [ratings, setRatings] = useState({});
  useEffect(() => {
    let isMounted = true;
    async function fetchRatings() {
      const newRatings = {};
      for (const card of cards) {
        // Safety check - skip cards without title
        if (!card || !card.title) {
          continue;
        }
        try {
          const res = await fetchAggregatedReviews(card.title);
          console.log(`Rating response for ${card.title}:`, res);
          // Ensure we store the rating properly
          const rating = res?.public_pulse_rating;
          if (rating !== undefined && rating !== null && rating !== 'N/A') {
            newRatings[card.title] = typeof rating === 'number' ? parseFloat(rating.toFixed(1)) : parseFloat(rating);
          } else {
            // Show N/A if no rating found
            newRatings[card.title] = 'N/A';
          }
        } catch (err) {
          console.error(`Error fetching rating for ${card.title}:`, err);
          // Show N/A on error
          newRatings[card.title] = 'N/A';
        }
      }
      if (isMounted) {
        setRatings(newRatings);
        console.log('Ratings fetched:', newRatings);
      }
    }
    if (cards.length > 0) {
      fetchRatings();
    }
    return () => { isMounted = false; };
  }, [cards]);

  const prefetchCache = useRef({});
  const handlePrefetch = async (title) => {
    if (!title || prefetchCache.current[title]) return;
    try {
      const data = await fetchAggregatedReviews(title);
      prefetchCache.current[title] = data;
    } catch {}
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(2)].map((_, i) => <Skeleton type="entity" key={i} />)}
        <div className="bg-white rounded-lg shadow p-4">
          {[...Array(2)].map((_, i) => <Skeleton type="news" key={i} />)}
        </div>
      </div>
    );
  }

  // Debug: log cards and ratings
  console.log('UniversalSearchResults - Results object:', results);
  console.log('UniversalSearchResults - Results keys:', results ? Object.keys(results) : 'null');
  console.log('UniversalSearchResults - Companies:', results?.companies);
  console.log('UniversalSearchResults - Movies:', results?.movies);
  console.log('UniversalSearchResults - Sports:', results?.sports);
  console.log('UniversalSearchResults - Cards:', cards);
  console.log('UniversalSearchResults - Ratings:', ratings);

  return (
    <div className="space-y-6">
      {cards.length > 0 ? (
        cards.map((card, idx) => {
          // Safety check - skip invalid cards
          if (!card || !card.title) {
            return null;
          }
          // Ensure cardTitle is a string
          const cardTitle = String(card.title || '').trim();
          if (!cardTitle) {
            return null;
          }
          const entityPath = `/entity/${encodeURIComponent(cardTitle.replace(/\s+/g, '-').toLowerCase())}`;
          const cardRating = ratings[cardTitle] !== undefined ? ratings[cardTitle] : 'N/A';
          return (
            <EntityCard
              key={idx}
              card={card}
              rating={cardRating}
              onRatingClick={() => navigate(entityPath, { state: { search, category } })}
              onMouseEnter={() => handlePrefetch(cardTitle)}
              search={search}
              category={category}
              navigate={navigate}
            />
          );
        })
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
          <p className="text-yellow-800 mb-2">No entity cards found. Try searching for a movie, company, or sports team.</p>
          {suggestions.length > 0 && onSearchChange && onSearch && (
            <div className="mt-2">
              <p className="text-sm font-semibold text-gray-700 mb-1">Did you mean:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.slice(0, 3).map((sugg, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      onSearchChange(sugg.text);
                      onSearch(sugg.text);
                    }}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
                  >
                    {sugg.text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      {/* News section - show related articles */}
      {results.news && Array.isArray(results.news) && results.news.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4 mt-6">
          <h3 className="text-xl font-bold mb-4">Related Articles</h3>
          <div>
            {results.news.map((item, idx) => (
              <NewsCard key={idx} item={item} onSelect={setSelectedNews} />
            ))}
          </div>
        </div>
      )}
      {/* Also handle old format news */}
      {results.news && !Array.isArray(results.news) && (
        <div className="bg-white rounded-lg shadow p-4 mt-6">
          <h3 className="text-xl font-bold mb-4">Related Articles</h3>
          <div>
            <NewsCard item={results.news} onSelect={setSelectedNews} />
          </div>
        </div>
      )}
    </div>
  );
}

function AISidebar({ selectedNews, aiResult, loading, onSummarize, onSentiment, onAsk, onQuestionChange, question }) {
  return (
    <div className="w-full md:w-96 bg-white rounded-lg shadow p-4 ml-0 md:ml-8 mt-6 md:mt-0">
      <h3 className="font-bold text-lg mb-2">AI Bot</h3>
      {selectedNews ? (
        <>
          <div className="font-semibold mb-2">{selectedNews.title}</div>
          <div className="mb-2 text-gray-600 line-clamp-2">{selectedNews.description}</div>
          <div className="flex gap-2 mb-2">
            <button onClick={onSummarize} className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">Summarize</button>
            <button onClick={onSentiment} className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">Sentiment</button>
          </div>
          <div className="mb-2">
            <input type="text" value={question} onChange={e => onQuestionChange(e.target.value)} placeholder="Ask AI about this news..." className="border px-2 py-1 rounded w-full mb-1" />
            <button onClick={onAsk} className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 mt-1">Ask</button>
          </div>
          {loading ? <div className="text-blue-600">Loading...</div> : aiResult && <div className="bg-gray-100 p-2 rounded mt-2"><b>AI:</b> {aiResult}</div>}
        </>
      ) : (
        <div className="text-gray-500">Select a news card to use AI features.</div>
      )}
    </div>
  );
}

function Home({ selectedCategory, selectedLanguage, setRefreshHandler, setGlobalLoading }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Search state
  const [search, setSearch] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  // AI sidebar state
  const [selectedNews, setSelectedNews] = useState(null);
  const [aiResult, setAiResult] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [question, setQuestion] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const debounceTimer = useRef(null);
  const suggestionsTimer = useRef(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [paginationInfo, setPaginationInfo] = useState(null);

  // Restore previous search/category from navigation state
  useEffect(() => {
    if (location.state && (location.state.search || location.state.category)) {
      setSearch(location.state.search || '');
      if (location.state.search) {
        setSearching(true);
        setGlobalLoading && setGlobalLoading(true);
        universalSearch(location.state.search, location.state.category)
          .then(res => {
            setSearchResults(res);
            setSearching(false);
          })
          .catch(() => {
            setError('Failed to search');
            setSearchResults(null);
            setSearching(false);
          });
      }
    }
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (!search) {
      setLoading(true);
      setGlobalLoading && setGlobalLoading(true);
      setError(null);
      
      // Use setTimeout to simulate async behavior but return immediately
      setTimeout(() => {
        fetchNews(selectedCategory, selectedLanguage)
          .then(data => {
            setNews(data);
            setLoading(false);
            setGlobalLoading && setGlobalLoading(false);
          })
          .catch(err => {
            console.error('News fetch error:', err);
            setError('Failed to fetch news');
            setNews([]);
            setLoading(false);
            setGlobalLoading && setGlobalLoading(false);
          });
      }, 100); // Small delay to show loading state briefly
    }
  }, [selectedCategory, selectedLanguage, search, setGlobalLoading]);

  // Handler for refresh button (memoized)
  const handleRefresh = useCallback(() => {
    setLoading(true);
    setGlobalLoading && setGlobalLoading(true);
    setError(null);
    setSearch('');
    setSearchResults(null);
    
    setTimeout(() => {
      fetchNews(selectedCategory, selectedLanguage)
        .then(data => {
          setNews(data);
          setLoading(false);
          setGlobalLoading && setGlobalLoading(false);
        })
        .catch(err => {
          console.error('News refresh error:', err);
          setError('Failed to fetch news');
          setNews([]);
          setLoading(false);
          setGlobalLoading && setGlobalLoading(false);
        });
    }, 100);
  }, [selectedCategory, selectedLanguage, setGlobalLoading]);

  // Register the refresh handler with parent (App)
  useEffect(() => {
    if (setRefreshHandler) setRefreshHandler(() => handleRefresh);
    return () => { if (setRefreshHandler) setRefreshHandler(null); };
  }, [setRefreshHandler, handleRefresh]);

  // Debounced search handler
  const handleSearch = useCallback((query = null, page = 1) => {
    const searchQuery = query || search;
    const searchPage = page || currentPage;
    
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults(null);
      return;
    }
    
    setSearching(true);
    setGlobalLoading && setGlobalLoading(true);
    setError(null);
    setShowSuggestions(false);
    
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(async () => {
      try {
        // Try unified search first, fallback to old search
        const res = await unifiedSearch(searchQuery, selectedCategory, searchPage, 20);
        setSearchResults(res);
        // Update pagination info
        if (res.total_results !== undefined) {
          setPaginationInfo({
            page: res.page || 1,
            per_page: res.per_page || 20,
            total_results: res.total_results,
            total_pages: res.total_pages,
            has_next: res.has_next,
            has_prev: res.has_prev
          });
          setCurrentPage(res.page || 1);
        }
      } catch (err) {
        console.error('Search error:', err);
        // Fallback to old search
        try {
          const res = await universalSearch(searchQuery, selectedCategory);
          setSearchResults(res);
        } catch (fallbackErr) {
          setError('Failed to search');
          setSearchResults(null);
          // If search fails, try to get suggestions for spell correction
          try {
            const suggs = await getSuggestions(searchQuery, selectedCategory);
            if (suggs.suggestions && suggs.suggestions.length > 0) {
              setSuggestions(suggs.suggestions);
              setShowSuggestions(true);
            }
          } catch (suggErr) {
            console.error('Error fetching suggestions:', suggErr);
          }
        }
      } finally {
        setSearching(false);
        setGlobalLoading && setGlobalLoading(false);
      }
    }, 500); // 500ms debounce
  }, [search, selectedCategory, setGlobalLoading, currentPage]);

  useEffect(() => {
    if (!search) {
      setSearchResults(null);
      return;
    }
    // Auto-search on query change (debounced)
    handleSearch();
    
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
      if (suggestionsTimer.current) clearTimeout(suggestionsTimer.current);
    };
  }, [search, handleSearch]);

  // AI handlers
  const handleSummarize = async () => {
    if (!selectedNews) return;
    setAiLoading(true);
    setAiResult('');
    const res = await summarizeNews(selectedNews.description || selectedNews.content || selectedNews.title);
    setAiResult(res.summary || res.error || 'No summary.');
    setAiLoading(false);
  };
  const handleSentiment = async () => {
    if (!selectedNews) return;
    setAiLoading(true);
    setAiResult('');
    const res = await analyzeSentiment(selectedNews.description || selectedNews.content || selectedNews.title);
    setAiResult(res.sentiment || res.error || 'No sentiment.');
    setAiLoading(false);
  };
  const handleAsk = async () => {
    if (!selectedNews || !question) return;
    setAiLoading(true);
    setAiResult('');
    const res = await askAI(selectedNews.description || selectedNews.content || selectedNews.title, question);
    setAiResult(res.answer || res.error || 'No answer.');
    setAiLoading(false);
  };

  return (
    <div className="flex flex-col md:flex-row items-start max-w-7xl mx-auto">
      <div className="flex-1 min-w-0">
        <h1 className="text-3xl font-bold mb-4">Trending News & Ratings</h1>
        <form onSubmit={e => { e.preventDefault(); handleSearch(); }} className="mb-6 relative">
          <div className="flex relative">
            <input
              className="flex-1 border border-gray-300 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              type="text"
              placeholder="Search anything..."
              value={search}
              onChange={e => {
                const value = e.target.value;
                setSearch(value);
                // Debounced suggestions
                if (suggestionsTimer.current) {
                  clearTimeout(suggestionsTimer.current);
                }
                if (value.length >= 2) {
                  suggestionsTimer.current = setTimeout(async () => {
                    try {
                      const suggs = await getSuggestions(value, selectedCategory);
                      setSuggestions(suggs);
                      setShowSuggestions(true);
                    } catch (err) {
                      console.error('Error fetching suggestions:', err);
                    }
                  }, 300);
                } else {
                  setSuggestions([]);
                  setShowSuggestions(false);
                }
              }}
              onFocus={() => {
                if (suggestions.length > 0) setShowSuggestions(true);
              }}
              onBlur={() => {
                // Delay to allow clicking on suggestions
                setTimeout(() => setShowSuggestions(false), 200);
              }}
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-r hover:bg-blue-700 transition"
              disabled={searching}
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
          {/* Suggestions dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div
              ref={suggestionsRef}
              className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              {suggestions.map((sugg, idx) => (
                <div
                  key={idx}
                  className="px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  onClick={() => {
                    setSearch(sugg.text);
                    setShowSuggestions(false);
                    handleSearch(sugg.text);
                  }}
                >
                  <div className="font-medium text-gray-900">{sugg.text}</div>
                  {sugg.type && (
                    <div className="text-xs text-gray-500 capitalize">{sugg.type}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </form>
        {search && searchResults ? (
          <>
            <UniversalSearchResults 
              results={searchResults} 
              navigate={navigate} 
              loading={loading} 
              setSelectedNews={setSelectedNews} 
              search={search} 
              category={selectedCategory} 
              suggestions={suggestions}
              onSearchChange={setSearch}
              onSearch={handleSearch}
            />
            {/* Pagination Controls */}
            {paginationInfo && paginationInfo.total_pages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => {
                    if (paginationInfo.has_prev) {
                      const newPage = paginationInfo.page - 1;
                      setCurrentPage(newPage);
                      handleSearch(search, newPage);
                    }
                  }}
                  disabled={!paginationInfo.has_prev}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-700">
                  Page {paginationInfo.page} of {paginationInfo.total_pages} ({paginationInfo.total_results} results)
                </span>
                <button
                  onClick={() => {
                    if (paginationInfo.has_next) {
                      const newPage = paginationInfo.page + 1;
                      setCurrentPage(newPage);
                      handleSearch(search, newPage);
                    }
                  }}
                  disabled={!paginationInfo.has_next}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div>
            {loading ? (
              <div>Loading news...</div>
            ) : error ? (
              <div className="text-red-600">{error}</div>
            ) : news.length === 0 ? (
              <div>No news found.</div>
            ) : (
              <div>
                {news.map((item, idx) => (
                  <NewsCard key={idx} item={item} onSelect={setSelectedNews} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      <div className="hidden md:block md:w-96 ml-8 sticky top-8 self-start">
        <AISidebar
          selectedNews={selectedNews}
          aiResult={aiResult}
          loading={aiLoading}
          onSummarize={handleSummarize}
          onSentiment={handleSentiment}
          onAsk={handleAsk}
          onQuestionChange={setQuestion}
          question={question}
        />
      </div>
      {/* On mobile, show sidebar below */}
      <div className="block md:hidden w-full mt-6">
        <AISidebar
          selectedNews={selectedNews}
          aiResult={aiResult}
          loading={aiLoading}
          onSummarize={handleSummarize}
          onSentiment={handleSentiment}
          onAsk={handleAsk}
          onQuestionChange={setQuestion}
          question={question}
        />
      </div>
    </div>
  );
}

export default Home; 