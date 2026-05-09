from __future__ import annotations

from _smoke_common import result, runtime
from commnet.core.config import ConfigManager
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.ux.nav_model import ADMIN_SECTIONS, route_rows
from commnet.ux.ui_config import normalized_ui
from commnet.server.app import CommNetHandler

paths = runtime(); store = SQLiteStore(paths); store.initialize(); cfg = ConfigManager(paths).ensure_default(); audit = AuditLogger(paths, store)
checks = {
    'nav_sections_present': len(ADMIN_SECTIONS) >= 8,
    'route_rows_present': len(route_rows()) >= 20,
    'ui_defaults_merged': normalized_ui(cfg).get('nav_style') in ('top','rail','hybrid'),
    'hud_method_present': hasattr(CommNetHandler, 'page_admin_hud'),
    'display_settings_present': hasattr(CommNetHandler, 'page_display_settings'),
}
raise SystemExit(result('hud_acceptance_report.json', checks, {'sections': [s.label for s in ADMIN_SECTIONS]}))
