import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    return json.loads((ROOT / "registries" / name).read_text(encoding="utf-8"))


def test_requirements_exist():
    data = load("requirements.json")
    assert len(data["requirements"]) >= 40


def test_onboarding_tools_exist():
    data = load("onboarding_tools.json")
    assert len(data["tools"]) >= 30
    assert all(t["status"] == "SPEC_ONLY" for t in data["tools"])
