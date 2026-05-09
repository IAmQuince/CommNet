from __future__ import annotations

from typing import Any
from commnet.network.path_selector import detect_network_paths, selected_or_best_path, is_apipa


def build_base_urls(lan_addresses: list[Any], port: int) -> list[str]:
    seen: list[str] = []
    for item in lan_addresses:
        ip = item.get('address') if isinstance(item, dict) else item
        if not ip or str(ip).startswith('127.') or is_apipa(str(ip)):
            continue
        url = f'http://{ip}:{int(port)}'
        if url not in seen:
            seen.append(url)
    return seen or [f'http://127.0.0.1:{int(port)}']


def build_link_set(cfg: dict[str, Any], lan_addresses: list[Any] | None = None) -> dict[str, Any]:
    port = int(cfg.get('server_port', 8765))
    paths = detect_network_paths(port)
    selected = selected_or_best_path(cfg, paths)
    if selected and selected.get('suggested_url'):
        base = selected['suggested_url'].rstrip('/')
        bases = [base]
        selected_reason = selected.get('reason','')
        selected_path = selected
    else:
        bases = build_base_urls(lan_addresses or [], port)
        base = bases[0]
        selected_reason = 'No valid selected network path; using fallback.'
        selected_path = None
    code = cfg.get('last_access_code') or '[set access code in Quick Setup if required]'
    user_id = cfg.get('commnet_user_id') or 'CommNet_UNSET'
    return {
        'base_urls': bases,
        'visitor': base + '/',
        'portal': base + '/portal',
        'share': base + '/share',
        'welcome': base + '/welcome',
        'admin_local': f'http://127.0.0.1:{port}/admin',
        'selected_network_path': selected_path,
        'selected_reason': selected_reason,
        'peer_invite_text': f'Join my local CommNet node: {user_id}\nOpen: {base}/\nAccess code: {code}\nWorks only on the same LAN/Wi-Fi unless a gateway is configured.',
        'node_card': {
            'commnet_user_id': user_id,
            'display_name': cfg.get('node_display_name') or cfg.get('node_name'),
            'visitor_url': base + '/',
            'share_url': base + '/share',
            'visibility_mode': cfg.get('visibility_mode'),
            'scope_note': 'LAN-only unless gateway configured',
            'selected_network_path': selected_path,
        }
    }
