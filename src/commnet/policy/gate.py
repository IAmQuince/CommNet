from __future__ import annotations

class PolicyGate:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def can_publish_service(self, service_id: str) -> bool:
        svc = (self.cfg.get('services') or {}).get(service_id, {})
        return bool(svc.get('enabled') and svc.get('visible_in_portal'))

    def can_publish_files_by_default(self) -> bool:
        return False
