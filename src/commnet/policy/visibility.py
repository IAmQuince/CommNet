from __future__ import annotations

def visibility_label(mode: str) -> str:
    return mode.replace('_', ' ').title()
