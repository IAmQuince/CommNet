from pathlib import Path
import json, sys
root = Path(__file__).resolve().parents[2]
data = json.loads((root/"registries"/"resource_limits.json").read_text(encoding="utf-8"))
errors = []
for field in ["max_global_queue_depth","max_worker_threads","no_blocking_ui_thread","no_infinite_retry","audit_resource_events"]:
    if field not in data.get("global", {}): errors.append(f"global resource limits missing {field}")
for profile in ["low_bandwidth","standard","bulk","opportunistic","short_range"]:
    if profile not in data.get("profiles", {}): errors.append(f"missing resource profile {profile}")
# Ensure Meshtastic low bandwidth behavior exists indirectly.
if data.get("profiles", {}).get("low_bandwidth", {}).get("large_files_allowed") is not False:
    errors.append("low_bandwidth profile must explicitly disallow large files")
out = root/"audit_reports"/"active"/"resource_limits_report.md"
out.write_text("# Resource Limits Report\n\n" + ("PASS\n" if not errors else "FAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"), encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
