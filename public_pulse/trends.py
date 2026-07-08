from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List


@dataclass
class TrendResult:
    slope: float
    direction: str
    top_terms: List[str]


class TrendAnalyzer:
    """Trend analysis over timestamped sentiment events using scikit-learn."""

    def analyze(self, events: Iterable[Dict[str, object]]) -> TrendResult:
        event_list = list(events)
        if len(event_list) < 2:
            raise ValueError("at least two events are required for trend analysis")

        points = self._build_points(event_list)
        slope = self._linear_slope(points)

        if slope > 0.02:
            direction = "upward"
        elif slope < -0.02:
            direction = "downward"
        else:
            direction = "stable"

        top_terms = self._top_terms(event_list)
        return TrendResult(slope=slope, direction=direction, top_terms=top_terms)

    def _build_points(self, events: List[Dict[str, object]]) -> List[tuple[float, float]]:
        sorted_events = sorted(events, key=lambda e: str(e["timestamp"]))

        base_time = datetime.fromisoformat(str(sorted_events[0]["timestamp"]))
        points: List[tuple[float, float]] = []
        for event in sorted_events:
            current = datetime.fromisoformat(str(event["timestamp"]))
            delta_hours = (current - base_time).total_seconds() / 3600.0
            points.append((delta_hours, float(event["score"])))
        return points

    def _linear_slope(self, points: List[tuple[float, float]]) -> float:
        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np

            x = np.array([p[0] for p in points]).reshape(-1, 1)
            y = np.array([p[1] for p in points])
            model = LinearRegression().fit(x, y)
            return float(model.coef_[0])
        except Exception:
            first_x, first_y = points[0]
            last_x, last_y = points[-1]
            if last_x == first_x:
                return 0.0
            return (last_y - first_y) / (last_x - first_x)

    def _top_terms(self, events: List[Dict[str, object]]) -> List[str]:
        tokens: List[str] = []
        for event in events:
            text = str(event.get("text", "")).lower()
            tokens.extend([word.strip(".,!?;:()[]{}\"'") for word in text.split() if len(word) > 3])

        common = Counter(token for token in tokens if token).most_common(5)
        return [token for token, _ in common]
