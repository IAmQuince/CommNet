from __future__ import annotations

from commnet.transport.base import DeliveryResult
from commnet.transport.planner import RoutePlanner

class DeliveryEngine:
    def __init__(self, registry, audit_logger=None, store=None):
        self.registry = registry
        self.audit = audit_logger
        self.store = store
        self.planner = RoutePlanner(registry)
    def send(self, message) -> DeliveryResult:
        message.status='queued'
        if self.store: self.store.insert_message(message)
        chosen, estimates = self.planner.choose_route(message)
        rejected=[e.to_dict() for e in estimates if (chosen is None or e.adapter_id != chosen.adapter_id)]
        score={'estimates':[e.to_dict() for e in estimates]}
        if self.store:
            self.store.insert_route_decision(message.message_id, None if chosen is None else chosen.adapter_id, score, rejected,
                                             'deterministic route choice' if chosen else 'no allowed route')
        if self.audit:
            self.audit.write('route_decision', {'message_id': message.message_id, 'chosen': None if chosen is None else chosen.to_dict(), 'estimates':[e.to_dict() for e in estimates]})
        if chosen is None:
            message.status='deferred'
            if self.store: self.store.update_message_status(message.message_id, 'deferred')
            result=DeliveryResult(message.message_id,'none',False,'deferred','No available allowed route; message deferred')
            if self.store: self.store.insert_delivery_attempt(message.message_id,'none',False,result.to_dict())
            return result
        adapter=self.registry.get(chosen.adapter_id)
        message.status='attempting'
        if self.store: self.store.update_message_status(message.message_id, 'attempting')
        result=adapter.send(message)
        if self.store:
            self.store.update_message_status(message.message_id, result.status)
            self.store.insert_delivery_attempt(message.message_id, adapter.adapter_id, result.success, result.to_dict(), result.peer_id, result.latency_ms)
        if self.audit: self.audit.write('delivery_attempt', result.to_dict())
        return result
