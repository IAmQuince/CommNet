from __future__ import annotations

import importlib.util
import sys
from typing import Any


def pyserial_available() -> bool:
    return importlib.util.find_spec('serial') is not None


def list_serial_ports() -> list[dict[str, Any]]:
    if pyserial_available():
        try:
            from serial.tools import list_ports  # type: ignore
            return [
                {'device': p.device, 'description': p.description, 'hwid': p.hwid, 'source': 'pyserial'}
                for p in list_ports.comports()
            ]
        except Exception as exc:
            return [{'device': '', 'description': 'pyserial probe failed', 'hwid': str(exc), 'source': 'error'}]
    if sys.platform.startswith('win'):
        return [{'device': f'COM{i}', 'description': 'candidate COM port (pyserial not installed)', 'hwid': '', 'source': 'candidate'} for i in range(1, 17)]
    return [{'device': '/dev/ttyUSB0', 'description': 'candidate serial port (pyserial not installed)', 'hwid': '', 'source': 'candidate'}]
