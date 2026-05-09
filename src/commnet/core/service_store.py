from __future__ import annotations

from commnet.core.config_schema import SERVICE_IDS, SERVICE_LABELS


def portal_services(cfg: dict) -> list[dict]:
    services = cfg.get('services') or {}
    out = []
    for sid in SERVICE_IDS:
        data = services.get(sid, {})
        if data.get('enabled') and data.get('visible_in_portal'):
            out.append({'service_id': sid, 'label': SERVICE_LABELS.get(sid, sid), **data})
    return out


def sync_services_to_db(store, cfg: dict) -> None:
    store.upsert_services(cfg.get('services') or {})
