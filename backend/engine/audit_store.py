"""Small, deterministic audit trail for the prototype's route decisions."""
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List


class RouteAuditStore:
    def __init__(self, limit: int = 100):
        self._events = deque(maxlen=limit)

    def record(self, result: Dict[str, Any]) -> None:
        for recommendation in result.get("recommendations", []):
            self._events.appendleft({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "origin": result["origin"],
                "destination": result["destination"],
                "scenario": result.get("active_scenario") or "Normal operations",
                "persona": recommendation["persona"],
                "eta_hours": recommendation["adjusted_eta"],
                "p85_hours": recommendation["confidence_band"]["p85_hours"],
                "risk": recommendation["threat_level"],
                "cost_usd": recommendation["total_cost"],
            })

    def recent(self) -> List[Dict[str, Any]]:
        return list(self._events)
