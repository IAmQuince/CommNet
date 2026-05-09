"""CommNet command entry point.

This file can be run directly from the BAT launchers without installing the package.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


def _ensure_src_on_path() -> Path:
    here = Path(__file__).resolve()
    src = here.parents[1]
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return here.parents[2]


PACKAGE_ROOT = _ensure_src_on_path()

from commnet.core.paths import RuntimePaths
from commnet.core.config import ConfigManager
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.core.support_bundle import SupportBundle
from commnet.server.app import run_server
from commnet.diagnostics.runner import DiagnosticsRunner
from commnet.transport.registry import build_default_registry
from commnet.transport.engine import DeliveryEngine
from commnet.transport.messages import MessageEnvelope

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def _runtime() -> RuntimePaths:
    return RuntimePaths(PACKAGE_ROOT)


def _url(path: str = "/api/status", host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}{path}"


def server_alive(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    try:
        with urllib.request.urlopen(_url('/api/status', host, port), timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def command_serve(args: argparse.Namespace) -> int:
    paths = _runtime()
    paths.ensure_all()
    cfg = ConfigManager(paths)
    cfg.ensure_default()
    store = SQLiteStore(paths)
    store.initialize()
    audit = AuditLogger(paths, store)
    audit.write('server_start_requested', {'host': args.host, 'port': args.port})
    return run_server(PACKAGE_ROOT, paths, host=args.host, port=args.port)


def _spawn_server_if_needed(host: str, port: int, bind_host: str | None = None) -> None:
    check_host = '127.0.0.1' if host in ('0.0.0.0', '::') else host
    if server_alive(check_host, port):
        return
    paths = _runtime()
    paths.ensure_all()
    log_path = paths.logs / 'launcher_server_stdout.log'
    err_path = paths.logs / 'launcher_server_stderr.log'
    cmd = [sys.executable, str(Path(__file__).resolve()), 'serve', '--host', (bind_host or host), '--port', str(port)]
    with log_path.open('ab') as out, err_path.open('ab') as err:
        subprocess.Popen(cmd, cwd=str(PACKAGE_ROOT), stdout=out, stderr=err, stdin=subprocess.DEVNULL)
    for _ in range(30):
        if server_alive(check_host, port):
            return
        time.sleep(0.2)
    raise RuntimeError('CommNet server did not become reachable within startup timeout.')


def command_launch(args: argparse.Namespace) -> int:
    host, port = args.host, args.port
    cfg0 = ConfigManager(_runtime()).ensure_default()
    bind_host = '0.0.0.0' if cfg0.get('lan_access_enabled') and cfg0.get('lan_bind_confirmed') else host
    _spawn_server_if_needed(host, port, bind_host)
    page = 'admin' if args.page == 'admin' else 'portal'
    open_path = '/portal' if page == 'portal' else '/admin/hud'
    if page == 'admin':
        cfg = ConfigManager(_runtime()).ensure_default()
        if not cfg.get('first_run_complete'):
            open_path = '/admin/setup'
    webbrowser.open(_url(open_path, host, port))
    print(f'CommNet {page} opened at {_url(open_path, host, port)}')
    return 0


def command_stop(args: argparse.Namespace) -> int:
    if not server_alive(args.host, args.port):
        print('CommNet server is not currently reachable.')
        return 0
    try:
        with urllib.request.urlopen(_url('/api/shutdown', args.host, args.port), timeout=3) as resp:
            print(resp.read().decode('utf-8', errors='replace'))
    except urllib.error.URLError as exc:
        print(f'Shutdown request sent; connection closed or unavailable: {exc}')
    time.sleep(0.5)
    return 0


def command_status(args: argparse.Namespace) -> int:
    try:
        with urllib.request.urlopen(_url('/api/status', args.host, args.port), timeout=2) as resp:
            print(resp.read().decode('utf-8', errors='replace'))
            return 0
    except Exception as exc:
        print(json.dumps({'running': False, 'error': str(exc)}, indent=2))
        return 1


def command_diagnostics(args: argparse.Namespace) -> int:
    paths = _runtime()
    paths.ensure_all()
    report = DiagnosticsRunner(PACKAGE_ROOT, paths).run(write_reports=True)
    print(f"Diagnostics status: {report['overall_status']}")
    print(f"Markdown report: {paths.reports / 'diagnostic_report.md'}")
    print(f"JSON report: {paths.reports / 'diagnostic_report.json'}")
    return 0 if report['overall_status'] in ('PASS', 'WARN') else 2


def command_support_bundle(args: argparse.Namespace) -> int:
    paths = _runtime()
    paths.ensure_all()
    DiagnosticsRunner(PACKAGE_ROOT, paths).run(write_reports=True)
    bundle = SupportBundle(PACKAGE_ROOT, paths).create()
    print(f'Support bundle created: {bundle}')
    return 0


def command_loopback(args: argparse.Namespace) -> int:
    paths = _runtime()
    paths.ensure_all()
    store = SQLiteStore(paths)
    store.initialize()
    audit = AuditLogger(paths, store)
    registry = build_default_registry()
    engine = DeliveryEngine(registry, audit, store)
    msg = MessageEnvelope.create(payload_class='text_message', body='loopback smoke test', destination='self')
    result = engine.send(msg)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 2



def command_controller(args: argparse.Namespace) -> int:
    from commnet.control_window import CommNetControlWindow
    return CommNetControlWindow(PACKAGE_ROOT).run()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='CommNet shell command line')
    sub = parser.add_subparsers(dest='command', required=True)

    serve = sub.add_parser('serve')
    serve.add_argument('--host', default=DEFAULT_HOST)
    serve.add_argument('--port', type=int, default=DEFAULT_PORT)
    serve.set_defaults(func=command_serve)

    launch = sub.add_parser('launch')
    launch.add_argument('--page', choices=['admin', 'portal'], default='admin')
    launch.add_argument('--host', default=DEFAULT_HOST)
    launch.add_argument('--port', type=int, default=DEFAULT_PORT)
    launch.set_defaults(func=command_launch)

    stop = sub.add_parser('stop')
    stop.add_argument('--host', default=DEFAULT_HOST)
    stop.add_argument('--port', type=int, default=DEFAULT_PORT)
    stop.set_defaults(func=command_stop)

    status = sub.add_parser('status')
    status.add_argument('--host', default=DEFAULT_HOST)
    status.add_argument('--port', type=int, default=DEFAULT_PORT)
    status.set_defaults(func=command_status)

    diag = sub.add_parser('diagnostics')
    diag.set_defaults(func=command_diagnostics)

    bundle = sub.add_parser('support-bundle')
    bundle.set_defaults(func=command_support_bundle)

    loop = sub.add_parser('loopback-test')
    loop.set_defaults(func=command_loopback)

    controller = sub.add_parser('controller')
    controller.set_defaults(func=command_controller)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print('Interrupted.')
        return 130
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
