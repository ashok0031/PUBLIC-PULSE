import unittest

from public_pulse.sentiment import SentimentAnalyzer
from public_pulse.trends import TrendAnalyzer


class SentimentAnalyzerTests(unittest.TestCase):
    def test_fallback_sentiment_positive(self) -> None:
        analyzer = SentimentAnalyzer()
        analyzer._pipelines = {"bert": None, "roberta": None}

        result = analyzer.analyze("I love this great product", model="bert")

        self.assertEqual(result.label, "POSITIVE")
        self.assertEqual(result.model, "bert-fallback")

    def test_invalid_model_rejected(self) -> None:
        analyzer = SentimentAnalyzer()
        analyzer._pipelines = {"bert": None, "roberta": None}

        with self.assertRaises(ValueError):
            analyzer.analyze("hello", model="xlnet")


class TrendAnalyzerTests(unittest.TestCase):
    def test_trend_direction_upward(self) -> None:
        analyzer = TrendAnalyzer()
        events = [
            {"timestamp": "2026-01-01T00:00:00", "score": 0.1, "text": "public reaction is low"},
            {"timestamp": "2026-01-01T02:00:00", "score": 0.5, "text": "public reaction improves"},
            {"timestamp": "2026-01-01T04:00:00", "score": 0.8, "text": "public reaction is great"},
        ]

        result = analyzer.analyze(events)

        self.assertEqual(result.direction, "upward")
        self.assertGreater(result.slope, 0)
        self.assertIn("public", result.top_terms)

    def test_requires_two_events(self) -> None:
        analyzer = TrendAnalyzer()

        with self.assertRaises(ValueError):
            analyzer.analyze([{"timestamp": "2026-01-01T00:00:00", "score": 0.5, "text": "only one"}])


if __name__ == "__main__":
    unittest.main()
