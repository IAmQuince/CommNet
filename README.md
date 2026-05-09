# CommNet — 20260508_10_CommNetPortalPolish

CommNet is a local-first/LAN-first community portal and admin console demonstrator.

This package builds on `20260508_09_CommNetServiceTrayMesh` and focuses on cosmetic polish, shell separation, account controls, and route-tested display-setting persistence.

## Start

Run:

```bat
Start_CommNet.bat
```

This opens the persistent CommNet Control Window. Use it to open the Admin HUD, open the Portal, copy invite links, view diagnostics, or stop the server.

A headless launcher is retained:

```bat
Start_CommNet_Headless.bat
```

## Default admin

Fresh runtimes seed this local admin account:

```text
username: admin
password: password
```

The password is stored through the hash path, but it is intentionally insecure as a first-use appliance default. Change it before inviting other users onto the network.

## Main pages

```text
/admin/hud          Admin HUD; requires admin-capable login
/portal             CommNet user portal
/account            Account dashboard
/account/profile    User profile
/account/icon       Blank/generated icon control
/account/settings   User-facing display settings
/bbs                Local boards/threads/replies
/retroweb           RetroWeb local social/profile area
/admin/devices/meshtastic   Meshtastic install/probe/test page
```

## Admin boundary

`/admin/*` routes are no longer granted merely because the browser is on localhost. A user must have owner/admin role or explicit `admin.hud.view` permission.

Normal users can use the CommNet Portal and request more access. Admin-capable users get a `Switch to Admin HUD` option in the upper-right account dropdown.

## Display settings

Dark/light mode, density, and icon mode are applied through the shared renderer. This run adds route-level checks to catch pages that forget to apply persisted UI classes.

User-facing settings are available at:

```text
/account/settings
```

Admin display settings remain available at:

```text
/admin/settings/display
```

## Validation

Run:

```bat
Run_PortalPolish_Smoke.bat
```

This runs the cosmetic/access/settings checks for this package.

For the retained previous suite:

```bat
Run_ServiceTrayMesh_Smoke.bat
```

## Current known limits

- Generated account icons are implemented; full uploaded avatar file handling is deferred.
- UI settings are node-level in this prototype, not fully per-user yet.
- Meshtastic live validation requires a physical node and optional local dependencies.
- Local auth is not a production internet-facing security system.
