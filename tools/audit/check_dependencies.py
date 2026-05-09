from pathlib import Path
import json, sys
root = Path(__file__).resolve().parents[2]
reg = root / "registries" / "dependencies.json"
profiles = root / "registries" / "install_profiles.json"
errors = []
data = json.loads(reg.read_text(encoding="utf-8"))
libs = {x["name"] for x in data.get("libraries", [])}
required = {"bottle","meshtastic","pyserial","paho-mqtt","rns","lxmf","zeroconf","bleak","waitress"}
missing = sorted(required - libs)
if missing:
    errors.append("Missing required expected library entries: " + ", ".join(missing))
pdata = json.loads(profiles.read_text(encoding="utf-8"))
for prof in pdata.get("profiles", []):
    for lib in prof.get("required_libraries", []) + prof.get("optional_libraries", []):
        if lib not in libs and lib not in {"python_stdlib","recommended_core","future_phone_client","future_drone_client"}:
            errors.append(f"Profile {prof['id']} references unknown library {lib}")
out = root / "audit_reports" / "active" / "dependency_report.md"
out.write_text("# Dependency Report\n\n" + ("PASS\n" if not errors else "FAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"), encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
