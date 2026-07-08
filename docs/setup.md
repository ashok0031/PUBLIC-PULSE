# Setup Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- npm
- Git

## Backend Setup
1. `cd server`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in secrets
4. `python run.py`

## Frontend Setup
1. `cd client`
2. `npm install`
3. `npm start`

## Running Tests
- Backend: `pytest server/app/tests/`
- Frontend: `npm test` in `client/` 