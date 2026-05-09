
from __future__ import annotations

from pathlib import Path
from typing import Any

from commnet.share.path_guard import PathGuardError, safe_resolve, visitor_name


def list_entries(share: dict[str, Any], rel_path: str = '', max_entries: int = 500) -> dict[str, Any]:
    if not share.get('allow_list'):
        raise PermissionError('Listing is disabled for this share.')
    target = safe_resolve(share['root_path'], rel_path)
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError('Folder does not exist.')
    entries = []
    too_many = False
    for i, child in enumerate(sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))):
        if i >= max_entries:
            too_many = True
            break
        name = child.name
        if name.startswith('.') or name in {'__pycache__'}:
            continue
        entries.append({'name': visitor_name(child), 'is_dir': child.is_dir(), 'size': child.stat().st_size if child.is_file() else None})
    return {'path': rel_path or '', 'entries': entries, 'too_many': too_many}


def resolve_download(share: dict[str, Any], rel_path: str) -> Path:
    if not share.get('allow_download'):
        raise PermissionError('Downloads are disabled for this share.')
    target = safe_resolve(share['root_path'], rel_path)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError('File does not exist.')
    return target
