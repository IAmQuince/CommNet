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
    claim_patterns = [
        re.compile(r"\bfully implemented\b", re.I),
        re.compile(r"\bproduction ready\b", re.I),
        re.compile(r"\bsecure by design and implemented\b", re.I),
        re.compile(r"\bmesh networking is implemented\b", re.I),
        re.compile(r"\bportal is implemented\b", re.I),
        re.compile(r"\badmin console is implemented\b", re.I),
    ]
    files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".json", ".txt", ".toml"}]
    for p in files:
        if "audit_reports" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat in claim_patterns:
            for m in pat.finditer(text):
                issues.append(f"Possible overclaim in {rel(p)}:{text.count(chr(10), 0, m.start()) + 1}: {m.group(0)}")
    lines.append(f"Files scanned: `{len(files)}`")
    lines += ["", "## Issues"]
    lines += [f"- {i}" for i in issues] if issues else ["- None"]
    return write_report("overclaim_scan.md", "Implementation Claim Scan", lines, not issues)

if __name__ == "__main__":
    raise SystemExit(main())
