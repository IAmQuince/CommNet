from __future__ import annotations

from urllib.parse import parse_qs


def parse_form(handler) -> dict[str, list[str]]:
    length = int(handler.headers.get('Content-Length', '0') or '0')
    raw = handler.rfile.read(length).decode('utf-8', errors='replace')
    return parse_qs(raw, keep_blank_values=True)


def first(form: dict[str, list[str]], key: str, default: str = '') -> str:
    values = form.get(key)
    return values[0] if values else default


def many(form: dict[str, list[str]], key: str) -> list[str]:
    return form.get(key, [])


def checked(form: dict[str, list[str]], key: str) -> bool:
    return key in form
