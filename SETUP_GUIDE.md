# 🚀 Public Pulse - Google-Style Architecture Setup Guide

Welcome to the upgraded Public Pulse application! This guide will walk you through setting up the new Google-style architecture that makes your app lightning-fast and professional-grade.

## 🎯 What's New in This Version

### **Backend Improvements**
- ✅ **Background Task Processing** with Celery + Redis
- ✅ **Smart Deduplication** using multiple strategies
- ✅ **Search Indexing** with Meilisearch (Google-style fast search)
- ✅ **API Rate Limit Handling** with intelligent fallbacks
- ✅ **Caching & Storage** of pre-fetched news data
- ✅ **Scheduled Background Jobs** for automatic news updates

### **Frontend Improvements**
- ✅ **Modern React Components** with Tailwind CSS
- ✅ **Instant Search** with real-time suggestions
- ✅ **Advanced Filtering** by source, bias, and reliability
- ✅ **Responsive Design** for all devices
- ✅ **Loading States** and skeleton loaders

### **Architecture Benefits**
- 🚀 **Instant Response Times** (no more waiting for API calls)
- 🔄 **Automatic Background Updates** every 6 hours
- 🎯 **Smart Content Deduplication** (no more duplicate articles)
- 📊 **Bias Transparency** and source reliability scoring
- 🧠 **AI-Powered Analysis** with Gemini integration

## 🛠️ Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Docker** (optional, for easy service setup)
- **Git** for version control

## 🚀 Quick Start (Recommended)

### **Option 1: Using Docker (Easiest)**

1. **Clone and navigate to the project:**
   ```bash
   cd public-pulse
   ```

2. **Start all services with Docker:**
   ```bash
   docker-compose up -d
   ```

3. **Run the migration script:**
   ```bash
   python migrate_to_new_structure.py
   ```

4. **Access your app:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000
   - Meilisearch: http://localhost:7700

### **Option 2: Local Setup**

1. **Install Python dependencies:**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Start background services:**
   ```bash
   # In project root
   python start_background_services.py
   ```

3. **In a new terminal, start the Flask app:**
   ```bash
   cd server
   python run.py
   ```

4. **In another terminal, start the React frontend:**
   ```bash
   cd client
   npm install
   npm start
   ```

## 🔧 Detailed Setup Instructions

### **Step 1: Environment Configuration**

1. **Copy the environment template:**
   ```bash
   cd server
   cp env.example .env
   ```

2. **Edit `.env` with your API keys:**
   ```bash
   # News API Keys
   NEWSDATA_API_KEY=your_newsdata_api_key_here
   NEWSAPI_API_KEY=your_newsapi_api_key_here
   DATAGOVIN_API_KEY=your_datagovin_api_key_here
   GNEWS_API_KEY=your_gnews_api_key_here
   MEDIASTACK_API_KEY=your_mediastack_api_key_here
   
   # AI API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Email Configuration
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_email_app_password
   ```

### **Step 2: Database Setup**

1. **Run the migration script:**
   ```bash
   python migrate_to_new_structure.py
   ```

   This will:
   - Create the new database structure
   - Migrate existing data (if any)
   - Create sample data for testing
   - Set up the search index

### **Step 3: Background Services**

1. **Start Redis:**
   ```bash
   # On Windows: Download Redis from GitHub releases
   # On macOS: brew install redis && brew services start redis
   # On Linux: sudo systemctl start redis
   ```

2. **Start Meilisearch:**
   ```bash
   # Download from: https://docs.meilisearch.com/learn/getting_started/installation.html
   # Or use Docker: docker run -p 7700:7700 getmeili/meilisearch:latest
   ```

3. **Start the background scheduler:**
   ```bash
   python start_background_services.py
   ```

### **Step 4: Test the System**

1. **Check service health:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test the new API endpoints:**
   ```bash
   # Get all news
   curl http://localhost:5000/api/v2/news/
   
   # Search for specific content
   curl "http://localhost:5000/api/v2/news/?q=government%20schemes"
   
   # Get categories
   curl http://localhost:5000/api/v2/news/categories
   
   # Get sources
   curl http://localhost:5000/api/v2/news/sources
   ```

## 📊 Monitoring & Management

### **Background Task Status**

Check the status of background tasks:
```bash
curl http://localhost:5000/api/background/status
```

### **Manual Task Execution**

Run specific tasks immediately:
```bash
# Refresh all news
curl -X POST http://localhost:5000/api/v2/news/refresh

# Reindex search
curl -X POST http://localhost:5000/api/background/reindex
```

### **Logs and Debugging**

- **Flask logs:** Check the terminal where you started the Flask app
- **Background task logs:** Check the scheduler terminal
- **Database logs:** Check `server/logs/` directory

## 🔍 Understanding the New Architecture

### **How It Works**

1. **Background Fetching:** News is fetched every 6 hours in the background
2. **Smart Storage:** Articles are stored in your database with deduplication
3. **Instant Search:** Meilisearch provides Google-style fast search
4. **User Requests:** Users get instant results from your database, not external APIs

### **Data Flow**

```
External APIs → Background Fetcher → Database Storage → Search Index → User Requests
     ↓              ↓                    ↓              ↓            ↓
   Rate Limited   Celery Tasks      PostgreSQL    Meilisearch   Instant Results
```

### **Scheduled Tasks**

- **Every 6 hours:** Fetch news from all sources
- **Daily at 2 AM:** Reindex search for optimal performance
- **Weekly:** Clean up expired articles and optimize database

## 🚨 Troubleshooting

### **Common Issues**

1. **Redis Connection Error:**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return "PONG"
   ```

2. **Meilisearch Connection Error:**
   ```bash
   # Check if Meilisearch is running
   curl http://localhost:7700/health
   # Should return health status
   ```

3. **Database Migration Errors:**
   ```bash
   # Reset database and try again
   cd server
   rm instance/app.db
   python migrate_to_new_structure.py
   ```

4. **Background Tasks Not Running:**
   ```bash
   # Check if Celery workers are running
   ps aux | grep celery
   # Start the scheduler again
   python start_background_services.py
   ```

### **Performance Issues**

1. **Slow Search:**
   - Check if Meilisearch is running
   - Verify the search index has data
   - Check background task logs

2. **High Memory Usage:**
   - Monitor Redis memory usage
   - Check for memory leaks in background tasks
   - Restart services if needed

## 🔮 Next Steps

### **Immediate Improvements**

1. **Add more news sources** to `app/services/news_fetcher.py`
2. **Customize deduplication logic** in `app/services/deduplication.py`
3. **Enhance AI analysis** in your existing AI routes
4. **Add user preferences** for personalized feeds

### **Future Enhancements**

1. **PostgreSQL Migration:** When ready, migrate from SQLite to PostgreSQL
2. **CDN Integration:** Add CloudFlare or AWS CloudFront for global performance
3. **Mobile App:** Create React Native app using the same API
4. **Advanced Analytics:** Add user behavior tracking and content recommendations

## 📚 API Documentation

### **New Endpoints**

- `GET /api/v2/news/` - Get news with search, filtering, and pagination
- `GET /api/v2/news/categories` - Get available categories with counts
- `GET /api/v2/news/sources` - Get news sources with reliability scores
- `GET /api/v2/news/trending` - Get trending articles
- `POST /api/v2/news/refresh` - Manually trigger news refresh
- `GET /api/v2/news/search/suggestions` - Get search suggestions
- `GET /api/v2/news/article/<id>` - Get specific article with similar articles

### **Query Parameters**

- `q` - Search query
- `category` - Filter by category
- `page` - Page number (default: 1)
- `per_page` - Articles per page (default: 20, max: 50)
- `sort` - Sort by: published_at, created_at, source_reliability, ai_sentiment
- `source` - Filter by news source
- `bias` - Filter by bias: left, neutral, right

## 🎉 Congratulations!

You've successfully upgraded Public Pulse to a professional-grade, Google-style news aggregation platform! 

**Key Benefits You Now Have:**
- ⚡ **Lightning-fast performance** (no more waiting for APIs)
- 🔄 **Automatic content updates** every 6 hours
- 🎯 **Smart content deduplication** (no more duplicates)
- 📊 **Transparent bias scoring** and source reliability
- 🧠 **AI-powered analysis** and insights
- 📱 **Modern, responsive UI** that works on all devices

**Your app now feels like a real-world, professional application instead of a "project"!**

## 🤝 Need Help?

If you encounter any issues or have questions:

1. **Check the logs** in the terminal outputs
2. **Verify service status** using the health check endpoints
3. **Review this guide** for troubleshooting steps
4. **Check the code comments** for detailed explanations

Happy coding! 🚀


