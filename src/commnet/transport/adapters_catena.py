from __future__ import annotations

import importlib.util
import time
from typing import Any

from commnet.hardware.catena_protocol import (
    make_ping, make_id_request, make_status_request, make_cfg, make_tx,
    parse_line, delivery_semantics, expected_response_types, split_cmn1_frames,
)
from commnet.transport.fake_serial import FakeCatenaSerial


class CatenaSerialLoRaAdapter:
    adapter_id = 'catena_serial_lora'
    display_name = 'Catena USB Serial LoRa'

    def __init__(self, port: str = '', baud: int = 115200, fake: bool = True, timeout: float = 3.0):
        self.port = port
        self.baud = int(baud or 115200)
        self.fake = bool(fake)
        self.timeout = float(timeout or 3.0)
        self._fake_dev = FakeCatenaSerial()

    def dependency_status(self) -> dict[str, Any]:
        spec = importlib.util.find_spec('serial')
        return {'package': 'pyserial', 'import_name': 'serial', 'installed': bool(spec), 'required_for_real_hardware': True}

    def status(self) -> dict[str, Any]:
        dep = self.dependency_status()
        return {
            'adapter_id': self.adapter_id,
            'display_name': self.display_name,
            'available': self.fake or dep['installed'],
            'mode': 'fake' if self.fake else 'serial',
            'port': self.port,
            'baud': self.baud,
            'dependency': dep,
            'delivery_semantics': 'ACK means local hardware accepted command; remote RF delivery requires RX/REMOTE_ACK.',
        }

    def _matches_expected(self, sent_line: str, parsed: dict[str, Any]) -> bool:
        if parsed.get('type') not in expected_response_types(sent_line):
            return False
        try:
            sent = parse_line(sent_line)
        except Exception:
            return True
        sent_type = sent.get('type')
        if sent_type in {'TX'} and parsed.get('type') == 'ACK':
            sent_id = (sent.get('fields') or {}).get('id')
            ack_id = (parsed.get('fields') or {}).get('id')
            return not sent_id or not ack_id or sent_id == ack_id
        return True

    def _transact_real(self, line: str) -> dict[str, Any]:
        if importlib.util.find_spec('serial') is None:
            raise RuntimeError('pyserial is not installed')
        if not self.port:
            raise RuntimeError('Catena COM port is not configured')
        import serial  # type: ignore
        transcript: list[dict[str, Any]] = []
        deadline = time.time() + self.timeout
        with serial.Serial(self.port, self.baud, timeout=0.25, write_timeout=self.timeout) as ser:
            try:
                ser.reset_input_buffer()
            except Exception:
                pass
            ser.write((line.strip() + '\n').encode('utf-8'))
            ser.flush()
            while time.time() < deadline:
                raw_bytes = ser.readline()
                if not raw_bytes:
                    continue
                raw_text = raw_bytes.decode('utf-8', errors='replace')
                for frame in split_cmn1_frames(raw_text):
                    item = {'raw': frame}
                    try:
                        parsed = parse_line(frame)
                        item['parsed'] = parsed
                        item['type'] = parsed.get('type')
                        transcript.append(item)
                        if self._matches_expected(line, parsed):
                            return {'raw': frame, 'parsed': parsed, 'transcript': transcript}
                    except Exception as exc:
                        item['error'] = str(exc)
                        transcript.append(item)
            raise TimeoutError('no matching Catena response before timeout; transcript=' + repr(transcript[-5:]))

    def transact(self, line: str) -> dict[str, Any]:
        started = time.time()
        try:
            if self.fake:
                raw = self._fake_dev.transact(line, self.timeout)
                parsed = parse_line(raw)
                payload = {'raw': raw, 'parsed': parsed, 'transcript': [{'raw': raw, 'parsed': parsed, 'type': parsed.get('type')}]}
            else:
                payload = self._transact_real(line)
                raw = payload['raw']
                parsed = payload['parsed']
            return {
                'ok': True, 'sent': line, 'received': raw, 'parsed': parsed,
                'transcript': payload.get('transcript', []),
                'semantics': delivery_semantics(parsed),
                'latency_ms': int((time.time()-started)*1000)
            }
        except Exception as exc:
            return {'ok': False, 'sent': line, 'error': str(exc), 'latency_ms': int((time.time()-started)*1000)}

    def ping(self, nonce: str = '12345') -> dict[str, Any]:
        return self.transact(make_ping(nonce))

    def identify(self) -> dict[str, Any]:
        return self.transact(make_id_request())

    def status_request(self) -> dict[str, Any]:
        return self.transact(make_status_request())

    def configure_radio(self, profile: str = 'us915_test', sf: int = 7, bw: int = 125, cr: str = '45', txp: int = 10) -> dict[str, Any]:
        return self.transact(make_cfg(profile, sf, bw, cr, txp))

    def send_text(self, message_id: str, payload_class: str, body: str) -> dict[str, Any]:
        return self.transact(make_tx(message_id, payload_class, body))
