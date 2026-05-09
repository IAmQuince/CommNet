from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from _smoke_common import result, write_report

scripts = [
    'run_hud_smoke.py', 'run_ui_settings_smoke.py', 'run_auth_smoke.py', 'run_permission_request_smoke.py',
    'run_mail_smoke.py', 'run_share_policy_smoke.py', 'run_device_verification_smoke.py', 'run_route_access_smoke.py'
]
root = Path(__file__).resolve().parent
results = {}
for script in scripts:
    proc = subprocess.run([sys.executable, str(root / script)], cwd=str(root.parents[1]), text=True, capture_output=True, timeout=45)
    results[script] = {'returncode': proc.returncode, 'stdout': proc.stdout[-4000:], 'stderr': proc.stderr[-4000:]}
checks = {script: info['returncode'] == 0 for script, info in results.items()}
write_report('usability_hud_acceptance_detail.json', {'results': results})
raise SystemExit(result('usability_hud_acceptance_report.json', checks, {}))
