from __future__ import annotations

from commnet.transport.base import AdapterStatus, DeliveryResult, RouteEstimate, TransportAdapter, TransportCapabilities

class LocalLoopbackAdapter(TransportAdapter):
    adapter_id = 'local_loopback'
    display_name = 'Local Loopback'
    def probe(self):
        return AdapterStatus(self.adapter_id, self.display_name, 'available', True, True, True, True, True,
                             payload_limit=4096, latency_class='very_low', bandwidth_class='local', notes='Working local self-test adapter')
    def capabilities(self):
        return TransportCapabilities(direct=True, broadcast=False, bundle=False, emergency=True, max_payload=4096)
    def estimate(self, message):
        allowed = message.destination in {'self','local','loopback'} or message.target in {'self','local','loopback'}
        return RouteEstimate(self.adapter_id, allowed, 100 if allowed else -100, 'self/local destination' if allowed else 'not addressed to local node')
    def send(self, message):
        message.status = 'delivered'
        return DeliveryResult(message.message_id, self.adapter_id, True, 'delivered', 'Delivered through local loopback')
