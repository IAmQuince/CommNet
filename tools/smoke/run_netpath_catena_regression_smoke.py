from __future__ import annotations
import subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
scripts=['run_import_smoke.py','run_node_identity_smoke.py','run_network_path_smoke.py','run_link_selection_smoke.py','run_catena_transcript_smoke.py','run_catena_real_adapter_fakeport_smoke.py']
lines=['# NetPath Catena Regression Smoke']
ok=True
for script in scripts:
    cp=subprocess.run([sys.executable, str(root/'tools'/'smoke'/script)], cwd=str(root), text=True, capture_output=True)
    lines.append(f'- {script}: {"PASS" if cp.returncode==0 else "FAIL"}')
    if cp.returncode!=0:
        ok=False; lines.append('```'); lines.append(cp.stdout+cp.stderr); lines.append('```')
(root/'proof'/'netpath_catena_regression_smoke_report.md').write_text('\n'.join(lines)+'\n\nResult: '+('PASS' if ok else 'FAIL')+'\n', encoding='utf-8')
raise SystemExit(0 if ok else 1)
