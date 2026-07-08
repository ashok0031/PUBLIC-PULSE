# Public Pulse

## Overview
Public Pulse is a real-time, AI-powered trend and rating platform for government schemes, private companies, educational institutions, healthcare, sports, and entertainment. It aggregates news, reviews, and ratings from public APIs and sources, analyzes them using AI/ML models, and presents them in a modern, professional UI.

## Features
- User authentication (username/email/phone)
- Trending news and reviews from multiple sectors
- AI-driven sentiment, topic, and trend analysis
- Multilingual support
- Review and rating system
- Responsive, accessible design
- Only registered/official entities shown

## Tech Stack
- **Frontend:** React, Tailwind CSS
- **Backend:** Flask, Python, AI/ML (RoBERTa, BERTopic, KeyBERT)
- **Database:** SQLite (dev), MongoDB (optional)
- **APIs:** Reddit, YouTube, NewsAPI, data.gov.in, NIRF, TMDb, etc.

## Project Structure
```
public-pulse/
├── client/         # Frontend (React + Tailwind CSS)
├── server/         # Backend (Flask + AI/ML)
├── database/       # DB models and seed data
├── ml_models/      # Pretrained/fine-tuned models
├── data/           # Static data files
├── docs/           # Documentation
├── .env            # Environment variables
├── requirements.txt
├── package.json
└── README.md
```

## Setup
1. Clone the repo
2. Install backend dependencies: `pip install -r requirements.txt`
3. Install frontend dependencies: `cd client && npm install`
4. Set up `.env` files for secrets and API keys
5. Run backend: `python server/run.py`
6. Run frontend: `cd client && npm start`

## Contribution
- Fork the repo and create a feature branch
- Add/modify code with clear commit messages
- Ensure tests pass before PR
- See `docs/` for more

---
For more details, see the `docs/` folder. 