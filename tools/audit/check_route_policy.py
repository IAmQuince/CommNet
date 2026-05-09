from pathlib import Path
import json, sys
root = Path(__file__).resolve().parents[2]
policy = json.loads((root/"registries"/"route_policy.json").read_text(encoding="utf-8"))
payloads = json.loads((root/"registries"/"payload_classes.json").read_text(encoding="utf-8"))
adapters = json.loads((root/"registries"/"transport_adapters.json").read_text(encoding="utf-8"))
adapter_ids = {a["adapter_id"] for a in adapters.get("adapters", [])}
errors = []
for key in ["deterministic_process","scoring_inputs","tie_break_order","global_disallow_rules"]:
    if not policy.get(key): errors.append(f"route_policy missing {key}")
for pc in payloads.get("classes", []):
    for field in ["id","priority","typical_size","privacy","latency","deadline","allowed","disallowed","audit"]:
        if field not in pc: errors.append(f"payload {pc.get('id','UNKNOWN')} missing {field}")
    for aid in pc.get("allowed", []) + pc.get("disallowed", []):
        if aid not in adapter_ids:
            errors.append(f"payload {pc.get('id')} references unknown adapter {aid}")
out = root/"audit_reports"/"active"/"route_policy_report.md"
out.write_text("# Route Policy Report\n\n" + ("PASS\n" if not errors else "FAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"), encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
