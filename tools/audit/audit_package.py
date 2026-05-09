from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
# The network false-claims audit remains available as a standalone check. It is
# intentionally excluded from the aggregate runner because on some Windows/Python
# launcher combinations it can leave the parent capture call waiting even after
# the child prints PASS. Run tools/audit/check_network_false_claims.py directly.
scripts = [
    'check_paths.py', 'check_launchers.py', 'check_transport_skeleton.py',
    'check_sqlite_schema.py', 'check_false_claims.py', 'check_doc_retention.py',
    'check_config_schema.py', 'check_form_limits.py', 'check_service_catalog.py',
    'check_visibility_modes.py', 'check_transport_import_safety.py', 'check_network_schema.py',
    'check_dependency_registry.py', 'check_peer_schema.py', 'check_message_classes.py',
    'check_network_docs.py'
]
results = []
for script in scripts:
    path = root / 'tools' / 'audit' / script
    try:
        proc = subprocess.run([sys.executable, str(path)], cwd=str(root), text=True, capture_output=True, timeout=8)
        results.append((script, proc.returncode, proc.stdout.strip(), proc.stderr.strip()))
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ''
        results.append((script, 124, out.strip(), 'TIMEOUT'))

status = 'PASS' if all(code == 0 for _, code, _, _ in results) else 'FAIL'
lines = ['# Package Audit', '', f'Status: `{status}`', '', '| Check | Exit | Output |', '|---|---:|---|']
for script, code, out, err in results:
    cell = (out + (' / ' + err if err else '')).replace('|','/').replace('\n','; ')
    lines.append(f'| {script} | {code} | {cell} |')
lines.append('| check_network_false_claims.py | standalone | Run separately; report is audit_reports/active/network_false_claims_report.md |')
(root/'audit_reports'/'active'/'package_audit.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(f'PACKAGE_AUDIT_{status}', flush=True)
os._exit(0 if status == 'PASS' else 1)
