from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class NavSection:
    section_id: str
    label: str
    icon: str
    color: str
    summary: str
    href: str
    routes: tuple[tuple[str, str], ...]


ADMIN_SECTIONS: tuple[NavSection, ...] = (
    NavSection('hud', 'HUD', '⌂', 'neutral', 'One-page operating console.', '/admin/hud', (('/admin/hud', 'Admin HUD'),)),
    NavSection('network', 'Network & Invites', '🌐', 'blue', 'LAN paths, invite links, join help.', '/admin/network', (
        ('/admin/network', 'Network Dashboard'), ('/admin/network-paths', 'Network Paths'), ('/admin/network-wizard', 'Network Wizard'), ('/admin/share-links', 'Copy Links'), ('/help/join', 'Join Help'),
    )),
    NavSection('sharing', 'Sharing & Files', '📁', 'green', 'Shared roots, previews, file policy.', '/admin/shares', (
        ('/admin/shares', 'Share HUD'), ('/admin/shares/new', 'New Share'), ('/admin/files', 'File Roots'), ('/share', 'Visitor Shares'),
    )),
    NavSection('users', 'Users & Permissions', '👥', 'purple', 'Accounts, roles, requests, resets.', '/admin/users', (
        ('/admin/users', 'Users'), ('/admin/users/requests', 'Permission Requests'), ('/admin/users/password-resets', 'Password Resets'), ('/signup', 'Sign Up'),
    )),
    NavSection('mail', 'Mail', '✉️', 'teal', 'Local internal CommNet mail.', '/admin/mail', (
        ('/admin/mail', 'Admin Mail'), ('/mail', 'User Mail'), ('/mail/compose', 'Compose'),
    )),
    NavSection('devices', 'Devices & Catena', '📡', 'orange', 'Serial, Catena, hardware verification.', '/admin/devices', (
        ('/admin/devices', 'Devices'), ('/admin/devices/detected', 'Detected Devices'), ('/admin/devices/meshtastic', 'Meshtastic'), ('/admin/catena', 'Catena'), ('/admin/catena-transcript', 'Catena Transcript'),
    )),
    NavSection('apps', 'Portal Apps', '🕹️', 'indigo', 'RetroWeb, BBS, emergency information.', '/admin/apps', (
        ('/admin/apps', 'Portal Apps'), ('/portal', 'Open Portal'), ('/admin/apps/retroweb', 'RetroWeb Admin'), ('/retroweb', 'Open RetroWeb'), ('/admin/apps/bbs', 'BBS Admin'), ('/bbs', 'Open BBS'), ('/admin/apps/emergency', 'Emergency'),
    )),
    NavSection('diagnostics', 'Diagnostics & Audit', '🩺', 'gray', 'System diagnostics, route matrix, audit.', '/admin/diagnostics', (
        ('/admin/diagnostics', 'Diagnostics'), ('/admin/audit', 'Audit'), ('/admin/config', 'Config'), ('/sitemap', 'Site Map'),
    )),
    NavSection('settings', 'Settings', '⚙️', 'amber', 'Display and local configuration settings.', '/admin/settings/display', (
        ('/admin/settings/display', 'Display Settings'), ('/admin/profile', 'Profile'), ('/admin/privacy', 'Privacy'), ('/admin/services', 'Services'),
    )),
)

DOMAIN_META = {section.section_id: section for section in ADMIN_SECTIONS}

STATUS_LABELS = {
    'ready': 'Ready',
    'needs_setup': 'Needs setup',
    'warning': 'Warning',
    'blocked': 'Blocked',
    'simulated': 'Simulated',
    'connected': 'Connected',
    'unverified': 'Unverified',
    'admin_only': 'Admin only',
    'guest_visible': 'Guest visible',
    'enabled': 'Enabled',
    'disabled': 'Disabled',
}


def section_for_path(path: str) -> NavSection:
    path = (path or '/admin/hud').rstrip('/') or '/'
    best = ADMIN_SECTIONS[0]
    best_len = 0
    for section in ADMIN_SECTIONS:
        for route, _ in section.routes:
            route_base = route.rstrip('/') or '/'
            if path == route_base or path.startswith(route_base + '/'):
                if len(route_base) > best_len:
                    best = section
                    best_len = len(route_base)
        if path == section.href or path.startswith(section.href.rstrip('/') + '/'):
            if len(section.href) > best_len:
                best = section
                best_len = len(section.href)
    return best


def primary_nav() -> list[dict[str, str]]:
    return [
        {'label': s.label, 'href': s.href, 'icon': s.icon, 'color': s.color, 'section_id': s.section_id}
        for s in ADMIN_SECTIONS
    ]


def route_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for section in ADMIN_SECTIONS:
        for href, label in section.routes:
            rows.append({'section': section.label, 'icon': section.icon, 'color': section.color, 'href': href, 'label': label})
    return rows
