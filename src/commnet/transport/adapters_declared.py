from __future__ import annotations

import importlib.util
from commnet.transport.base import AdapterStatus, TransportAdapter

class DeclaredAdapter(TransportAdapter):
    required_imports: list[str] = []
    package_note: str = 'specified for future implementation'
    def probe(self):
        missing = [name for name in self.required_imports if importlib.util.find_spec(name.split('.')[0]) is None]
        installed = not missing
        state = 'dependency_missing' if missing else 'installed_not_configured'
        return AdapterStatus(self.adapter_id, self.display_name, state, installed, False, False, False, False,
                             payload_limit=0, latency_class='unknown', bandwidth_class='unknown',
                             last_error=', '.join(missing), notes=self.package_note)

class MeshtasticSerialAdapter(DeclaredAdapter):
    adapter_id='meshtastic_serial'; display_name='Meshtastic Serial'; required_imports=['meshtastic','serial']; package_note='First-class LoRa profile; hardware messaging deferred.'
class MeshtasticTcpAdapter(DeclaredAdapter):
    adapter_id='meshtastic_tcp'; display_name='Meshtastic TCP'; required_imports=['meshtastic']; package_note='First-class Meshtastic TCP profile; deferred.'
class MeshtasticBleAdapter(DeclaredAdapter):
    adapter_id='meshtastic_ble'; display_name='Meshtastic BLE'; required_imports=['meshtastic','bleak']; package_note='BLE profile; dependency/hardware-sensitive and deferred.'
class MeshtasticMqttAdapter(DeclaredAdapter):
    adapter_id='meshtastic_mqtt'; display_name='Meshtastic MQTT'; required_imports=['meshtastic','paho.mqtt.client']; package_note='MQTT bridge profile; deferred.'
class ReticulumAdapter(DeclaredAdapter):
    adapter_id='reticulum_rns'; display_name='Reticulum RNS'; required_imports=['RNS']; package_note='First-class resilient backbone profile; deferred.'
class LxmfAdapter(DeclaredAdapter):
    adapter_id='reticulum_lxmf'; display_name='LXMF Messaging'; required_imports=['LXMF','RNS']; package_note='Reticulum messaging profile; deferred.'
class BluetoothBleAdapter(DeclaredAdapter):
    adapter_id='bluetooth_ble'; display_name='Bluetooth BLE'; required_imports=['bleak']; package_note='Optional Bluetooth profile; deferred.'
class GenericSerialAdapter(DeclaredAdapter):
    adapter_id='generic_serial'; display_name='Generic Serial'; required_imports=['serial']; package_note='Serial/radio profile; deferred.'
class StorageNodeAdapter(DeclaredAdapter):
    adapter_id='storage_node'; display_name='Storage Node'; required_imports=[]; package_note='Custody/cache adapter specified; not implemented.'
class RemovableMediaAdapter(DeclaredAdapter):
    adapter_id='removable_media'; display_name='Removable Media'; required_imports=[]; package_note='USB/store-carry-forward specified; not implemented.'
class PhoneCacheAdapter(DeclaredAdapter):
    adapter_id='phone_cache'; display_name='Phone Cache'; required_imports=[]; package_note='Mobile cache concept specified; simulated later.'
class DroneMuleAdapter(DeclaredAdapter):
    adapter_id='drone_mule'; display_name='Drone/Data Mule'; required_imports=[]; package_note='Future carrier concept specified; simulated later.'
