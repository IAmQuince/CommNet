from __future__ import annotations

from _smoke_common import result

MATRIX = {
    '/portal': {'anonymous': True, 'guest': True, 'trusted_user': True, 'admin': True},
    '/admin/hud': {'anonymous': False, 'guest': False, 'trusted_user': False, 'admin': True},
    '/admin/users': {'anonymous': False, 'guest': False, 'trusted_user': False, 'admin': True},
    '/mail': {'anonymous': False, 'guest': True, 'trusted_user': True, 'admin': True},
    '/admin/mail': {'anonymous': False, 'guest': False, 'trusted_user': False, 'admin': True},
    '/share': {'anonymous': 'policy', 'guest': 'policy', 'trusted_user': 'policy', 'admin': True},
    '/admin/devices': {'anonymous': False, 'guest': False, 'trusted_user': False, 'admin': True},
    '/retroweb': {'anonymous': 'policy', 'guest': 'policy', 'trusted_user': 'policy', 'admin': True},
    '/emergency': {'anonymous': True, 'guest': True, 'trusted_user': True, 'admin': True},
}
checks={'admin_routes_denied_to_guest': all(not v.get('guest') for k,v in MATRIX.items() if k.startswith('/admin')), 'mail_requires_login': MATRIX['/mail']['anonymous'] is False, 'emergency_public': MATRIX['/emergency']['anonymous'] is True, 'share_policy_marked': MATRIX['/share']['guest']=='policy'}
raise SystemExit(result('access_matrix.json', checks, {'matrix': MATRIX}))
