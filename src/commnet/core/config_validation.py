from __future__ import annotations

import re
from typing import Any

from commnet.core.config_schema import (
    DEPLOYMENT_PROFILES, FILE_VISIBILITY, FORM_LIMITS, NODE_ROLES, PEER_TRUST_STATES,
    PRIVACY_MODES, SERVICE_IDS, TRANSPORT_PROFILES, VISIBILITY_MODES, SHARE_PERMISSION_PROFILES, SHARE_VISIBILITY_MODES, LAN_ACCESS_MODES,
)

SAFE_TEXT_RE = re.compile(r"^[A-Za-z0-9 _\.\-\'\(\),:/\\]*$")
SAFE_URL_RE = re.compile(r"^https?://[A-Za-z0-9_\.\-:\[\]]{1,220}(/.*)?$")


def clean_text(value: Any) -> str:
    value = '' if value is None else str(value)
    return value.replace('\x00', '').strip()


def validate_text(name: str, value: Any, field_key: str | None = None) -> tuple[str, list[str]]:
    key = field_key or name
    value = clean_text(value)
    limit = FORM_LIMITS.get(key, {'min': 0, 'max': 500})
    errors = []
    if len(value) < int(limit.get('min', 0)):
        errors.append(f'{name} is too short; minimum is {limit["min"]} characters.')
    if len(value) > int(limit.get('max', 500)):
        errors.append(f'{name} is too long; maximum is {limit["max"]} characters.')
    if not SAFE_TEXT_RE.match(value):
        errors.append(f'{name} contains characters outside the conservative safe set.')
    return value, errors


def validate_url(name: str, value: Any, field_key: str = 'peer_url') -> tuple[str, list[str]]:
    value = clean_text(value)
    limit = FORM_LIMITS.get(field_key, {'min': 8, 'max': 260})
    errors: list[str] = []
    if len(value) < int(limit.get('min', 8)):
        errors.append(f'{name} is too short.')
    if len(value) > int(limit.get('max', 260)):
        errors.append(f'{name} is too long.')
    if not SAFE_URL_RE.match(value):
        errors.append(f'{name} must be an http:// or https:// URL with conservative characters.')
    return value.rstrip('/'), errors


def validate_choice(name: str, value: Any, allowed: list[str]) -> tuple[str, list[str]]:
    value = clean_text(value)
    if value not in allowed:
        return allowed[0], [f'{name} must be one of: {", ".join(allowed)}.']
    return value, []


def validate_multi_choice(name: str, values: list[str] | tuple[str, ...], allowed: list[str]) -> tuple[list[str], list[str]]:
    out = []
    errors = []
    for value in values:
        value = clean_text(value)
        if value in allowed and value not in out:
            out.append(value)
        elif value:
            errors.append(f'{name} includes unknown value {value}.')
    return out, errors


def _validate_bool(name: str, value: Any) -> list[str]:
    return [] if isinstance(value, bool) else [f'{name} must be boolean.']


def _validate_int(name: str, value: Any, min_value: int, max_value: int) -> list[str]:
    if not isinstance(value, int):
        return [f'{name} must be an integer.']
    if not (min_value <= value <= max_value):
        return [f'{name} must be between {min_value} and {max_value}.']
    return []


def validate_config(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _, e = validate_text('node_name', cfg.get('node_name'), 'node_name'); errors += e
    _, e = validate_text('admin_display_name', cfg.get('admin_display_name'), 'admin_display_name'); errors += e
    _, e = validate_choice('deployment_profile', cfg.get('deployment_profile'), DEPLOYMENT_PROFILES); errors += e
    _, e = validate_choice('node_role', cfg.get('node_role'), NODE_ROLES); errors += e
    _, e = validate_choice('visibility_mode', cfg.get('visibility_mode'), VISIBILITY_MODES); errors += e
    _, e = validate_choice('privacy_mode', cfg.get('privacy_mode'), PRIVACY_MODES); errors += e
    _, e = validate_choice('default_peer_trust', cfg.get('default_peer_trust', 'untrusted'), PEER_TRUST_STATES); errors += e
    transports = cfg.get('desired_transport_profiles') or []
    if not isinstance(transports, list):
        errors.append('desired_transport_profiles must be a list.')
    else:
        _, e = validate_multi_choice('desired_transport_profiles', transports, TRANSPORT_PROFILES); errors += e
    services = cfg.get('services') or {}
    if not isinstance(services, dict):
        errors.append('services must be a dictionary.')
    else:
        for sid in services:
            if sid not in SERVICE_IDS:
                errors.append(f'unknown service id: {sid}')
    site = cfg.get('personal_site') or {}
    if isinstance(site, dict):
        _, e = validate_choice('personal_site.visibility', site.get('visibility', 'private'), FILE_VISIBILITY); errors += e
    for name in ['network_enabled', 'lan_http_enabled', 'allow_manual_peers', 'allow_inbound_peer_messages', 'quick_setup_complete', 'lan_access_enabled', 'lan_bind_confirmed', 'access_code_required_default', 'hide_dotfiles', 'hide_system_files', 'show_virtual_paths_only', 'commweb_landing_enabled', 'admin_localhost_only', 'visitor_admin_block_enabled', 'captive_assist_enabled', 'captive_portal_api_enabled']:
        errors += _validate_bool(name, cfg.get(name))
    for name, lo, hi in [
        ('server_port', 1, 65535), ('lan_bind_port', 1, 65535),
        ('max_global_queue_depth', 1, 100000), ('max_adapter_queue_depth', 1, 10000),
        ('max_delivery_retries', 0, 20), ('adapter_probe_interval_sec', 1, 3600),
        ('max_download_size_mb', 1, 100000), ('max_upload_size_mb', 1, 100000),
    ]:
        errors += _validate_int(name, cfg.get(name), lo, hi)
    if cfg.get('lan_access_mode', 'localhost_only') not in LAN_ACCESS_MODES:
        errors.append('lan_access_mode must be a known LAN access mode.')
    if cfg.get('default_share_permission', 'list_and_download') not in SHARE_PERMISSION_PROFILES:
        errors.append('default_share_permission must be a known permission profile.')
    if cfg.get('default_share_visibility', 'private') not in SHARE_VISIBILITY_MODES:
        errors.append('default_share_visibility must be a known share visibility mode.')
    return errors
