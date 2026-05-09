# Release Notes — 20260508_10_CommNetPortalPolish

This release is a cosmetic and interaction-polish pass focused on making the common-user CommNet Portal feel as structured as the Admin HUD while tightening the boundary between user and admin areas.

## Highlights

- The CommNet Portal now has its own side panel and HUD-style dashboard.
- Admin HUD and CommNet Portal are visually and structurally separated.
- General users no longer get `/admin/*` just because they are on the local machine; admin routes require an admin-capable session.
- The upper-right account menu now exists across the app.
- Users get account, profile, profile icon, display settings, and security pages.
- The default profile icon is blank until a generated icon is created.
- Display settings were revisited and route-tested so dark/light mode and density persist across major page families.

## Recommended first run

1. Extract the zip.
2. Run `Start_CommNet.bat`.
3. Sign in as `admin` / `password` when opening the Admin HUD.
4. Open `/portal` to review the user-facing side panel and account menu.
5. Open `/account/settings` and toggle theme/density, then move through Portal, BBS, RetroWeb, and Account pages to verify persistence.
6. Create a normal user and verify that account can use the portal but not `/admin/hud`.

## Validation

Run `Run_PortalPolish_Smoke.bat` for this run's targeted smoke tests.

## Known limits

- Generated profile icons are supported; full uploaded-image avatar handling remains deferred.
- Admin account still starts as `admin` / `password` on fresh runtime for appliance-style first use; change it before inviting other users.
- Meshtastic live verification still depends on physical hardware and local optional dependencies.
