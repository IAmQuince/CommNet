from __future__ import annotations

import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
if str(root / 'src') not in sys.path:
    sys.path.insert(0, str(root / 'src'))

# Stable aggregate smoke list. Server and LAN adapter smokes are retained as
# standalone scripts because they launch subprocess/network resources and are
# easier to diagnose independently on Windows laptops.
scripts = [
    'run_import_smoke.py', 'run_db_smoke.py', 'run_transport_smoke.py',
    'run_launcher_static_check.py', 'run_config_smoke.py', 'run_policy_smoke.py',
    'run_services_smoke.py', 'run_device_store_smoke.py', 'run_file_roots_smoke.py',
    'run_dependency_probe_smoke.py', 'run_peer_store_smoke.py', 'run_route_planner_smoke.py',
    'run_delivery_engine_smoke.py'
]
failures = []
for script in scripts:
    print(f'Running {script}...', flush=True)
    try:
        runpy.run_path(str(root / 'tools' / 'smoke' / script), run_name='__main__')
    except SystemExit as exc:
        code = int(exc.code or 0) if isinstance(exc.code, int) or exc.code is None else 1
        if code != 0:
            failures.append((script, code))
    except Exception as exc:
        failures.append((script, f'{type(exc).__name__}: {exc}'))
if failures:
    for script, code in failures:
        print(f'FAIL {script}: {code}')
    raise SystemExit(2)
print('Standalone retained: run_server_smoke.py')
print('Standalone retained: run_lan_adapter_smoke.py')
print('ALL_SMOKE_PASS')
