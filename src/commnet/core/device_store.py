from __future__ import annotations

from commnet.core.config_schema import DEVICE_TYPES, TRUST_STATES, TRANSPORT_PROFILES
from commnet.core.config_validation import validate_multi_choice, validate_text, validate_choice


class DeviceStore:
    def __init__(self, store, audit=None):
        self.store = store
        self.audit = audit

    def add(self, display_name: str, device_type: str, trust_state: str, notes: str = '', desired_transports: list[str] | None = None) -> str:
        name, errors = validate_text('display_name', display_name, 'device_name')
        dtype, e = validate_choice('device_type', device_type, DEVICE_TYPES); errors += e
        trust, e = validate_choice('trust_state', trust_state, TRUST_STATES); errors += e
        notes, e = validate_text('notes', notes, 'device_notes'); errors += e
        transports, e = validate_multi_choice('desired_transports', desired_transports or [], TRANSPORT_PROFILES); errors += e
        if errors:
            raise ValueError('; '.join(errors))
        device_id = self.store.add_device(name, dtype, trust, notes, transports)
        if self.audit:
            self.audit.write('device_added', {'device_id': device_id, 'display_name': name, 'device_type': dtype, 'trust_state': trust})
        return device_id

    def delete(self, device_id: str) -> None:
        self.store.delete_device(device_id)
        if self.audit:
            self.audit.write('device_deleted', {'device_id': device_id})

    def list(self):
        return self.store.list_devices()
