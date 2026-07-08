import React from 'react';

export function SkeletonCard({ type = 'entity' }) {
  // type: 'entity', 'news', 'review'
  if (type === 'entity') {
    return (
      <div className="bg-white rounded-lg shadow p-4 flex items-center justify-between mb-6 animate-pulse">
        <div className="flex items-center">
          <div className="w-20 h-20 bg-gray-200 rounded mr-4" />
          <div>
            <div className="h-5 bg-gray-200 rounded w-32 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-48 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-24 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-20" />
          </div>
        </div>
        <div className="flex flex-col items-end min-w-[120px]">
          <div className="h-4 bg-gray-200 rounded w-16 mb-2" />
          <div className="h-8 bg-gray-200 rounded w-12" />
        </div>
      </div>
    );
  }
  if (type === 'news') {
    return (
      <div className="flex flex-col md:flex-row bg-white rounded-lg shadow mb-6 overflow-hidden animate-pulse">
        <div className="flex-shrink-0 w-full md:w-64 h-48 md:h-auto bg-gray-200" style={{ minWidth: '16rem', maxWidth: '16rem' }} />
        <div className="flex flex-col p-4 flex-1 justify-between">
          <div>
            <div className="h-5 bg-gray-200 rounded w-40 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-24 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-64 mb-4" />
          </div>
          <div className="h-8 bg-gray-200 rounded w-24" />
        </div>
      </div>
    );
  }
  if (type === 'review') {
    return (
      <div className="bg-white rounded shadow p-3 flex flex-col md:flex-row md:items-center justify-between animate-pulse">
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-64 mb-2" />
          <div className="h-3 bg-gray-100 rounded w-32" />
        </div>
      </div>
    );
  }
  return null;
}

export function SkeletonText({ width = 'w-32', height = 'h-4', className = '' }) {
  return <div className={`bg-gray-200 rounded ${width} ${height} ${className} animate-pulse`} />;
}

export function SkeletonStarRating() {
  return (
    <div className="flex items-center gap-1 animate-pulse">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="w-7 h-7 bg-gray-200 rounded-full" />
      ))}
    </div>
  );
}

export default SkeletonCard; 