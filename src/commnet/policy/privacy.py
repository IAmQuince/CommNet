from __future__ import annotations

def is_private(cfg: dict) -> bool:
    return cfg.get('visibility_mode') in {'private_local_only', 'visible_on_this_machine'}
