from __future__ import annotations

SITE_MAP = {
    'CommWeb Visitor Area': [
        ('/welcome', 'Welcome / default visitor landing'),
        ('/sitemap', 'Visitor site map'),
        ('/portal', 'CommWeb portal'),
        ('/share', 'Shared files'),
        ('/portal/directory', 'Community directory'),
        ('/portal/library', 'Library'),
        ('/portal/emergency', 'Emergency board'),
        ('/portal/bbs', 'BBS'),
        ('/portal/retroweb', 'RetroWeb'),
        ('/portal/demos', 'Demos'),
    ],
    'Admin Configuration Area': [
        ('/admin', 'Admin dashboard'),
        ('/admin/network-wizard', 'Network setup wizard'),
        ('/admin/site-map', 'Admin site map'),
        ('/admin/quick-setup', 'Quick Setup'),
        ('/admin/lan', 'LAN access'),
        ('/admin/shares', 'Share roots'),
        ('/admin/share-links', 'Copyable links'),
        ('/admin/peers', 'Peers'),
        ('/admin/transports', 'Transports'),
        ('/admin/messages', 'Messages'),
        ('/admin/catena', 'Catena hardware demo'),
        ('/admin/diagnostics', 'Diagnostics'),
        ('/admin/config', 'Configuration management'),
        ('/admin/audit', 'Audit log'),
    ],
    'Hardware / Demo Area': [
        ('/demo/catena', 'Catena Serial LoRa Messenger'),
        ('/api/loopback-test', 'Loopback API self-test'),
        ('/admin/messages', 'LAN peer message tests'),
    ],
}
