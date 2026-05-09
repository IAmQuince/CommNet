from __future__ import annotations

from commnet.network.path_selector import detect_network_paths, selected_or_best_path


def access_urls(addresses: list[dict], port: int) -> list[str]:
    # Preserve old API but do not advertise APIPA/invalid addresses.
    urls: list[str] = []
    for item in addresses:
        ip = item.get('address') or item.get('ipv4_address') if isinstance(item, dict) else item
        if not ip or str(ip).startswith('127.') or str(ip).startswith('169.254.'):
            continue
        url = f'http://{ip}:{int(port)}/'
        if url not in urls:
            urls.append(url)
    return urls or [f'http://127.0.0.1:{int(port)}/']


def selected_access_url(cfg: dict, port: int | None = None) -> str:
    port = int(port or cfg.get('server_port', 8765))
    paths = detect_network_paths(port)
    selected = selected_or_best_path(cfg, paths)
    if selected and selected.get('suggested_url'):
        return selected['suggested_url']
    return f'http://127.0.0.1:{port}/'
