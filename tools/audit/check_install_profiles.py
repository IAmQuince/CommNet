from pathlib import Path
import json, sys
root = Path(__file__).resolve().parents[2]
data = json.loads((root/"registries"/"install_profiles.json").read_text(encoding="utf-8"))
required = {"minimal_local_demo","lan_wifi_node","meshtastic_lora_node","reticulum_node","full_experimental_node","developer_node"}
ids = {x["id"] for x in data.get("profiles", [])}
errors = []
for x in sorted(required - ids): errors.append(f"Missing profile {x}")
for prof in data.get("profiles", []):
    for field in ["id","label","required_libraries","hardware_assumptions","features","fail_soft"]:
        if field not in prof: errors.append(f"Profile {prof.get('id','UNKNOWN')} missing {field}")
out = root/"audit_reports"/"active"/"install_profile_report.md"
out.write_text("# Install Profile Report\n\n" + ("PASS\n" if not errors else "FAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"), encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
