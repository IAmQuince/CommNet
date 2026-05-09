
from __future__ import annotations

PERMISSION_PROFILES = {
    'private': {'allow_list': False, 'allow_download': False, 'allow_upload': False, 'allow_delete': False, 'allow_overwrite': False},
    'list_only': {'allow_list': True, 'allow_download': False, 'allow_upload': False, 'allow_delete': False, 'allow_overwrite': False},
    'list_and_download': {'allow_list': True, 'allow_download': True, 'allow_upload': False, 'allow_delete': False, 'allow_overwrite': False},
    'preview_only': {'allow_list': True, 'allow_download': False, 'allow_upload': False, 'allow_delete': False, 'allow_overwrite': False},
    'dropbox_upload_only': {'allow_list': False, 'allow_download': False, 'allow_upload': True, 'allow_delete': False, 'allow_overwrite': False},
    'list_download_upload_inbox': {'allow_list': True, 'allow_download': True, 'allow_upload': True, 'allow_delete': False, 'allow_overwrite': False},
    'advanced_custom': {'allow_list': True, 'allow_download': True, 'allow_upload': False, 'allow_delete': False, 'allow_overwrite': False},
}

SHARE_VISIBILITY = ['private', 'lan_visible', 'approved_peers', 'community_visible']
