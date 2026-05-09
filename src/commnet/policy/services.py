from __future__ import annotations

def service_visible(cfg: dict, service_id: str) -> bool:
    service = (cfg.get('services') or {}).get(service_id, {})
    return bool(service.get('enabled') and service.get('visible_in_portal'))
