from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
wheels = root/"wheels"
errors = []
claimed = list(wheels.rglob("wheel_manifest*.json")) + list(wheels.rglob("*.whl.claim"))
if claimed:
    errors.append("Found files that look like wheel claims: " + ", ".join(str(p.relative_to(root)) for p in claimed))
# In this requirements package, no .whl files are required. If present, they are listed only as physical files, not claimed.
whls = list(wheels.rglob("*.whl"))
out = root/"audit_reports"/"active"/"wheelhouse_report.md"
body = "# Wheelhouse Report\n\n"
body += "PASS\n\n"
body += f"Physical wheel files found: {len(whls)}\n\n"
if whls:
    body += "\n".join(f"- {p.relative_to(root)}" for p in whls) + "\n"
if errors:
    body = "# Wheelhouse Report\n\nFAIL\n\n" + "\n".join(f"- {e}" for e in errors) + "\n"
out.write_text(body, encoding="utf-8")
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
