from pathlib import Path
import json, sys
root = Path(__file__).resolve().parents[2]
data = json.loads((root/"registries"/"transport_adapters.json").read_text(encoding="utf-8"))
required_fields = data.get("required_fields", [])
errors = []
ids = set()
for adapter in data.get("adapters", []):
    aid = adapter.get("adapter_id")
    if aid in ids: errors.append(f"Duplicate adapter {aid}")
    ids.add(aid)
    for field in required_fields:
        if field not in adapter: errors.append(f"Adapter {aid} missing {field}")
required_ids = {"meshtastic_serial","meshtastic_tcp","meshtastic_ble","meshtastic_mqtt","reticulum_rns","reticulum_lxmf","lan_http","bluetooth_ble","storage_node","phone_cache","drone_mule"}
for aid in sorted(required_ids - ids): errors.append(f"Missing expected adapter {aid}")
out = root/"audit_reports"/"active"/"transport_registry_report.md"
out.write_text("# Transport Registry Report\n\n" + ("PASS\n" if not errors else "FAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"), encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
