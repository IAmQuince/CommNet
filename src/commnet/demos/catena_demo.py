from __future__ import annotations

import uuid
from typing import Any

from commnet.transport.adapters_catena import CatenaSerialLoRaAdapter


def make_adapter_from_config(cfg: dict[str, Any]) -> CatenaSerialLoRaAdapter:
    mode = cfg.get('catena_demo_mode', 'fake_until_configured')
    fake = mode != 'real_serial'
    return CatenaSerialLoRaAdapter(
        port=cfg.get('catena_com_port', ''),
        baud=int(cfg.get('catena_baud_rate', 115200)),
        fake=fake,
        timeout=float(cfg.get('catena_ack_timeout_ms', 3000)) / 1000.0,
    )


def run_action(cfg: dict[str, Any], action: str, body: str = 'Hello from CommNet') -> dict[str, Any]:
    adapter = make_adapter_from_config(cfg)
    if action == 'ping':
        return adapter.ping(uuid.uuid4().hex[:8])
    if action == 'id':
        return adapter.identify()
    if action == 'status':
        return adapter.status_request()
    if action == 'cfg':
        return adapter.configure_radio('us915_test', 7, 125, '45', 10)
    if action == 'tx':
        return adapter.send_text('cat_' + uuid.uuid4().hex[:10], 'text_message', body)
    return {'ok': False, 'error': 'unknown Catena action'}
