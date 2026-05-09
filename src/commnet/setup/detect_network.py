
from __future__ import annotations
import socket

def detect_lan_addresses() -> list[dict]:
    found = []
    try:
        host = socket.gethostname()
        infos = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_DGRAM)
        for info in infos:
            ip = info[4][0]
            if ip not in [x['address'] for x in found]:
                found.append({'address': ip, 'loopback': ip.startswith('127.'), 'source': 'hostname'})
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip not in [x['address'] for x in found]:
            found.append({'address': ip, 'loopback': ip.startswith('127.'), 'source': 'udp_route_probe_no_data_sent'})
    except Exception:
        pass
    if '127.0.0.1' not in [x['address'] for x in found]:
        found.insert(0, {'address': '127.0.0.1', 'loopback': True, 'source': 'loopback'})
    return found
