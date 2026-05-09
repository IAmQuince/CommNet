from __future__ import annotations

from _smoke_common import result, runtime
from commnet.core.config import ConfigManager
from commnet.ux.ui_config import UI_DEFAULTS, apply_ui_form, normalized_ui

paths = runtime(); mgr = ConfigManager(paths); cfg = mgr.ensure_default()
form = {'theme':['dark'], 'nav_style':['rail'], 'card_density':['compact'], 'icon_mode':['emoji'], 'hud_diagnostics':['full'], 'admin_home':['hud'], 'guest_card_style':['detailed'], 'show_unavailable_guest_apps':['grayed'], 'color_coding':['on'], 'show_advanced_cards':['on'], 'show_demo_services':['on'], 'show_simulated_devices':['off']}
first = lambda f,k,d='': f.get(k,[d])[0]
apply_ui_form(cfg, form, first); mgr.save(cfg, snapshot=True, reason='ui_settings_smoke')
ui = normalized_ui(mgr.load())
checks = {'theme_saved': ui['theme']=='dark', 'nav_saved': ui['nav_style']=='rail', 'density_saved': ui['card_density']=='compact', 'bool_saved': ui['show_simulated_devices'] is False}
# restore default to keep smoke non-invasive
cfg = mgr.load(); cfg['ui'] = dict(UI_DEFAULTS); mgr.save(cfg, snapshot=True, reason='ui_settings_smoke_restore')
raise SystemExit(result('ui_settings_report.json', checks, {'ui': ui}))
