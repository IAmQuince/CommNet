from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "audit_reports" / "active"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
INTENDED_BASE = Path(r"C:\Users\iaq16\Documents\Code\CommNet")
PACKAGE_ROOT_NAME = ROOT.name

REQUIRED_DIRS = [
    ".github", "audit_reports", "audit_reports/active", "audit_reports/archive",
    "docs", "docs/active", "docs/archive", "docs/templates", "proof", "registries",
    "runtime", "src", "src/commnet", "tests", "tools", "tools/audit"
]
REQUIRED_FILES = [
    "README.md", "RELEASE_MANIFEST.md", "RELEASE_NOTES.md", ".gitignore",
    ".pre-commit-config.yaml", "CODEOWNERS", "CONTRIBUTING.md", "pyproject.toml"
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(relpath: str):
    with (ROOT / relpath).open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_front_matter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    raw = text[4:end]
    body = text[end + 5:]
    meta = {}
    current_key = None
    current_list = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*", line):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            if value == "[]":
                meta[key] = []
                current_list = None
            elif value == "":
                meta[key] = {}
                current_list = None
            else:
                meta[key] = value.strip('"')
                current_list = None
        elif line.strip().startswith("-") and current_key:
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(line.strip()[1:].strip())
        elif line.startswith("  ") and current_key and isinstance(meta.get(current_key), dict):
            sub = line.strip()
            if ":" in sub:
                k, v = sub.split(":", 1)
                meta[current_key][k.strip()] = v.strip().strip('"')
    return meta, body


def write_report(name: str, title: str, lines: list[str], ok: bool) -> int:
    status = "PASS" if ok else "FAIL"
    out = [f"# {title}", "", f"Status: `{status}`", ""] + lines + [""]
    (REPORT_DIR / name).write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"{title}: {status}")
    return 0 if ok else 1


def main() -> int:
    issues = []
    lines = []
    docs_reg = read_json("registries/documents.json")["documents"]
    doc_paths = sorted((ROOT / "docs" / "active").glob("*.md"))
    registry_by_id = {d["document_id"]: d for d in docs_reg}
    actual_ids = {}
    for p in doc_paths:
        meta, body = parse_front_matter(p.read_text(encoding="utf-8"))
        if meta and meta.get("document_id"):
            actual_ids[meta["document_id"]] = rel(p)
    for doc_id, path in actual_ids.items():
        if doc_id not in registry_by_id:
            issues.append(f"Document {doc_id} missing from registries/documents.json")
        elif registry_by_id[doc_id].get("path") != path:
            issues.append(f"Document {doc_id} path mismatch: registry={registry_by_id[doc_id].get('path')} actual={path}")
    for doc_id, d in registry_by_id.items():
        if doc_id not in actual_ids:
            issues.append(f"Registry document {doc_id} not found in docs/active")
    reqs = read_json("registries/requirements.json")["requirements"]
    req_ids = [r["id"] for r in reqs]
    if len(req_ids) != len(set(req_ids)):
        issues.append("Duplicate requirement IDs in requirements.json")
    tools = read_json("registries/onboarding_tools.json")["tools"]
    for t in tools:
        if t.get("status") != "SPEC_ONLY":
            issues.append(f"Onboarding tool {t.get('tool_id')} has non pre-code status {t.get('status')}")
        if t.get("requirement_id") not in req_ids:
            issues.append(f"Onboarding tool {t.get('tool_id')} requirement_id not found: {t.get('requirement_id')}")
    lines.append(f"Documents in registry: `{len(registry_by_id)}`")
    lines.append(f"Active markdown docs: `{len(actual_ids)}`")
    lines.append(f"Requirements: `{len(reqs)}`")
    lines.append(f"Onboarding tools: `{len(tools)}`")
    lines += ["", "## Issues"]
    lines += [f"- {i}" for i in issues] if issues else ["- None"]
    return write_report("registry_sync_report.md", "Registry Sync Report", lines, not issues)

if __name__ == "__main__":
    raise SystemExit(main())
