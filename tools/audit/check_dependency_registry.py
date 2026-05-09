from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[2]
path=root/'registries/dependency_checks.json'
data=json.loads(path.read_text())
required={'meshtastic','pyserial','paho-mqtt','rns','lxmf','bleak','zeroconf','psutil','waitress'}
packages={x.get('package_name') for x in data}
missing=sorted(required-packages)
report=root/'audit_reports/active/dependency_probe_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Dependency Probe Registry Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: '+', '.join(missing)+'\n'), encoding='utf-8')
if missing: sys.exit(1)
print('DEPENDENCY_REGISTRY_PASS')
