from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from commnet.core.paths import RuntimePaths


def runtime():
    paths = RuntimePaths(ROOT)
    paths.ensure_all()
    return paths


def write_report(name: str, data: dict) -> Path:
    paths = runtime()
    out = paths.reports / name
    out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')
    return out


def result(name: str, checks: dict[str, bool], extra: dict | None = None) -> int:
    status = 'PASS' if all(checks.values()) else 'FAIL'
    payload = {'status': status, 'checks': checks, 'extra': extra or {}}
    path = write_report(name, payload)
    print(f"{name}: {status} -> {path}")
    if status != 'PASS':
        for k, v in checks.items():
            if not v:
                print(f"FAIL: {k}")
    return 0 if status == 'PASS' else 2
