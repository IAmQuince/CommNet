from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any

PAYLOAD_CLASSES = ['text_message','emergency_alert','directory_update','device_status','route_probe']
PRIORITIES = ['low','normal','high','emergency']

@dataclass
class MessageEnvelope:
    message_id: str
    payload_class: str
    body: str
    destination: str = 'self'
    sender_node_id: str = ''
    target: str = 'self'
    priority: str = 'normal'
    privacy_class: str = 'local'
    latency_class: str = 'normal'
    payload_json: dict[str, Any] | None = None
    payload_size: int = 0
    status: str = 'created'
    expires_at: str | None = None

    @classmethod
    def create(cls, payload_class: str, body: str, destination: str = 'self', priority: str = 'normal',
               privacy_class: str = 'local', sender_node_id: str = '', target: str | None = None):
        if payload_class not in PAYLOAD_CLASSES:
            payload_class = 'text_message'
        if priority not in PRIORITIES:
            priority = 'normal'
        payload = {'body': body}
        exp = (datetime.utcnow() + timedelta(hours=24)).isoformat() + 'Z'
        return cls('msg_' + uuid.uuid4().hex[:16], payload_class, body[:4000], destination, sender_node_id,
                   target or destination, priority, privacy_class, 'normal', payload, len(body.encode('utf-8')), 'created', exp)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(**{**{'payload_json': {}}, **data})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
