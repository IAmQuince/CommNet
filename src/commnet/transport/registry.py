from __future__ import annotations

from commnet.transport.adapters_loopback import LocalLoopbackAdapter
from commnet.transport.adapters_lan import LanHttpAdapter
from commnet.transport.adapters_declared import (
    BluetoothBleAdapter, DroneMuleAdapter, GenericSerialAdapter,
    LxmfAdapter, MeshtasticBleAdapter, MeshtasticMqttAdapter, MeshtasticSerialAdapter,
    MeshtasticTcpAdapter, PhoneCacheAdapter, RemovableMediaAdapter, ReticulumAdapter,
    StorageNodeAdapter,
)

class AdapterRegistry:
    def __init__(self, adapters): self.adapters=list(adapters)
    def statuses(self): return [a.probe().to_dict() for a in self.adapters]
    def available(self): return [a for a in self.adapters if a.probe().available]
    def get(self, adapter_id: str):
        for a in self.adapters:
            if a.adapter_id == adapter_id: return a
        raise KeyError(adapter_id)

def build_default_registry(peer_store=None) -> AdapterRegistry:
    return AdapterRegistry([
        LocalLoopbackAdapter(), LanHttpAdapter(peer_store),
        MeshtasticSerialAdapter(), MeshtasticTcpAdapter(), MeshtasticBleAdapter(), MeshtasticMqttAdapter(),
        ReticulumAdapter(), LxmfAdapter(), BluetoothBleAdapter(), GenericSerialAdapter(),
        StorageNodeAdapter(), RemovableMediaAdapter(), PhoneCacheAdapter(), DroneMuleAdapter(),
    ])
