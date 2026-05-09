import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_have_front_matter_and_ids():
    """Every active document keeps machine-readable front matter.

    Older CommNet docs were intentionally lightweight and do not all carry
    section anchors yet. Section anchors are validated when present, but the
    non-regression requirement for this package is that active documents keep
    parseable front matter and a document_id.
    """
    for p in (ROOT / "docs" / "active").glob("*.md"):
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---\n"), p
        assert "document_id:" in text, p
        m = re.search(r"document_id:\s*([^\n]+)", text)
        assert m, p
        doc_id = m.group(1).strip().strip('"')
        assert doc_id, p
        if "[SEC:" in text:
            assert f"[SEC:{doc_id}::" in text, p
