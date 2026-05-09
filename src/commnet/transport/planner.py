from __future__ import annotations

class RoutePlanner:
    def __init__(self, registry): self.registry=registry
    def choose_route(self, message):
        estimates=[a.estimate(message) for a in self.registry.adapters]
        candidates=[e for e in estimates if e.allowed]
        candidates.sort(key=lambda e: (-e.score, e.adapter_id))
        chosen=candidates[0] if candidates else None
        return chosen, estimates
    def decision_dict(self, message):
        chosen, estimates = self.choose_route(message)
        return {
            'message_id': message.message_id,
            'chosen_adapter': None if chosen is None else chosen.adapter_id,
            'candidates': [e.to_dict() for e in estimates if e.allowed],
            'rejected': [e.to_dict() for e in estimates if not e.allowed],
            'reason': 'deterministic score order' if chosen else 'no available route',
        }
