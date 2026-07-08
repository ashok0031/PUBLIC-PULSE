from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SentimentResult:
    label: str
    score: float
    model: str


class SentimentAnalyzer:
    """AI-integrated sentiment analysis with HuggingFace BERT and RoBERTa support."""

    BERT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
    ROBERTA_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __init__(self) -> None:
        self._pipelines: Dict[str, object] = {}
        self._load_pipeline("bert", self.BERT_MODEL)
        self._load_pipeline("roberta", self.ROBERTA_MODEL)

    def _load_pipeline(self, alias: str, model_name: str) -> None:
        try:
            from transformers import pipeline

            self._pipelines[alias] = pipeline("sentiment-analysis", model=model_name)
        except Exception:
            # Keep runtime resilient when transformers/models are unavailable.
            self._pipelines[alias] = None

    def analyze(self, text: str, model: str = "roberta") -> SentimentResult:
        if not text or not text.strip():
            raise ValueError("text must be a non-empty string")

        model_alias = model.lower()
        if model_alias not in self._pipelines:
            raise ValueError("model must be either 'bert' or 'roberta'")

        pipeline_obj = self._pipelines[model_alias]
        if pipeline_obj is None:
            return self._fallback_sentiment(text, model_alias)

        raw: List[Dict[str, object]] = pipeline_obj(text)
        top = raw[0]
        label = str(top.get("label", "NEUTRAL")).upper()
        score = float(top.get("score", 0.0))

        return SentimentResult(label=label, score=score, model=model_alias)

    def _fallback_sentiment(self, text: str, model_alias: str) -> SentimentResult:
        lowered = text.lower()
        positive_words = {"good", "great", "love", "excellent", "happy", "awesome", "win"}
        negative_words = {"bad", "terrible", "hate", "awful", "sad", "angry", "loss"}

        positive_hits = sum(word in lowered for word in positive_words)
        negative_hits = sum(word in lowered for word in negative_words)

        if positive_hits > negative_hits:
            label = "POSITIVE"
            score = 0.75
        elif negative_hits > positive_hits:
            label = "NEGATIVE"
            score = 0.75
        else:
            label = "NEUTRAL"
            score = 0.5

        return SentimentResult(label=label, score=score, model=f"{model_alias}-fallback")
