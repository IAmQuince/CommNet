from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortalSection:
    section_id: str
    label: str
    icon: str
    color: str
    summary: str
    href: str
    routes: tuple[tuple[str, str], ...]
    requires_login: bool = False


PORTAL_SECTIONS: tuple[PortalSection, ...] = (
    PortalSection('home', 'Home', '⌂', 'neutral', 'Community dashboard.', '/portal', (('/portal', 'Portal Home'), ('/welcome', 'Welcome'))),
    PortalSection('files', 'Files', '📁', 'green', 'Shared folders and safe previews.', '/share', (('/share', 'Shared Files'),), False),
    PortalSection('mail', 'Mail', '✉️', 'teal', 'Internal local mailbox.', '/mail', (('/mail', 'Inbox'), ('/mail/compose', 'Compose'), ('/mail/sent', 'Sent')), True),
    PortalSection('requests', 'Request Access', '📨', 'purple', 'Ask for apps, folders, or capabilities.', '/requests/new', (('/requests/new', 'New Request'), ('/account/requests', 'My Requests')), True),
    PortalSection('bbs', 'BBS', '💬', 'teal', 'Local boards, threads, and replies.', '/bbs', (('/bbs', 'BBS Home'), ('/bbs/board/announcements', 'Announcements'), ('/bbs/board/general', 'General')), False),
    PortalSection('retroweb', 'RetroWeb', '🕹️', 'indigo', 'Local RetroWeb social/profile area.', '/retroweb', (('/retroweb', 'RetroWeb Home'), ('/retroweb/profile', 'Profile + Icon')), True),
    PortalSection('emergency', 'Emergency Info', '🚨', 'red', 'Priority notices and outage information.', '/emergency', (('/emergency', 'Emergency Info'),), False),
    PortalSection('directory', 'Community Directory', '🌐', 'blue', 'Local nodes, sites, and services.', '/portal/directory', (('/portal/directory', 'Directory'),), False),
    PortalSection('demos', 'Demos', '📡', 'orange', 'Hardware and transport demos.', '/portal/demos', (('/portal/demos', 'Demos'), ('/demo/catena', 'Catena Demo')), False),
    PortalSection('account', 'Account Settings', '⚙️', 'amber', 'Profile, icon, display, and security.', '/account', (('/account', 'My Account'), ('/account/profile', 'Profile'), ('/account/icon', 'Profile Icon'), ('/account/settings', 'Display Settings'), ('/account/security', 'Security')), True),
)


def section_for_portal_path(path: str) -> PortalSection:
    path = (path or '/portal').rstrip('/') or '/'
    best = PORTAL_SECTIONS[0]
    best_len = 0
    for section in PORTAL_SECTIONS:
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


def portal_route_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for section in PORTAL_SECTIONS:
        for href, label in section.routes:
            rows.append({'section': section.label, 'icon': section.icon, 'color': section.color, 'href': href, 'label': label})
    return rows
