from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_src_package_is_marked():
    init = ROOT / "src" / "commnet" / "__init__.py"
    assert init.exists()
    text = init.read_text(encoding="utf-8")
    assert "CommNet local configuration package" in text
    assert "__version__" in text
