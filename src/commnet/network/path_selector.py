from __future__ import annotations

import ipaddress
import re
import socket
import subprocess
import uuid
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class NetworkPath:
    path_id: str
    adapter_name: str
    ipv4_address: str
    subnet_mask: str = ''
    gateway: str = ''
    dns_suffix: str = ''
    connected: bool = True
    source: str = 'unknown'
    classification: str = 'warning'
    recommendation_score: int = 0
    reason: str = ''
    suggested_url: str = ''

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _stable_id(adapter: str, ip: str) -> str:
    base = f'{adapter}|{ip}'
    return 'net_' + uuid.uuid5(uuid.NAMESPACE_URL, base).hex[:12]


def is_apipa(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network('169.254.0.0/16')
    except Exception:
        return False


def is_private_lan(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return bool(addr.is_private and not addr.is_loopback and not is_apipa(ip))
    except Exception:
        return False


def classify_path(adapter_name: str, ip: str, gateway: str = '', connected: bool = True, source: str = 'unknown') -> tuple[str, int, str]:
    if not connected:
        return 'invalid', -100, 'media disconnected'
    if not ip:
        return 'invalid', -100, 'no IPv4 address'
    try:
        addr = ipaddress.ip_address(ip)
    except Exception:
        return 'invalid', -100, 'invalid IPv4 address'
    if addr.is_loopback:
        return 'invalid', -80, 'loopback address is local-only'
    if is_apipa(ip):
        return 'invalid', -60, 'self-assigned/APIPA address; router DHCP was not detected'
    if is_private_lan(ip) and gateway:
        return 'recommended', 100, 'private LAN address with router/gateway'
    if is_private_lan(ip):
        return 'warning', 60, 'private LAN address but no gateway detected'
    if addr.is_global:
        return 'warning', 30, 'public-looking address; verify this is intended'
    return 'warning', 10, 'address detected but not clearly usable'


def _parse_ipconfig(text: str, port: int) -> list[NetworkPath]:
    paths: list[NetworkPath] = []
    current_name = ''
    current: dict[str, Any] = {}

    def flush():
        nonlocal current_name, current
        if not current_name:
            return
        ip = current.get('ipv4', '')
        gateway = current.get('gateway', '')
        connected = not current.get('disconnected', False)
        if ip or current.get('disconnected'):
            cls, score, reason = classify_path(current_name, ip, gateway, connected, 'ipconfig')
            paths.append(NetworkPath(
                path_id=_stable_id(current_name, ip or current_name),
                adapter_name=current_name,
                ipv4_address=ip,
                subnet_mask=current.get('subnet',''),
                gateway=gateway,
                dns_suffix=current.get('dns_suffix',''),
                connected=connected,
                source='ipconfig',
                classification=cls,
                recommendation_score=score,
                reason=reason,
                suggested_url=f'http://{ip}:{port}/' if ip and cls != 'invalid' else '',
            ))
        current_name = ''
        current = {}

    adapter_re = re.compile(r'^(.*adapter .+):\s*$', re.IGNORECASE)
    for raw in text.splitlines():
        line = raw.rstrip('\r')
        m = adapter_re.match(line.strip())
        if m:
            flush()
            current_name = m.group(1).strip()
            current = {}
            continue
        if not current_name:
            continue
        low = line.lower()
        if 'media disconnected' in low:
            current['disconnected'] = True
        if 'connection-specific dns suffix' in low and ':' in line:
            current['dns_suffix'] = line.split(':',1)[1].strip()
        if 'ipv4 address' in low and ':' in line:
            val = line.split(':',1)[1].strip().split('(')[0].strip()
            current['ipv4'] = val
        if 'autoconfiguration ipv4 address' in low and ':' in line:
            val = line.split(':',1)[1].strip().split('(')[0].strip()
            current['ipv4'] = val
        if 'subnet mask' in low and ':' in line:
            current['subnet'] = line.split(':',1)[1].strip()
        if 'default gateway' in low and ':' in line:
            val = line.split(':',1)[1].strip()
            if val and re.match(r'^\d+\.\d+\.\d+\.\d+$', val):
                current['gateway'] = val
    flush()
    return paths


def detect_network_paths(port: int = 8765) -> list[dict[str, Any]]:
    paths: list[NetworkPath] = []
    if __import__('sys').platform.startswith('win'):
        try:
            cp = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=4)
            text = cp.stdout or cp.stderr or ''
            paths.extend(_parse_ipconfig(text, port))
        except Exception:
            pass
    # Fallback hostname/UDP route probing, preserving usability on non-Windows and in tests.
    seen_ips = {p.ipv4_address for p in paths if p.ipv4_address}
    try:
        host = socket.gethostname()
        for info in socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_DGRAM):
            ip = info[4][0]
            if ip not in seen_ips:
                cls, score, reason = classify_path('hostname route', ip, '', True, 'hostname')
                paths.append(NetworkPath(_stable_id('hostname route', ip), 'hostname route', ip, source='hostname', classification=cls, recommendation_score=score, reason=reason, suggested_url=f'http://{ip}:{port}/' if cls != 'invalid' else ''))
                seen_ips.add(ip)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip not in seen_ips:
            cls, score, reason = classify_path('default route probe', ip, '', True, 'udp_route_probe_no_data_sent')
            paths.append(NetworkPath(_stable_id('default route probe', ip), 'default route probe', ip, source='udp_route_probe_no_data_sent', classification=cls, recommendation_score=score, reason=reason, suggested_url=f'http://{ip}:{port}/' if cls != 'invalid' else ''))
            seen_ips.add(ip)
    except Exception:
        pass
    if not paths:
        cls, score, reason = classify_path('loopback', '127.0.0.1', '', True, 'fallback')
        paths.append(NetworkPath(_stable_id('loopback','127.0.0.1'), 'loopback', '127.0.0.1', source='fallback', classification=cls, recommendation_score=score, reason=reason, suggested_url=f'http://127.0.0.1:{port}/'))
    # Stable order: recommended first, then warnings, invalid last.
    return [p.to_dict() for p in sorted(paths, key=lambda p: (p.recommendation_score, p.adapter_name), reverse=True)]


def best_network_path(paths: list[dict[str, Any]]) -> dict[str, Any] | None:
    usable = [p for p in paths if p.get('classification') in {'recommended', 'warning'} and p.get('ipv4_address') and not is_apipa(str(p.get('ipv4_address')))]
    if not usable:
        return None
    return sorted(usable, key=lambda p: int(p.get('recommendation_score',0)), reverse=True)[0]


def selected_or_best_path(cfg: dict[str, Any], paths: list[dict[str, Any]]) -> dict[str, Any] | None:
    selected_id = cfg.get('selected_network_path_id')
    if selected_id:
        for p in paths:
            if p.get('path_id') == selected_id and p.get('classification') != 'invalid':
                return p
    preferred_ip = cfg.get('preferred_visitor_ip')
    if preferred_ip:
        for p in paths:
            if p.get('ipv4_address') == preferred_ip and p.get('classification') != 'invalid':
                return p
    return best_network_path(paths)
