---
document_id: CMN-SEC-SPEC-004
doc_id: CMN-SEC-SPEC-004
revision: r0_WIP
title: Admin Boundary
package: 20260508_10_CommNetPortalPolish
status: WIP
---

# CMN-SEC-SPEC-004 — Admin Boundary

## Rule

Admin pages are not available merely because the request comes from localhost. `/admin/*` requires a current session with owner/admin role or an explicit permission matching `admin.hud.view`.

## Behavior

- Anonymous local request to `/admin/hud` redirects to login.
- Normal signed-in user receives an access-denied portal page.
- Admin-capable user receives the Admin HUD.
- The account dropdown only shows `Switch to Admin HUD` when `/api/session` reports `can_admin=true`.

## Validation

`tools/dev/run_admin_boundary_smoke.py` confirms the anonymous, normal-user, and admin cases.
