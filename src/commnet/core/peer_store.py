from __future__ import annotations

import json
import uuid
from urllib.parse import urlparse
from typing import Any

PEER_TRUST_STATES = ['untrusted', 'known', 'trusted', 'blocked', 'self']

def validate_url(url: str) -> str:
    url = (url or '').strip().rstrip('/')
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('Peer URL must start with http:// or https://')
    if not parsed.netloc:
        raise ValueError('Peer URL must include a host and optional port')
    return url

class PeerStore:
    def __init__(self, store, audit_logger=None):
        self.store = store
        self.audit = audit_logger
        self.store.initialize()

    def add(self, display_name: str, base_url: str, trust_state: str = 'known', notes: str = '') -> str:
        display_name = (display_name or 'Unnamed Peer').strip()[:64]
        base_url = validate_url(base_url)
        if trust_state not in PEER_TRUST_STATES:
            trust_state = 'known'
        peer_id = 'peer_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('INSERT INTO peers(peer_id, display_name, base_url, trust_state, notes) VALUES (?, ?, ?, ?, ?)',
                         (peer_id, display_name, base_url, trust_state, (notes or '')[:500]))
            conn.commit()
        if self.audit:
            self.audit.write('peer_added', {'peer_id': peer_id, 'base_url': base_url, 'trust_state': trust_state})
        return peer_id

    def delete(self, peer_id: str) -> None:
        with self.store.connect() as conn:
            conn.execute('DELETE FROM peers WHERE peer_id=?', (peer_id,))
            conn.commit()
        if self.audit:
            self.audit.write('peer_removed', {'peer_id': peer_id})

    def set_trust(self, peer_id: str, trust_state: str) -> None:
        if trust_state not in PEER_TRUST_STATES:
            raise ValueError('Invalid trust state')
        with self.store.connect() as conn:
            conn.execute('UPDATE peers SET trust_state=?, updated_at=CURRENT_TIMESTAMP WHERE peer_id=?', (trust_state, peer_id))
            conn.commit()
        if self.audit:
            self.audit.write('peer_trust_updated', {'peer_id': peer_id, 'trust_state': trust_state})

    def get(self, peer_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute('SELECT * FROM peers WHERE peer_id=?', (peer_id,)).fetchone()
        return dict(row) if row else None

    def list(self) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('SELECT * FROM peers ORDER BY updated_at DESC, created_at DESC').fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            try:
                d['last_handshake'] = json.loads(d.get('last_handshake_json') or '{}')
            except Exception:
                d['last_handshake'] = {}
            out.append(d)
        return out

    def record_handshake(self, peer_id: str, result: str, details: dict[str, Any]) -> None:
        handshake_id = 'hs_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('INSERT INTO peer_handshakes(handshake_id, peer_id, result, details_json) VALUES (?, ?, ?, ?)',
                         (handshake_id, peer_id, result, json.dumps(details, sort_keys=True)))
            if result == 'ok':
                conn.execute('UPDATE peers SET last_seen_at=CURRENT_TIMESTAMP, last_status=?, last_handshake_json=?, updated_at=CURRENT_TIMESTAMP WHERE peer_id=?',
                             (result, json.dumps(details, sort_keys=True), peer_id))
            else:
                conn.execute('UPDATE peers SET last_status=?, last_handshake_json=?, updated_at=CURRENT_TIMESTAMP WHERE peer_id=?',
                             (result, json.dumps(details, sort_keys=True), peer_id))
            conn.commit()
        if self.audit:
            self.audit.write('peer_handshake', {'peer_id': peer_id, 'result': result, 'details': details})
