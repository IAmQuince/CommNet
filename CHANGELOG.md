# CHANGELOG — 20260508_10_CommNetPortalPolish

## Added

- Dedicated CommNet Portal shell with user-facing side navigation.
- Stronger Admin HUD versus CommNet Portal separation through distinct shell classes and navigation models.
- `src/commnet/ux/portal_model.py` for portal navigation groups.
- Upper-right account dropdown shared across Admin, Portal, Account, BBS, RetroWeb, Mail, Share, and Emergency pages.
- `/api/session` for safe account-menu hydration: signed-in state, display name, role, admin switch eligibility, and icon state.
- Account pages:
  - `/account/profile`
  - `/account/icon`
  - `/account/settings`
  - `/account/security`
- User profile storage table for about text and account icon state.
- Generated account icon support; blank icon remains the default until a user creates one.
- Server-side `/admin/*` permission boundary.
- Clean Admin HUD access-denied page for non-admin users.
- Portal status row with visible share, unread mail, pending request, and admin-switch availability indicators.
- Portal-polish smoke scripts:
  - `run_admin_boundary_smoke.py`
  - `run_shell_separation_smoke.py`
  - `run_account_dropdown_smoke.py`
  - `run_user_settings_route_smoke.py`

## Changed

- `/admin/*` now requires an owner/admin role or an explicit `admin.hud.view` permission.
- Unauthenticated local users are redirected to login before reaching the Admin HUD.
- Normal signed-in users can use the portal but cannot switch to, or manually open, the Admin HUD.
- Portal pages now use a sidebar layout similar in richness to the Admin HUD without exposing admin controls.
- User display settings use the same renderer/config path as admin display settings so theme and density persist between pages.
- Top bar now reserves a clear identity/control area on the right.
- `server_version` and `/api/status` package status updated to `PORTAL_POLISH_READY_WITH_DEBT`.

## Preserved

- Persistent control-window launcher.
- Default admin account bootstrap: `admin` / `password`.
- Default-password warning.
- Notification badges and HUD attention states.
- BBS boards, threads, replies, and seeded welcome post.
- RetroWeb profile/social/gallery/posts/comments behavior.
- Meshtastic dependency detection, fake adapter, serial probe/send-test paths, admin page, and API status.
- Shares, mail, permission requests, Catena fake/serial scaffolding, QuickShare, network path selection, APIPA rejection, and diagnostics.

## Deferred

- Full uploaded avatar processing/resizing. The server-side table supports icon state, but this run only implements blank/generated account icons safely.
- Per-user UI preferences. The current prototype persists local display settings through the node config so the route-level renderer is consistent.
- Production-grade authentication, internet exposure, and role federation.
- Full RetroWeb media import/playback migration.
- Meshtastic live hardware proof without the user's physical node.
