from __future__ import annotations

from commnet.core.config_schema import FILE_VISIBILITY
from commnet.core.config_validation import validate_choice, validate_text


class FileRootStore:
    def __init__(self, store, audit=None):
        self.store = store
        self.audit = audit

    def add(self, label: str, root_path: str, default_visibility: str, scan_enabled: bool, include_subfolders: bool, review_required: bool) -> str:
        label, errors = validate_text('label', label, 'file_root_label')
        root_path, e = validate_text('root_path', root_path, 'file_root_path'); errors += e
        visibility, e = validate_choice('default_visibility', default_visibility, FILE_VISIBILITY); errors += e
        if errors:
            raise ValueError('; '.join(errors))
        root_id = self.store.add_file_root(label, root_path, visibility, scan_enabled, include_subfolders, review_required)
        if self.audit:
            self.audit.write('file_root_added', {'root_id': root_id, 'label': label, 'default_visibility': visibility, 'scan_enabled': scan_enabled})
        return root_id

    def delete(self, root_id: str) -> None:
        self.store.delete_file_root(root_id)
        if self.audit:
            self.audit.write('file_root_deleted', {'root_id': root_id})

    def list(self):
        return self.store.list_file_roots()
