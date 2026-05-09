from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from commnet.transport.base import AdapterStatus, DeliveryResult, RouteEstimate, TransportAdapter, TransportCapabilities

class LanHttpAdapter(TransportAdapter):
    adapter_id = 'lan_http'
    display_name = 'LAN/Wi-Fi HTTP Peer'
    def __init__(self, peer_store=None, timeout=2.0):
        self.peer_store = peer_store
        self.timeout = timeout
    def probe(self):
        return AdapterStatus(self.adapter_id, self.display_name, 'implemented_manual_peers', True, True, False, True, True,
                             payload_limit=16000, latency_class='low', bandwidth_class='medium', notes='Manual peer handshake and small JSON message delivery implemented')
    def capabilities(self):
        return TransportCapabilities(direct=True, broadcast=False, bundle=False, emergency=True, max_payload=16000)
    def estimate(self, message):
        peer_id = message.destination
        allowed = bool(peer_id and peer_id.startswith('peer_'))
        return RouteEstimate(self.adapter_id, allowed, 60 if allowed else -80, 'manual peer route' if allowed else 'destination is not a peer')
    def handshake(self, peer: dict):
        url = peer['base_url'].rstrip('/') + '/api/node/hello'
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return True, {'url': url, 'response': data}
        except Exception as exc:
            return False, {'url': url, 'error': type(exc).__name__ + ': ' + str(exc)}
    def send(self, message):
        if self.peer_store is None:
            return DeliveryResult(message.message_id, self.adapter_id, False, 'failed', 'No peer store attached')
        peer = self.peer_store.get(message.destination)
        if not peer:
            return DeliveryResult(message.message_id, self.adapter_id, False, 'failed', 'Peer not found', message.destination)
        if peer.get('trust_state') == 'blocked':
            return DeliveryResult(message.message_id, self.adapter_id, False, 'policy_blocked', 'Peer is blocked', peer.get('peer_id'))
        payload = json.dumps({'message': message.to_dict()}).encode('utf-8')
        if len(payload) > 16000:
            return DeliveryResult(message.message_id, self.adapter_id, False, 'failed', 'Payload too large for LAN test adapter', peer.get('peer_id'))
        req = urllib.request.Request(peer['base_url'].rstrip() + '/api/node/receive', data=payload, method='POST', headers={'Content-Type':'application/json'})
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode('utf-8')
            return DeliveryResult(message.message_id, self.adapter_id, True, 'delivered', text[:500], peer.get('peer_id'), int((time.time()-start)*1000))
        except Exception as exc:
            return DeliveryResult(message.message_id, self.adapter_id, False, 'failed', type(exc).__name__ + ': ' + str(exc), peer.get('peer_id'), int((time.time()-start)*1000))
