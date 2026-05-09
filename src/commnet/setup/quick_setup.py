
from __future__ import annotations
from pathlib import Path
from typing import Any

from commnet.setup.detect_computer import detect_computer
from commnet.setup.detect_drives import detect_drives, detect_common_folders, recommended_public_folder
from commnet.setup.detect_network import detect_lan_addresses
from commnet.share.store import ShareStore


def detect_all() -> dict[str, Any]:
    return {'computer': detect_computer(), 'drives': detect_drives(), 'common_folders': detect_common_folders(), 'lan_addresses': detect_lan_addresses()}


def create_recommended_public_folder() -> Path:
    p = recommended_public_folder()
    p.mkdir(parents=True, exist_ok=True)
    readme = p / 'README_CommNet_Public.txt'
    if not readme.exists():
        readme.write_text('Files placed in this folder may be shared through CommNet only after you enable the share.\n', encoding='utf-8')
    inbox = p / '_CommNet_Inbox'
    inbox.mkdir(exist_ok=True)
    return p


def apply_quick_share(store, audit, cfg_mgr, cfg: dict, package_root: Path, mode: str, root_path: str, label: str, virtual_name: str, lan_enabled: bool, permission_profile: str, require_code: bool, access_code: str = '') -> str | None:
    share_store = ShareStore(store, audit, package_root)
    share_id = None
    selected_count = 0
    if mode != 'private_only':
        if not root_path:
            root_path = str(create_recommended_public_folder())
        share_id = share_store.add_share(label or 'CommNet Public', root_path, virtual_name or 'Public', visibility_mode='lan_visible' if lan_enabled else 'private', permission_profile=permission_profile, enabled=lan_enabled, require_access_code=require_code)
        selected_count = 1
    if access_code:
        share_store.set_access_code(access_code)
    cfg['quick_setup_complete'] = True
    cfg['lan_access_enabled'] = bool(lan_enabled)
    cfg['lan_access_mode'] = 'lan_visible' if lan_enabled else 'localhost_only'
    cfg['lan_bind_confirmed'] = bool(lan_enabled)
    cfg['server_host'] = '0.0.0.0' if lan_enabled else '127.0.0.1'
    cfg['lan_bind_host'] = cfg['server_host']
    cfg_mgr.save(cfg, snapshot=True, reason='quick_share_setup')
    share_store.record_quick_setup(mode, lan_enabled, selected_count, 'applied')
    if audit:
        audit.write('quick_share_setup_applied', {'mode': mode, 'lan_enabled': lan_enabled, 'share_id': share_id, 'access_code_required': require_code})
    return share_id
