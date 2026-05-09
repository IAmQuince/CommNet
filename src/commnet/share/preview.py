from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from commnet.share.path_guard import safe_resolve

TEXT_EXTS = {'.txt', '.md', '.csv', '.log', '.json', '.py', '.ini'}
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
BLOCKED_EXTS = {'.html', '.htm', '.js', '.mjs', '.vbs', '.bat', '.cmd', '.ps1', '.exe', '.dll', '.scr'}


def preview_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return 'image'
    if ext in TEXT_EXTS:
        return 'text'
    if ext in BLOCKED_EXTS:
        return 'blocked'
    return 'metadata'


def resolve_preview(share: dict[str, Any], rel_path: str) -> tuple[Path, str]:
    # preview is intentionally stricter than download; allow_download is not required.
    if not share.get('allow_preview') and share.get('permission_profile') not in ('preview_only', 'list_preview_download'):
        raise PermissionError('Preview is disabled for this share.')
    target = safe_resolve(share['root_path'], rel_path)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError('File does not exist.')
    return target, preview_kind(target)


def read_text_preview(path: Path, max_bytes: int = 64_000) -> str:
    raw = path.read_bytes()[:max_bytes]
    return raw.decode('utf-8', errors='replace')


def metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        'name': path.name,
        'suffix': path.suffix.lower(),
        'size_bytes': stat.st_size,
        'mime_type': mimetypes.guess_type(str(path))[0] or 'application/octet-stream',
        'preview_kind': preview_kind(path),
    }
