from __future__ import annotations
import subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
scripts=['check_network_path_rules.py','check_apipa_not_recommended.py','check_link_selected_path.py','check_catena_real_adapter.py','check_catena_delivery_claims.py']
lines=['# NetPath Catena Audit']
ok=True
for script in scripts:
    cp=subprocess.run([sys.executable, str(root/'tools'/'audit'/script)], cwd=str(root), text=True, capture_output=True)
    lines.append(f'- {script}: {"PASS" if cp.returncode==0 else "FAIL"}')
    if cp.returncode!=0:
        ok=False; lines.append('```'); lines.append(cp.stdout+cp.stderr); lines.append('```')
(root/'audit_reports'/'active'/'netpath_catena_audit.md').write_text('\n'.join(lines)+'\n\nResult: '+('PASS' if ok else 'FAIL')+'\n', encoding='utf-8')
raise SystemExit(0 if ok else 1)
