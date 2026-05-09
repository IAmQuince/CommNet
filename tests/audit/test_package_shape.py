from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_roots_exist():
    for rel in ["docs/active", "registries", "tools/audit", "audit_reports/active", "src/commnet"]:
        assert (ROOT / rel).exists(), rel
