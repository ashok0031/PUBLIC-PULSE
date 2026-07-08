from __future__ import annotations

from typing import Any, Dict, List

from .sentiment import SentimentAnalyzer
from .trends import TrendAnalyzer


def create_app() -> Any:
    try:
        from flask import Flask, jsonify, request
    except Exception as exc:
        raise RuntimeError("Flask is required to run the REST API") from exc

    app = Flask(__name__)
    sentiment_analyzer = SentimentAnalyzer()
    trend_analyzer = TrendAnalyzer()

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/api/v1/sentiment")
    def sentiment() -> Any:
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        text = payload.get("text", "")
        model = payload.get("model", "roberta")

        try:
            result = sentiment_analyzer.analyze(str(text), model=str(model))
        except ValueError:
            return jsonify({"error": "invalid sentiment request payload"}), 400

        return jsonify({"label": result.label, "score": result.score, "model": result.model})

    @app.post("/api/v1/trends")
    def trends() -> Any:
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        events = payload.get("events", [])

        if not isinstance(events, list):
            return jsonify({"error": "events must be a list"}), 400

        try:
            result = trend_analyzer.analyze(events)
        except (ValueError, KeyError):
            return jsonify({"error": "invalid trend request payload"}), 400

        return jsonify(
            {
                "slope": result.slope,
                "direction": result.direction,
                "top_terms": result.top_terms,
            }
        )

    return app
