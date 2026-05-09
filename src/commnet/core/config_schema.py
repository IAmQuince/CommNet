from __future__ import annotations

SERVICE_IDS = [
    'community_portal', 'personal_site', 'directory', 'library', 'makerspace', 'emergency',
    'marketplace', 'bbs', 'retroweb', 'events', 'work_board', 'file_registry',
    'device_registry', 'transport_diagnostics'
]

SERVICE_LABELS = {
    'community_portal': 'Community Portal',
    'personal_site': 'Personal Site',
    'directory': 'Community Directory',
    'library': 'Library',
    'makerspace': 'Makerspace',
    'emergency': 'Emergency Broadcast',
    'marketplace': 'Marketplace',
    'bbs': 'BBS',
    'retroweb': 'RetroWeb',
    'events': 'Events / Concert Demo',
    'work_board': 'Work / Services',
    'file_registry': 'File Registry',
    'device_registry': 'Device Registry',
    'transport_diagnostics': 'Transport Diagnostics',
}

DEPLOYMENT_PROFILES = [
    'minimal_local_demo', 'home_private', 'home_shared', 'school_classroom', 'school_admin',
    'library_local', 'makerspace', 'neighborhood', 'emergency_outage', 'developer_demo'
]
NODE_ROLES = ['personal_node', 'admin_node', 'portal_node', 'storage_node', 'gateway_node', 'school_node', 'demo_node']
VISIBILITY_MODES = [
    'private_local_only', 'visible_on_this_machine', 'visible_to_local_lan',
    'visible_to_approved_peers', 'visible_to_community_directory', 'gateway_exposed'
]
PRIVACY_MODES = ['strict_private', 'balanced_local', 'community_visible', 'gateway_exposed']
TRANSPORT_PROFILES = [
    'local_loopback', 'lan_wifi', 'meshtastic_lora', 'reticulum_lxmf', 'bluetooth',
    'storage_node', 'removable_media', 'phone_cache', 'drone_mule_sim'
]
DEVICE_TYPES = [
    'windows_pc', 'phone', 'raspberry_pi', 'meshtastic_radio', 'lora_microcontroller',
    'router', 'nas', 'storage_node', 'bluetooth_device', 'unknown'
]
TRUST_STATES = ['untrusted', 'known', 'trusted', 'blocked', 'owner_device']
PEER_TRUST_STATES = ['untrusted', 'known', 'trusted', 'blocked', 'self']
FILE_VISIBILITY = ['private', 'local_only', 'approved_peers', 'community_visible']
PAYLOAD_CLASSES = ['text_message', 'emergency_alert', 'directory_update', 'device_status', 'route_probe']
PRIORITIES = ['bulk', 'normal', 'urgent', 'emergency']

FORM_LIMITS = {
    'node_name': {'min': 3, 'max': 64},
    'admin_display_name': {'min': 1, 'max': 64},
    'location_label': {'min': 0, 'max': 64},
    'node_description': {'min': 0, 'max': 500},
    'device_name': {'min': 1, 'max': 64},
    'device_notes': {'min': 0, 'max': 500},
    'peer_name': {'min': 1, 'max': 64},
    'peer_url': {'min': 8, 'max': 260},
    'peer_notes': {'min': 0, 'max': 500},
    'message_body': {'min': 1, 'max': 2000},
    'file_root_label': {'min': 1, 'max': 64},
    'file_root_path': {'min': 1, 'max': 260},
    'share_label': {'min': 1, 'max': 64},
    'share_virtual_name': {'min': 1, 'max': 64},
    'share_root_path': {'min': 1, 'max': 260},
    'access_code': {'min': 4, 'max': 64},
    'username': {'min': 3, 'max': 32},
    'password': {'min': 8, 'max': 128},
    'password_hint': {'min': 0, 'max': 160},
    'mail_subject': {'min': 1, 'max': 160},
    'mail_body': {'min': 1, 'max': 5000},
    'permission_request_reason': {'min': 0, 'max': 500},
}

SHARE_PERMISSION_PROFILES = [
    'private', 'list_only', 'list_and_download', 'dropbox_upload_only',
    'list_download_upload_inbox', 'advanced_custom'
]
SHARE_VISIBILITY_MODES = ['private', 'lan_visible', 'approved_peers', 'community_visible']
LAN_ACCESS_MODES = ['localhost_only', 'lan_visible']
QUICK_SETUP_MODES = ['private_only', 'share_one_folder', 'share_selected_folders', 'advanced_drive_share']


DEFAULT_SERVICES = {
    sid: {
        'enabled': sid in {'community_portal', 'directory', 'emergency', 'bbs', 'transport_diagnostics'},
        'visible_in_portal': sid in {'directory', 'emergency', 'bbs'},
        'requires_review': sid in {'library', 'makerspace', 'marketplace', 'retroweb', 'personal_site'},
        'status': 'configured' if sid in {'community_portal', 'directory', 'emergency', 'bbs', 'transport_diagnostics'} else 'available_disabled',
    }
    for sid in SERVICE_IDS
}

DEFAULT_CONFIG = {
    'schema_version': 6,

    'node_id': '',
    'commnet_user_id': '',
    'node_display_name': '',
    'selected_network_path_id': '',
    'preferred_visitor_ip': '',
    'preferred_visitor_url': '',
    'selected_gateway': '',
    'selected_adapter_name': '',
    'hide_invalid_network_links': True,
    'warn_on_apipa_addresses': True,
    'identity_created_at': '',
    'preferred_lan_url': '',
    'copy_link_format': 'plain_text',
    'visitor_link_enabled': True,
    'peer_invite_enabled': False,
    'catena_adapter_enabled': False,
    'catena_com_port': '',
    'catena_baud_rate': 115200,
    'catena_ack_timeout_ms': 3000,
    'catena_payload_limit': 180,
    'catena_demo_mode': 'fake_until_configured',
    'first_run_complete': False,
    'node_name': 'Local CommNet Node',
    'deployment_profile': 'minimal_local_demo',
    'node_role': 'demo_node',
    'visibility_mode': 'private_local_only',
    'privacy_mode': 'strict_private',
    'admin_display_name': 'Local Admin',
    'location_label': '',
    'node_description': 'Local CommNet demonstrator node.',
    'server_host': '127.0.0.1',
    'server_port': 8765,
    'network_enabled': True,
    'lan_http_enabled': True,
    'lan_bind_host': '127.0.0.1',
    'lan_bind_port': 8765,
    'allow_manual_peers': True,
    'allow_inbound_peer_messages': False,
    'default_peer_trust': 'untrusted',
    'route_policy_profile': 'safe_local_first',
    'max_global_queue_depth': 1000,
    'max_adapter_queue_depth': 100,
    'max_delivery_retries': 3,
    'adapter_probe_interval_sec': 30,
    'desired_transport_profiles': ['local_loopback'],
    'quick_setup_complete': False,
    'lan_access_enabled': False,
    'lan_access_mode': 'localhost_only',
    'lan_bind_confirmed': False,
    'access_code_required_default': True,
    'default_share_permission': 'list_and_download',
    'default_share_visibility': 'private',
    'max_download_size_mb': 250,
    'max_upload_size_mb': 50,
    'hide_dotfiles': True,
    'hide_system_files': True,
    'show_virtual_paths_only': True,
    'commweb_landing_enabled': True,
    'default_visitor_route': '/portal',
    'admin_localhost_only': True,
    'visitor_admin_block_enabled': True,
    'captive_assist_enabled': True,
    'captive_portal_api_enabled': True,
    'router_integration_mode': 'guidance_only',
    'local_auth_enabled': True,
    'auth_bootstrap_local_only': True,
    'default_guest_role': 'guest',
    'retroweb_separate_login': True,
    'ui': {
        'theme': 'light',
        'nav_style': 'hybrid',
        'card_density': 'comfortable',
        'color_coding': True,
        'icon_mode': 'emoji',
        'show_advanced_cards': False,
        'show_demo_services': True,
        'show_simulated_devices': True,
        'hud_diagnostics': 'summary',
        'admin_home': 'hud',
        'guest_card_style': 'simple',
        'show_unavailable_guest_apps': 'grayed',
    },
    'emergency_info': {
        'public': True,
        'title': 'CommNet Emergency Info',
        'body': 'No emergency bulletin has been posted by the admin.',
        'outage_banner': False,
    },
    'personal_site': {
        'enabled': False,
        'title': 'Local CommNet Site',
        'summary': 'Personal site publishing is configured locally but not shared by default.',
        'visibility': 'private',
    },
    'services': DEFAULT_SERVICES,
}
