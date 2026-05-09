from __future__ import annotations

import importlib.metadata
import importlib.util
from typing import Any

DEPENDENCY_CHECKS = [
    {'dependency_id': 'meshtastic', 'package_name': 'meshtastic', 'import_name': 'meshtastic', 'profile': 'meshtastic_lora'},
    {'dependency_id': 'pyserial', 'package_name': 'pyserial', 'import_name': 'serial', 'profile': 'serial_lora'},
    {'dependency_id': 'paho_mqtt', 'package_name': 'paho-mqtt', 'import_name': 'paho.mqtt.client', 'profile': 'meshtastic_mqtt'},
    {'dependency_id': 'rns', 'package_name': 'rns', 'import_name': 'RNS', 'profile': 'reticulum'},
    {'dependency_id': 'lxmf', 'package_name': 'lxmf', 'import_name': 'LXMF', 'profile': 'reticulum_lxmf'},
    {'dependency_id': 'bleak', 'package_name': 'bleak', 'import_name': 'bleak', 'profile': 'bluetooth'},
    {'dependency_id': 'zeroconf', 'package_name': 'zeroconf', 'import_name': 'zeroconf', 'profile': 'lan_discovery'},
    {'dependency_id': 'psutil', 'package_name': 'psutil', 'import_name': 'psutil', 'profile': 'diagnostics'},
    {'dependency_id': 'waitress', 'package_name': 'waitress', 'import_name': 'waitress', 'profile': 'server'},
]

def _version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except Exception:
        return None

def check_dependency(item: dict[str, str]) -> dict[str, Any]:
    import_name = item['import_name']
    installed = importlib.util.find_spec(import_name.split('.')[0]) is not None
    return {**item, 'installed': bool(installed), 'version': _version(item['package_name']) if installed else None,
            'notes': 'installed' if installed else 'not installed; feature remains unavailable but UI should still launch'}

def check_all_dependencies(store=None) -> list[dict[str, Any]]:
    results = [check_dependency(x) for x in DEPENDENCY_CHECKS]
    if store is not None:
        for r in results:
            store.record_dependency(r['import_name'], r['package_name'], r['installed'], r.get('version'), r.get('notes',''))
    return results
