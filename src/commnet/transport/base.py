from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class AdapterStatus:
    adapter_id: str
    display_name: str
    state: str
    installed: bool
    configured: bool
    hardware_present: bool
    available: bool
    healthy: bool
    queue_depth: int = 0
    payload_limit: int = 1024
    latency_class: str = 'unknown'
    bandwidth_class: str = 'unknown'
    last_error: str = ''
    notes: str = ''
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class TransportCapabilities:
    direct: bool = False
    broadcast: bool = False
    bundle: bool = False
    emergency: bool = False
    max_payload: int = 1024
    def to_dict(self): return asdict(self)

@dataclass
class RouteEstimate:
    adapter_id: str
    allowed: bool
    score: int
    reason: str
    def to_dict(self): return asdict(self)

@dataclass
class DeliveryResult:
    message_id: str
    adapter_id: str
    success: bool
    status: str
    detail: str
    peer_id: str | None = None
    latency_ms: int | None = None
    def to_dict(self): return asdict(self)

class TransportAdapter:
    adapter_id = 'base'
    display_name = 'Base Adapter'
    def probe(self) -> AdapterStatus:
        return AdapterStatus(self.adapter_id, self.display_name, 'declared', False, False, False, False, False, notes='Base adapter')
    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities()
    def estimate(self, message) -> RouteEstimate:
        st = self.probe()
        return RouteEstimate(self.adapter_id, bool(st.available), 0 if st.available else -1000, st.notes)
    def send(self, message) -> DeliveryResult:
        return DeliveryResult(message.message_id, self.adapter_id, False, 'not_implemented', 'Adapter is declared but not implemented')
    def receive(self): return []
    def health(self): return self.probe()
    def shutdown(self): pass
