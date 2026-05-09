---
document_id: CMN-UX-SPEC-005
doc_id: CMN-UX-SPEC-005
revision: r0_WIP
title: Portal Shell and Account Menu
package: 20260508_10_CommNetPortalPolish
status: WIP
---

# CMN-UX-SPEC-005 — Portal Shell and Account Menu

## Portal shell

The portal shell shall provide a side navigation panel with user-facing routes:

- Home
- Files
- Mail
- Request Access
- BBS
- RetroWeb
- Emergency Info
- Community Directory
- Demos
- Account Settings

The portal shell shall not expose admin configuration controls.

## Admin shell

The admin shell shall retain the Admin HUD side panel and identify itself as an admin area.

## Account menu

All normal pages shall include the upper-right account menu. It is hydrated by `/api/session`.

Signed-out users see:

- Sign in
- Create account
- Switch to CommNet Portal

Signed-in users see:

- My Account
- Profile
- Profile Icon
- Display Settings
- Mail
- Requests
- Switch to CommNet Portal
- Sign out

Admin-capable users additionally see:

- Switch to Admin HUD

## Profile icon

The default icon state is blank. A generated icon can be created from `/account/icon`.
