from __future__ import annotations

import html

from commnet.ux.nav_model import ADMIN_SECTIONS, STATUS_LABELS, section_for_path
from commnet.ux.portal_model import PORTAL_SECTIONS, section_for_portal_path
from commnet.ux.ui_config import css_classes


def esc(value) -> str:
    return html.escape('' if value is None else str(value), quote=True)


def _nav(active: str = 'admin', current_path: str = '', cfg: dict | None = None) -> str:
    if active == 'portal':
        primary = [
            ('/portal', 'Portal'), ('/share', 'Files'), ('/mail', 'Mail'),
            ('/bbs', 'BBS'), ('/retroweb', 'RetroWeb'), ('/emergency', 'Emergency'),
        ]
        return ''.join(f"<a href='{esc(href)}'>{esc(label)}</a>" for href, label in primary)
    links = []
    selected = section_for_path(current_path or '/admin/hud')
    for s in ADMIN_SECTIONS:
        active_cls = ' active' if s.section_id == selected.section_id else ''
        links.append(f"<a class='navlink nav-{esc(s.color)}{active_cls}' href='{esc(s.href)}'><span class='navicon'>{esc(s.icon)}</span>{esc(s.label)}</a>")
    return ''.join(links)


def _admin_rail(current_path: str = '/admin/hud') -> str:
    selected = section_for_path(current_path)
    blocks = ["<div class='rail-label'>ADMIN AREA</div>"]
    for s in ADMIN_SECTIONS:
        active_cls = ' active' if s.section_id == selected.section_id else ''
        route_links = ''.join(f"<a href='{esc(href)}'>{esc(label)}</a>" for href, label in s.routes)
        blocks.append(f"""
        <details class='rail-group rail-{esc(s.color)}{active_cls}'{ ' open' if active_cls else '' }>
          <summary><span>{esc(s.icon)}</span> {esc(s.label)}</summary>
          <div class='rail-links'>{route_links}</div>
        </details>
        """)
    blocks.append("<div class='rail-footer'><a href='/portal'>↔ Switch to CommNet Portal</a></div>")
    return "<aside class='app-rail admin-rail'>" + ''.join(blocks) + "</aside>"


def _portal_rail(current_path: str = '/portal') -> str:
    selected = section_for_portal_path(current_path)
    blocks = ["<div class='rail-label'>COMMNET PORTAL</div>"]
    for s in PORTAL_SECTIONS:
        active_cls = ' active' if s.section_id == selected.section_id else ''
        route_links = ''.join(f"<a href='{esc(href)}'>{esc(label)}</a>" for href, label in s.routes)
        login_tag = " <span class='tiny-muted'>login</span>" if s.requires_login else ''
        blocks.append(f"""
        <details class='rail-group rail-{esc(s.color)}{active_cls}'{ ' open' if active_cls else '' }>
          <summary><span>{esc(s.icon)}</span> {esc(s.label)}{login_tag}</summary>
          <div class='rail-links'>{route_links}</div>
        </details>
        """)
    return "<aside class='app-rail portal-rail'>" + ''.join(blocks) + "</aside>"


def _account_menu() -> str:
    # The identity state is filled by /static/app.js from /api/session so every page uses the same account dropdown.
    return """
    <div class='account-menu' id='account-menu' data-state='loading'>
      <button type='button' class='account-button' id='account-button' aria-haspopup='true' aria-expanded='false'>
        <span class='account-avatar blank' id='account-avatar'>○</span>
        <span class='account-name' id='account-name'>Guest</span>
        <span class='account-caret'>▾</span>
      </button>
      <div class='account-dropdown' id='account-dropdown' hidden>
        <a href='/login' data-menu='login'>Sign in</a>
        <a href='/signup' data-menu='signup'>Create account</a>
        <a href='/account' data-menu='account'>My Account</a>
        <a href='/account/profile' data-menu='profile'>Profile</a>
        <a href='/account/icon' data-menu='icon'>Profile Icon</a>
        <a href='/account/settings' data-menu='settings'>Display Settings</a>
        <a href='/mail' data-menu='mail'>Mail</a>
        <a href='/account/requests' data-menu='requests'>Requests</a>
        <a href='/portal' data-menu='portal'>Switch to CommNet Portal</a>
        <a href='/admin/hud' data-menu='admin'>Switch to Admin HUD</a>
        <a href='/logout' data-menu='logout'>Sign out</a>
      </div>
    </div>
    """


def layout(title: str, body: str, active: str = 'admin', cfg: dict | None = None, current_path: str = '') -> bytes:
    cfg = cfg or {}
    ui_classes = css_classes(cfg)
    nav = _nav(active, current_path, cfg)
    rail = _admin_rail(current_path or '/admin/hud') if active == 'admin' else (_portal_rail(current_path or '/portal') if active == 'portal' else '')
    home = '/admin/hud' if active == 'admin' else '/portal'
    context_label = 'Admin HUD' if active == 'admin' else 'CommNet Portal'
    shell_label = 'admin-shell' if active == 'admin' else 'portal-shell'
    crumbs = f"""
    <div class='breadcrumbs {esc(shell_label)}-crumbs'>
      <button onclick='history.back()'>Back</button>
      <a href='{home}'>{esc(context_label)}</a>
      <span>/</span><span>{esc(title)}</span>
    </div>
    """
    page = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{esc(title)} - CommNet</title>
  <link rel='stylesheet' href='/static/style.css'>
</head>
<body class='{esc(ui_classes)} page-{esc(active)} {esc(shell_label)}'>
  <header class='topbar {esc(shell_label)}-topbar'>
    <div class='brand'><strong>CommNet</strong><span class='muted'> {esc(context_label)}</span></div>
    <nav>{nav}</nav>
    {_account_menu()}
  </header>
  {crumbs}
  <div class='app-shell {esc(shell_label)}-layout'>
    {rail}
    <main class='page'>{body}</main>
  </div>
  <script src='/static/app.js'></script>
</body>
</html>"""
    return page.encode('utf-8')


def badge(status: str, label: str | None = None) -> str:
    key = (status or 'ready').lower().replace(' ', '_')
    text = label or STATUS_LABELS.get(key, status.replace('_', ' ').title())
    return f"<span class='status-badge status-{esc(key)}'>{esc(text)}</span>"


def card(title: str, text: str, href: str = '#', status: str = 'ready', domain: str = 'neutral', icon: str = '') -> str:
    return f"""<a class='card card-{esc(domain)}' href='{esc(href)}'>
      <div class='card-top'>{badge(status)}<span class='card-icon'>{esc(icon)}</span></div>
      <h3>{esc(title)}</h3>
      <p>{esc(text)}</p>
    </a>"""


def action_card(title: str, text: str, href: str, domain: str = 'neutral', icon: str = '➜', status: str = 'ready') -> str:
    return card(title, text, href, status, domain, icon)


def status_table(items: list[dict]) -> str:
    rows = []
    for item in items:
        rows.append(
            '<tr>'
            f"<td>{esc(item.get('display_name',''))}</td>"
            f"<td><code>{esc(item.get('state',''))}</code></td>"
            f"<td>{'yes' if item.get('installed') else 'no'}</td>"
            f"<td>{'yes' if item.get('available') else 'no'}</td>"
            f"<td>{esc(item.get('notes',''))}</td>"
            '</tr>'
        )
    return """<table><thead><tr><th>Adapter</th><th>State</th><th>Installed</th><th>Available</th><th>Notes</th></tr></thead><tbody>""" + ''.join(rows) + "</tbody></table>"


def select(name: str, options: list[str], value: str) -> str:
    opts = []
    for opt in options:
        sel = ' selected' if opt == value else ''
        opts.append(f"<option value='{esc(opt)}'{sel}>{esc(opt.replace('_',' ').title())}</option>")
    return f"<select name='{esc(name)}'>{''.join(opts)}</select>"


def checkbox(name: str, value: str = '1', checked: bool = False, label: str | None = None) -> str:
    ch = ' checked' if checked else ''
    text = esc(label if label is not None else name)
    return f"<label class='check'><input type='checkbox' name='{esc(name)}' value='{esc(value)}'{ch}> {text}</label>"


def input_text(name: str, value: str = '', size: int = 48, maxlength: int = 128, input_type: str = 'text', placeholder: str = '') -> str:
    ph = f" placeholder='{esc(placeholder)}'" if placeholder else ''
    return f"<input type='{esc(input_type)}' name='{esc(name)}' value='{esc(value)}' size='{size}' maxlength='{maxlength}'{ph}>"


def textarea(name: str, value: str = '', rows: int = 4, maxlength: int = 500) -> str:
    return f"<textarea name='{esc(name)}' rows='{rows}' maxlength='{maxlength}'>{esc(value)}</textarea>"


def message_box(message: str = '', kind: str = 'notice') -> str:
    if not message:
        return ''
    return f"<div class='{esc(kind)}'>{esc(message)}</div>"
