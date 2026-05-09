from __future__ import annotations

import base64
from typing import Any

PREFIX = 'CMN1'
MAX_LINE = 240


def b64u(text: str) -> str:
    data = base64.urlsafe_b64encode(text.encode('utf-8')).decode('ascii')
    return data.rstrip('=')


def unb64u(data: str) -> str:
    pad = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + pad).encode('ascii')).decode('utf-8', errors='replace')


def make_ping(nonce: str) -> str:
    return f'{PREFIX}|PING|nonce={nonce}'


def make_id_request() -> str:
    return f'{PREFIX}|ID?'


def make_status_request() -> str:
    return f'{PREFIX}|STATUS?'


def make_cfg(profile: str = 'us915_test', sf: int = 7, bw: int = 125, cr: str = '45', txp: int = 10) -> str:
    return f'{PREFIX}|CFG|profile={profile}|sf={int(sf)}|bw={int(bw)}|cr={cr}|txp={int(txp)}'


def make_tx(message_id: str, payload_class: str, body: str, target: str = 'broadcast') -> str:
    line = f'{PREFIX}|TX|id={message_id}|class={payload_class}|to={target}|body={b64u(body)}'
    if len(line) > MAX_LINE:
        raise ValueError(f'Catena line too long: {len(line)} > {MAX_LINE}')
    return line


def split_cmn1_frames(raw: str) -> list[str]:
    text = (raw or '').replace('\r', '\n')
    frames: list[str] = []
    for part in text.split('\n'):
        part = part.strip()
        if not part:
            continue
        marker = PREFIX + '|'
        if part.count(marker) <= 1:
            frames.append(part)
        else:
            idxs = [i for i in range(len(part)) if part.startswith(marker, i)]
            for n, start in enumerate(idxs):
                end = idxs[n+1] if n+1 < len(idxs) else len(part)
                chunk = part[start:end].strip()
                if chunk:
                    frames.append(chunk)
    return frames


def parse_line(line: str) -> dict[str, Any]:
    raw = line.strip()
    parts = raw.split('|')
    if len(parts) < 2 or parts[0] != PREFIX:
        raise ValueError('not a CMN1 line')
    msg_type = parts[1]
    fields: dict[str, str] = {}
    for item in parts[2:]:
        if '=' in item:
            k, v = item.split('=', 1)
            fields[k] = v
    out: dict[str, Any] = {'prefix': PREFIX, 'type': msg_type, 'fields': fields, 'raw': raw}
    if 'body' in fields:
        try:
            out['body_text'] = unb64u(fields['body'])
        except Exception as exc:
            out['body_error'] = str(exc)
    return out


def expected_response_types(command_line: str) -> set[str]:
    try:
        parsed = parse_line(command_line)
        t = parsed.get('type')
    except Exception:
        return {'ACK', 'ERR'}
    if t == 'PING': return {'PONG', 'ERR'}
    if t == 'ID?': return {'ID', 'ERR'}
    if t == 'STATUS?': return {'STATUS', 'ERR'}
    if t in {'CFG', 'TX'}: return {'ACK', 'ERR'}
    return {'ACK', 'ERR'}


def delivery_semantics(parsed: dict[str, Any]) -> str:
    t = parsed.get('type')
    if t == 'ACK':
        status = (parsed.get('fields') or {}).get('status', '')
        if status == 'tx_started': return 'local_rf_tx_started'
        if status == 'tx_done': return 'local_rf_tx_done'
        return 'local_hardware_ack_only'
    if t == 'RX': return 'inbound_rf_message'
    if t == 'REMOTE_ACK': return 'remote_delivery_confirmed'
    if t == 'ERR': return 'hardware_error'
    return 'status_or_control'
