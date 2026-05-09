# Release Manifest

Package: `20260508_10_CommNetPortalPolish`  
Class: `PORTAL_POLISH_READY_WITH_DEBT`  
Date: `2026-05-08`  
Baseline: `20260508_09_CommNetServiceTrayMesh`

## Included roots

- `.github/`
- `audit_reports/`
- `docs/`
- `proof/`
- `registries/`
- `requirements/`
- `src/`
- `tests/`
- `tools/`
- `wheels/`

## Primary source additions and updates

- `src/commnet/ux/portal_model.py`
- Updated `src/commnet/server/app.py`
- Updated `src/commnet/server/templates.py`
- Updated `src/commnet/web/static/app.js`
- Updated `src/commnet/web/static/style.css`
- Updated `src/commnet/core/db.py`
- Updated `src/commnet/identity/user_store.py`

## Primary run scripts

- `Start_CommNet.bat`
- `Start_CommNet_Headless.bat`
- `Run_PortalPolish_Smoke.bat`
- `Run_ServiceTrayMesh_Smoke.bat`

## Primary docs added

- `docs/active/CMN-RUN-SPEC-010_PortalPolish_r0_WIP.md`
- `docs/active/CMN-UX-SPEC-005_PortalShellAccountMenu_r0_WIP.md`
- `docs/active/CMN-SEC-SPEC-004_AdminBoundary_r0_WIP.md`

## Primary proof reports

- `runtime/local/reports/admin_boundary_report.json`
- `runtime/local/reports/shell_separation_report.json`
- `runtime/local/reports/account_dropdown_report.json`
- `runtime/local/reports/user_settings_route_report.json`
- Retained reports for default admin, portal grid, BBS, RetroWeb, Meshtastic, and usability HUD acceptance.
