import React, { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { fetchAggregatedReviews, submitUserReview } from '../services/api';
import { SkeletonCard as Skeleton, SkeletonStarRating } from '../components/SkeletonLoader';

function StarRatingInput({ value, onChange }) {
  const [hovered, setHovered] = useState(null);
  return (
    <div className="flex items-center">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-8 h-8 cursor-pointer transition-all ${star <= (hovered ?? value) ? 'text-yellow-400 scale-110' : 'text-gray-300'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
          onClick={() => onChange(star)}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(null)}
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.967a1 1 0 00.95.69h4.18c.969 0 1.371 1.24.588 1.81l-3.388 2.46a1 1 0 00-.364 1.118l1.287 3.966c.3.922-.755 1.688-1.54 1.118l-3.388-2.46a1 1 0 00-1.175 0l-3.388 2.46c-.784.57-1.838-.196-1.54-1.118l1.287-3.966a1 1 0 00-.364-1.118l-3.388-2.46c-.783-.57-.38-1.81.588-1.81h4.18a1 1 0 00.95-.69l1.286-3.967z" />
        </svg>
      ))}
    </div>
  );
}

function StarRating({ value, max = 5 }) {
  return (
    <div className="flex items-center">
      {[...Array(max)].map((_, i) => (
        <svg
          key={i}
          className={`w-7 h-7 transition-all ${i < Math.round(value) ? 'text-yellow-400 scale-110' : 'text-gray-300'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.967a1 1 0 00.95.69h4.18c.969 0 1.371 1.24.588 1.81l-3.388 2.46a1 1 0 00-.364 1.118l1.287 3.966c.3.922-.755 1.688-1.54 1.118l-3.388-2.46a1 1 0 00-1.175 0l-3.388 2.46c-.784.57-1.838-.196-1.54-1.118l1.287-3.966a1 1 0 00-.364-1.118l-3.388-2.46c-.783-.57-.38-1.81.588-1.81h4.18a1 1 0 00.95-.69l1.286-3.967z" />
        </svg>
      ))}
    </div>
  );
}

function PPLogo() {
  return (
    <div className="flex flex-col items-center mr-2">
      <span className="font-extrabold text-blue-700 text-2xl leading-none">P</span>
      <span className="font-extrabold text-blue-700 text-2xl leading-none rotate-180">P</span>
    </div>
  );
}

function ReviewSection({ entityName, setGlobalLoading }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [userReview, setUserReview] = useState('');
  const [userRating, setUserRating] = useState(5);
  const [submitting, setSubmitting] = useState(false);
  const [submitMsg, setSubmitMsg] = useState('');
  const [user] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch {
      return null;
    }
  });
  // Check if user already reviewed
  const userHasReviewed = user && data && data.classified_reviews && (
    [...data.classified_reviews.positive, ...data.classified_reviews.neutral, ...data.classified_reviews.negative].some(r => r.source === 'User' && r.user_id === user?.id)
  );

  useEffect(() => {
    if (!entityName) return;
    setLoading(true);
    setError(null);
    setGlobalLoading && setGlobalLoading(true);
    fetchAggregatedReviews(entityName)
      .then(res => {
        setData(res);
        setLoading(false);
        setGlobalLoading && setGlobalLoading(false);
      })
      .catch(() => {
        setError('Failed to fetch reviews');
        setLoading(false);
        setGlobalLoading && setGlobalLoading(false);
      });
  }, [entityName, setGlobalLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitMsg('');
    setGlobalLoading && setGlobalLoading(true);
    // For demo, use user_id=1
    const res = await submitUserReview(entityName, 1, userReview, userRating);
    if (res && res.message) {
      setSubmitMsg('Review submitted!');
      setUserReview('');
      setUserRating(5);
      fetchAggregatedReviews(entityName).then(setData);
    } else {
      setSubmitMsg(res.error || 'Failed to submit review');
    }
    setSubmitting(false);
    setGlobalLoading && setGlobalLoading(false);
  };

  if (!entityName) return null;
  if (loading) return (
    <div className="bg-gray-100 p-4 rounded ml-8 mr-8">
      <div className="flex items-center mb-4">
        <div className="mr-2"><SkeletonStarRating /></div>
        <div className="h-6 bg-gray-200 rounded w-32 mb-2 animate-pulse" />
      </div>
      {[...Array(3)].map((_, i) => <Skeleton type="review" key={i} />)}
    </div>
  );
  if (error) return <div className="bg-gray-100 p-4 rounded ml-8 mr-8 text-red-600">{error}</div>;
  if (!data || data.error) return <div className="bg-gray-100 p-4 rounded ml-8 mr-8 text-red-600">{data?.error || 'No reviews found.'}</div>;

  let allReviews = [
    ...data.classified_reviews.positive,
    ...data.classified_reviews.neutral,
    ...data.classified_reviews.negative
  ];
  if (filter !== 'all') {
    allReviews = allReviews.filter(r => r.sentiment === filter);
  }

  return (
    <div className="bg-gray-100 p-4 rounded ml-8 mr-8">
      <div className="flex items-center mb-4">
        <PPLogo />
        <span className="font-bold text-lg mr-2">Public Pulse Rating:</span>
        <span className="text-2xl font-bold text-blue-700 mr-2">{data.public_pulse_rating ?? 'N/A'}</span>
        <StarRating value={data.public_pulse_rating ?? 0} />
        <span className="ml-4 text-gray-600">({data.review_count} reviews from {Object.entries(data.source_counts).map(([src, cnt]) => `${cnt} ${src}`).join(', ')})</span>
      </div>
      {user ? (
        userHasReviewed ? (
          <div className="mb-6 text-green-700 font-semibold">You have already submitted a review for this entity.</div>
        ) : (
      <form onSubmit={handleSubmit} className="mb-6 flex flex-col md:flex-row items-center gap-2">
        <textarea
          className="flex-1 border border-gray-300 rounded px-4 py-2 focus:outline-none"
          placeholder="Write your review..."
          value={userReview}
          onChange={e => setUserReview(e.target.value)}
          required
        />
        <div className="flex items-center gap-2">
          <span className="text-gray-700">Your Rating:</span>
          <StarRatingInput value={userRating} onChange={setUserRating} />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          disabled={submitting || !userReview}
        >
          {submitting ? 'Submitting...' : 'Submit Review'}
        </button>
        {submitMsg && <span className="ml-2 text-green-700 font-semibold">{submitMsg}</span>}
      </form>
        )
      ) : (
        <div className="mb-6 text-blue-700 font-semibold">Please <a href="/login" className="underline">login</a> or <a href="/signup" className="underline">signup</a> to submit a review.</div>
      )}
      <div className="mb-4 flex gap-2">
        <button onClick={() => setFilter('all')} className={`px-3 py-1 rounded ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border border-blue-600'}`}>All</button>
        <button onClick={() => setFilter('positive')} className={`px-3 py-1 rounded ${filter === 'positive' ? 'bg-green-600 text-white' : 'bg-white text-green-600 border border-green-600'}`}>Positive</button>
        <button onClick={() => setFilter('neutral')} className={`px-3 py-1 rounded ${filter === 'neutral' ? 'bg-gray-600 text-white' : 'bg-white text-gray-600 border border-gray-600'}`}>Neutral</button>
        <button onClick={() => setFilter('negative')} className={`px-3 py-1 rounded ${filter === 'negative' ? 'bg-red-600 text-white' : 'bg-white text-red-600 border border-red-600'}`}>Negative</button>
      </div>
      <div className="space-y-4">
        {allReviews.length === 0 ? (
          <div className="text-gray-500 text-base">No reviews found for this filter.</div>
        ) : (
          allReviews.map((r, idx) => (
            <div key={idx} className="bg-white rounded shadow p-3 flex flex-col md:flex-row md:items-center justify-between">
              <div className="flex-1">
                <div className="text-base mb-1 font-medium">{r.text.length > 200 ? r.text.slice(0, 200) + '...' : r.text}</div>
                <div className="text-xs text-gray-500">Source: {r.source_url ? <a href={r.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{r.source}</a> : r.source} | Sentiment: <span className={r.sentiment === 'positive' ? 'text-green-700' : r.sentiment === 'negative' ? 'text-red-700' : 'text-gray-700'}>{r.sentiment}</span> | Rating: {r.rating}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function Entity({ setGlobalLoading }) {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const entityName = id ? id.replace(/-/g, ' ') : '';
  // Restore previous search if available
  const prevSearch = location.state?.search || '';
  const prevCategory = location.state?.category || '';
  return (
    <div>
      <button
        className="ml-8 mt-6 mb-2 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 text-blue-700 font-semibold"
        onClick={() => {
          if (prevSearch || prevCategory) {
            navigate('/', { state: { search: prevSearch, category: prevCategory } });
          } else {
            navigate(-1);
          }
        }}
      >
        ← Back to Results
      </button>
      <h2 className="text-2xl font-semibold mb-4 ml-8 mt-2">Reviews & Public Pulse Rating</h2>
      <ReviewSection entityName={entityName} setGlobalLoading={setGlobalLoading} />
    </div>
  );
}

export default Entity; 