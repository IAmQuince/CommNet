# Run Status — 20260508_10_CommNetPortalPolish

Status: `PORTAL_POLISH_READY_WITH_DEBT`

## Launchers

- `Start_CommNet.bat` — persistent controller window launcher.
- `Start_CommNet_Headless.bat` — previous headless launcher pattern.
- `Run_PortalPolish_Smoke.bat` — run-specific cosmetic/access/settings smoke suite.
- `Run_ServiceTrayMesh_Smoke.bat` — retained and expanded compatibility smoke suite.

## Implemented

- CommNet Portal now has a HUD-quality side panel and richer portal dashboard behavior.
- Admin HUD and CommNet Portal use separate shells: `admin-shell` and `portal-shell`.
- Upper-right account menu is rendered on all normal pages and hydrated from `/api/session`.
- Signed-out users see sign-in/create-account options; signed-in users see account/profile/icon/settings/mail/request/logout options.
- Admin-capable users see `Switch to Admin HUD`; normal users do not.
- `/admin/*` now enforces server-side admin permission rather than relying on localhost access alone.
- User-facing account pages added: profile, profile icon, display settings, and security.
- Blank profile icon is shown by default; generated account icon support is available from `/account/icon`.
- Display settings persistence was revisited and route-tested across Portal, Account, BBS, RetroWeb, Mail-adjacent portal pages, and Admin shell paths.
- Prior BBS, RetroWeb social/profile/icon, default admin, controller, mail, permissions, shares, Catena, and Meshtastic features retained.

## Validation status

- Source/tool/test compile: PASS.
- Pytest doc/scaffold checks: PASS.
- Package audit: PASS.
- Navigation audit: PASS.
- Network false-claims audit: PASS.
- General false-claims audit: PASS.
- Admin boundary smoke: PASS.
- Shell separation smoke: PASS.
- Account dropdown smoke: PASS.
- User settings route persistence smoke: PASS.
- Default admin smoke: PASS.
- Portal grid smoke: PASS.
- BBS thread smoke: PASS.
- RetroWeb social/profile/icon smoke: PASS.
- Meshtastic dependency smoke: PASS.
- Meshtastic fake adapter smoke: PASS.
- Usability HUD acceptance: PASS.

## Remaining debt

- Profile image upload route is intentionally conservative/deferred; this run provides blank/generated profile icons.
- True Windows system tray icon remains deferred behind the controller-window baseline.
- Meshtastic live hardware validation still requires the user's actual device, drivers, and optional dependencies.
- Some inherited doc-control metadata warnings may remain from older WIP docs.
