# QuickShare Smoke Report

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/smoke/run_quickshare_smoke.py

QuickShare smoke: PASS

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/smoke/run_network_smoke.py

DEPENDENCY_PROBE_SMOKE_PASS
PEER_STORE_SMOKE_PASS
ROUTE_PLANNER_SMOKE_PASS
DELIVERY_ENGINE_SMOKE_PASS
LAN_ADAPTER_SMOKE_PASS
NETWORK_SMOKE_PASS

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/audit/check_lan_access_defaults.py

LAN access defaults audit: PASS

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/audit/check_visitor_admin_separation.py

Visitor/admin separation audit: PASS

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/audit/check_path_guard_rules.py

Path guard audit: PASS

$ /opt/pyvenv/bin/python /mnt/data/20260508_05_QuickShare/tools/audit/check_permission_profiles.py

Permission profile audit: PASS
