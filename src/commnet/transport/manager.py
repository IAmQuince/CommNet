from __future__ import annotations
from commnet.core.peer_store import PeerStore
from commnet.transport.engine import DeliveryEngine
from commnet.transport.registry import build_default_registry

class TransportManager:
    def __init__(self, store, audit_logger=None):
        self.peer_store = PeerStore(store, audit_logger)
        self.registry = build_default_registry(self.peer_store)
        self.engine = DeliveryEngine(self.registry, audit_logger, store)
    def statuses(self): return self.registry.statuses()
    def send(self, message): return self.engine.send(message)
