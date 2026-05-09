from __future__ import annotations

from copy import deepcopy
from typing import Any

UI_DEFAULTS: dict[str, Any] = {
    'theme': 'light',
    'nav_style': 'hybrid',
    'card_density': 'comfortable',
    'color_coding': True,
    'icon_mode': 'emoji',
    'show_advanced_cards': False,
    'show_demo_services': True,
    'show_simulated_devices': True,
    'hud_diagnostics': 'summary',
    'admin_home': 'hud',
    'guest_card_style': 'simple',
    'show_unavailable_guest_apps': 'grayed',
}

UI_OPTIONS: dict[str, list[str]] = {
    'theme': ['light', 'dark', 'auto'],
    'nav_style': ['top', 'rail', 'hybrid'],
    'card_density': ['comfortable', 'compact', 'dense'],
    'color_coding': ['on', 'off'],
    'icon_mode': ['emoji', 'text', 'symbols'],
    'show_advanced_cards': ['on', 'off'],
    'show_demo_services': ['on', 'off'],
    'show_simulated_devices': ['on', 'off'],
    'hud_diagnostics': ['hidden', 'summary', 'full'],
    'admin_home': ['hud', 'shares', 'network', 'users'],
    'guest_card_style': ['simple', 'detailed'],
    'show_unavailable_guest_apps': ['hidden', 'grayed'],
}


def normalized_ui(cfg: dict[str, Any]) -> dict[str, Any]:
    ui = deepcopy(UI_DEFAULTS)
    raw = cfg.get('ui') or {}
    if isinstance(raw, dict):
        ui.update({k: v for k, v in raw.items() if k in ui})
    # tolerate legacy string bools and form values
    for key in ('color_coding', 'show_advanced_cards', 'show_demo_services', 'show_simulated_devices'):
        val = ui.get(key)
        if isinstance(val, str):
            ui[key] = val.lower() in ('1', 'true', 'yes', 'on')
        else:
            ui[key] = bool(val)
    for key, choices in UI_OPTIONS.items():
        if key in ('color_coding', 'show_advanced_cards', 'show_demo_services', 'show_simulated_devices'):
            continue
        if ui.get(key) not in choices:
            ui[key] = UI_DEFAULTS[key]
    return ui


def apply_ui_form(cfg: dict[str, Any], form: dict[str, list[str]], first) -> dict[str, Any]:
    ui = normalized_ui(cfg)
    for key in ('theme', 'nav_style', 'card_density', 'icon_mode', 'hud_diagnostics', 'admin_home', 'guest_card_style', 'show_unavailable_guest_apps'):
        value = first(form, key, str(ui.get(key)))
        if value in UI_OPTIONS[key]:
            ui[key] = value
    for key in ('color_coding', 'show_advanced_cards', 'show_demo_services', 'show_simulated_devices'):
        ui[key] = first(form, key, 'off') == 'on'
    cfg['ui'] = ui
    return cfg


def css_classes(cfg: dict[str, Any]) -> str:
    ui = normalized_ui(cfg)
    classes = [f"theme-{ui['theme']}", f"nav-{ui['nav_style']}", f"density-{ui['card_density']}", f"icons-{ui['icon_mode']}"]
    classes.append('color-coded' if ui.get('color_coding') else 'color-muted')
    return ' '.join(classes)
