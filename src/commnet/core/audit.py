from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class AuditLogger:
    def __init__(self, paths, store=None):
        self.paths = paths
        self.store = store
        self.path = paths.logs / 'audit.jsonl'

    def write(self, event_type: str, details: dict[str, Any] | None = None) -> None:
        self.paths.ensure_all()
        event = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'details': details or {},
        }
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, sort_keys=True) + '\n')
        if self.store is not None:
            try:
                self.store.insert_audit(event_type, details or {})
            except Exception:
                # Audit logging to file must remain resilient even if SQLite has a problem.
                pass
