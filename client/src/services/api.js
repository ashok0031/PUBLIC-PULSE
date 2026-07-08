const API_BASE = 'http://localhost:5000/api';

export async function login(identifier, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: identifier, password })
  });
  return res.json();
}

export async function signup(form) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form)
  });
  return res.json();
}

export async function fetchEntities() {
  const res = await fetch(`${API_BASE}/entities/`);
  return res.json();
}

export async function fetchEntity(id) {
  const res = await fetch(`${API_BASE}/entities/${id}`);
  return res.json();
}

export async function fetchReviews(entityId) {
  const res = await fetch(`${API_BASE}/reviews/${entityId}`);
  return res.json();
}

export async function fetchNews(category, language) {
  try {
    // Call the actual backend API
    const categoryParam = category ? `?category=${encodeURIComponent(category)}` : '';
    const res = await fetch(`${API_BASE}/news/${categoryParam}`);
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    
    // Ensure we return at least 20 items if available
    if (Array.isArray(data) && data.length > 0) {
      return data.slice(0, Math.max(20, data.length)); // Return at least 20, or all if less
    }
    
    // Fallback to empty array if no data
    return [];
  } catch (error) {
    console.error('Error fetching news:', error);
    // Return empty array on error instead of static data
    return [];
  }
}

export async function sendOtp(email) {
  const res = await fetch(`${API_BASE}/auth/send-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return res.json();
}

export async function verifyOtp(email, otp) {
  const res = await fetch(`${API_BASE}/auth/verify-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, otp })
  });
  return res.json();
}

export async function universalSearch(query, category = null) {
  let url = `${API_BASE}/search/?query=${encodeURIComponent(query)}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  const res = await fetch(url);
  return res.json();
}

// New unified search endpoint with pagination
export async function unifiedSearch(query, category = null, page = 1, perPage = 20) {
  let url = `${API_BASE}/search/unified?query=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      mode: 'cors',
    });
    if (!res.ok) {
      console.error('Unified search failed:', res.status, res.statusText);
      // Fallback to old search if unified fails
      return universalSearch(query, category);
    }
    const data = await res.json();
    console.log('Unified search response:', data);
    return data;
  } catch (error) {
    console.error('Unified search error:', error);
    // Fallback to old search if unified fails
    return universalSearch(query, category);
  }
}

// Search suggestions/autocomplete
export async function getSuggestions(query, category = null, limit = 10) {
  if (!query || query.length < 2) return [];
  let url = `${API_BASE}/suggestions/?q=${encodeURIComponent(query)}&limit=${limit}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    return [];
  }
}

export async function wikipediaSearch(query) {
  const url = `${API_BASE}/search/wikipedia?query=${encodeURIComponent(query)}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchAggregatedReviews(query, category = null) {
  let url = `${API_BASE}/reviews/aggregate?query=${encodeURIComponent(query)}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  const res = await fetch(url);
  return res.json();
}

export async function submitUserReview(entity_name, user_id, text, rating) {
  const res = await fetch(`${API_BASE}/reviews/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entity_name, user_id, text, rating })
  });
  return res.json();
}

export async function summarizeNews(text) {
  const res = await fetch('http://localhost:5000/api/ai/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return res.json();
}

export async function analyzeSentiment(text) {
  const res = await fetch('http://localhost:5000/api/ai/sentiment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return res.json();
}

export async function askAI(text, question) {
  const res = await fetch('http://localhost:5000/api/ai/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, question })
  });
  return res.json();
}

export async function fetchWikipediaFallback(query) {
  // Use universal search as fallback since Wikipedia endpoint might not be working
  const res = await fetch(`${API_BASE}/search/?query=${encodeURIComponent(query)}`);
  const data = await res.json();
  // Return in Wikipedia format for consistency
  if (data.wikipedia) {
    return { wikipedia: data.wikipedia };
  } else if (data.company) {
    return { wikipedia: data.company };
  } else if (data.movie) {
    return { wikipedia: data.movie };
  } else if (data.sports) {
    return { wikipedia: data.sports };
  } else if (data.gov_scheme) {
    return { wikipedia: data.gov_scheme };
  } else if (data.finance) {
    return { wikipedia: data.finance };
  }
  return {};
} 