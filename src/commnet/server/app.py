from __future__ import annotations

import html
import json
import mimetypes
import threading
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse, quote

from commnet.core.audit import AuditLogger
from commnet.core.config import ConfigManager
from commnet.core.config_schema import (
    DEPLOYMENT_PROFILES, DEVICE_TYPES, FILE_VISIBILITY, NODE_ROLES, PRIVACY_MODES,
    SERVICE_IDS, SERVICE_LABELS, TRANSPORT_PROFILES, TRUST_STATES, VISIBILITY_MODES,
)
from commnet.core.config_validation import validate_choice, validate_multi_choice, validate_text
from commnet.core.db import SQLiteStore
from commnet.core.device_store import DeviceStore
from commnet.core.peer_store import PeerStore, PEER_TRUST_STATES
from commnet.core.file_roots import FileRootStore
from commnet.core.service_store import portal_services, sync_services_to_db
from commnet.diagnostics.runner import DiagnosticsRunner
from commnet.policy.visibility import visibility_label
from commnet.server.forms import checked, first, many, parse_form
from commnet.server.templates import action_card, badge, card, checkbox, esc, input_text, layout, message_box, select, status_table, textarea
from commnet.transport.engine import DeliveryEngine
from commnet.transport.dependencies import check_all_dependencies
from commnet.transport.messages import MessageEnvelope, PAYLOAD_CLASSES, PRIORITIES
from commnet.transport.registry import build_default_registry
from commnet.share.store import ShareStore
from commnet.share.browser import list_entries, resolve_download
from commnet.share.path_guard import PathGuardError, safe_resolve
from commnet.setup.quick_setup import detect_all, create_recommended_public_folder, apply_quick_share
from commnet.network.lan_access import access_urls
from commnet.network.path_selector import detect_network_paths, selected_or_best_path, is_apipa
from commnet.identity.node_identity import ensure_node_identity, identity_summary
from commnet.links.link_builder import build_link_set
from commnet.ux.site_map import SITE_MAP
from commnet.hardware.serial_ports import list_serial_ports
from commnet.demos.catena_demo import run_action as run_catena_action, make_adapter_from_config
from commnet.identity.auth import AuthInputError
from commnet.identity.user_store import ROLE_PERMISSIONS, UserStore
from commnet.mail.store import MailStore
from commnet.share.preview import metadata as preview_metadata, read_text_preview, resolve_preview
from commnet.ux.nav_model import ADMIN_SECTIONS, route_rows
from commnet.ux.ui_config import UI_DEFAULTS, UI_OPTIONS, apply_ui_form, normalized_ui
from commnet.notifications.summary import build_notification_summary
from commnet.bbs.store import BBSStore
from commnet.retroweb.store import RetroWebStore, PALETTES, DEFAULT_ICON, render_icon
from commnet.hardware.meshtastic_probe import dependency_status as meshtastic_dependency_status, list_candidate_ports as meshtastic_candidate_ports, latest_status as meshtastic_latest_status, probe_serial as meshtastic_probe_serial, send_text as meshtastic_send_text


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class CommNetHandler(BaseHTTPRequestHandler):
    server_version = 'CommNetPortalPolish/0.0.10'

    def log_message(self, fmt, *args):
        return

    @property
    def ctx(self):
        return self.server.commnet_context

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/') or '/'
        try:
            if path.startswith('/static/'):
                return self.serve_static(path)
            if path.startswith('/api/'):
                return self.serve_api(path)
            if path == '/':
                return self.redirect('/welcome')
            if path == '/sitemap':
                _, store, audit, _, cfg = self._objects()
                return self.send_bytes(layout('Site Map', self.page_site_map(visitor=True), 'portal', cfg, path))
            if path in ('/login', '/logout', '/signup', '/account', '/account/profile', '/account/icon', '/account/settings', '/account/security', '/account/request-reset'):
                return self.serve_auth_get(path, parse_qs(parsed.query))
            if path.startswith('/mail'):
                return self.serve_mail(path, parse_qs(parsed.query))
            if path.startswith('/requests') or path.startswith('/account/requests'):
                return self.serve_requests(path, parse_qs(parsed.query))
            if path == '/emergency' or path.startswith('/retroweb') or path.startswith('/bbs') or path == '/help/join':
                return self.serve_public_app(path, parse_qs(parsed.query))
            if path.startswith('/demo/catena'):
                _, store, audit, _, cfg = self._objects()
                return self.send_bytes(layout('Catena Demo', self.page_catena_demo(query=parse_qs(parsed.query)), 'portal', cfg, path))
            if path in ('/welcome', '/captive', '/captive/status'):
                return self.serve_welcome(path)
            if path.startswith('/share'):
                return self.serve_share(path, parse_qs(parsed.query))
            if path.startswith('/admin'):
                if not self.is_local_client():
                    return self.visitor_admin_blocked()
                _, store, audit, _, cfg = self._objects()
                user = self.current_user(store, audit)
                if not self.user_can_admin(user, store, audit):
                    return self.admin_access_denied(user, cfg)
                return self.serve_admin(path, parse_qs(parsed.query))
            if path.startswith('/portal'):
                return self.serve_portal(path)
            return self.not_found()
        except Exception as exc:
            _, _store, _audit, _, _cfg = self._objects()
            return self.send_bytes(layout('Error', f"<h1>Error</h1><pre>{esc(str(exc))}</pre>", 'portal', _cfg, path), status=500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/') or '/'
        try:
            if path == '/api/node/receive':
                return self.handle_node_receive()
            if path in ('/login', '/logout', '/signup', '/account/profile', '/account/icon', '/account/settings', '/account/security', '/account/request-reset'):
                return self.handle_auth_post(path, parse_form(self))
            if path.startswith('/mail'):
                return self.handle_mail_post(path, parse_form(self))
            if path.startswith('/requests') or path.startswith('/account/requests'):
                return self.handle_requests_post(path, parse_form(self))
            if path.startswith('/bbs') or path.startswith('/retroweb'):
                return self.handle_public_app_post(path, parse_form(self))
            if path.startswith('/share'):
                return self.handle_share_post(path, parse_form(self))
            if path.startswith('/admin'):
                if not self.is_local_client():
                    return self.visitor_admin_blocked()
                _, store, audit, _, cfg = self._objects()
                user = self.current_user(store, audit)
                if not self.user_can_admin(user, store, audit):
                    return self.admin_access_denied(user, cfg)
                return self.handle_admin_post(path, parse_form(self))
            return self.send_json({'error': 'unknown post endpoint'}, status=404)
        except Exception as exc:
            body = f"<h1>Action Failed</h1><div class='error'>{esc(str(exc))}</div><p><a href='{esc(path)}'>Back</a></p>"
            _, _store, _audit, _, _cfg = self._objects()
            return self.send_bytes(layout('Action Failed', body, 'portal', _cfg, path), status=400)

    def send_bytes(self, data: bytes, content_type: str = 'text/html; charset=utf-8', status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, status: int = 200):
        data = json.dumps(obj, indent=2, sort_keys=True).encode('utf-8')
        self.send_bytes(data, 'application/json; charset=utf-8', status)

    def redirect(self, location: str):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    def redirect_with_cookie(self, location: str, session_id: str | None = None, clear: bool = False):
        self.send_response(302)
        self.send_header('Location', location)
        if clear:
            self.send_header('Set-Cookie', 'commnet_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax')
        elif session_id:
            self.send_header('Set-Cookie', f'commnet_session={session_id}; Path=/; HttpOnly; SameSite=Lax')
        self.end_headers()

    def session_id(self) -> str:
        raw = self.headers.get('Cookie', '')
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw)
        except cookies.CookieError:
            return ''
        morsel = jar.get('commnet_session')
        return morsel.value if morsel else ''

    def current_user(self, store=None, audit=None) -> dict | None:
        if store is None:
            _, store, audit, _, _ = self._objects()
        return UserStore(store, audit).get_session_user(self.session_id())

    def display_user(self, user: dict | None) -> str:
        if not user:
            return 'anonymous visitor'
        return f"{user.get('display_name')} ({user.get('role_id')})"


    def user_can_admin(self, user: dict | None, store=None, audit=None) -> bool:
        if store is None:
            _, store, audit, _, _ = self._objects()
        return UserStore(store, audit).user_has(user, 'admin.hud.view')

    def admin_access_denied(self, user: dict | None, cfg: dict | None = None):
        if not user:
            return self.redirect('/login?msg=Sign%20in%20with%20an%20admin%20account%20to%20open%20the%20Admin%20HUD')
        body = """
        <div class='permission-denied'>
          <h1>Admin HUD access denied</h1>
          <p>Your account can use the CommNet Portal, but it has not been granted Admin HUD access.</p>
          <p><a class='button' href='/portal'>Return to CommNet Portal</a> <a class='button secondary' href='/requests/new'>Request Access</a></p>
        </div>
        """
        return self.send_bytes(layout('Admin Access Denied', body, 'portal', cfg or {}, '/admin-denied'), status=403)

    def account_icon_payload(self, user: dict | None, store=None, audit=None) -> dict:
        if not user:
            return {'icon_kind': 'blank', 'icon_html': '○'}
        if store is None:
            _, store, audit, _, _ = self._objects()
        profile = UserStore(store, audit).profile_for_user(user.get('user_id',''))
        kind = profile.get('icon_kind') or 'blank'
        if kind == 'generated':
            try:
                data = json.loads(profile.get('icon_json') or '{}')
            except Exception:
                data = {}
            glyph = (data.get('glyph') or (user.get('display_name') or user.get('username') or '?')[:1]).upper()[:2]
            return {'icon_kind': 'generated', 'icon_html': esc(glyph)}
        if kind == 'uploaded':
            # Upload support is intentionally conservative in this run; invalid/missing uploads fall back to blank.
            return {'icon_kind': 'uploaded', 'icon_html': esc((user.get('display_name') or user.get('username') or '?')[:1].upper())}
        return {'icon_kind': 'blank', 'icon_html': '○'}

    def not_found(self):
        _, store, audit, _, cfg = self._objects()
        return self.send_bytes(layout('Not Found', '<h1>Not found</h1><p>The requested page does not exist yet.</p>', 'portal', cfg, self.path), status=404)

    def serve_static(self, path: str):
        rel = path[len('/static/'):]
        target = self.ctx['package_root'] / 'src' / 'commnet' / 'web' / 'static' / rel
        if not target.exists() or not target.is_file():
            return self.not_found()
        ctype = mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
        return self.send_bytes(target.read_bytes(), ctype)

    def _objects(self):
        paths = self.ctx['paths']
        store = SQLiteStore(paths); store.initialize()
        audit = AuditLogger(paths, store)
        cfg_mgr = ConfigManager(paths)
        cfg = cfg_mgr.ensure_default()
        ensure_node_identity(cfg)
        if cfg.pop('_identity_changed', False):
            cfg_mgr.save(cfg, snapshot=True, reason='ensure_node_identity')
        sync_services_to_db(store, cfg)
        try:
            UserStore(store, audit).ensure_default_admin()
        except Exception as exc:
            audit.write('default_admin_seed_failed', {'error': str(exc)[:500]})
        try:
            BBSStore(store, audit).ensure_seed()
        except Exception as exc:
            audit.write('bbs_seed_failed', {'error': str(exc)[:500]})
        return paths, store, audit, cfg_mgr, cfg

    def serve_admin(self, path: str, query: dict[str, list[str]] | None = None):
        paths, store, audit, cfg_mgr, cfg = self._objects()
        msg = first(query or {}, 'msg', '')
        if path in ('/admin', '/admin/hud'):
            return self.send_bytes(layout('Admin HUD', self.page_admin_hud(store, audit, cfg, msg), 'admin', cfg, path))
        if path == '/admin/settings' or path == '/admin/settings/display':
            return self.send_bytes(layout('Display Settings', self.page_display_settings(cfg, msg), 'admin', cfg, path))
        if path.startswith('/admin/users'):
            return self.send_bytes(layout('Users & Permissions', self.page_admin_users(store, audit, path, msg), 'admin', cfg, path))
        if path.startswith('/admin/mail'):
            return self.send_bytes(layout('Admin Mail', self.page_admin_mail(store, audit, path, msg), 'admin', cfg, path))
        if path.startswith('/admin/apps'):
            return self.send_bytes(layout('Portal Apps', self.page_admin_apps(store, audit, cfg, path, msg), 'admin', cfg, path))
        if path == '/admin/devices/meshtastic':
            return self.send_bytes(layout('Meshtastic Bridge', self.page_meshtastic_admin(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/devices/detected':
            return self.send_bytes(layout('Detected Devices', self.page_devices_detected(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/shares/new' or path == '/admin/shares/roots' or path == '/admin/shares/browse':
            return self.send_bytes(layout('New Share', self.page_share_new(store, audit, msg), 'admin', cfg, path))
        if path == '/admin/network-paths':
            return self.send_bytes(layout('Network Paths', self.page_network_paths(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/network-wizard':
            return self.send_bytes(layout('Network Wizard', self.page_network_wizard(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/share-links':
            return self.send_bytes(layout('Copyable Links', self.page_share_links(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/site-map':
            return self.send_bytes(layout('Site Map', self.page_site_map(visitor=False), 'admin', cfg, path))
        if path in ('/admin/catena', '/admin/catena-hardware', '/admin/catena-test'):
            return self.send_bytes(layout('Catena Hardware', self.page_catena_admin(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/catena-transcript':
            return self.send_bytes(layout('Catena Transcript', self.page_catena_transcript(store, msg), 'admin', cfg, path))
        if path in ('/admin/catena', '/admin/catena-hardware', '/admin/catena-test'):
            action = first(form, 'action', 'save')
            if action == 'save':
                cfg['catena_adapter_enabled'] = checked(form, 'catena_adapter_enabled')
                cfg['catena_com_port'] = first(form, 'catena_com_port', cfg.get('catena_com_port',''))
                cfg['catena_baud_rate'] = int(first(form, 'catena_baud_rate', str(cfg.get('catena_baud_rate',115200))) or 115200)
                cfg['catena_ack_timeout_ms'] = int(first(form, 'catena_ack_timeout_ms', str(cfg.get('catena_ack_timeout_ms',3000))) or 3000)
                cfg['catena_payload_limit'] = int(first(form, 'catena_payload_limit', str(cfg.get('catena_payload_limit',180))) or 180)
                cfg['catena_demo_mode'] = first(form, 'catena_demo_mode', cfg.get('catena_demo_mode','fake_until_configured'))
                cfg_mgr.save(cfg, snapshot=True, reason='catena_config_update')
                audit.write('catena_config_updated', {'mode': cfg.get('catena_demo_mode'), 'port': cfg.get('catena_com_port')})
                return self.redirect('/admin/catena?msg=Catena%20configuration%20saved')
            result = run_catena_action(cfg, action, first(form, 'body', 'Hello from CommNet'))
            store.insert_catena_event('txrx', json.dumps(result, sort_keys=True), result.get('parsed',{}).get('type',''), 'ok' if result.get('ok') else 'failed', result.get('error',''), cfg.get('catena_com_port',''))
            if action == 'tx':
                mid = result.get('parsed',{}).get('fields',{}).get('id') or 'catena_msg'
                store.insert_catena_message(mid, 'text_message', first(form,'body',''), 'accepted' if result.get('ok') else 'failed', 'not_proven', 'not_received', result)
            audit.write('catena_demo_action', {'action': action, 'ok': result.get('ok'), 'semantics': result.get('semantics')})
            return self.redirect('/admin/catena?msg=Catena%20' + action + '%20' + ('ok' if result.get('ok') else 'failed'))
        if path == '/admin/setup':
            return self.send_bytes(layout('First Run Setup', self.page_setup(cfg, msg), 'admin', cfg, path))
        if path == '/admin/profile':
            return self.send_bytes(layout('Profile', self.page_profile(cfg, msg), 'admin', cfg, path))
        if path == '/admin/privacy':
            return self.send_bytes(layout('Privacy', self.page_privacy(cfg, msg), 'admin', cfg, path))
        if path == '/admin/services':
            return self.send_bytes(layout('Services', self.page_services(cfg, msg), 'admin', cfg, path))
        if path == '/admin/network-paths':
            paths = detect_network_paths(int(cfg.get('server_port', 8765)))
            store.upsert_network_paths(paths)
            selected_id = first(form, 'path_id')
            selected = None
            for pth in paths:
                if pth.get('path_id') == selected_id:
                    selected = pth
                    break
            if not selected:
                return self.redirect('/admin/network-paths?msg=No%20network%20path%20selected')
            if selected.get('classification') == 'invalid':
                return self.redirect('/admin/network-paths?msg=Invalid%20network%20path%20not%20selected')
            cfg['selected_network_path_id'] = selected.get('path_id','')
            cfg['preferred_visitor_ip'] = selected.get('ipv4_address','')
            cfg['preferred_visitor_url'] = (selected.get('suggested_url') or '').rstrip('/')
            cfg['selected_gateway'] = selected.get('gateway','')
            cfg['selected_adapter_name'] = selected.get('adapter_name','')
            cfg_mgr.save(cfg, snapshot=True, reason='network_path_selected')
            store.select_network_path(selected)
            audit.write('network_path_selected', selected)
            return self.redirect('/admin/network-paths?msg=Network%20path%20selected')
        if path == '/admin/quick-setup':
            return self.send_bytes(layout('Quick Setup', self.page_quick_setup(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/lan':
            return self.send_bytes(layout('LAN Access', self.page_lan(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/shares':
            return self.send_bytes(layout('Shares', self.page_shares(store, audit, msg), 'admin', cfg, path))
        if path == '/admin/landing':
            return self.send_bytes(layout('Landing', self.page_landing(cfg, msg), 'admin', cfg, path))
        if path == '/admin/captive-assist':
            return self.send_bytes(layout('Captive Portal Assist', self.page_captive_assist(cfg, msg), 'admin', cfg, path))
        if path == '/admin/visitor-access' or path == '/admin/security':
            return self.send_bytes(layout('Visitor Access', self.page_visitor_access(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/network':
            return self.send_bytes(layout('Network', self.page_network(store, cfg, msg), 'admin', cfg, path))
        if path == '/admin/peers':
            return self.send_bytes(layout('Peers', self.page_peers(store, audit, msg), 'admin', cfg, path))
        if path == '/admin/messages':
            return self.send_bytes(layout('Messages', self.page_messages(store, audit, msg), 'admin', cfg, path))
        if path == '/admin/transports':
            return self.send_bytes(layout('Transport Status', self.page_transports(store, audit, cfg, msg), 'admin', cfg, path))
        if path == '/admin/peers':
            ps = PeerStore(store, audit)
            action = first(form, 'action')
            peer_id = first(form, 'peer_id')
            if action == 'delete':
                ps.delete(peer_id); return self.redirect('/admin/peers?msg=Peer%20removed')
            if action == 'trust':
                ps.set_trust(peer_id, 'trusted'); return self.redirect('/admin/peers?msg=Peer%20trusted')
            if action == 'block':
                ps.set_trust(peer_id, 'blocked'); return self.redirect('/admin/peers?msg=Peer%20blocked')
            if action == 'test':
                from commnet.transport.adapters_lan import LanHttpAdapter
                peer = ps.get(peer_id)
                ok, details = LanHttpAdapter(ps).handshake(peer) if peer else (False, {'error': 'peer not found'})
                ps.record_handshake(peer_id, 'ok' if ok else 'failed', details)
                return self.redirect('/admin/peers?msg=Handshake%20' + ('ok' if ok else 'failed'))
            ps.add(first(form,'display_name'), first(form,'base_url'), first(form,'trust_state','known'), first(form,'notes'))
            return self.redirect('/admin/peers?msg=Peer%20added')
        if path == '/admin/messages':
            if first(form, 'action') == 'send':
                ps = PeerStore(store, audit)
                registry = build_default_registry(ps)
                engine = DeliveryEngine(registry, audit, store)
                msg = MessageEnvelope.create(payload_class=first(form,'payload_class','text_message'), body=first(form,'body',''), destination=first(form,'destination','self'), priority=first(form,'priority','normal'), sender_node_id=cfg.get('node_id',''))
                result = engine.send(msg)
                return self.redirect('/admin/messages?msg=Delivery%20' + result.status)
        if path == '/admin/devices':
            return self.send_bytes(layout('Devices', self.page_devices(store, msg), 'admin', cfg, path))
        if path == '/admin/files':
            return self.send_bytes(layout('File Roots', self.page_files(store, msg), 'admin', cfg, path))
        if path == '/admin/config':
            return self.send_bytes(layout('Config Management', self.page_config(cfg_mgr, cfg, msg), 'admin', cfg, path))
        if path == '/admin/audit':
            return self.send_bytes(layout('Audit Log', self.page_audit(store), 'admin', cfg, path))
        if path == '/admin/diagnostics':
            report = DiagnosticsRunner(self.ctx['package_root'], paths).run(write_reports=True)
            body = f"<h1>Diagnostics</h1><p>Status: <strong>{esc(report['overall_status'])}</strong></p><p>SQLite integrity: <code>{esc(report['sqlite_integrity'])}</code></p>"
            body += '<p><a href="/api/diagnostics">View JSON diagnostics</a></p>'
            body += '<h2>Config validation</h2><pre>' + esc(json.dumps(report.get('config_validation'), indent=2)) + '</pre>'
            return self.send_bytes(layout('Diagnostics', body, 'admin', cfg, path))
        cards = ''.join([
            card('Network Paths', 'Choose the actual Wi-Fi/Ethernet/router path used for visitor links.', '/admin/network-paths', 'working'),
            card('Network Wizard', 'Guided laptop-router-Wi-Fi workflow with visitor test checklist.', '/admin/network-wizard', 'working'),
            card('Copyable Links', 'Visitor/share/peer invite addresses to paste or send.', '/admin/share-links', 'working'),
            card('Site Map', 'Clear structure of admin, visitor, and demo pages.', '/admin/site-map', 'working'),
            card('Catena', 'USB Serial LoRa Messenger hardware demo and fake serial test mode.', '/admin/catena', 'working'),
            card('First Run Setup', 'Guided local setup and review.', '/admin/setup', 'working'),
            card('Profile', f"Node: {cfg.get('node_name')}", '/admin/profile', 'working'),
            card('Privacy', f"Visibility: {cfg.get('visibility_mode')}", '/admin/privacy', 'working'),
            card('Services', 'Enable or hide community portal services.', '/admin/services', 'working'),
            card('Quick Setup', 'Detect this computer, drives, LAN addresses, and create a safe share.', '/admin/quick-setup', 'working'),
            card('LAN Access', 'Show router/Wi-Fi workflow and visitor URLs.', '/admin/lan', 'working'),
            card('Shares', 'Configure explicit share roots and permission profiles.', '/admin/shares', 'working'),
            card('Visitor Access', 'Security posture for LAN visitors and CommWeb landing.', '/admin/visitor-access', 'working'),
            card('Network', 'Peers, queue, route decisions, and delivery attempts.', '/admin/network', 'working'),
            card('Peers', 'Manual peer registration and LAN handshake tests.', '/admin/peers', 'working'),
            card('Messages', 'Loopback and LAN peer test messages through TransportManager.', '/admin/messages', 'working'),
            card('Transports', 'Dependency probes and adapter status.', '/admin/transports', 'working'),
            card('Devices', 'Manual device registry management.', '/admin/devices', 'working'),
            card('Files', 'Register file roots without publishing files.', '/admin/files', 'working'),
            card('Config', 'Export, import, snapshot, restore, or reset config.', '/admin/config', 'working'),
            card('Audit', 'Review recent configuration changes.', '/admin/audit', 'working'),
            card('Diagnostics', 'System, database, config, and transport status.', '/admin/diagnostics', 'working'),
        ])
        body = message_box(msg) + f"""
        <h1>CommNet Configuration</h1>
        <div class='summary'>
          <strong>{esc(cfg.get('node_name'))}</strong> · {esc(cfg.get('deployment_profile'))} · {esc(visibility_label(cfg.get('visibility_mode')))}
        </div>
        <p>This configuration run persists local node identity, privacy, services, file roots, devices, and snapshots.</p>
        <section class='grid'>{cards}</section>
        """
        return self.send_bytes(layout('Admin', body, 'admin', cfg, path))


    def page_admin_hud(self, store: SQLiteStore, audit: AuditLogger, cfg: dict, msg: str = '') -> str:
        user=self.current_user(store,audit); us=UserStore(store,audit); ms=MailStore(store,audit); ss=ShareStore(store,audit,self.ctx['package_root'])
        notes=build_notification_summary(store,audit,cfg); paths_detected=detect_network_paths(int(cfg.get('server_port',8765))); selected=selected_or_best_path(cfg,paths_detected); links=build_link_set(cfg,[])
        users=us.list_users(); pending=us.list_permission_requests('pending'); resets=us.list_password_resets(); shares=ss.summary(); mesh=notes.get('meshtastic',{}); mesh_state=mesh.get('state','not_tested')
        cat_adapter=make_adapter_from_config(cfg); cat_status=cat_adapter.status(); cat_state='simulated' if cfg.get('catena_demo_mode')!='real_only' and not cfg.get('catena_com_port') else ('connected' if cat_status.get('available') else 'unverified')
        network_state='ready' if selected and not is_apipa(str(selected.get('ipv4_address',''))) else 'warning'; lan_state='ready' if cfg.get('lan_access_enabled') else 'needs_setup'; pending_state='warning' if pending else 'ready'
        def dot(v): return "<span class='badge-dot'>!</span>" if v else ''
        selected_html='No usable LAN visitor path selected yet.' if not selected else f"{esc(selected.get('adapter_name'))} · {esc(selected.get('ipv4_address'))} · gateway {esc(selected.get('gateway'))}"
        warns=list(notes.get('warnings',[]));
        if selected and is_apipa(str(selected.get('ipv4_address',''))): warns.append('Selected/recommended path is APIPA/self-assigned.')
        if cat_state=='simulated': warns.append('Catena is in simulated/fake mode. Device rows are not proof of physical connection.')
        warn_html=''.join(f"<div class='warning'>⚠️ {esc(w)}</div>" for w in warns[:6]) or "<div class='notice'>No critical setup warnings detected by the HUD.</div>"
        default_pw_html="<div class='error attention'>❗ Default admin account is active: username <code>admin</code>, password <code>password</code>. Change it before letting other people onto the network.</div>" if notes.get('default_password_active') else ''
        return f"""{message_box(msg)}<h1>CommNet Admin HUD</h1>
        <div class='server-banner'><strong>Server running</strong><span>Admin HUD: <code>http://127.0.0.1:{esc(cfg.get('server_port',8765))}/admin/hud</code></span><span>Portal: <code>http://127.0.0.1:{esc(cfg.get('server_port',8765))}/portal</code></span><span><a href='/api/status'>status JSON</a></span></div>
        <div class='summary'><strong>{esc(cfg.get('node_name'))}</strong> · role/session: <code>{esc(self.display_user(user))}</code> · visibility: <code>{esc(cfg.get('visibility_mode'))}</code></div>{default_pw_html}
        <div class='quick-actions'><a class='button safe' href='/admin/share-links'>Copy Visitor Invite</a><a class='button' href='/admin/shares/new'>Add Shared Folder</a><a class='button' href='/admin/users'>Create User</a><a class='button' href='/admin/users/requests'>Review Requests ({len(pending)})</a><a class='button' href='/admin/mail'>Admin Mail</a><a class='button' href='/admin/devices/meshtastic'>Meshtastic</a><a class='button secondary' href='/portal'>Open Portal</a></div>
        <div class='kpi-row'><div class='kpi'><strong>{len(users)}</strong><span>local users</span></div><div class='kpi {'attention' if pending else ''}'><strong>{len(pending)}</strong><span>pending requests</span></div><div class='kpi {'attention-amber' if resets else ''}'><strong>{sum(1 for r in resets if r.get('status')=='pending')}</strong><span>password resets</span></div><div class='kpi {'attention' if notes.get('unread_admin_mail') else ''}'><strong>{notes.get('unread_admin_mail',0)}</strong><span>admin unread mail</span></div><div class='kpi'><strong>{shares.get('enabled_share_count',0)}</strong><span>enabled shares</span></div></div>{warn_html}
        <div class='hud-grid'>
        <section class='hud-zone {'attention-amber' if network_state=='warning' else ''}'><h2>🌐 Network & Invites {badge(network_state)}</h2><p><strong>Selected path:</strong> {selected_html}</p><p><strong>Visitor URL:</strong> <code>{esc(links.get('visitor',''))}</code></p><div class='grid two'>{action_card('Network Wizard','Phone/Wi-Fi/router checklist and invite workflow.','/admin/network-wizard','blue','🌐',lan_state)}{action_card('Copyable Links','Admin, visitor, share, and peer invite links.','/admin/share-links','blue','🔗','ready')}</div></section>
        <section class='hud-zone'><h2>📁 Sharing & Files {badge('ready' if shares.get('enabled_share_count') else 'needs_setup')}</h2><p>{shares.get('share_count',0)} configured shares · {shares.get('lan_visible_share_count',0)} LAN-visible.</p><div class='grid two'>{action_card('Add Shared Folder','Pick a root folder, set visibility, preview, password/code, and permissions.','/admin/shares/new','green','📁','ready')}{action_card('Preview as Visitor','Open the visitor share portal with current policies.','/share','green','👁️','guest_visible')}</div></section>
        <section class='hud-zone {'attention' if pending or resets else ''}'><h2>👥 Users & Permissions {badge(pending_state)} {dot(pending or resets)}</h2><p>{len(users)} local users · {len(pending)} pending permission requests.</p><div class='grid two'>{action_card('Manage Users','Create accounts, adjust roles, hints, and password resets.','/admin/users','purple','👥','ready')}{action_card('Review Requests','Approve or deny requests.','/admin/users/requests','purple','📨',pending_state)}</div></section>
        <section class='hud-zone {'attention' if notes.get('unread_admin_mail') else ''}'><h2>✉️ Internal Mail {badge('warning' if notes.get('unread_admin_mail') else 'ready')} {dot(notes.get('unread_admin_mail'))}</h2><p>Local SQLite-backed CommNet mail.</p><div class='grid two'>{action_card('Admin Mail','Inbox, compose, and local broadcast.','/admin/mail','teal','✉️','ready')}{action_card('User Mail View','Open the user-facing mailbox.','/mail','teal','📬','ready')}</div></section>
        <section class='hud-zone {'attention-amber' if mesh_state not in {'connected','receive_active'} else ''}'><h2>📡 Devices & Mesh {badge(mesh_state)} {dot(mesh_state in {'missing_dependency','probe_failed','not_tested'})}</h2><p>Catena: <code>{esc(cat_state)}</code> · Meshtastic: <code>{esc(mesh_state)}</code> · nodes seen: <code>{esc(mesh.get('nodes_seen',0))}</code></p><div class='grid two'>{action_card('Detected Devices','List serial candidates and verification states.','/admin/devices/detected','orange','🔎','unverified')}{action_card('Meshtastic Bridge','Install check, serial probe, send test, and transcript.','/admin/devices/meshtastic','orange','📶',mesh_state)}{action_card('Catena','Configure and test fake or real serial Catena.','/admin/catena','orange','📡',cat_state)}</div></section>
        <section class='hud-zone'><h2>🕹️ Portal Apps {badge('ready')}</h2><p>RetroWeb social profiles/icons, BBS boards, emergency info, and service controls.</p><div class='grid two'>{action_card('Open Portal','Open the user-facing CommNet portal grid.','/portal','indigo','🕹️','guest_visible')}{action_card('Manage Portal Apps','Enable, hide, or require review.','/admin/apps','indigo','⚙️','ready')}{action_card('Emergency Info','Edit outage/public emergency bulletin.','/admin/apps/emergency','red','🚨','ready')}</div></section>
        </div>"""

    def page_display_settings(self, cfg: dict, msg: str = '') -> str:
        ui = normalized_ui(cfg)
        bool_select = lambda name, val: select(name, ['on','off'], 'on' if val else 'off')
        return message_box(msg) + f"""
        <h1>Display Settings</h1>
        <div class='notice'>These settings are intentionally light: they change visual density, grouped navigation, symbols, and HUD behavior without requiring code edits.</div>
        <form method='post' action='/admin/settings/display' class='formcard'>
          <label>Theme<br>{select('theme', UI_OPTIONS['theme'], ui['theme'])}</label>
          <label>Navigation style<br>{select('nav_style', UI_OPTIONS['nav_style'], ui['nav_style'])}</label>
          <label>Card density<br>{select('card_density', UI_OPTIONS['card_density'], ui['card_density'])}</label>
          <label>Icon mode<br>{select('icon_mode', UI_OPTIONS['icon_mode'], ui['icon_mode'])}</label>
          <label>HUD diagnostics<br>{select('hud_diagnostics', UI_OPTIONS['hud_diagnostics'], ui['hud_diagnostics'])}</label>
          <label>Default admin page<br>{select('admin_home', UI_OPTIONS['admin_home'], ui['admin_home'])}</label>
          <label>Guest card style<br>{select('guest_card_style', UI_OPTIONS['guest_card_style'], ui['guest_card_style'])}</label>
          <label>Unavailable guest apps<br>{select('show_unavailable_guest_apps', UI_OPTIONS['show_unavailable_guest_apps'], ui['show_unavailable_guest_apps'])}</label>
          <label>Color coding<br>{bool_select('color_coding', ui['color_coding'])}</label>
          <label>Show advanced cards<br>{bool_select('show_advanced_cards', ui['show_advanced_cards'])}</label>
          <label>Show demo services<br>{bool_select('show_demo_services', ui['show_demo_services'])}</label>
          <label>Show simulated devices<br>{bool_select('show_simulated_devices', ui['show_simulated_devices'])}</label>
          <button type='submit' name='action' value='save'>Save Settings</button>
          <button type='submit' name='action' value='defaults'>Restore Defaults</button>
        </form>
        <h2>Current UI config</h2><pre>{esc(json.dumps(ui, indent=2, sort_keys=True))}</pre>
        """

    def page_admin_users(self, store: SQLiteStore, audit: AuditLogger, path: str, msg: str = '') -> str:
        us = UserStore(store, audit)
        if path.endswith('/requests'):
            rows=''.join(f"<tr><td>{esc(r.get('created_at'))}</td><td>{esc(r.get('display_name') or r.get('username') or r.get('user_id'))}</td><td>{esc(r.get('target_type'))}</td><td><code>{esc(r.get('target_id'))}</code></td><td><code>{esc(r.get('requested_permission'))}</code></td><td>{esc(r.get('reason'))}</td><td>{esc(r.get('status'))}</td><td><form method='post' action='/admin/users/requests'><input type='hidden' name='request_id' value='{esc(r.get('request_id'))}'><select name='decision'><option value='approved'>Approve</option><option value='denied'>Deny</option><option value='needs_info'>Needs Info</option></select><input name='admin_response' maxlength='500'><button type='submit'>Apply</button></form></td></tr>" for r in us.list_permission_requests())
            return message_box(msg)+"<h1>Permission Requests</h1><p>Users can request folders, apps, or capabilities. Approvals become durable grants.</p><table><thead><tr><th>Created</th><th>User</th><th>Target</th><th>ID</th><th>Permission</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead><tbody>"+(rows or '<tr><td colspan="8">No requests yet.</td></tr>')+"</tbody></table>"
        if path.endswith('/password-resets'):
            rows=''.join(f"<tr><td>{esc(r.get('created_at'))}</td><td>{esc(r.get('username'))}</td><td>{esc(r.get('note'))}</td><td>{esc(r.get('status'))}</td></tr>" for r in us.list_password_resets())
            return message_box(msg)+"<h1>Password Reset Requests</h1><table><thead><tr><th>Created</th><th>Username</th><th>Note</th><th>Status</th></tr></thead><tbody>"+(rows or '<tr><td colspan="4">No reset requests.</td></tr>')+"</tbody></table>"
        users=us.list_users()
        role_opts=list(ROLE_PERMISSIONS.keys())
        rows=[]
        for u in users:
            rows.append(f"<tr><td>{esc(u['display_name'])}</td><td><code>{esc(u['username'])}</code></td><td>{esc(u['role_id'])}</td><td>{esc(u['status'])}</td><td>{esc(u.get('password_hint',''))}</td><td>{esc(u.get('last_login_at') or '')}</td><td><form method='post' action='/admin/users'><input type='hidden' name='action' value='role'><input type='hidden' name='user_id' value='{esc(u['user_id'])}'>{select('role_id', role_opts, u['role_id'])}<button>Set</button></form><form method='post' action='/admin/users'><input type='hidden' name='action' value='reset_password'><input type='hidden' name='user_id' value='{esc(u['user_id'])}'><input type='password' name='new_password' maxlength='128' placeholder='Temporary password'><input name='password_hint' maxlength='160' placeholder='Hint'><button>Reset</button></form></td></tr>")
        return message_box(msg)+f"""
        <h1>Users & Permissions</h1>
        <div class='notice'>Local demo accounts use PBKDF2 password hashes with per-user salts. Passwords are not shown to the admin; the admin can set a temporary reset password.</div>
        <form method='post' action='/admin/users' class='formcard'>
          <input type='hidden' name='action' value='create'>
          <h2>Create local account</h2>
          <label>Username<br>{input_text('username','',32,32, placeholder='letters-numbers_.-')}</label>
          <label>Display name<br>{input_text('display_name','',40,64)}</label>
          <label>Password<br>{input_text('password','',40,128,'password')}</label>
          <label>Password hint<br>{input_text('password_hint','',60,160)}</label>
          <label>Role<br>{select('role_id', role_opts, 'user')}</label>
          <button type='submit'>Create User</button>
        </form>
        <h2>Accounts</h2><table><thead><tr><th>Name</th><th>Username</th><th>Role</th><th>Status</th><th>Hint</th><th>Last Login</th><th>Admin Actions</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="7">No accounts yet.</td></tr>'}</tbody></table>
        <p><a href='/admin/users/requests'>Permission requests</a> · <a href='/admin/users/password-resets'>Password reset requests</a></p>
        """

    def page_admin_mail(self, store: SQLiteStore, audit: AuditLogger, path: str, msg: str = '') -> str:
        us = UserStore(store, audit); ms = MailStore(store, audit)
        users = us.list_users()
        options = ''.join(f"<label class='check'><input type='checkbox' name='recipient_user_id' value='{esc(u['user_id'])}'> {esc(u['display_name'])} ({esc(u['username'])})</label>" for u in users)
        recent = []
        for u in users[:5]:
            for m in ms.inbox(u['user_id'], 3):
                recent.append(m)
        rows=''.join(f"<tr><td>{esc(m.get('created_at'))}</td><td>{esc(m.get('sender_name') or m.get('sender_user_id'))}</td><td>{esc(m.get('subject'))}</td><td>{'yes' if m.get('read_at') else 'no'}</td></tr>" for m in recent[:25])
        return message_box(msg)+f"""
        <h1>Internal CommNet Mail</h1>
        <div class='notice'>This is local internal mail only. No SMTP, internet email, attachments, or cross-node relay is claimed in this run.</div>
        <form method='post' action='/admin/mail' class='formcard'>
          <h2>Compose / Broadcast</h2>
          <label>Recipients<br>{options or '<em>No local users yet.</em>'}</label>
          {checkbox('broadcast', 'all', False, 'Broadcast to all local users')}
          <label>Subject<br>{input_text('subject','CommNet notice',80,160)}</label>
          <label>Body<br>{textarea('body','',6,5000)}</label>
          <button type='submit'>Send Internal Mail</button>
        </form>
        <h2>Recent local mail sample</h2><table><thead><tr><th>Time</th><th>From</th><th>Subject</th><th>Read</th></tr></thead><tbody>{rows or '<tr><td colspan="4">No mail yet.</td></tr>'}</tbody></table>
        """

    def page_admin_apps(self, store: SQLiteStore, audit: AuditLogger, cfg: dict, path: str, msg: str = '') -> str:
        if path.endswith('/emergency'):
            e = cfg.get('emergency_info') or {}
            return message_box(msg)+f"""<h1>Emergency Info</h1><form method='post' action='/admin/apps/emergency' class='formcard'>{checkbox('public', checked=bool(e.get('public')), label='Public on visitor portal')}{checkbox('outage_banner', checked=bool(e.get('outage_banner')), label='Show outage/emergency banner')}<label>Title<br>{input_text('title', e.get('title','CommNet Emergency Info'), 80, 160)}</label><label>Bulletin body<br>{textarea('body', e.get('body',''), 10, 5000)}</label><button type='submit'>Save Emergency Info</button></form><p><a href='/emergency'>Preview public emergency page</a></p>"""
        if path.endswith('/retroweb'):
            profiles=RetroWebStore(store,audit).profiles(25); gallery=''.join(f"<div class='rw-card'>{render_icon(p.get('icon_json'),44)}<strong>{esc(p.get('display_name'))}</strong><div class='rw-meta'>@{esc(p.get('handle'))}</div></div>" for p in profiles)
            return message_box(msg)+f"""<h1>RetroWeb Admin</h1><div class='notice'>RetroWeb remains a separate portal app. This page summarizes local profiles/social state; user experience lives at <a href='/retroweb'>/retroweb</a>.</div><section class='grid two'>{card('Open RetroWeb','Enter user-facing RetroWeb.','/retroweb','guest_visible','indigo','🕹️')}{card('RetroWeb Access Requests','Review users asking for RetroWeb access.','/admin/users/requests','ready','purple','📨')}</section><h2>Profile Gallery</h2><div class='portal-grid'>{gallery or '<div class="notice">No RetroWeb profiles yet.</div>'}</div>"""
        if path.endswith('/bbs'):
            boards=BBSStore(store,audit).boards(); board_cards=''.join(card(b.get('title'),f"{b.get('thread_count')} threads · {b.get('description')}",f"/bbs/board/{b.get('board_id')}",'ready','teal','💬') for b in boards)
            return message_box(msg)+f"""<h1>BBS Admin</h1><div class='notice'>The BBS now has boards, threads, replies, pinned welcome content, and a user-facing board layout.</div><section class='grid two'>{card('Open BBS','Open the user-facing board.','/bbs','guest_visible','teal','💬')}{card('Permission Requests','Review users asking for BBS access.','/admin/users/requests','ready','purple','📨')}</section><h2>Boards</h2><div class='bbs-board-list'>{board_cards}</div>"""
        cards=[]
        for sid,data in (cfg.get('services') or {}).items():
            state='guest_visible' if data.get('enabled') and data.get('visible_in_portal') else ('needs_setup' if data.get('enabled') else 'disabled')
            cards.append(card(SERVICE_LABELS.get(sid,sid), f"enabled={data.get('enabled')} · visible={data.get('visible_in_portal')} · review={data.get('requires_review')}", '/admin/services', state, 'indigo', '🕹️'))
        return message_box(msg)+f"""<h1>Portal Apps</h1><div class='notice'>Portal apps have two paths: open the user-facing app, or manage visibility/settings here.</div><section class='grid three'>{card('Open Portal','Go to the user-facing community portal grid.','/portal','guest_visible','indigo','🕹️')}{card('RetroWeb','Profiles, icon generator, user gallery, feed, comments.','/retroweb','guest_visible','indigo','🕹️')}{card('BBS','Boards, threads, replies, welcome post.','/bbs','guest_visible','teal','💬')}{card('Emergency Info','Public/outage bulletin.','/emergency','guest_visible','red','🚨')}</section><h2>Service Visibility</h2><section class='grid three'>{''.join(cards)}</section><p><a class='button' href='/admin/apps/emergency'>Edit Emergency Info</a> <a class='button' href='/admin/apps/retroweb'>RetroWeb Admin</a> <a class='button' href='/admin/apps/bbs'>BBS Admin</a> <a class='button secondary' href='/admin/services'>Service Visibility Table</a></p>"""

    def page_share_new(self, store: SQLiteStore, audit: AuditLogger, msg: str = '') -> str:
        detected = detect_all()
        opts=[]
        for d in detected.get('drives', []):
            opts.append(f"<option value='{esc(d.get('path'))}'>{esc(d.get('label'))}: {esc(d.get('path'))}</option>")
        for f in detected.get('common_folders', []):
            opts.append(f"<option value='{esc(f.get('path'))}'>{esc(f.get('name'))}: {esc(f.get('path'))}</option>")
        behaviors = ['invisible','count_only','list_only','preview_only','download','upload_inbox','admin_only']
        return message_box(msg)+f"""
        <h1>Add Shared Folder</h1>
        <div class='notice'>Select a root candidate, then assign visibility, preview/download behavior, and access-code policy from one page. Whole-drive sharing is allowed only after explicit admin intent and remains warned.</div>
        <form method='post' action='/admin/shares/new' class='formcard'>
          <label>Detected root/folder<br><select name='root_path'>{''.join(opts)}</select></label>
          <label>Or paste folder path<br>{input_text('root_path_manual','',80,260)}</label>
          <label>Label<br>{input_text('label','CommNet Public',40,64)}</label>
          <label>Virtual name<br>{input_text('virtual_name','Public',40,64)}</label>
          <label>Visibility<br>{select('visibility_mode', ['private','lan_visible','approved_peers','community_visible'], 'lan_visible')}</label>
          <label>Behavior<br>{select('visibility_behavior', behaviors, 'preview_only')}</label>
          <label>Permission profile<br>{select('permission_profile', ['private','list_only','preview_only','list_and_download','dropbox_upload_only','list_download_upload_inbox','advanced_custom'], 'preview_only')}</label>
          {checkbox('enabled', checked=True, label='Enable this share')}
          {checkbox('require_access_code', checked=True, label='Require access code')}
          {checkbox('allow_preview', checked=True, label='Allow safe previews for text/images')}
          <button type='submit'>Create Share</button>
        </form>
        """

    def page_devices_detected(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        ports=list_serial_ports(); mesh_ports=meshtastic_candidate_ports(); mesh_deps=meshtastic_dependency_status(); mesh_latest=meshtastic_latest_status(store)
        cat_adapter=make_adapter_from_config(cfg); cat_status=cat_adapter.status(); state='simulated' if cfg.get('catena_demo_mode')!='real_only' and not cfg.get('catena_com_port') else ('connected' if cat_status.get('available') else 'unverified')
        rows=''.join(f"<tr><td><code>{esc(p.get('device') or p.get('port') or '')}</code></td><td>{esc(p.get('description') or '')}</td><td>{esc(p.get('hwid') or '')}</td><td>{badge('unverified')}</td></tr>" for p in ports) or '<tr><td colspan="4">No pyserial serial ports detected, or pyserial is not installed.</td></tr>'
        mesh_rows=''.join(f"<tr><td><code>{esc(p.get('device') or '')}</code></td><td>{esc(p.get('description') or '')}</td><td>{esc(p.get('hwid') or '')}</td></tr>" for p in mesh_ports) or '<tr><td colspan="3">No candidate ports detected.</td></tr>'
        mesh_state=mesh_latest.get('state') or mesh_deps.get('state') or 'not_tested'
        return message_box(msg)+f"""<h1>Detected Devices</h1><div class='notice'>Detection is honest: a serial row is only a candidate until a handshake/test succeeds.</div><section class='grid three'>{card('Catena State', f"mode={cfg.get('catena_demo_mode')} · port={cfg.get('catena_com_port') or 'none'}", '/admin/catena', state, 'orange', '📡')}{card('Meshtastic Bridge', f"dependency={mesh_deps.get('state')} · latest={mesh_state}", '/admin/devices/meshtastic', mesh_state, 'orange', '📶')}{card('Device Registry','Manual rows remain configured/unverified until tested.','/admin/devices','unverified','orange','🧾')}</section><h2>Serial candidates</h2><table><thead><tr><th>Port</th><th>Description</th><th>HWID</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table><h2>Meshtastic candidate ports</h2><table><thead><tr><th>Port</th><th>Description</th><th>HWID</th></tr></thead><tbody>{mesh_rows}</tbody></table><p><a class='button' href='/admin/catena'>Open Catena Test</a> <a class='button' href='/admin/devices/meshtastic'>Open Meshtastic Bridge</a></p>"""

    def page_meshtastic_admin(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        deps=meshtastic_dependency_status(); latest=meshtastic_latest_status(store); ports=meshtastic_candidate_ports()
        opts="<option value=''>Auto-detect / default</option>" + ''.join(f"<option value='{esc(p.get('device',''))}'>{esc(p.get('device',''))} · {esc(p.get('description',''))}</option>" for p in ports if p.get('device'))
        with store.connect() as conn: events=conn.execute('SELECT * FROM meshtastic_events ORDER BY created_at DESC LIMIT 30').fetchall()
        rows=[]
        for e in events:
            try: details=json.loads(e['details_json'])
            except Exception: details={}
            rows.append(f"<tr><td>{esc(e['created_at'])}</td><td>{esc(e['event_type'])}</td><td>{badge(e['state'])}</td><td><pre>{esc(json.dumps(details,indent=2,sort_keys=True))}</pre></td></tr>")
        install="<div class='warning'>Optional setup: <code>py -3 -m pip install -r requirements\\requirements_meshtastic.txt</code>. If no COM port appears, install the board USB serial driver and reconnect.</div>" if not deps.get('meshtastic_installed') or not deps.get('pyserial_installed') else "<div class='notice'>Meshtastic and pyserial imports are available. Plug in a node and run Probe Serial.</div>"
        return message_box(msg)+f"""<h1>Meshtastic Bridge</h1><div class='notice'>CommNet uses Meshtastic only for short low-bandwidth messages: ping, bulletin, mail notice, access request notice, and peer hints. No files, media, passwords, password hints, or session tokens are sent over mesh.</div><div class='mesh-status'><div class='kpi'><strong>{badge(deps.get('state','missing_dependency'))}</strong><span>dependency state</span></div><div class='kpi'><strong>{esc(deps.get('meshtastic_version') or 'not installed')}</strong><span>meshtastic package</span></div><div class='kpi'><strong>{esc(deps.get('pyserial_version') or 'not installed')}</strong><span>pyserial package</span></div><div class='kpi'><strong>{badge(latest.get('state','not_tested'))}</strong><span>latest live probe</span></div><div class='kpi'><strong>{esc(latest.get('nodes_seen',0))}</strong><span>nodes seen</span></div></div>{install}<form method='post' action='/admin/devices/meshtastic' class='formcard'><h2>Probe / Send Test</h2><label>Serial port<br><select name='port'>{opts}</select></label><label>Test message<br>{input_text('body','CMN1|PING|body=hello from CommNet',80,180)}</label><button type='submit' name='action' value='probe'>Probe Serial</button><button type='submit' name='action' value='send_text'>Send Test Text</button><button type='submit' name='action' value='fake'>Fake Smoke</button></form><h2>Checklist</h2><ol><li>Install optional dependencies.</li><li>Install CP210x/CH9102 serial driver if needed.</li><li>Plug in the node.</li><li>Probe serial.</li></ol><h2>Transcript</h2><table><thead><tr><th>Time</th><th>Event</th><th>State</th><th>Details</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="4">No Meshtastic events recorded yet.</td></tr>'}</tbody></table>"""



    def is_local_client(self) -> bool:
        addr = self.client_address[0] if self.client_address else ''
        return addr in ('127.0.0.1', '::1', 'localhost')

    def visitor_admin_blocked(self):
        body = """
        <h1>Admin is local-only</h1>
        <div class='notice'>This CommNet node presents the visitor CommWeb interface to LAN devices by default. Admin/configuration pages are available only from the local computer unless explicitly changed in a future security model.</div>
        <p><a href='/welcome'>Go to CommWeb landing</a> · <a href='/share'>Shared files</a> · <a href='/portal'>Portal</a></p>
        """
        _, store, audit, _, cfg = self._objects()
        return self.send_bytes(layout('Visitor Access Blocked', body, 'portal', cfg, '/welcome'), status=403)


    def serve_auth_get(self, path: str, query: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        us = UserStore(store, audit)
        msg = first(query, 'msg', '')
        if path == '/logout':
            us.revoke_session(self.session_id())
            return self.redirect_with_cookie('/welcome?msg=Logged%20out', clear=True)
        if path in ('/account', '/account/profile', '/account/icon', '/account/settings', '/account/security'):
            user = self.current_user(store, audit)
            if not user:
                return self.redirect('/login?msg=Please%20log%20in')
            profile = us.profile_for_user(user['user_id'])
            grants = us.grants_for_user(user['user_id'])
            icon_payload = self.account_icon_payload(user, store, audit)
            icon_preview_cls = 'generated' if icon_payload.get('icon_kind') == 'generated' else ''
            if path == '/account/profile':
                body = message_box(msg) + f"""
                <h1>Profile</h1>
                <div class='account-panel'>
                  <div class='account-profile-card'><div class='account-icon-preview {icon_preview_cls}'>{icon_payload.get('icon_html','○')}</div><strong>{esc(user.get('display_name'))}</strong><p class='muted'>@{esc(user.get('username'))} · {esc(user.get('role_id'))}</p></div>
                  <form method='post' action='/account/profile' class='formcard'>
                    <h2>Edit profile</h2>
                    <label>Display name<br>{input_text('display_name', user.get('display_name',''), 64, 64)}</label>
                    <label>About me<br>{textarea('about', profile.get('about',''), 5, 500)}</label>
                    <button type='submit'>Save Profile</button>
                  </form>
                </div>
                """
                return self.send_bytes(layout('Profile', body, 'portal', cfg, path))
            if path == '/account/icon':
                try:
                    icon = json.loads(profile.get('icon_json') or '{}')
                except Exception:
                    icon = {'glyph': (user.get('display_name') or '?')[:1].upper(), 'palette': 'commnet'}
                body = message_box(msg) + f"""
                <h1>Profile Icon</h1>
                <div class='notice'>A blank icon is used until you create or upload one. This run includes a local generated icon path; upload support remains conservative and non-executing.</div>
                <div class='account-panel'>
                  <div class='account-profile-card'><h2>Current icon</h2><div class='account-icon-preview {icon_preview_cls}'>{icon_payload.get('icon_html','○')}</div><p>Kind: <code>{esc(profile.get('icon_kind','blank'))}</code></p></div>
                  <form method='post' action='/account/icon' class='formcard'>
                    <h2>Create generated icon</h2>
                    <label>Glyph<br>{input_text('glyph', icon.get('glyph') or (user.get('display_name') or '?')[:1].upper(), 4, 2)}</label>
                    <label>Seed / note<br>{input_text('seed', icon.get('seed') or user.get('username',''), 32, 64)}</label>
                    <button type='submit' name='action' value='generate'>Generate Icon</button>
                    <button type='submit' name='action' value='blank'>Reset to Blank</button>
                  </form>
                </div>
                """
                return self.send_bytes(layout('Profile Icon', body, 'portal', cfg, path))
            if path == '/account/settings':
                ui = normalized_ui(cfg)
                body = message_box(msg) + f"""
                <h1>User Display Settings</h1>
                <div class='notice'>These are user-facing display settings. They use the same renderer as the Admin HUD so dark/light mode and density persist across Portal, Account, BBS, RetroWeb, Mail, and Emergency pages.</div>
                <form method='post' action='/account/settings' class='formcard'>
                  <label>Theme<br>{select('theme', UI_OPTIONS['theme'], ui['theme'])}</label>
                  <label>Card density<br>{select('card_density', UI_OPTIONS['card_density'], ui['card_density'])}</label>
                  <label>Icon mode<br>{select('icon_mode', UI_OPTIONS['icon_mode'], ui['icon_mode'])}</label>
                  <label>Unavailable guest apps<br>{select('show_unavailable_guest_apps', UI_OPTIONS['show_unavailable_guest_apps'], ui['show_unavailable_guest_apps'])}</label>
                  <button type='submit'>Save Display Settings</button>
                </form>
                <p><a href='/admin/settings/display'>Admin display settings</a> are available only to users with Admin HUD access.</p>
                """
                return self.send_bytes(layout('Display Settings', body, 'portal', cfg, path))
            if path == '/account/security':
                body = message_box(msg) + f"""
                <h1>Security</h1>
                <div class='notice'>Change your local CommNet password and hint. Passwords are stored as salted PBKDF2 hashes, not plaintext.</div>
                <form method='post' action='/account/security' class='formcard'>
                  <label>New password<br>{input_text('new_password','',40,128,'password')}</label>
                  <label>Password hint<br>{input_text('password_hint','',60,160)}</label>
                  <button type='submit'>Change Password</button>
                </form>
                """
                return self.send_bytes(layout('Security', body, 'portal', cfg, path))
            body = message_box(msg) + f"""
            <h1>Account</h1>
            <div class='summary'>Signed in as <strong>{esc(user.get('display_name'))}</strong> · role <code>{esc(user.get('role_id'))}</code></div>
            <section class='portal-grid'>
              {card('Profile','Display name, about text, and local profile details.','/account/profile','ready','amber','👤')}
              {card('Profile Icon','Blank, generated, or uploaded profile icon.','/account/icon','ready','amber','○')}
              {card('Display Settings','Theme, density, and user-facing visual preferences.','/account/settings','ready','amber','⚙️')}
              {card('Security','Change password and password hint.','/account/security','ready','red','🔐')}
              {card('Mail','Open your local CommNet mailbox.','/mail','ready','teal','✉️')}
              {card('Requests','Review your permission requests.','/account/requests','ready','purple','📨')}
            </section>
            <h2>Approved grants</h2><pre>{esc(json.dumps(grants, indent=2, sort_keys=True))}</pre>
            """
            return self.send_bytes(layout('Account', body, 'portal', cfg, path))
        if path == '/signup':
            bootstrap = us.bootstrap_needed()
            role_note = 'First account created locally becomes owner.' if bootstrap else 'New accounts default to guest/user until an admin grants more access.'
            body = message_box(msg) + f"""
            <h1>Create CommNet Account</h1>
            <div class='notice'>{esc(role_note)}</div>
            <form method='post' action='/signup' class='formcard'>
              <label>Username<br>{input_text('username','',32,32, placeholder='letters-numbers_.-')}</label>
              <label>Display name<br>{input_text('display_name','',40,64)}</label>
              <label>Password<br>{input_text('password','',40,128,'password')}</label>
              <label>Password hint<br>{input_text('password_hint','',60,160)}</label>
              <button type='submit'>Create Account</button>
            </form>
            <p><a href='/login'>Already have an account?</a></p>
            """
            return self.send_bytes(layout('Sign Up', body, 'portal', cfg, path))
        if path == '/account/request-reset':
            body = message_box(msg)+f"""
            <h1>Request Password Reset</h1>
            <form method='post' action='/account/request-reset' class='formcard'>
              <label>Username<br>{input_text('username','',32,32)}</label>
              <label>Note to admin<br>{textarea('note','',4,500)}</label>
              <button type='submit'>Request Reset</button>
            </form>
            """
            return self.send_bytes(layout('Password Reset', body, 'portal', cfg, path))
        body = message_box(msg)+f"""
        <h1>Login</h1>
        <form method='post' action='/login' class='formcard'>
          <label>Username<br>{input_text('username','',32,32)}</label>
          <label>Password<br>{input_text('password','',40,128,'password')}</label>
          <button type='submit'>Login</button>
        </form>
        <p><a href='/signup'>Create account</a> · <a href='/account/request-reset'>Request password reset</a></p>
        """
        return self.send_bytes(layout('Login', body, 'portal', cfg, path))

    def handle_auth_post(self, path: str, form: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        us = UserStore(store, audit)
        try:
            if path == '/signup':
                role = 'owner' if us.bootstrap_needed() and self.is_local_client() else cfg.get('default_guest_role','guest')
                user_id = us.create_user(first(form,'username'), first(form,'display_name'), first(form,'password'), role, first(form,'password_hint',''))
                user = us.authenticate(first(form,'username'), first(form,'password'), self.client_address[0] if self.client_address else '', self.headers.get('User-Agent',''))
                return self.redirect_with_cookie('/account?msg=Account%20created', user.get('session_id'))
            if path == '/login':
                user = us.authenticate(first(form,'username'), first(form,'password'), self.client_address[0] if self.client_address else '', self.headers.get('User-Agent',''))
                return self.redirect_with_cookie('/account?msg=Logged%20in', user.get('session_id'))
            if path == '/account/profile':
                user = self.current_user(store, audit)
                if not user:
                    return self.redirect('/login?msg=Login%20required')
                us.update_display_name(user['user_id'], first(form,'display_name',user.get('display_name','')))
                us.update_profile(user['user_id'], first(form,'about',''))
                return self.redirect('/account/profile?msg=Profile%20saved')
            if path == '/account/icon':
                user = self.current_user(store, audit)
                if not user:
                    return self.redirect('/login?msg=Login%20required')
                action = first(form, 'action', 'generate')
                if action == 'blank':
                    us.set_icon(user['user_id'], 'blank', '{}')
                else:
                    glyph = (first(form,'glyph') or (user.get('display_name') or '?')[:1].upper())[:2]
                    icon = {'glyph': glyph, 'seed': first(form,'seed',user.get('username',''))[:64], 'source': 'account_icon_generator'}
                    us.set_icon(user['user_id'], 'generated', json.dumps(icon, sort_keys=True))
                return self.redirect('/account/icon?msg=Profile%20icon%20saved')
            if path == '/account/settings':
                user = self.current_user(store, audit)
                if not user:
                    return self.redirect('/login?msg=Login%20required')
                ui = normalized_ui(cfg)
                for key in ('theme','card_density','icon_mode','show_unavailable_guest_apps'):
                    value = first(form, key, str(ui.get(key)))
                    if value in UI_OPTIONS[key]:
                        ui[key] = value
                cfg['ui'] = ui
                cfg_mgr.save(cfg, snapshot=True, reason='user_display_settings_update')
                audit.write('user_display_settings_updated', {'user_id': user.get('user_id'), 'theme': ui.get('theme'), 'density': ui.get('card_density')})
                return self.redirect('/account/settings?msg=Display%20settings%20saved')
            if path == '/account/security':
                user = self.current_user(store, audit)
                if not user:
                    return self.redirect('/login?msg=Login%20required')
                us.reset_password(user['user_id'], first(form,'new_password'), first(form,'password_hint',''))
                return self.redirect('/account/security?msg=Password%20changed')
            if path == '/account/request-reset':
                us.request_password_reset(first(form,'username'), first(form,'note',''))
                return self.redirect('/login?msg=Reset%20request%20sent%20to%20admin')
            if path == '/logout':
                us.revoke_session(self.session_id())
                return self.redirect_with_cookie('/welcome', clear=True)
        except AuthInputError as exc:
            return self.redirect(path + '?msg=' + quote(str(exc)))
        return self.redirect('/login')

    def serve_mail(self, path: str, query: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        us = UserStore(store, audit); ms = MailStore(store, audit)
        user = self.current_user(store, audit)
        if not user:
            return self.redirect('/login?msg=Login%20required%20for%20mail')
        msg = first(query, 'msg', '')
        if path.startswith('/mail/message/'):
            mid = path.split('/')[-1]
            m = ms.read(mid, user['user_id'])
            if not m:
                return self.send_bytes(layout('Mail Not Found', '<h1>Mail not found</h1>', 'portal', cfg, path), status=404)
            recips = ', '.join((r.get('display_name') or r.get('username') or r.get('recipient_user_id')) for r in m.get('recipients', []))
            body = f"<h1>{esc(m.get('subject'))}</h1><div class='summary'>From {esc(m.get('sender_name') or m.get('sender_user_id'))} · To {esc(recips)} · {esc(m.get('created_at'))}</div><pre>{esc(m.get('body'))}</pre><p><a href='/mail'>Back to inbox</a></p>"
            return self.send_bytes(layout('Mail Message', body, 'portal', cfg, path))
        if path.endswith('/compose'):
            users = [u for u in us.list_users() if u['user_id'] != user['user_id']]
            opts = ''.join(f"<option value='{esc(u['user_id'])}'>{esc(u['display_name'])} ({esc(u['username'])})</option>" for u in users)
            body = message_box(msg)+f"""
            <h1>Compose Mail</h1>
            <form method='post' action='/mail/compose' class='formcard'>
              <label>To<br><select name='recipient_user_id'>{opts}</select></label>
              <label>Subject<br>{input_text('subject','',80,160)}</label>
              <label>Body<br>{textarea('body','',8,5000)}</label>
              <button type='submit'>Send</button>
            </form>
            """
            return self.send_bytes(layout('Compose Mail', body, 'portal', cfg, path))
        inbox = ms.inbox(user['user_id'])
        sent = ms.sent(user['user_id']) if path.endswith('/sent') else []
        rows = ''.join(f"<tr><td>{esc(m.get('created_at'))}</td><td>{esc(m.get('sender_name') or m.get('sender_user_id'))}</td><td><a href='/mail/message/{esc(m.get('message_id'))}'>{esc(m.get('subject'))}</a></td><td>{'unread' if not m.get('read_at') else 'read'}</td></tr>" for m in inbox)
        srows = ''.join(f"<tr><td>{esc(m.get('created_at'))}</td><td>{esc(m.get('subject'))}</td></tr>" for m in sent)
        body = message_box(msg)+f"""
        <h1>Mail</h1>
        <div class='summary'>Signed in as {esc(user.get('display_name'))}. Unread: {ms.unread_count(user['user_id'])}</div>
        <p><a class='button' href='/mail/compose'>Compose</a> <a class='button secondary' href='/mail/sent'>Sent</a></p>
        <h2>Inbox</h2><table><thead><tr><th>Time</th><th>From</th><th>Subject</th><th>Status</th></tr></thead><tbody>{rows or '<tr><td colspan="4">No inbox mail.</td></tr>'}</tbody></table>
        {('<h2>Sent</h2><table><thead><tr><th>Time</th><th>Subject</th></tr></thead><tbody>'+ (srows or '<tr><td colspan="2">No sent mail.</td></tr>') + '</tbody></table>') if path.endswith('/sent') else ''}
        """
        return self.send_bytes(layout('Mail', body, 'portal', cfg, path))

    def handle_mail_post(self, path: str, form: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        user = self.current_user(store, audit)
        if not user:
            return self.redirect('/login?msg=Login%20required')
        if path == '/mail/compose':
            MailStore(store, audit).send(user['user_id'], [first(form,'recipient_user_id')], first(form,'subject'), first(form,'body'))
            return self.redirect('/mail?msg=Mail%20sent')
        return self.redirect('/mail')

    def serve_requests(self, path: str, query: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        us = UserStore(store, audit)
        user = self.current_user(store, audit)
        if not user:
            return self.redirect('/login?msg=Login%20required%20to%20request%20access')
        msg = first(query, 'msg', '')
        if path.endswith('/new') or path == '/requests':
            shares = ShareStore(store, audit, self.ctx['package_root']).list_shares(False)
            share_opts = ''.join(f"<option value='share:{esc(s['share_id'])}:share.{esc(s['share_id'])}.preview'>{esc(s['label'])} preview</option><option value='share:{esc(s['share_id'])}:share.{esc(s['share_id'])}.download'>{esc(s['label'])} download</option>" for s in shares)
            app_opts = """
              <option value='portal:retroweb:portal.retroweb.view'>RetroWeb access</option>
              <option value='portal:bbs:portal.bbs.view'>BBS access</option>
              <option value='mail:mail:mail.use'>Internal mail</option>
            """
            body = message_box(msg)+f"""
            <h1>Request More Access</h1>
            <form method='post' action='/requests/new' class='formcard'>
              <label>Request target<br><select name='target'>{share_opts}{app_opts}</select></label>
              <label>Reason<br>{textarea('reason','',5,500)}</label>
              <button type='submit'>Send Request to Admin</button>
            </form>
            <p><a href='/account/requests'>My requests</a></p>
            """
            return self.send_bytes(layout('Request Access', body, 'portal', cfg, path))
        rows=''.join(f"<tr><td>{esc(r.get('created_at'))}</td><td>{esc(r.get('target_type'))}</td><td>{esc(r.get('requested_permission'))}</td><td>{esc(r.get('status'))}</td><td>{esc(r.get('admin_response'))}</td></tr>" for r in us.list_permission_requests())
        body=message_box(msg)+"<h1>My Requests</h1><table><thead><tr><th>Created</th><th>Target</th><th>Permission</th><th>Status</th><th>Admin response</th></tr></thead><tbody>"+(rows or '<tr><td colspan="5">No requests yet.</td></tr>')+"</tbody></table>"
        return self.send_bytes(layout('My Requests', body, 'portal', cfg, path))

    def handle_requests_post(self, path: str, form: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        user = self.current_user(store, audit)
        if not user:
            return self.redirect('/login?msg=Login%20required')
        target = first(form, 'target')
        try:
            target_type, target_id, perm = target.split(':', 2)
        except ValueError:
            target_type, target_id, perm = 'general', '', 'request.review'
        UserStore(store, audit).create_permission_request(user['user_id'], target_type, target_id, perm, first(form,'reason',''))
        return self.redirect('/account/requests?msg=Request%20sent')

    def serve_public_app(self, path: str, query: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects(); user=self.current_user(store,audit)
        if path == '/help/join':
            links=build_link_set(cfg,[]); body=f"<h1>Join CommNet From Wi-Fi</h1><div class='notice'>Use the visitor URL, not 127.0.0.1. Your phone must be on the same router/Wi-Fi network and the computer firewall must allow Python on the local network.</div><ol><li>Connect to the CommNet router/Wi-Fi.</li><li>Open <code>{esc(links.get('visitor',''))}</code>.</li><li>If it fails, check Windows Firewall, router guest/client isolation, and whether LAN access is enabled.</li></ol><p><a href='/welcome'>Back to welcome</a></p>"
            return self.send_bytes(layout('Join Help', body, 'portal', cfg, path))
        if path.startswith('/retroweb'): return self.serve_retroweb(path, query or {}, store, audit, cfg, user)
        if path.startswith('/bbs'): return self.serve_bbs(path, query or {}, store, audit, cfg, user)
        if path == '/emergency':
            e=cfg.get('emergency_info') or {}; banner="<div class='error'>🚨 Outage / emergency mode is active.</div>" if e.get('outage_banner') else ''
            body=f"<h1>{esc(e.get('title','CommNet Emergency Info'))}</h1>{banner}<pre>{esc(e.get('body','No emergency bulletin has been posted by the admin.'))}</pre><p><a href='/portal'>Back to portal</a></p>"
            return self.send_bytes(layout('Emergency Info', body, 'portal', cfg, path))
        return self.not_found()

    def serve_bbs(self, path: str, query: dict[str, list[str]], store: SQLiteStore, audit: AuditLogger, cfg: dict, user: dict | None):
        bbs=BBSStore(store,audit); msg=first(query,'msg','')
        if path.startswith('/bbs/thread/'):
            tid=path.split('/')[-1]; thread=bbs.thread(tid)
            if not thread: return self.send_bytes(layout('BBS Thread Not Found','<h1>Thread not found</h1>','portal',cfg,path),status=404)
            posts=''.join(f"<article class='bbs-post'><div class='bbs-meta'>{esc(r.get('author_name') or ('system' if not r.get('author_user_id') else r.get('author_user_id')))} · {esc(r.get('created_at'))}</div><pre>{esc(r.get('body'))}</pre></article>" for r in bbs.replies(tid))
            reply_form=f"<form method='post' action='/bbs/reply/{esc(tid)}' class='formcard'><h2>Reply</h2><label>Body<br>{textarea('body','',5,5000)}</label><button>Reply</button></form>" if user and not int(thread.get('locked') or 0) else ("<div class='notice'><a href='/login'>Login</a> to reply.</div>" if not user else "<div class='warning'>This thread is locked.</div>")
            body=message_box(msg)+f"<h1>{esc(thread.get('title'))}</h1><div class='summary'>Board: <a href='/bbs/board/{esc(thread.get('board_id'))}'>{esc(thread.get('board_title'))}</a> · {badge('warning','Pinned') if int(thread.get('pinned') or 0) else ''} {badge('blocked','Locked') if int(thread.get('locked') or 0) else ''}</div>{posts}{reply_form}<p><a href='/bbs'>BBS home</a></p>"
            return self.send_bytes(layout('BBS Thread',body,'portal',cfg,path))
        board_id='general'
        if path.startswith('/bbs/board/'): board_id=path.split('/')[-1]
        board=bbs.board(board_id); boards=bbs.boards(); board_cards=''.join(card(b.get('title'),f"{b.get('description')} · {b.get('thread_count')} threads",f"/bbs/board/{b.get('board_id')}",'ready' if b.get('board_id')==board_id else 'guest_visible','teal','💬') for b in boards)
        threads=bbs.threads(board_id if board else None,50); thread_rows=''.join(f"<article class='bbs-thread'><h3><a href='/bbs/thread/{esc(t.get('thread_id'))}'>{'📌 ' if int(t.get('pinned') or 0) else ''}{esc(t.get('title'))}{' 🔒' if int(t.get('locked') or 0) else ''}</a></h3><div class='bbs-meta'>{esc(t.get('board_title'))} · by {esc(t.get('author_name') or 'system')} · {esc(t.get('reply_count'))} replies · {esc(t.get('last_reply_at') or t.get('created_at'))}</div></article>" for t in threads)
        if user:
            opts=''.join(f"<option value='{esc(b.get('board_id'))}' {'selected' if b.get('board_id')==board_id else ''}>{esc(b.get('title'))}</option>" for b in boards); form=f"<form method='post' action='/bbs/new' class='formcard'><h2>New thread</h2><label>Board<br><select name='board_id'>{opts}</select></label><label>Title<br>{input_text('title','',80,160)}</label><label>Body<br>{textarea('body','',6,5000)}</label><button>Post Thread</button></form>"
        else: form="<div class='notice'><a href='/login'>Login</a> to create BBS threads and replies.</div>"
        body=message_box(msg)+f"<h1>CommNet BBS</h1><div class='portal-hero'>Local boards, threads, replies, pinned posts, and outage-friendly messages.</div><h2>Boards</h2><div class='bbs-board-list'>{board_cards}</div><h2>{esc(board.get('title') if board else 'Recent Threads')}</h2>{thread_rows or '<div class=notice>No threads in this board yet.</div>'}{form}"
        return self.send_bytes(layout('BBS',body,'portal',cfg,path))

    def serve_retroweb(self, path: str, query: dict[str, list[str]], store: SQLiteStore, audit: AuditLogger, cfg: dict, user: dict | None):
        rw=RetroWebStore(store,audit); msg=first(query,'msg','')
        if not user:
            body=f"<h1>RetroWeb</h1><div class='notice'>RetroWeb is a separate local social/media platform reached through the CommNet portal. Log in first, then build a RetroWeb profile and icon.</div><section class='portal-grid'>{card('Log in to RetroWeb','Use your local CommNet account.','/login','needs_setup','indigo','🕹️')}{card('Request RetroWeb Access','Ask the admin to approve RetroWeb access.','/requests/new','ready','purple','📨')}</section>"
            return self.send_bytes(layout('RetroWeb',body,'portal',cfg,path))
        profile=rw.profile_for_user(user['user_id'])
        if path == '/retroweb/profile':
            icon=(profile or {}).get('icon_json') or dict(DEFAULT_ICON); palette_opts=''.join(f"<option value='{esc(k)}' {'selected' if icon.get('palette')==k else ''}>{esc(k.replace('_',' ').title())}</option>" for k in PALETTES); shape_opts=''.join(f"<option value='{esc(k)}' {'selected' if icon.get('shape')==k else ''}>{esc(k.title())}</option>" for k in ['orb','diamond','square','capsule']); pattern_opts=''.join(f"<option value='{esc(k)}' {'selected' if icon.get('pattern')==k else ''}>{esc(k.title())}</option>" for k in ['rings','grid','burst','plain'])
            body=message_box(msg)+f"<h1>RetroWeb Profile + Icon Generator</h1><div class='rw-profile-card'><h2>Current icon</h2>{render_icon(icon,88)} <strong>{esc((profile or {}).get('display_name') or user.get('display_name'))}</strong></div><form method='post' action='/retroweb/profile' class='formcard'><h2>Profile</h2><label>RetroWeb handle<br>{input_text('handle',(profile or {}).get('handle') or user.get('username',''),32,32)}</label><label>Display name<br>{input_text('display_name',(profile or {}).get('display_name') or user.get('display_name',''),64,64)}</label><label>About me<br>{textarea('about',(profile or {}).get('about',''),5,500)}</label><h2>Icon generator</h2><label>Palette<br><select name='palette'>{palette_opts}</select></label><label>Shape<br><select name='shape'>{shape_opts}</select></label><label>Glyph<br>{input_text('glyph',icon.get('glyph','★'),4,2)}</label><label>Pattern<br><select name='pattern'>{pattern_opts}</select></label><button>Save RetroWeb Profile</button></form><p><a href='/retroweb'>Back to RetroWeb</a></p>"
            return self.send_bytes(layout('RetroWeb Profile',body,'portal',cfg,path))
        profiles=rw.profiles(); feed=rw.feed(); profile_prompt=f"<div class='warning attention-amber'>RetroWeb profile not created yet. <a href='/retroweb/profile'>Create your profile and icon</a>.</div>" if not profile else f"<div class='rw-profile-card'>{render_icon(profile.get('icon_json'),72)}<strong>{esc(profile.get('display_name'))}</strong><div class='rw-meta'>@{esc(profile.get('handle'))}</div><p>{esc(profile.get('about'))}</p><p><a class='button secondary' href='/retroweb/profile'>Edit Profile/Icon</a></p></div>"
        gallery=''.join(f"<div class='rw-card'>{render_icon(p.get('icon_json'),48)}<strong>{esc(p.get('display_name'))}</strong><div class='rw-meta'>@{esc(p.get('handle'))}</div></div>" for p in profiles[:24]) or '<div class=notice>No RetroWeb profiles yet.</div>'
        post_form=f"<form method='post' action='/retroweb/post' class='formcard'><h2>Post to RetroWeb</h2><label>Message<br>{textarea('body','',4,1200)}</label><button>Post</button></form>" if profile else ''
        posts=[]
        for post in feed:
            comments=rw.comments_for(post.get('post_id')); comment_html=''.join(f"<div class='rw-comment'>{render_icon(c.get('icon_json'),28)}<strong>{esc(c.get('display_name') or c.get('handle') or 'user')}</strong><div>{esc(c.get('body'))}</div></div>" for c in comments); comment_form=f"<form method='post' action='/retroweb/comment' class='formcard'><input type='hidden' name='post_id' value='{esc(post.get('post_id'))}'><label>Comment<br>{input_text('body','',80,800)}</label><button>Comment</button></form>" if profile else ''
            posts.append(f"<article class='rw-post'>{render_icon(post.get('icon_json'),48)}<strong>{esc(post.get('display_name') or post.get('handle') or 'user')}</strong><div class='rw-meta'>{esc(post.get('created_at'))} · {esc(post.get('comment_count'))} comments</div><p>{esc(post.get('body'))}</p>{comment_html}{comment_form}</article>")
        body=message_box(msg)+f"<h1>RetroWeb Local Social</h1><div class='portal-hero'>Profile creation, generated icons, user gallery, posts, and comments are retained from the RetroWeb direction while keeping RetroWeb as a separate portal app.</div><div class='rw-shell'><aside>{profile_prompt}<h2>User Gallery</h2>{gallery}</aside><section><h2>Feed</h2>{post_form}<div class='rw-feed'>{''.join(posts) or '<div class=notice>No RetroWeb posts yet. Create the first post.</div>'}</div></section></div>"
        return self.send_bytes(layout('RetroWeb',body,'portal',cfg,path))

    def handle_public_app_post(self, path: str, form: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects(); user=self.current_user(store,audit)
        if path == '/bbs/new':
            if not user: return self.redirect('/login?msg=Login%20required')
            tid=BBSStore(store,audit).create_thread(first(form,'board_id','general'),first(form,'title','Untitled'),first(form,'body',''),user['user_id']); return self.redirect('/bbs/thread/'+tid+'?msg=Thread%20created')
        if path.startswith('/bbs/reply/'):
            if not user: return self.redirect('/login?msg=Login%20required')
            tid=path.split('/')[-1]; BBSStore(store,audit).reply(tid,first(form,'body',''),user['user_id']); return self.redirect('/bbs/thread/'+tid+'?msg=Reply%20posted')
        if path == '/retroweb/profile':
            if not user: return self.redirect('/login?msg=Login%20required')
            icon={'palette':first(form,'palette','arcade'),'shape':first(form,'shape','orb'),'glyph':first(form,'glyph','★'),'pattern':first(form,'pattern','rings')}; RetroWebStore(store,audit).create_or_update_profile(user['user_id'],first(form,'handle',user.get('username','')),first(form,'display_name',user.get('display_name','')),first(form,'about',''),icon); return self.redirect('/retroweb?msg=RetroWeb%20profile%20saved')
        if path == '/retroweb/post':
            if not user: return self.redirect('/login?msg=Login%20required')
            rw=RetroWebStore(store,audit)
            if not rw.profile_for_user(user['user_id']): return self.redirect('/retroweb/profile?msg=Create%20a%20RetroWeb%20profile%20first')
            rw.post(user['user_id'],first(form,'body','')); return self.redirect('/retroweb?msg=RetroWeb%20post%20created')
        if path == '/retroweb/comment':
            if not user: return self.redirect('/login?msg=Login%20required')
            rw=RetroWebStore(store,audit)
            if not rw.profile_for_user(user['user_id']): return self.redirect('/retroweb/profile?msg=Create%20a%20RetroWeb%20profile%20first')
            rw.comment(first(form,'post_id',''),user['user_id'],first(form,'body','')); return self.redirect('/retroweb?msg=Comment%20posted')
        return self.redirect('/portal')

    def serve_welcome(self, path: str):
        _, store, audit, cfg_mgr, cfg = self._objects()
        share_store = ShareStore(store, audit, self.ctx['package_root'])
        if path == '/captive/status':
            return self.send_json({'captive': False, 'user-portal-url': self.absolute_url('/welcome'), 'venue-info-url': self.absolute_url('/portal'), 'commnet': True, 'mode': 'captive_assist_guidance_only'})
        if path == '/captive':
            return self.redirect('/welcome')
        cards = ''.join([
            card('CommWeb Portal', 'Community entry point for this local node.', '/portal', 'visitor-default'),
            card('Shared Files', 'Browse only folders explicitly approved by the owner.', '/share', 'working'),
            card('About This Node', f"Node: {cfg.get('node_name')} · Visibility: {cfg.get('visibility_mode')}", '/portal', 'info'),
        ])
        body = f"""
        <h1>Welcome to CommWeb</h1>
        <div class='notice'>LAN visitors land here by default. Admin pages are blocked for non-local visitors.</div>
        <p>Node: <strong>{esc(cfg.get('node_name'))}</strong></p>
        <section class='grid'>{cards}</section>
        <h2>Current sharing posture</h2>
        <pre>{esc(json.dumps(share_store.summary(), indent=2, sort_keys=True))}</pre>
        """
        return self.send_bytes(layout('CommWeb Landing', body, 'portal', cfg, path))

    def absolute_url(self, path: str) -> str:
        host = self.headers.get('Host') or f"127.0.0.1:{self.server.server_address[1]}"
        return f"http://{host}{path}"

    def page_quick_setup(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        detected = detect_all()
        lan_urls = access_urls(detected['lan_addresses'], int(cfg.get('server_port', 8765)))
        drives = ''.join(f"<tr><td>{esc(d.get('label'))}</td><td><code>{esc(d.get('path'))}</code></td><td>{'yes' if d.get('readable') else 'no'}</td></tr>" for d in detected['drives'])
        folders = ''.join(f"<option value='{esc(f['path'])}'>{esc(f['name'])}: {esc(f['path'])}</option>" for f in detected['common_folders'])
        return message_box(msg) + f"""
        <h1>Quick Setup</h1>
        <div class='notice'>Recommended path: share one explicit folder, not an entire drive. LAN access remains off until you apply it here.</div>
        <h2>Detected computer</h2><pre>{esc(json.dumps(detected['computer'], indent=2))}</pre>
        <h2>Detected LAN URLs</h2><ul>{''.join(f'<li><code>{esc(u)}</code></li>' for u in lan_urls)}</ul>
        <h2>Detected storage</h2><table><thead><tr><th>Label</th><th>Path</th><th>Readable</th></tr></thead><tbody>{drives}</tbody></table>
        <form method='post' action='/admin/quick-setup' class='formcard'>
          <h2>Apply quick sharing configuration</h2>
          <label>Mode<br>{select('mode', ['private_only','share_one_folder','share_selected_folders','advanced_drive_share'], 'share_one_folder')}</label>
          <label>Recommended or selected folder<br><select name='root_path'>{folders}</select></label>
          <label>Share label<br>{input_text('label','CommNet Public',40,64)}</label>
          <label>Virtual name shown to visitors<br>{input_text('virtual_name','Public',40,64)}</label>
          <label>Permission profile<br>{select('permission_profile', ['list_only','list_and_download','dropbox_upload_only','list_download_upload_inbox'], 'list_and_download')}</label>
          {checkbox('lan_enabled', checked=False, label='Enable LAN access so devices on the same router/Wi-Fi can open CommWeb')}
          {checkbox('require_access_code', checked=True, label='Require local visitor access code')}
          <label>Optional access code<br>{input_text('access_code','',30,64)}</label>
          <div class='warning'>Enabling LAN access binds CommNet to the local network. Do not enable this on public or untrusted Wi-Fi. Visitors see CommWeb/share, not admin.</div>
          <button type='submit'>Apply Quick Setup</button>
        </form>
        """

    def page_lan(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        detected = detect_all()
        urls = access_urls(detected['lan_addresses'], int(cfg.get('server_port',8765)))
        return message_box(msg) + f"""
        <h1>LAN Access</h1>
        <div class='notice'>Workflow: laptop Ethernet to router, second device on router Wi-Fi, open the visitor URL below.</div>
        <p>Current LAN access: <strong>{esc(cfg.get('lan_access_mode'))}</strong>. Server host config: <code>{esc(cfg.get('server_host'))}</code></p>
        <h2>Visitor URLs</h2><ul>{''.join(f'<li><code>{esc(u)}</code></li>' for u in urls)}</ul>
        <form method='post' action='/admin/lan' class='formcard'>
          {checkbox('lan_enabled', checked=bool(cfg.get('lan_access_enabled')), label='Allow devices on my local network to access CommNet visitor pages')}
          <div class='warning'>This exposes only visitor-safe CommWeb/share routes by default. Admin/config/API routes remain localhost-only.</div>
          <button type='submit'>Save LAN Access Mode</button>
        </form>
        <h2>Likely troubleshooting</h2><ul><li>Windows Firewall may block Python.</li><li>Guest Wi-Fi/client isolation may block Wi-Fi-to-Ethernet access.</li><li>Use the LAN IP, not 127.0.0.1, from the phone.</li></ul>
        <p><a href='/admin/captive-assist'>Captive Portal Assist</a></p>
        """

    def page_shares(self, store: SQLiteStore, audit: AuditLogger, msg: str = '') -> str:
        ss = ShareStore(store, audit, self.ctx['package_root'])
        behaviors = ['invisible','count_only','list_only','preview_only','download','upload_inbox','admin_only']
        rows = []
        for s in ss.list_shares(False):
            rows.append(f"""
            <tr>
              <td>{esc(s['label'])}<br><span class='muted'><code>/{esc(s['virtual_name'])}</code></span></td>
              <td>{esc(s.get('visibility_mode'))}</td><td>{esc(s.get('permission_profile'))}</td><td>{esc(s.get('visibility_behavior') or 'download')}</td>
              <td>{'yes' if s.get('enabled') else 'no'}</td><td>{'yes' if s.get('allow_preview') else 'no'}</td><td>{'yes' if s.get('require_access_code') else 'no'}</td>
              <td><form method='post' action='/admin/shares'>
                <input type='hidden' name='action' value='policy'><input type='hidden' name='share_id' value='{esc(s['share_id'])}'>
                {select('visibility_mode', ['private','lan_visible','approved_peers','community_visible'], s.get('visibility_mode','private'))}
                {select('visibility_behavior', behaviors, s.get('visibility_behavior') or 'download')}
                {select('permission_profile', ['private','list_only','preview_only','list_and_download','dropbox_upload_only','list_download_upload_inbox','advanced_custom'], s.get('permission_profile','list_and_download'))}
                {checkbox('enabled', checked=bool(s.get('enabled')), label='Enabled')}
                {checkbox('require_access_code', checked=bool(s.get('require_access_code')), label='Code')}
                {checkbox('allow_preview', checked=bool(s.get('allow_preview')), label='Preview')}
                <button type='submit'>Save</button>
              </form><form method='post' action='/admin/shares'><input type='hidden' name='action' value='delete'><input type='hidden' name='share_id' value='{esc(s['share_id'])}'><button type='submit'>Remove</button></form></td>
            </tr>""")
        return message_box(msg) + f"""
        <h1>Share HUD</h1>
        <div class='notice'>Only explicit share roots can be served. Physical paths are hidden from visitors. Use behavior modes to control whether a share is invisible, count-only, list-only, preview-only, downloadable, upload-inbox, or admin-only.</div>
        <p><a class='button safe' href='/admin/shares/new'>Add Shared Folder</a> <a class='button secondary' href='/share'>Preview visitor share page</a></p>
        <form method='post' action='/admin/shares' class='formcard'>
          <input type='hidden' name='action' value='add'>
          <h2>Fast manual add</h2>
          <label>Label<br>{input_text('label','CommNet Public',40,64)}</label>
          <label>Folder path<br>{input_text('root_path','',80,260)}</label>
          <label>Virtual name<br>{input_text('virtual_name','Public',40,64)}</label>
          <label>Visibility<br>{select('visibility_mode', ['private','lan_visible','approved_peers','community_visible'], 'private')}</label>
          <label>Behavior<br>{select('visibility_behavior', behaviors, 'preview_only')}</label>
          <label>Permission profile<br>{select('permission_profile', ['private','list_only','preview_only','list_and_download','dropbox_upload_only','list_download_upload_inbox','advanced_custom'], 'preview_only')}</label>
          {checkbox('enabled', checked=False, label='Enable this share')}
          {checkbox('require_access_code', checked=True, label='Require access code')}
          {checkbox('allow_preview', checked=True, label='Allow safe preview')}
          <button type='submit'>Add Share Root</button>
        </form>
        <h2>Configured shares</h2><table><thead><tr><th>Label</th><th>Visibility</th><th>Profile</th><th>Behavior</th><th>Enabled</th><th>Preview</th><th>Code</th><th>Actions</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="8">No shares yet.</td></tr>'}</tbody></table>
        """

    def page_landing(self, cfg: dict, msg: str = '') -> str:
        return message_box(msg) + f"""
        <h1>CommWeb Landing</h1>
        <p>Root path <code>/</code> redirects LAN visitors to <code>/welcome</code>, which links to <code>/portal</code> and <code>/share</code>.</p>
        <p>Admin localhost-only: <code>{esc(cfg.get('admin_localhost_only'))}</code></p>
        """

    def page_captive_assist(self, cfg: dict, msg: str = '') -> str:
        detected = detect_all(); urls = access_urls(detected['lan_addresses'], int(cfg.get('server_port',8765)))
        return message_box(msg) + f"""
        <h1>Captive Portal Assist</h1>
        <div class='notice'>This run provides landing/captive-assist endpoints and router guidance. It does not reconfigure arbitrary routers or force all Wi-Fi users to CommWeb.</div>
        <h2>Landing URLs for router configuration</h2><ul>{''.join(f'<li><code>{esc(u)}</code></li>' for u in urls)}</ul>
        <p>Assist endpoints: <code>/captive</code>, <code>/captive/status</code>, <code>/.well-known/commnet-captive</code> if added by a future router integration.</p>
        <p>True captive portal mode requires router/gateway control such as OpenWrt/NoDogSplash or equivalent DHCP/DNS/firewall behavior.</p>
        """

    def page_visitor_access(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        ss = ShareStore(store, None, self.ctx['package_root'])
        return message_box(msg) + f"""
        <h1>Visitor Access / Security Posture</h1>
        <pre>{esc(json.dumps({'lan_access_enabled': cfg.get('lan_access_enabled'), 'lan_access_mode': cfg.get('lan_access_mode'), 'admin_localhost_only': cfg.get('admin_localhost_only'), 'share_summary': ss.summary()}, indent=2, sort_keys=True))}</pre>
        """



    def page_network_paths(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        paths = detect_network_paths(int(cfg.get('server_port', 8765)))
        store.upsert_network_paths(paths)
        selected = selected_or_best_path(cfg, paths)
        rows = []
        for p in paths:
            badge = p.get('classification')
            checked_attr = ' checked' if selected and selected.get('path_id') == p.get('path_id') else ''
            rows.append(
                "<tr>"
                f"<td><input type='radio' name='path_id' value='{esc(p.get('path_id'))}'{checked_attr}></td>"
                f"<td>{esc(p.get('adapter_name'))}</td>"
                f"<td><code>{esc(p.get('ipv4_address'))}</code></td>"
                f"<td><code>{esc(p.get('gateway'))}</code></td>"
                f"<td><span class='badge'>{esc(badge)}</span></td>"
                f"<td>{esc(p.get('reason'))}</td>"
                f"<td><code>{esc(p.get('suggested_url'))}</code></td>"
                "</tr>"
            )
        selected_html = '<div class="notice">No valid visitor network selected yet.</div>'
        if selected:
            selected_html = f"<div class='notice'>Selected/recommended visitor path: <strong>{esc(selected.get('adapter_name'))}</strong> · <code>{esc(selected.get('ipv4_address'))}</code> · gateway <code>{esc(selected.get('gateway'))}</code><br>Visitor URL: <code>{esc(selected.get('suggested_url'))}</code></div>"
        return message_box(msg) + f"""
        <h1>Network Path Selector</h1>
        {selected_html}
        <div class='warning'>CommNet will not recommend self-assigned <code>169.254.x.x</code> addresses as normal visitor links. Those usually mean the router did not provide DHCP on that adapter.</div>
        <form method='post' action='/admin/network-paths' class='formcard'>
          <table><thead><tr><th>Use</th><th>Adapter</th><th>IPv4</th><th>Gateway/router</th><th>Status</th><th>Reason</th><th>Suggested URL</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="7">No network paths detected.</td></tr>'}</tbody></table>
          <button type='submit'>Use Selected Network For Visitor Links</button>
        </form>
        <p><a href='/admin/share-links'>Copy links using selected path</a> · <a href='/admin/lan'>LAN settings</a></p>
        """

    def page_site_map(self, visitor: bool = False) -> str:
        sections = []
        for title, items in SITE_MAP.items():
            links = ''.join(f"<li><a href='{esc(href)}'>{esc(href)}</a> — {esc(desc)}</li>" for href, desc in items)
            sections.append(f"<h2>{esc(title)}</h2><ul>{links}</ul>")
        return "<h1>CommNet Site Map</h1><div class='notice'>This page shows the admin, visitor, and demo structure so navigation is explicit.</div><div class='sitemap'>" + ''.join(sections) + "</div>"

    def page_network_wizard(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        paths = detect_network_paths(int(cfg.get('server_port', 8765)))
        selected = selected_or_best_path(cfg, paths)
        links = build_link_set(cfg, [])
        checks = [
            ('Server running', True),
            ('Valid network path selected/recommended', bool(selected)),
            ('Selected path is not APIPA', bool(selected and not is_apipa(str(selected.get('ipv4_address'))))),
            ('LAN access enabled', bool(cfg.get('lan_access_enabled'))),
            ('Visitor landing route active', bool(cfg.get('commweb_landing_enabled'))),
            ('Admin localhost-only', bool(cfg.get('admin_localhost_only'))),
        ]
        check_html = ''.join(f"<span class='badge {'okbadge' if ok else 'dangerbadge'}'>{esc(label)}: {'yes' if ok else 'no'}</span>" for label, ok in checks)
        selected_box = '<div class="warning">No valid network path selected. Open Network Paths first.</div>'
        if selected:
            selected_box = f"<div class='notice'>Using <strong>{esc(selected.get('adapter_name'))}</strong> at <code>{esc(selected.get('ipv4_address'))}</code> via router <code>{esc(selected.get('gateway'))}</code>. Visitor URL: <code>{esc(links['visitor'])}</code></div>"
        return message_box(msg) + f"""
        <h1>Network Setup Wizard</h1>
        <div class='notice'>Goal: laptop connected to router, another device on router Wi-Fi, visitor opens the CommWeb link and never sees admin by default.</div>
        {selected_box}
        <div class='bigstep'><strong>1.</strong> Open <a href='/admin/network-paths'>Network Paths</a> and choose the Wi-Fi/Ethernet path that the visitor will use.</div>
        <div class='bigstep'><strong>2.</strong> Enable LAN access from <a href='/admin/lan'>LAN settings</a> if visitors should connect from another device.</div>
        <div class='bigstep'><strong>3.</strong> Use <a href='/admin/quick-setup'>Quick Setup</a> to choose one explicit share folder.</div>
        <div class='bigstep'><strong>4.</strong> Send the visitor this URL: <code>{esc(links['visitor'])}</code></div>
        <div class='bigstep'><strong>5.</strong> Verify the visitor sees <a href='/welcome'>CommWeb</a> or <a href='/share'>Shared Files</a>, not <code>/admin</code>.</div>
        <h2>Readiness checklist</h2><p>{check_html}</p>
        <h2>Copy-ready invite</h2><textarea readonly rows='5'>{esc(links['peer_invite_text'])}</textarea>
        <p><a class='button' href='/admin/share-links'>Open all copyable links</a> · <a href='/admin/network-paths'>Choose network path</a> · <a href='/admin/shares'>Shares</a></p>
        """

    def page_share_links(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        paths = detect_network_paths(int(cfg.get('server_port', 8765)))
        selected = selected_or_best_path(cfg, paths)
        links = build_link_set(cfg, [])
        def copybox(label, value):
            return f"<h2>{esc(label)}</h2><div class='copybox'><textarea readonly rows='2'>{esc(value)}</textarea><button type='button' onclick=\"navigator.clipboard&&navigator.clipboard.writeText(this.parentElement.querySelector('textarea').value)\">Copy</button></div>"
        status = '<div class="warning">No valid selected network path. Links may fall back to localhost until you choose one.</div>'
        if selected:
            status = f"<div class='notice'>Links are based on selected path: <strong>{esc(selected.get('adapter_name'))}</strong> · <code>{esc(selected.get('ipv4_address'))}</code>. {esc(selected.get('reason'))}</div>"
        boxes = [
            copybox('Visitor landing page', links['visitor']),
            copybox('CommWeb portal', links['portal']),
            copybox('Shared files', links['share']),
            copybox('Admin local-only URL', links['admin_local']),
            copybox('Peer invite text', links['peer_invite_text']),
            copybox('Node card JSON', json.dumps(links['node_card'], indent=2, sort_keys=True)),
        ]
        return message_box(msg) + "<h1>Copyable CommNet Links</h1>" + status + "<div class='notice'>These links are LAN-only unless a gateway is configured. Send them to people on the same Wi-Fi/router/network path.</div><p><a href='/admin/network-paths'>Change selected network path</a></p>" + ''.join(boxes)

    def page_catena_admin(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        ports = list_serial_ports()
        port_opts = ''.join(f"<option value='{esc(p['device'])}' {'selected' if p['device']==cfg.get('catena_com_port') else ''}>{esc(p['device'] or '(none)')} — {esc(p.get('description',''))}</option>" for p in ports)
        adapter = make_adapter_from_config(cfg)
        events = store.catena_events_recent(10)
        evrows = ''.join(f"<tr><td>{esc(e['created_at'])}</td><td>{esc(e['direction'])}</td><td>{esc(e['parsed_type'])}</td><td>{esc(e['result'])}</td><td><code>{esc(e['line_text_redacted'])}</code></td></tr>" for e in events)
        return message_box(msg) + f"""
        <h1>Catena USB Serial LoRa Messenger</h1>
        <div class='notice'>This is a generic Catena serial LoRa adapter. It is not Meshtastic. Fake mode works without hardware.</div>
        <pre>{esc(json.dumps(adapter.status(), indent=2, sort_keys=True))}</pre>
        <form method='post' action='/admin/catena' class='formcard'>
          <input type='hidden' name='action' value='save'>
          {checkbox('catena_adapter_enabled', checked=bool(cfg.get('catena_adapter_enabled')), label='Enable Catena adapter profile')}
          <label>Mode<br>{select('catena_demo_mode', ['fake_until_configured','real_serial'], cfg.get('catena_demo_mode','fake_until_configured'))}</label>
          <label>COM port<br><select name='catena_com_port'>{port_opts}</select></label>
          <label>Baud rate<br>{input_text('catena_baud_rate', str(cfg.get('catena_baud_rate',115200)), 16, 12)}</label>
          <label>ACK timeout ms<br>{input_text('catena_ack_timeout_ms', str(cfg.get('catena_ack_timeout_ms',3000)), 16, 12)}</label>
          <label>Payload limit chars<br>{input_text('catena_payload_limit', str(cfg.get('catena_payload_limit',180)), 16, 12)}</label>
          <button type='submit'>Save Catena Config</button>
        </form>
        <h2>Demo actions</h2>
        <form method='post' action='/admin/catena' class='formcard'>
          <label>Test body<br>{input_text('body','Hello from CommNet over Catena',70,180)}</label>
          <button name='action' value='ping'>PING</button>
          <button name='action' value='id'>ID?</button>
          <button name='action' value='status'>STATUS?</button>
          <button name='action' value='cfg'>CFG us915_test</button>
          <button name='action' value='tx'>TX text message</button>
        </form>
        <div class='warning'>A Catena ACK means local hardware accepted the command. It is not remote RF delivery unless RX/REMOTE_ACK is returned.</div>
        <h2>Recent Catena events</h2><table><thead><tr><th>Time</th><th>Direction</th><th>Type</th><th>Result</th><th>Line/details</th></tr></thead><tbody>{evrows or '<tr><td colspan="5">No Catena events yet.</td></tr>'}</tbody></table>
        <p><a href='/demo/catena'>Open visitor/demo view</a> · <a href='/admin/catena-transcript'>Catena transcript</a> · <a href='/admin/catena-hardware'>Hardware page</a></p>
        """


    def page_catena_transcript(self, store: SQLiteStore, msg: str = '') -> str:
        events = store.catena_events_recent(50)
        rows = ''.join(f"<tr><td>{esc(e.get('created_at'))}</td><td>{esc(e.get('port'))}</td><td>{esc(e.get('direction'))}</td><td>{esc(e.get('parsed_type'))}</td><td>{esc(e.get('result'))}</td><td><code>{esc(e.get('line_text_redacted'))}</code></td><td>{esc(e.get('error'))}</td></tr>" for e in events)
        return message_box(msg) + "<h1>Catena Transcript</h1><p>This is a redacted transcript summary. ACK is local hardware ACK unless RX/REMOTE_ACK is observed.</p><table><thead><tr><th>Time</th><th>Port</th><th>Direction</th><th>Type</th><th>Result</th><th>Line/details</th><th>Error</th></tr></thead><tbody>" + (rows or '<tr><td colspan="7">No Catena events yet.</td></tr>') + '</tbody></table>'

    def page_catena_demo(self, query: dict | None = None) -> str:
        _, store, audit, cfg_mgr, cfg = self._objects()
        adapter = make_adapter_from_config(cfg)
        return f"""
        <h1>Catena Serial LoRa Demo</h1>
        <div class='notice'>Demo status: fake serial mode works without hardware; real serial mode requires pyserial and configured Catena firmware.</div>
        <pre>{esc(json.dumps(adapter.status(), indent=2, sort_keys=True))}</pre>
        <p>Use <a href='/admin/catena'>Admin / Catena</a> from the local computer to configure the COM port and send test messages.</p>
        <h2>Delivery semantics</h2>
        <p><strong>ACK</strong> = local Catena accepted the command. <strong>RX/REMOTE_ACK</strong> = evidence of RF receipt.</p>
        """

    def page_setup(self, cfg: dict, msg: str = '') -> str:
        return message_box(msg) + f"""
        <h1>First Run Setup</h1>
        <p>This single-page wizard applies changes only when you click Apply Setup.</p>
        <form method='post' action='/admin/setup' class='formcard'>
          <h2>Node identity</h2>
          <label>Node name<br>{input_text('node_name', cfg.get('node_name',''), 60, 64)}</label>
          <label>Admin display name<br>{input_text('admin_display_name', cfg.get('admin_display_name',''), 60, 64)}</label>
          <label>Location label<br>{input_text('location_label', cfg.get('location_label',''), 60, 64)}</label>
          <label>Description<br>{textarea('node_description', cfg.get('node_description',''), 4, 500)}</label>
          <h2>Profile and privacy</h2>
          <label>Deployment profile<br>{select('deployment_profile', DEPLOYMENT_PROFILES, cfg.get('deployment_profile'))}</label>
          <label>Node role<br>{select('node_role', NODE_ROLES, cfg.get('node_role'))}</label>
          <label>Privacy mode<br>{select('privacy_mode', PRIVACY_MODES, cfg.get('privacy_mode'))}</label>
          <label>Visibility mode<br>{select('visibility_mode', VISIBILITY_MODES, cfg.get('visibility_mode'))}</label>
          <h2>Desired communication profiles</h2>
          {self.transport_checkboxes(cfg)}
          <h2>Services visible in portal</h2>
          {self.service_checkboxes(cfg)}
          <p><button type='submit'>Apply Setup</button></p>
        </form>
        """

    def page_profile(self, cfg: dict, msg: str = '') -> str:
        return message_box(msg) + f"""
        <h1>Node Profile</h1>
        <form method='post' action='/admin/profile' class='formcard'>
          <label>Node name<br>{input_text('node_name', cfg.get('node_name',''), 60, 64)}</label>
          <label>Admin display name<br>{input_text('admin_display_name', cfg.get('admin_display_name',''), 60, 64)}</label>
          <label>Location label<br>{input_text('location_label', cfg.get('location_label',''), 60, 64)}</label>
          <label>Description<br>{textarea('node_description', cfg.get('node_description',''), 4, 500)}</label>
          <label>Deployment profile<br>{select('deployment_profile', DEPLOYMENT_PROFILES, cfg.get('deployment_profile'))}</label>
          <label>Node role<br>{select('node_role', NODE_ROLES, cfg.get('node_role'))}</label>
          <button type='submit'>Save Profile</button>
        </form>
        """

    def page_privacy(self, cfg: dict, msg: str = '') -> str:
        return message_box(msg) + f"""
        <h1>Privacy and Visibility</h1>
        <div class='notice'>Default posture is private/local-only. Changing visibility does not publish files by itself.</div>
        <form method='post' action='/admin/privacy' class='formcard'>
          <label>Privacy mode<br>{select('privacy_mode', PRIVACY_MODES, cfg.get('privacy_mode'))}</label>
          <label>Visibility mode<br>{select('visibility_mode', VISIBILITY_MODES, cfg.get('visibility_mode'))}</label>
          <button type='submit'>Save Privacy Settings</button>
        </form>
        <h2>Current meaning</h2><p><strong>{esc(visibility_label(cfg.get('visibility_mode')))}</strong></p>
        <p>Your node remains local/private unless you explicitly choose wider visibility and later enable a working transport profile.</p>
        """

    def service_checkboxes(self, cfg: dict) -> str:
        services = cfg.get('services') or {}
        rows = []
        for sid in SERVICE_IDS:
            data = services.get(sid, {})
            rows.append(f"<tr><td>{esc(SERVICE_LABELS.get(sid, sid))}<input type='hidden' name='service_id' value='{esc(sid)}'></td>"
                        f"<td>{checkbox('svc_enabled_' + sid, checked=bool(data.get('enabled')), label='Enabled')}</td>"
                        f"<td>{checkbox('svc_visible_' + sid, checked=bool(data.get('visible_in_portal')), label='Visible')}</td>"
                        f"<td>{checkbox('svc_review_' + sid, checked=bool(data.get('requires_review')), label='Review')}</td></tr>")
        return "<table><thead><tr><th>Service</th><th>Enabled</th><th>Portal</th><th>Review</th></tr></thead><tbody>" + ''.join(rows) + '</tbody></table>'

    def page_services(self, cfg: dict, msg: str = '') -> str:
        return message_box(msg) + f"""
        <h1>Services</h1>
        <p>Disabled services are hidden from the CommNet portal. Nothing here enables real peer publishing yet.</p>
        <form method='post' action='/admin/services' class='formcard'>
          {self.service_checkboxes(cfg)}
          <button type='submit'>Save Services</button>
        </form>
        """

    def transport_checkboxes(self, cfg: dict) -> str:
        desired = set(cfg.get('desired_transport_profiles') or [])
        return '<div class="checks">' + ''.join(checkbox('transport_profile', tp, tp in desired, tp.replace('_',' ').title()) for tp in TRANSPORT_PROFILES) + '</div>'

    def page_transports(self, store: SQLiteStore, audit: AuditLogger, cfg: dict, msg: str = '') -> str:
        peers = PeerStore(store, audit)
        registry = build_default_registry(peers)
        statuses = registry.statuses()
        deps = check_all_dependencies(store)
        dep_rows = []
        for d in deps:
            dep_rows.append('<tr><td><code>'+esc(d['package_name'])+'</code></td><td><code>'+esc(d['import_name'])+'</code></td><td>'+('yes' if d['installed'] else 'no')+'</td><td>'+esc(d.get('version') or '')+'</td><td>'+esc(d.get('profile',''))+'</td></tr>')
        body = message_box(msg) + '<h1>Transport Profiles and Adapter Status</h1>'
        body += '<p>Loopback and manually configured LAN HTTP tests are implemented. Meshtastic, Reticulum/LXMF, Bluetooth, storage nodes, and data-mule carriers are dependency/status aware but not active hardware transports yet.</p>'
        body += "<form method='post' action='/admin/transports' class='formcard'><h2>Desired profiles</h2>" + self.transport_checkboxes(cfg) + "<button type='submit'>Save Desired Profiles</button></form>"
        body += '<h2>Adapter status</h2>' + status_table(statuses)
        body += '<h2>Dependency probes</h2><table><thead><tr><th>Package</th><th>Import</th><th>Installed</th><th>Version</th><th>Profile</th></tr></thead><tbody>' + ''.join(dep_rows) + '</tbody></table>'
        body += "<p><button onclick='runLoopback()'>Run loopback self-test</button></p><pre id='loopback-output'></pre>"
        return body

    def page_network(self, store: SQLiteStore, cfg: dict, msg: str = '') -> str:
        peers = PeerStore(store).list()
        counts = store.table_counts()
        attempts = store.delivery_attempts_recent(8)
        routes = store.route_decisions_recent(8)
        dep = check_all_dependencies(store)
        dep_missing = [d['package_name'] for d in dep if not d['installed']]
        rows = ''.join('<tr><td>'+esc(a.get('started_at') or a.get('created_at'))+'</td><td><code>'+esc(a.get('adapter_id'))+'</code></td><td>'+esc(a.get('result'))+'</td><td>'+esc(a.get('error'))+'</td></tr>' for a in attempts)
        rrows = ''.join('<tr><td>'+esc(r.get('created_at'))+'</td><td><code>'+esc(r.get('chosen_adapter'))+'</code></td><td>'+esc(r.get('reason'))+'</td></tr>' for r in routes)
        body = message_box(msg) + '<h1>Network Dashboard</h1>'
        body += '<div class="notice">Safe default: server binds to <code>'+esc(cfg.get('lan_bind_host','127.0.0.1'))+'</code>; inbound peer messages are '+esc(str(cfg.get('allow_inbound_peer_messages', False)))+'.</div>'
        body += '<section class="grid two">'
        body += card('Peers', str(len(peers))+' manual peers registered.', '/admin/peers', 'working')
        body += card('Messages', str(counts.get('messages',0))+' messages in SQLite queue/history.', '/admin/messages', 'working')
        body += card('Delivery Attempts', str(counts.get('delivery_attempts',0))+' attempts recorded.', '/admin/messages', 'working')
        body += card('Missing Optional Dependencies', ', '.join(dep_missing[:4]) if dep_missing else 'All probed optional packages installed.', '/admin/transports', 'status')
        body += '</section>'
        body += '<h2>Recent delivery attempts</h2><table><thead><tr><th>Time</th><th>Adapter</th><th>Result</th><th>Error</th></tr></thead><tbody>'+(rows or '<tr><td colspan="4">No delivery attempts yet.</td></tr>')+'</tbody></table>'
        body += '<h2>Recent route decisions</h2><table><thead><tr><th>Time</th><th>Chosen</th><th>Reason</th></tr></thead><tbody>'+(rrows or '<tr><td colspan="3">No route decisions yet.</td></tr>')+'</tbody></table>'
        return body

    def page_peers(self, store: SQLiteStore, audit: AuditLogger, msg: str = '') -> str:
        peers = PeerStore(store, audit).list()
        rows=[]
        for peer in peers:
            rows.append('<tr><td>'+esc(peer.get('display_name'))+'</td><td><code>'+esc(peer.get('base_url'))+'</code></td><td>'+esc(peer.get('trust_state'))+'</td><td>'+esc(peer.get('last_status'))+'</td><td><form method="post" action="/admin/peers"><input type="hidden" name="peer_id" value="'+esc(peer.get('peer_id'))+'"><button name="action" value="test">Test</button> <button name="action" value="trust">Trust</button> <button name="action" value="block">Block</button> <button name="action" value="delete">Remove</button></form></td></tr>')
        form = """<form method='post' action='/admin/peers' class='formcard'><input type='hidden' name='action' value='add'>
        <label>Display name<br><input name='display_name' maxlength='64'></label>
        <label>Base URL<br><input name='base_url' size='60' maxlength='260' placeholder='http://127.0.0.1:8766'></label>
        <label>Trust state<br>""" + select('trust_state', PEER_TRUST_STATES, 'known') + """</label>
        <label>Notes<br><textarea name='notes' rows='3' maxlength='500'></textarea></label><button type='submit'>Add Peer</button></form>"""
        return message_box(msg) + '<h1>Peer Nodes</h1><p>Manual peer registration is working. Automatic LAN discovery is deferred.</p><h2>Add peer</h2>'+form+'<h2>Registered peers</h2><table><thead><tr><th>Name</th><th>URL</th><th>Trust</th><th>Handshake</th><th>Action</th></tr></thead><tbody>'+(''.join(rows) or '<tr><td colspan="5">No peers yet.</td></tr>')+'</tbody></table>'

    def page_messages(self, store: SQLiteStore, audit: AuditLogger, msg: str = '') -> str:
        peers = PeerStore(store, audit).list()
        messages = store.messages_recent(20)
        attempts = store.delivery_attempts_recent(20)
        peer_opts = "<option value='self'>Local loopback</option>" + ''.join("<option value='"+esc(p['peer_id'])+"'>"+esc(p['display_name'])+"</option>" for p in peers)
        mrows = ''.join('<tr><td>'+esc(m.get('created_at'))+'</td><td><code>'+esc(m.get('message_id'))+'</code></td><td>'+esc(m.get('payload_class'))+'</td><td>'+esc(m.get('target') or m.get('destination'))+'</td><td>'+esc(m.get('status'))+'</td></tr>' for m in messages)
        arows = ''.join('<tr><td>'+esc(a.get('created_at') or a.get('started_at'))+'</td><td><code>'+esc(a.get('message_id'))+'</code></td><td><code>'+esc(a.get('adapter_id'))+'</code></td><td>'+esc(a.get('result'))+'</td></tr>' for a in attempts)
        form = """<form method='post' action='/admin/messages' class='formcard'><input type='hidden' name='action' value='send'>
        <label>Destination<br><select name='destination'>"""+peer_opts+"""</select></label>
        <label>Payload class<br>"""+select('payload_class', PAYLOAD_CLASSES, 'text_message')+"""</label>
        <label>Priority<br>"""+select('priority', PRIORITIES, 'normal')+"""</label>
        <label>Message body<br><textarea name='body' rows='4' maxlength='2000'>CommNet network test message</textarea></label>
        <button type='submit'>Send Test Message</button></form>"""
        return message_box(msg)+'<h1>Messages and Delivery</h1><p>Messages are submitted through TransportManager. Loopback works; LAN peer delivery works only for reachable configured peers.</p>'+form+'<h2>Recent messages</h2><table><thead><tr><th>Created</th><th>ID</th><th>Class</th><th>Target</th><th>Status</th></tr></thead><tbody>'+(mrows or '<tr><td colspan="5">No messages yet.</td></tr>')+'</tbody></table><h2>Delivery attempts</h2><table><thead><tr><th>Time</th><th>Message</th><th>Adapter</th><th>Result</th></tr></thead><tbody>'+(arows or '<tr><td colspan="4">No attempts yet.</td></tr>')+'</tbody></table>'

    def page_devices(self, store: SQLiteStore, msg: str = '') -> str:
        devices = store.list_devices()
        rows = ''.join(f"<tr><td>{esc(d['display_name'])}</td><td>{esc(d['device_type'])}</td><td>{esc(d['trust_state'])}</td><td>{esc(', '.join(d.get('desired_transports', [])))}</td><td><form method='post' action='/admin/devices'><input type='hidden' name='action' value='delete'><input type='hidden' name='device_id' value='{esc(d['device_id'])}'><button type='submit'>Remove</button></form></td></tr>" for d in devices)
        return message_box(msg) + f"""
        <h1>Device Registry</h1>
        <p>Manual device management is active. Automatic discovery is deferred.</p>
        <h2>Add device</h2>
        <form method='post' action='/admin/devices' class='formcard'>
          <input type='hidden' name='action' value='add'>
          <label>Display name<br>{input_text('display_name', '', 40, 64)}</label>
          <label>Device type<br>{select('device_type', DEVICE_TYPES, 'unknown')}</label>
          <label>Trust state<br>{select('trust_state', TRUST_STATES, 'known')}</label>
          <label>Desired transports<br>{''.join(checkbox('desired_transports', tp, False, tp.replace('_',' ').title()) for tp in TRANSPORT_PROFILES)}</label>
          <label>Notes<br>{textarea('notes', '', 3, 500)}</label>
          <button type='submit'>Add Device</button>
        </form>
        <h2>Known devices</h2>
        <table><thead><tr><th>Name</th><th>Type</th><th>Trust</th><th>Transports</th><th>Action</th></tr></thead><tbody>{rows or '<tr><td colspan="5">No devices registered yet.</td></tr>'}</tbody></table>
        """

    def page_files(self, store: SQLiteStore, msg: str = '') -> str:
        roots = store.list_file_roots()
        rows = ''.join(f"<tr><td>{esc(r['label'])}</td><td><code>{esc(r['root_path'])}</code></td><td>{esc(r['default_visibility'])}</td><td>{'yes' if r['scan_enabled'] else 'no'}</td><td>{'yes' if r['review_required'] else 'no'}</td><td><form method='post' action='/admin/files'><input type='hidden' name='action' value='delete'><input type='hidden' name='root_id' value='{esc(r['root_id'])}'><button type='submit'>Remove</button></form></td></tr>" for r in roots)
        return message_box(msg) + f"""
        <h1>File Registry Roots</h1>
        <div class='notice'>Adding a root does not publish files. Full indexing and transfer are deferred.</div>
        <form method='post' action='/admin/files' class='formcard'>
          <input type='hidden' name='action' value='add'>
          <label>Label<br>{input_text('label', '', 40, 64)}</label>
          <label>Root path<br>{input_text('root_path', '', 80, 260)}</label>
          <label>Default visibility<br>{select('default_visibility', FILE_VISIBILITY, 'private')}</label>
          {checkbox('scan_enabled', checked=False, label='Enable future scans for this root')}
          {checkbox('include_subfolders', checked=True, label='Include subfolders')}
          {checkbox('review_required', checked=True, label='Require review before sharing')}
          <button type='submit'>Add File Root</button>
        </form>
        <h2>Registered roots</h2>
        <table><thead><tr><th>Label</th><th>Path</th><th>Visibility</th><th>Scan</th><th>Review</th><th>Action</th></tr></thead><tbody>{rows or '<tr><td colspan="6">No file roots registered yet.</td></tr>'}</tbody></table>
        """

    def page_config(self, cfg_mgr: ConfigManager, cfg: dict, msg: str = '') -> str:
        snapshots = cfg_mgr.snapshot_index()
        snap_rows = ''.join(f"<tr><td>{esc(s['created_at'])}</td><td>{esc(s['reason'])}</td><td><code>{esc(s['filename'])}</code></td><td><form method='post' action='/admin/config'><input type='hidden' name='action' value='restore'><input type='hidden' name='filename' value='{esc(s['filename'])}'><button type='submit'>Restore</button></form></td></tr>" for s in reversed(snapshots[-20:]))
        return message_box(msg) + f"""
        <h1>Configuration Management</h1>
        <div class='grid two'>
          <form method='post' action='/admin/config' class='formcard'><input type='hidden' name='action' value='snapshot'><h2>Create snapshot</h2><button type='submit'>Create Snapshot</button></form>
          <form method='post' action='/admin/config' class='formcard'><input type='hidden' name='action' value='reset'><h2>Reset safe defaults</h2><button type='submit'>Reset</button></form>
        </div>
        <h2>Export current config</h2><textarea readonly rows='14'>{esc(cfg_mgr.export_config_text())}</textarea>
        <h2>Import config JSON</h2><form method='post' action='/admin/config' class='formcard'><input type='hidden' name='action' value='import'><textarea name='config_json' rows='10'></textarea><button type='submit'>Import Config</button></form>
        <h2>Snapshots</h2><table><thead><tr><th>Created</th><th>Reason</th><th>File</th><th>Action</th></tr></thead><tbody>{snap_rows or '<tr><td colspan="4">No snapshots yet.</td></tr>'}</tbody></table>
        """

    def page_audit(self, store: SQLiteStore) -> str:
        events = store.audit_recent(100)
        rows = ''.join(f"<tr><td>{esc(e['ts'])}</td><td><code>{esc(e['event_type'])}</code></td><td><pre>{esc(json.dumps(e.get('details',{}), indent=2, sort_keys=True))}</pre></td></tr>" for e in events)
        return f"<h1>Audit Log</h1><table><thead><tr><th>Time</th><th>Event</th><th>Details</th></tr></thead><tbody>{rows or '<tr><td colspan="3">No audit events yet.</td></tr>'}</tbody></table>"

    def handle_admin_post(self, path: str, form: dict[str, list[str]]):
        paths, store, audit, cfg_mgr, cfg = self._objects()
        if path == '/admin/settings/display':
            action = first(form, 'action', 'save')
            if action == 'defaults':
                cfg['ui'] = dict(UI_DEFAULTS)
            else:
                apply_ui_form(cfg, form, first)
            cfg_mgr.save(cfg, snapshot=True, reason='ui_display_settings_update')
            audit.write('ui_display_settings_updated', {'action': action, 'ui': cfg.get('ui', {})})
            return self.redirect('/admin/settings/display?msg=Display%20settings%20saved')
        if path == '/admin/users':
            us = UserStore(store, audit)
            action = first(form, 'action', 'create')
            if action == 'create':
                us.create_user(first(form,'username'), first(form,'display_name'), first(form,'password'), first(form,'role_id','user'), first(form,'password_hint',''))
                return self.redirect('/admin/users?msg=User%20created')
            if action == 'role':
                us.set_role(first(form,'user_id'), first(form,'role_id','user'))
                return self.redirect('/admin/users?msg=Role%20updated')
            if action == 'reset_password':
                us.reset_password(first(form,'user_id'), first(form,'new_password'), first(form,'password_hint',''))
                return self.redirect('/admin/users?msg=Password%20reset')
        if path == '/admin/users/requests':
            us = UserStore(store, audit)
            us.resolve_permission_request(first(form,'request_id'), first(form,'decision','denied'), 'local_admin', first(form,'admin_response',''))
            return self.redirect('/admin/users/requests?msg=Request%20updated')
        if path == '/admin/mail' or path == '/admin/mail/broadcast':
            us = UserStore(store, audit)
            ms = MailStore(store, audit)
            recipients = many(form, 'recipient_user_id')
            if first(form, 'broadcast') == 'all':
                recipients = [u['user_id'] for u in us.list_users()]
            if not recipients:
                return self.redirect('/admin/mail?msg=No%20recipients%20selected')
            ms.send(us.admin_user_id(), recipients, first(form,'subject','Admin message'), first(form,'body',''), system_message=True, broadcast=first(form,'broadcast')=='all')
            return self.redirect('/admin/mail?msg=Mail%20sent')
        if path.startswith('/admin/apps'):
            if path == '/admin/apps/emergency':
                cfg['emergency_info'] = {
                    'public': checked(form,'public'),
                    'title': first(form,'title','CommNet Emergency Info')[:160],
                    'body': first(form,'body','')[:5000],
                    'outage_banner': checked(form,'outage_banner'),
                }
                cfg_mgr.save(cfg, snapshot=True, reason='emergency_info_update')
                audit.write('emergency_info_updated', {'public': cfg['emergency_info']['public'], 'outage_banner': cfg['emergency_info']['outage_banner']})
                return self.redirect('/admin/apps/emergency?msg=Emergency%20info%20saved')
            self._apply_services_form(cfg, form)
            cfg_mgr.save(cfg, snapshot=True, reason='portal_apps_update')
            sync_services_to_db(store, cfg)
            return self.redirect('/admin/apps?msg=Portal%20apps%20saved')
        if path == '/admin/shares/new':
            ss = ShareStore(store, audit, self.ctx['package_root'])
            chosen_root = first(form,'root_path_manual') or first(form,'root_path')
            ss.add_share(first(form,'label'), chosen_root, first(form,'virtual_name'), first(form,'visibility_mode','private'), first(form,'permission_profile','list_and_download'), checked(form,'enabled'), checked(form,'require_access_code'), first(form,'visibility_behavior','download'), checked(form,'allow_preview'))
            return self.redirect('/admin/shares?msg=Share%20created')
        if path == '/admin/network-paths':
            paths = detect_network_paths(int(cfg.get('server_port', 8765)))
            store.upsert_network_paths(paths)
            selected_id = first(form, 'path_id')
            selected = None
            for pth in paths:
                if pth.get('path_id') == selected_id:
                    selected = pth
                    break
            if not selected:
                return self.redirect('/admin/network-paths?msg=No%20network%20path%20selected')
            if selected.get('classification') == 'invalid':
                return self.redirect('/admin/network-paths?msg=Invalid%20network%20path%20not%20selected')
            cfg['selected_network_path_id'] = selected.get('path_id','')
            cfg['preferred_visitor_ip'] = selected.get('ipv4_address','')
            cfg['preferred_visitor_url'] = (selected.get('suggested_url') or '').rstrip('/')
            cfg['selected_gateway'] = selected.get('gateway','')
            cfg['selected_adapter_name'] = selected.get('adapter_name','')
            cfg_mgr.save(cfg, snapshot=True, reason='network_path_selected')
            store.select_network_path(selected)
            audit.write('network_path_selected', selected)
            return self.redirect('/admin/network-paths?msg=Network%20path%20selected')
        if path == '/admin/quick-setup':
            mode = first(form, 'mode', 'share_one_folder')
            root_path = first(form, 'root_path')
            if not root_path:
                root_path = str(create_recommended_public_folder())
            share_id = apply_quick_share(store, audit, cfg_mgr, cfg, self.ctx['package_root'], mode, root_path, first(form,'label','CommNet Public'), first(form,'virtual_name','Public'), checked(form,'lan_enabled'), first(form,'permission_profile','list_and_download'), checked(form,'require_access_code'), first(form,'access_code',''))
            return self.redirect('/admin/quick-setup?msg=Quick%20Setup%20applied.%20Restart%20CommNet%20to%20apply%20LAN%20bind%20changes.')
        if path == '/admin/lan':
            enabled = checked(form, 'lan_enabled')
            cfg['lan_access_enabled'] = enabled
            cfg['lan_access_mode'] = 'lan_visible' if enabled else 'localhost_only'
            cfg['lan_bind_confirmed'] = enabled
            cfg['server_host'] = '0.0.0.0' if enabled else '127.0.0.1'
            cfg['lan_bind_host'] = cfg['server_host']
            cfg_mgr.save(cfg, snapshot=True, reason='lan_access_update')
            audit.write('lan_access_updated', {'enabled': enabled})
            return self.redirect('/admin/lan?msg=LAN%20access%20updated.%20Restart%20CommNet%20to%20apply%20bind%20changes.')
        if path == '/admin/shares':
            ss = ShareStore(store, audit, self.ctx['package_root'])
            if first(form, 'action') == 'delete':
                ss.delete_share(first(form, 'share_id'))
                return self.redirect('/admin/shares?msg=Share%20removed')
            action = first(form, 'action')
            if action == 'policy':
                ss.update_share_policy(first(form,'share_id'), first(form,'visibility_mode','private'), first(form,'permission_profile','list_and_download'), first(form,'visibility_behavior','download'), checked(form,'enabled'), checked(form,'require_access_code'), checked(form,'allow_preview'))
                return self.redirect('/admin/shares?msg=Share%20policy%20updated')
            ss.add_share(first(form,'label'), first(form,'root_path'), first(form,'virtual_name'), first(form,'visibility_mode','private'), first(form,'permission_profile','list_and_download'), checked(form,'enabled'), checked(form,'require_access_code'), first(form,'visibility_behavior','download'), checked(form,'allow_preview'))
            return self.redirect('/admin/shares?msg=Share%20added')
        if path == '/admin/catena':
            action = first(form, 'action', 'save')
            if action == 'save':
                cfg['catena_adapter_enabled'] = checked(form, 'catena_adapter_enabled')
                cfg['catena_com_port'] = first(form, 'catena_com_port', cfg.get('catena_com_port',''))
                cfg['catena_baud_rate'] = int(first(form, 'catena_baud_rate', str(cfg.get('catena_baud_rate',115200))) or 115200)
                cfg['catena_ack_timeout_ms'] = int(first(form, 'catena_ack_timeout_ms', str(cfg.get('catena_ack_timeout_ms',3000))) or 3000)
                cfg['catena_payload_limit'] = int(first(form, 'catena_payload_limit', str(cfg.get('catena_payload_limit',180))) or 180)
                cfg['catena_demo_mode'] = first(form, 'catena_demo_mode', cfg.get('catena_demo_mode','fake_until_configured'))
                cfg_mgr.save(cfg, snapshot=True, reason='catena_config_update')
                audit.write('catena_config_updated', {'mode': cfg.get('catena_demo_mode'), 'port': cfg.get('catena_com_port')})
                return self.redirect('/admin/catena?msg=Catena%20configuration%20saved')
            result = run_catena_action(cfg, action, first(form, 'body', 'Hello from CommNet'))
            store.insert_catena_event('txrx', json.dumps(result, sort_keys=True), result.get('parsed',{}).get('type',''), 'ok' if result.get('ok') else 'failed', result.get('error',''), cfg.get('catena_com_port',''))
            if action == 'tx':
                mid = result.get('parsed',{}).get('fields',{}).get('id') or 'catena_msg'
                store.insert_catena_message(mid, 'text_message', first(form,'body',''), 'accepted' if result.get('ok') else 'failed', 'not_proven', 'not_received', result)
            audit.write('catena_demo_action', {'action': action, 'ok': result.get('ok'), 'semantics': result.get('semantics')})
            return self.redirect('/admin/catena?msg=Catena%20' + action + '%20' + ('ok' if result.get('ok') else 'failed'))
        if path == '/admin/setup':
            self._apply_profile_form(cfg, form)
            self._apply_privacy_form(cfg, form)
            self._apply_transports_form(cfg, form)
            self._apply_services_form(cfg, form)
            cfg['first_run_complete'] = True
            cfg_mgr.save(cfg, snapshot=True, reason='first_run_setup')
            audit.write('first_run_setup_applied', {'node_name': cfg.get('node_name')})
            return self.redirect('/admin?msg=Setup%20applied')
        if path == '/admin/profile':
            self._apply_profile_form(cfg, form)
            cfg_mgr.save(cfg, snapshot=True, reason='profile_update')
            audit.write('profile_updated', {'node_name': cfg.get('node_name')})
            return self.redirect('/admin/profile?msg=Profile%20saved')
        if path == '/admin/privacy':
            self._apply_privacy_form(cfg, form)
            cfg_mgr.save(cfg, snapshot=True, reason='privacy_update')
            audit.write('privacy_updated', {'visibility_mode': cfg.get('visibility_mode'), 'privacy_mode': cfg.get('privacy_mode')})
            return self.redirect('/admin/privacy?msg=Privacy%20saved')
        if path == '/admin/services':
            self._apply_services_form(cfg, form)
            cfg_mgr.save(cfg, snapshot=True, reason='services_update')
            sync_services_to_db(store, cfg)
            audit.write('services_updated', {'enabled': [k for k,v in cfg.get('services',{}).items() if v.get('enabled')]})
            return self.redirect('/admin/services?msg=Services%20saved')
        if path == '/admin/transports':
            self._apply_transports_form(cfg, form)
            cfg_mgr.save(cfg, snapshot=True, reason='transports_update')
            audit.write('transport_profiles_updated', {'desired': cfg.get('desired_transport_profiles')})
            return self.redirect('/admin/transports?msg=Transport%20profiles%20saved')
        if path == '/admin/peers':
            ps = PeerStore(store, audit)
            action = first(form, 'action')
            peer_id = first(form, 'peer_id')
            if action == 'delete':
                ps.delete(peer_id); return self.redirect('/admin/peers?msg=Peer%20removed')
            if action == 'trust':
                ps.set_trust(peer_id, 'trusted'); return self.redirect('/admin/peers?msg=Peer%20trusted')
            if action == 'block':
                ps.set_trust(peer_id, 'blocked'); return self.redirect('/admin/peers?msg=Peer%20blocked')
            if action == 'test':
                from commnet.transport.adapters_lan import LanHttpAdapter
                peer = ps.get(peer_id)
                ok, details = LanHttpAdapter(ps).handshake(peer) if peer else (False, {'error': 'peer not found'})
                ps.record_handshake(peer_id, 'ok' if ok else 'failed', details)
                return self.redirect('/admin/peers?msg=Handshake%20' + ('ok' if ok else 'failed'))
            ps.add(first(form,'display_name'), first(form,'base_url'), first(form,'trust_state','known'), first(form,'notes'))
            return self.redirect('/admin/peers?msg=Peer%20added')
        if path == '/admin/messages':
            if first(form, 'action') == 'send':
                ps = PeerStore(store, audit)
                registry = build_default_registry(ps)
                engine = DeliveryEngine(registry, audit, store)
                msg = MessageEnvelope.create(payload_class=first(form,'payload_class','text_message'), body=first(form,'body',''), destination=first(form,'destination','self'), priority=first(form,'priority','normal'), sender_node_id=cfg.get('node_id',''))
                result = engine.send(msg)
                return self.redirect('/admin/messages?msg=Delivery%20' + result.status)
        if path == '/admin/devices/meshtastic':
            action = first(form, 'action', 'probe')
            port = first(form, 'port', '')
            if action == 'fake':
                from commnet.transport.meshtastic_adapter import FakeMeshtasticAdapter
                result = FakeMeshtasticAdapter(store).send_text(first(form,'body','CMN1|PING|fake=1'))
                from commnet.hardware.meshtastic_probe import record_event
                record_event(store, 'fake_smoke', result, result.get('state','simulated'))
                return self.redirect('/admin/devices/meshtastic?msg=Fake%20Meshtastic%20smoke%20recorded')
            if action == 'send_text':
                result = meshtastic_send_text(store, first(form,'body','CMN1|PING|body=hello from CommNet'), port)
                return self.redirect('/admin/devices/meshtastic?msg=Send%20test%20' + ('ok' if result.get('ok') else 'failed'))
            result = meshtastic_probe_serial(store, port)
            return self.redirect('/admin/devices/meshtastic?msg=Probe%20' + ('connected' if result.get('ok') else 'failed'))
        if path == '/admin/devices':
            ds = DeviceStore(store, audit)
            action = first(form, 'action')
            if action == 'delete':
                ds.delete(first(form, 'device_id'))
                return self.redirect('/admin/devices?msg=Device%20removed')
            ds.add(first(form,'display_name'), first(form,'device_type'), first(form,'trust_state'), first(form,'notes'), many(form,'desired_transports'))
            return self.redirect('/admin/devices?msg=Device%20added')
        if path == '/admin/files':
            fs = FileRootStore(store, audit)
            action = first(form, 'action')
            if action == 'delete':
                fs.delete(first(form, 'root_id'))
                return self.redirect('/admin/files?msg=File%20root%20removed')
            fs.add(first(form,'label'), first(form,'root_path'), first(form,'default_visibility'), checked(form,'scan_enabled'), checked(form,'include_subfolders'), checked(form,'review_required'))
            return self.redirect('/admin/files?msg=File%20root%20added')
        if path == '/admin/config':
            action = first(form, 'action')
            if action == 'snapshot':
                cfg_mgr.snapshot('manual_snapshot')
                audit.write('config_snapshot_created', {})
                return self.redirect('/admin/config?msg=Snapshot%20created')
            if action == 'reset':
                cfg_mgr.reset_safe_defaults(); audit.write('config_reset_safe_defaults', {})
                return self.redirect('/admin/config?msg=Config%20reset')
            if action == 'restore':
                fn = first(form, 'filename')
                cfg_mgr.restore_snapshot(fn); audit.write('config_snapshot_restored', {'filename': fn})
                return self.redirect('/admin/config?msg=Snapshot%20restored')
            if action == 'import':
                cfg_mgr.import_config_text(first(form, 'config_json')); audit.write('config_imported', {})
                return self.redirect('/admin/config?msg=Config%20imported')
        return self.redirect('/admin')

    def _apply_profile_form(self, cfg: dict, form: dict[str, list[str]]) -> None:
        errors = []
        for key in ['node_name','admin_display_name','location_label','node_description']:
            value, e = validate_text(key, first(form, key, cfg.get(key,'')), key); errors += e; cfg[key] = value
        for key, allowed in [('deployment_profile', DEPLOYMENT_PROFILES), ('node_role', NODE_ROLES)]:
            value, e = validate_choice(key, first(form, key, cfg.get(key)), allowed); errors += e; cfg[key] = value
        if errors: raise ValueError('; '.join(errors))

    def _apply_privacy_form(self, cfg: dict, form: dict[str, list[str]]) -> None:
        errors = []
        value, e = validate_choice('privacy_mode', first(form,'privacy_mode',cfg.get('privacy_mode')), PRIVACY_MODES); errors += e; cfg['privacy_mode'] = value
        value, e = validate_choice('visibility_mode', first(form,'visibility_mode',cfg.get('visibility_mode')), VISIBILITY_MODES); errors += e; cfg['visibility_mode'] = value
        if errors: raise ValueError('; '.join(errors))

    def _apply_transports_form(self, cfg: dict, form: dict[str, list[str]]) -> None:
        values, errors = validate_multi_choice('transport_profile', many(form, 'transport_profile'), TRANSPORT_PROFILES)
        if 'local_loopback' not in values:
            values.insert(0, 'local_loopback')
        if errors: raise ValueError('; '.join(errors))
        cfg['desired_transport_profiles'] = values

    def _apply_services_form(self, cfg: dict, form: dict[str, list[str]]) -> None:
        services = cfg.get('services') or {}
        for sid in SERVICE_IDS:
            current = services.get(sid, {})
            current['enabled'] = checked(form, 'svc_enabled_' + sid)
            current['visible_in_portal'] = checked(form, 'svc_visible_' + sid)
            current['requires_review'] = checked(form, 'svc_review_' + sid)
            current['status'] = 'configured' if current['enabled'] else 'available_disabled'
            services[sid] = current
        cfg['services'] = services

    def serve_portal(self, path: str):
        _, store, audit, cfg_mgr, cfg = self._objects()
        user = self.current_user(store, audit)
        if path != '/portal':
            sid = path.split('/')[-1]
            if sid in {'emergency','bbs','retroweb'}:
                return self.serve_public_app('/' + sid, {})
            title = sid.replace('-', ' ').title()
            if sid not in {'directory','sites','library','makerspace','marketplace','events','work','demos'}:
                return self.not_found()
            body = f"<h1>{esc(title)}</h1>"
            body += f"<p>Node: <strong>{esc(cfg.get('node_name'))}</strong>. Visibility: <code>{esc(cfg.get('visibility_mode'))}</code>.</p>"
            body += '<p>This community component is represented in the config UI. Functional network demos are added later.</p><p><a href="/portal">Back to portal</a></p>'
            return self.send_bytes(layout(title, body, 'portal', cfg, path))
        cards = []
        portal_defs = [
            ('share','Shared Files','Browse folders and files made visible to your account or access code.','/share','📁','green'),
            ('mail','Internal Mail','Local CommNet mailbox and messages.','/mail','✉️','teal'),
            ('requests','Request Access','Ask the admin for more apps, folders, or capabilities.','/requests/new','📨','purple'),
            ('emergency','Emergency Info','Priority notices and outage mode.','/emergency','🚨','red'),
            ('bbs','BBS','Local message board with boards, threads, and replies.','/bbs','💬','teal'),
            ('retroweb','RetroWeb','Local RetroWeb social profiles, icons, posts, and comments.','/retroweb','🕹️','indigo'),
            ('directory','Community Directory','Find local nodes, sites, and services.','/portal/directory','🌐','blue'),
            ('demos','Demos','Hardware and transport demonstrations, including Catena and mesh status.','/portal/demos','📡','orange'),
            ('account','My Account','Profile, icon, security, and display settings.','/account','⚙️','amber'),
        ]
        services = cfg.get('services') or {}
        slug_to_service = {'share':'file_registry','mail':'community_portal','requests':'community_portal','account':'community_portal'}
        show_unavailable = normalized_ui(cfg).get('show_unavailable_guest_apps') != 'hidden'
        for slug, title, text, href, icon, domain in portal_defs:
            sid = slug_to_service.get(slug, slug)
            svc = services.get(sid, {'enabled': True, 'visible_in_portal': True})
            allowed = slug in {'share','mail','requests','emergency','account'} or (svc.get('enabled') and svc.get('visible_in_portal'))
            if allowed:
                cards.append(card(title, text, href, 'guest_visible', domain, icon))
            elif show_unavailable:
                cards.append(card(title, 'Not currently visible; request access from the admin.', '/requests/new', 'needs_setup', domain, icon))
        us = UserStore(store, audit); ms = MailStore(store, audit); ss = ShareStore(store, audit, self.ctx['package_root'])
        pending_count = len([r for r in us.list_permission_requests() if user and r.get('user_id') == user.get('user_id') and r.get('status') == 'pending']) if user else 0
        unread_count = ms.unread_count(user['user_id']) if user else 0
        shares = ss.summary()
        signed = self.display_user(user)
        switch_admin = "<a class='button secondary' href='/admin/hud'>Switch to Admin HUD</a>" if self.user_can_admin(user, store, audit) else ""
        body = f"""
        <h1>CommNet Community Portal</h1>
        <div class='portal-dashboard'>
          <div class='portal-hero'><strong>{esc(cfg.get('node_name'))}</strong><br>Signed in: <code>{esc(signed)}</code><br>This is the user-facing entry point. Admin configuration remains separate on the Admin HUD. {switch_admin}</div>
          <div class='portal-status-row'>
            <div class='kpi'><strong>{esc(shares.get('lan_visible_share_count',0))}</strong><span>visible shares</span></div>
            <div class='kpi {'attention' if unread_count else ''}'><strong>{esc(unread_count)}</strong><span>unread mail</span></div>
            <div class='kpi {'attention-amber' if pending_count else ''}'><strong>{esc(pending_count)}</strong><span>pending requests</span></div>
            <div class='kpi'><strong>{'yes' if self.user_can_admin(user, store, audit) else 'no'}</strong><span>admin switch available</span></div>
          </div>
          <section class='portal-grid'>{''.join(cards)}</section>
        </div>
        """
        return self.send_bytes(layout('Portal', body, 'portal', cfg, path))


    def _share_authorized(self, ss: ShareStore, share: dict, query: dict[str, list[str]]) -> bool:
        if not share.get('require_access_code'):
            return True
        code = first(query, 'code', '')
        return ss.verify_code(code)

    def serve_share(self, path: str, query: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        ss = ShareStore(store, audit, self.ctx['package_root'])
        remote = self.client_address[0] if self.client_address else ''
        if path == '/share':
            shares = [s for s in ss.list_shares(visitor_visible=True) if s.get('visibility_behavior') not in ('invisible','admin_only')]
            rows = []
            for s in shares:
                code_param = '&code=' + esc(first(query, 'code')) if first(query, 'code') else ''
                behavior = s.get('visibility_behavior') or 'download'
                extra = ''
                if behavior == 'count_only':
                    try:
                        c = ss.share_count(s)
                        extra = f" · {c.get('files',0)} files / {c.get('folders',0)} folders"
                    except Exception:
                        extra = ' · count unavailable'
                rows.append(f"<li><a href='/share/{esc(s['share_id'])}?{code_param.lstrip('&')}'>{esc(s['label'])}</a> <span class='muted'>/{esc(s['virtual_name'])} · {esc(behavior)}{esc(extra)}</span></li>")
            access_form = "<form method='get' action='/share'><label>Access code <input name='code'></label><button type='submit'>Apply Code</button></form>"
            body = f"""
            <h1>Shared Files</h1>
            <div class='notice'>Only folders explicitly approved by this CommNet node owner are shown here. Share behavior can be invisible, count-only, list-only, preview-only, download, upload inbox, or admin-only.</div>
            {access_form}
            <ul>{''.join(rows) or '<li>No LAN-visible shares are enabled.</li>'}</ul>
            <p><a href='/welcome'>Back to CommWeb landing</a></p>
            """
            ss.log_access(remote, 'list_shares', 'ok', reason=f'{len(shares)} shares visible')
            return self.send_bytes(layout('Shared Files', body, 'portal', cfg, path))
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[1] == 'preview':
            share_id = parts[2]
            share = ss.get_share(share_id)
            if not share or not share.get('enabled') or share.get('visibility_behavior') in ('invisible','admin_only','count_only','list_only'):
                ss.log_access(remote, 'preview', 'denied', share_id, reason='preview disabled or share unavailable')
                return self.send_bytes(layout('Preview unavailable', '<h1>Preview unavailable</h1>', 'portal', cfg, path), status=403)
            if not self._share_authorized(ss, share, query):
                ss.log_access(remote, 'preview', 'denied', share_id, reason='access code required')
                return self.send_bytes(layout('Access Code Required', '<h1>Access code required</h1>', 'portal', cfg, path), status=403)
            rel = first(query, 'p', '')
            try:
                target, kind = resolve_preview(share, rel)
                if kind == 'image':
                    data = target.read_bytes()
                    self.send_response(200)
                    self.send_header('Content-Type', mimetypes.guess_type(str(target))[0] or 'image/*')
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Cache-Control', 'no-store')
                    self.end_headers(); self.wfile.write(data)
                    ss.log_access(remote, 'preview', 'ok', share_id, rel)
                    return
                if kind == 'text':
                    body = f"<h1>Preview: {esc(target.name)}</h1><div class='notice'>Safe text preview; content is escaped and limited.</div><pre>{esc(read_text_preview(target))}</pre><p><a href='/share/{esc(share_id)}?code={esc(first(query,'code'))}'>Back to share</a></p>"
                    ss.log_access(remote, 'preview', 'ok', share_id, rel)
                    return self.send_bytes(layout('Preview', body, 'portal', cfg, path))
                meta = preview_metadata(target)
                body = f"<h1>Preview metadata</h1><pre>{esc(json.dumps(meta, indent=2, sort_keys=True))}</pre><div class='warning'>This file type is not executed or rendered by CommNet preview.</div>"
                ss.log_access(remote, 'preview', 'metadata', share_id, rel)
                return self.send_bytes(layout('Preview metadata', body, 'portal', cfg, path))
            except Exception as exc:
                ss.log_access(remote, 'preview', 'denied', share_id, rel, str(exc))
                return self.send_bytes(layout('Preview denied', f'<h1>Preview denied</h1><pre>{esc(str(exc))}</pre>', 'portal', cfg, path), status=403)
        if len(parts) >= 3 and parts[1] == 'download':
            share_id = parts[2]
            share = ss.get_share(share_id)
            if not share or not share.get('enabled'):
                ss.log_access(remote, 'download', 'denied', share_id, reason='share disabled or missing')
                return self.send_bytes(layout('Denied', '<h1>Share unavailable</h1>', 'portal', cfg, path), status=404)
            if share.get('visibility_behavior') not in ('download',) or not share.get('allow_download'):
                ss.log_access(remote, 'download', 'denied', share_id, reason='download disabled by share behavior')
                return self.send_bytes(layout('Download Disabled', '<h1>Downloads are disabled for this share.</h1>', 'portal', cfg, path), status=403)
            if not self._share_authorized(ss, share, query):
                ss.log_access(remote, 'download', 'denied', share_id, reason='access code required')
                return self.send_bytes(layout('Access Code Required', '<h1>Access code required</h1><p>Return to <a href="/share">shares</a> and enter the code.</p>', 'portal', cfg, path), status=403)
            rel = first(query, 'p', '')
            try:
                target = resolve_download(share, rel)
                data = target.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Content-Disposition', 'attachment; filename="' + target.name.replace('"','') + '"')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers(); self.wfile.write(data)
                ss.log_access(remote, 'download', 'ok', share_id, rel)
                return
            except Exception as exc:
                ss.log_access(remote, 'download', 'denied', share_id, rel, str(exc))
                return self.send_bytes(layout('Download Denied', f'<h1>Download denied</h1><pre>{esc(str(exc))}</pre>', 'portal', cfg, path), status=403)
        if len(parts) >= 2:
            share_id = parts[1]
            share = ss.get_share(share_id)
            if not share or not share.get('enabled') or share.get('visibility_mode') not in ('lan_visible','community_visible') or share.get('visibility_behavior') in ('invisible','admin_only'):
                ss.log_access(remote, 'browse', 'denied', share_id, reason='share disabled, hidden, or private')
                return self.send_bytes(layout('Share unavailable', '<h1>Share unavailable</h1>', 'portal', cfg, path), status=404)
            if not self._share_authorized(ss, share, query):
                ss.log_access(remote, 'browse', 'denied', share_id, reason='access code required')
                return self.send_bytes(layout('Access Code Required', "<h1>Access code required</h1><form method='get'><label>Access code <input name='code'></label><button type='submit'>Open Share</button></form>", 'portal', cfg, path), status=403)
            rel = first(query, 'p', '')
            behavior = share.get('visibility_behavior') or 'download'
            if behavior == 'count_only':
                c = ss.share_count(share)
                body = f"<h1>{esc(share['label'])}</h1><div class='notice'>Count-only mode: names and contents are hidden.</div><p>Files: <strong>{c.get('files',0)}</strong> · Folders: <strong>{c.get('folders',0)}</strong></p><p><a href='/share?code={esc(first(query,'code'))}'>All shares</a></p>"
                ss.log_access(remote, 'count', 'ok', share_id, rel)
                return self.send_bytes(layout(share['label'], body, 'portal', cfg, path))
            try:
                listing = list_entries(share, rel)
                code = first(query, 'code')
                codeq = '&code=' + esc(code) if code else ''
                up = ''
                if rel:
                    parent = '/'.join(rel.replace('\\','/').split('/')[:-1])
                    up = f"<p><a href='/share/{esc(share_id)}?p={esc(parent)}{codeq}'>Up</a></p>"
                rows = []
                for e in listing['entries']:
                    child = (rel + '/' + e['name']).strip('/')
                    if e['is_dir']:
                        rows.append(f"<tr><td>folder</td><td><a href='/share/{esc(share_id)}?p={esc(child)}{codeq}'>{esc(e['name'])}</a></td><td></td></tr>")
                    else:
                        actions=[]
                        if behavior in ('preview_only','download') and share.get('allow_preview'):
                            actions.append(f"<a href='/share/preview/{esc(share_id)}?p={esc(child)}{codeq}'>Preview</a>")
                        if behavior == 'download' and share.get('allow_download'):
                            actions.append(f"<a href='/share/download/{esc(share_id)}?p={esc(child)}{codeq}'>Download</a>")
                        rows.append(f"<tr><td>file</td><td>{esc(e['name'])}</td><td>{' · '.join(actions) or '<span class=muted>not available</span>'}</td></tr>")
                upload = ''
                if share.get('allow_upload') and behavior in ('upload_inbox','download'):
                    upload = f"""<h2>Upload text note to inbox</h2><form method='post' action='/share/{esc(share_id)}/upload'><input type='hidden' name='code' value='{esc(code)}'><label>Filename <input name='filename' value='visitor_note.txt'></label><textarea name='file_text' rows='5'></textarea><button type='submit'>Upload Note</button></form>"""
                body = f"<h1>{esc(share['label'])}</h1><div class='notice'>Virtual path: /{esc(share['virtual_name'])}/{esc(rel)} · behavior: <code>{esc(behavior)}</code></div>{up}<table><thead><tr><th>Type</th><th>Name</th><th>Action</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan=3>No files visible.</td></tr>'}</tbody></table>{upload}<p><a href='/share?code={esc(code)}'>All shares</a></p>"
                ss.log_access(remote, 'browse', 'ok', share_id, rel)
                return self.send_bytes(layout(share['label'], body, 'portal', cfg, path))
            except Exception as exc:
                ss.log_access(remote, 'browse', 'denied', share_id, rel, str(exc))
                return self.send_bytes(layout('Browse denied', f'<h1>Browse denied</h1><pre>{esc(str(exc))}</pre>', 'portal', cfg, path), status=403)
        return self.not_found()

    def handle_share_post(self, path: str, form: dict[str, list[str]]):
        _, store, audit, cfg_mgr, cfg = self._objects()
        ss = ShareStore(store, audit, self.ctx['package_root'])
        remote = self.client_address[0] if self.client_address else ''
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[2] == 'upload':
            share_id = parts[1]
            share = ss.get_share(share_id)
            code = first(form, 'code', '')
            if not share or not share.get('enabled') or not share.get('allow_upload'):
                ss.log_access(remote, 'upload', 'denied', share_id, reason='upload disabled')
                return self.send_bytes(layout('Upload Denied', '<h1>Upload denied</h1>', 'portal', cfg, path), status=403)
            if share.get('require_access_code') and not ss.verify_code(code):
                ss.log_access(remote, 'upload', 'denied', share_id, reason='bad access code')
                return self.send_bytes(layout('Upload Denied', '<h1>Access code required</h1>', 'portal', cfg, path), status=403)
            filename = first(form, 'filename', 'visitor_note.txt').replace('\\','_').replace('/','_').replace(':','_')[:80] or 'visitor_note.txt'
            text = first(form, 'file_text', '')
            if len(text.encode('utf-8')) > int(cfg.get('max_upload_size_mb',50)) * 1024 * 1024:
                return self.send_bytes(layout('Upload Denied', '<h1>Upload too large</h1>', 'portal', cfg, path), status=413)
            inbox = safe_resolve(share['root_path'], share.get('upload_subfolder') or '_CommNet_Inbox')
            inbox.mkdir(parents=True, exist_ok=True)
            target = (inbox / filename).resolve()
            target.write_text(text, encoding='utf-8')
            ss.log_access(remote, 'upload', 'ok', share_id, filename)
            return self.redirect(f'/share/{share_id}?code={code}')
        return self.not_found()

    def handle_node_receive(self):
        length = int(self.headers.get('Content-Length', '0') or '0')
        if length > 20000:
            return self.send_json({'accepted': False, 'error': 'payload too large'}, status=413)
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode('utf-8'))
            message = data.get('message') or {}
        except Exception as exc:
            return self.send_json({'accepted': False, 'error': 'invalid json: ' + str(exc)}, status=400)
        paths, store, audit, cfg_mgr, cfg = self._objects()
        if not cfg.get('allow_inbound_peer_messages', False):
            audit.write('inbound_peer_message_rejected', {'reason': 'inbound disabled', 'message_id': message.get('message_id')})
            return self.send_json({'accepted': False, 'error': 'inbound peer messages disabled by policy'}, status=403)
        try:
            msg = MessageEnvelope.from_dict(message)
            msg.status = 'delivered'
            store.insert_message(msg)
            store.update_message_status(msg.message_id, 'delivered')
            audit.write('inbound_peer_message_accepted', {'message_id': msg.message_id, 'payload_class': msg.payload_class})
            return self.send_json({'accepted': True, 'message_id': msg.message_id})
        except Exception as exc:
            audit.write('inbound_peer_message_rejected', {'reason': str(exc)})
            return self.send_json({'accepted': False, 'error': str(exc)}, status=400)

    def serve_api(self, path: str):
        paths, store, audit, cfg_mgr, cfg = self._objects()
        visitor_safe = {'/api/status','/api/session','/api/node/hello','/api/node/status','/api/node/ping','/api/share-summary','/api/captive/status'}
        if not self.is_local_client() and path not in visitor_safe and not path.startswith('/api/node/'):
            return self.send_json({'error': 'admin/config API is localhost-only for LAN visitors'}, status=403)
        if path == '/api/status':
            return self.send_json({
                'running': True,
                'package_status': 'PORTAL_POLISH_READY_WITH_DEBT',
                'node_name': cfg.get('node_name'),
                'first_run_complete': cfg.get('first_run_complete'),
                'visibility_mode': cfg.get('visibility_mode'),
                'enabled_services': [k for k,v in (cfg.get('services') or {}).items() if v.get('enabled')],
                'server': {'host': self.server.server_address[0], 'port': self.server.server_address[1]},
            })
        if path == '/api/session':
            user = self.current_user(store, audit)
            icon = self.account_icon_payload(user, store, audit)
            return self.send_json({
                'signed_in': bool(user),
                'user_id': user.get('user_id') if user else '',
                'username': user.get('username') if user else '',
                'display_name': user.get('display_name') if user else 'Guest',
                'role_id': user.get('role_id') if user else 'guest',
                'can_admin': self.user_can_admin(user, store, audit),
                'icon_kind': icon.get('icon_kind', 'blank'),
                'icon_html': icon.get('icon_html', '○'),
            })
        if path == '/api/config':
            return self.send_json(cfg_mgr.redact(cfg))
        if path == '/api/devices':
            return self.send_json({'devices': store.list_devices()})
        if path == '/api/file-roots':
            return self.send_json({'file_roots': store.list_file_roots()})
        if path == '/api/diagnostics':
            return self.send_json(DiagnosticsRunner(self.ctx['package_root'], paths).run(write_reports=True))
        if path == '/api/transports':
            return self.send_json({'adapters': build_default_registry().statuses(), 'desired_profiles': cfg.get('desired_transport_profiles')})
        if path == '/api/loopback-test':
            registry = build_default_registry()
            engine = DeliveryEngine(registry, audit, store)
            msg = MessageEnvelope.create(payload_class='text_message', body='browser loopback test', destination='self')
            result = engine.send(msg)
            return self.send_json({'message': msg.to_dict(), 'result': result.to_dict()})
        if path == '/api/node/hello':
            return self.send_json({'hello': 'commnet', 'node_name': cfg.get('node_name'), 'visibility_mode': cfg.get('visibility_mode'), 'package_status': 'PORTAL_POLISH_READY_WITH_DEBT'})
        if path == '/api/node/status' or path == '/api/node/ping':
            return self.send_json({'ok': True, 'node_name': cfg.get('node_name'), 'counts': store.table_counts(), 'server': {'host': self.server.server_address[0], 'port': self.server.server_address[1]}})
        if path == '/api/peers':
            return self.send_json({'peers': PeerStore(store, audit).list()})
        if path == '/api/messages':
            return self.send_json({'messages': store.messages_recent(), 'attempts': store.delivery_attempts_recent(), 'routes': store.route_decisions_recent()})
        if path == '/api/dependencies':
            return self.send_json({'dependencies': check_all_dependencies(store)})
        if path == '/api/share-summary':
            return self.send_json(ShareStore(store, audit, self.ctx['package_root']).summary())
        if path == '/api/captive/status':
            return self.send_json({'captive': False, 'user-portal-url': self.absolute_url('/welcome'), 'mode': 'captive_assist_guidance_only'})
        if path == '/api/catena/status':
            adapter = make_adapter_from_config(cfg)
            return self.send_json({'adapter': adapter.status(), 'serial_ports': list_serial_ports(), 'events': store.catena_events_recent(10), 'messages': store.catena_messages_recent(10)})
        if path == '/api/meshtastic/status':
            deps = meshtastic_dependency_status(); latest = meshtastic_latest_status(store)
            with store.connect() as conn:
                events = [dict(r) for r in conn.execute('SELECT * FROM meshtastic_events ORDER BY created_at DESC LIMIT 20').fetchall()]
            return self.send_json({'dependency': deps, 'latest': latest, 'candidate_ports': meshtastic_candidate_ports(), 'events': events})
        if path == '/api/links':
            detected = detect_all()
            return self.send_json(build_link_set(cfg, detected['lan_addresses']))
        if path == '/api/network-paths':
            paths = detect_network_paths(int(cfg.get('server_port', 8765)))
            return self.send_json({'paths': paths, 'selected': selected_or_best_path(cfg, paths)})
        if path == '/api/network-diagnostics':
            return self.send_json({'counts': store.table_counts(), 'dependencies': check_all_dependencies(store), 'adapters': build_default_registry(PeerStore(store, audit)).statuses(), 'peers': PeerStore(store, audit).list(), 'messages': store.messages_recent(10), 'attempts': store.delivery_attempts_recent(10)})
        if path == '/api/shutdown':
            audit.write('server_shutdown_requested', {})
            self.send_json({'shutdown': 'requested'})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        return self.send_json({'error': 'unknown api endpoint'}, status=404)


def run_server(package_root: Path, paths, host: str = '127.0.0.1', port: int = 8765) -> int:
    paths.ensure_all()
    store = SQLiteStore(paths)
    store.initialize()
    ConfigManager(paths).touch_started()
    server = ReusableThreadingHTTPServer((host, int(port)), CommNetHandler)
    server.commnet_context = {'package_root': Path(package_root), 'paths': paths}
    state = {'host': host, 'port': int(port)}
    paths.server_state.write_text(json.dumps(state, indent=2), encoding='utf-8')
    try:
        server.serve_forever(poll_interval=0.25)
        return 0
    finally:
        server.server_close()
        try:
            paths.server_state.unlink()
        except FileNotFoundError:
            pass
