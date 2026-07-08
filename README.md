# PUBLIC-PULSE

Public Pulse is a Python project for **AI-integrated sentiment analysis and trend analysis** using:

- NLP with **HuggingFace**
- **BERT** and **RoBERTa** sentiment models
- **scikit-learn** trend modeling
- **REST APIs** for integration

## Features

- `POST /api/v1/sentiment` for sentiment analysis
- `POST /api/v1/trends` for sentiment trend analysis
- `GET /health` for service health checks
- Graceful fallback logic when ML runtime dependencies are unavailable

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run API:

```bash
python -c "from public_pulse import create_app; create_app().run(host='0.0.0.0', port=8000)"
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Example requests

Sentiment:

```bash
curl -X POST http://localhost:8000/api/v1/sentiment \
  -H 'Content-Type: application/json' \
  -d '{"text":"People are happy with the new policy", "model":"roberta"}'
```

Trend analysis:

```bash
curl -X POST http://localhost:8000/api/v1/trends \
  -H 'Content-Type: application/json' \
  -d '{
    "events": [
      {"timestamp":"2026-01-01T00:00:00", "score":0.25, "text":"public reaction low"},
      {"timestamp":"2026-01-01T01:00:00", "score":0.50, "text":"public reaction improving"},
      {"timestamp":"2026-01-01T02:00:00", "score":0.72, "text":"public reaction positive"}
    ]
  }'
```
