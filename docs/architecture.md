# Public Pulse Architecture

## Overview
- **Frontend:** React + Tailwind CSS
- **Backend:** Flask (Python) + AI/ML models
- **Database:** SQLite (dev), MongoDB (optional)
- **APIs:** Reddit, YouTube, NewsAPI, data.gov.in, NIRF, TMDb, etc.

## Data Flow
1. User interacts with React frontend
2. Frontend calls Flask backend APIs
3. Backend fetches data from external APIs or database
4. AI/ML models analyze text for sentiment, topics, keywords
5. Results are stored/cached in DB and sent to frontend
6. Frontend displays news, reviews, ratings, trends

## Key Modules
- **Authentication** (JWT/session)
- **News/Review Scraper**
- **Entity Registry**
- **AI/ML Analysis**
- **Trend Calculation**
- **User Reviews**
- **Multilingual Support** 