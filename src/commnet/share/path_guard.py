
from __future__ import annotations

from pathlib import Path

BLOCKED_NAMES = {'.git', '__pycache__', 'runtime', 'src', 'tools', 'audit_reports', 'proof', 'registries', 'wheels'}
BLOCKED_SUFFIXES = {'.sqlite', '.db', '.pyc', '.log'}

class PathGuardError(ValueError):
    pass


def _clean_rel(rel_path: str | None) -> str:
    rel = (rel_path or '').replace('\\', '/').strip().lstrip('/')
    parts = []
    for part in rel.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            raise PathGuardError('Path traversal is blocked.')
        if ':' in part:
            raise PathGuardError('Absolute or drive-qualified paths are blocked.')
        parts.append(part)
    return '/'.join(parts)


def safe_resolve(root_path: str, rel_path: str | None = '') -> Path:
    root = Path(root_path).expanduser().resolve()
    rel = _clean_rel(rel_path)
    target = (root / rel).resolve() if rel else root
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PathGuardError('Resolved path escaped the approved share root.') from exc
    return target


def validate_share_root(root_path: str, package_root: Path | None = None) -> tuple[bool, str]:
    try:
        root = Path(root_path).expanduser().resolve()
    except Exception as exc:
        return False, f'Could not resolve path: {exc}'
    if not root.exists():
        return False, 'Path does not exist.'
    if not root.is_dir():
        return False, 'Share root must be a folder.'
    if package_root is not None:
        try:
            root.relative_to(Path(package_root).resolve())
            return False, 'CommNet package/source/runtime folders cannot be shared directly.'
        except ValueError:
            pass
    parts = {p.lower() for p in root.parts}
    if parts.intersection(BLOCKED_NAMES):
        return False, 'This path contains a blocked system/package folder name.'
    return True, 'ok'


def visitor_name(path: Path) -> str:
    name = path.name or str(path)
    if len(name) > 120:
        return name[:117] + '...'
    return name
