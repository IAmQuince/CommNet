
from __future__ import annotations
import platform, socket, getpass

def detect_computer() -> dict:
    return {
        'machine_name': socket.gethostname(),
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'user': getpass.getuser(),
    }
