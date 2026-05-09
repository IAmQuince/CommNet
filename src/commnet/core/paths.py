from __future__ import annotations

import os
from pathlib import Path


class RuntimePaths:
    """Centralized runtime path manager.

    Runtime paths are intentionally kept under runtime/local by default so the
    source package remains clean and private user state has one obvious home.
    """

    def __init__(self, package_root: Path):
        self.package_root = Path(package_root).resolve()
        override = os.environ.get('COMMNET_RUNTIME_DIR')
        self.local = Path(override).resolve() if override else self.package_root / 'runtime' / 'local'
        self.config = self.local / 'config'
        self.db = self.local / 'db'
        self.logs = self.local / 'logs'
        self.reports = self.local / 'reports'
        self.sites = self.local / 'sites'
        self.imports = self.local / 'imports'
        self.cache = self.local / 'cache'
        self.bundles = self.local / 'bundles'
        self.support = self.local / 'support'
        self.server_state = self.local / 'server_state.json'

    def ensure_all(self) -> None:
        for path in [
            self.local, self.config, self.db, self.logs, self.reports,
            self.sites, self.imports, self.cache, self.bundles, self.support,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def relative(self, path: Path) -> str:
        try:
            return str(Path(path).resolve().relative_to(self.package_root))
        except Exception:
            return str(path)
