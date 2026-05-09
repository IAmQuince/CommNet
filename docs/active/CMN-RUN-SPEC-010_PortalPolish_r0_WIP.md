---
document_id: CMN-RUN-SPEC-010
doc_id: CMN-RUN-SPEC-010
revision: r0_WIP
title: Portal Polish Run Specification
package: 20260508_10_CommNetPortalPolish
status: WIP
---

# CMN-RUN-SPEC-010 — Portal Polish

## Purpose

This run makes the CommNet Portal feel as structured and polished as the Admin HUD while creating a stronger boundary between common-user and admin experiences.

## Requirements addressed

- Common users receive a side panel and access to user-safe settings.
- Admin HUD and CommNet Portal are separated through distinct shells.
- User identity controls live in the upper-right account dropdown.
- Blank profile icon is shown until a user creates a generated icon.
- Users with admin capability can switch to Admin HUD; normal users cannot.
- `/admin/*` is protected server-side.
- Dark/light mode and density persistence are checked across page families.

## Added validation

- `run_admin_boundary_smoke.py`
- `run_shell_separation_smoke.py`
- `run_account_dropdown_smoke.py`
- `run_user_settings_route_smoke.py`

## Known limits

- Uploaded avatar processing is deferred.
- Per-user display settings are deferred; the node-level display config is used consistently.
