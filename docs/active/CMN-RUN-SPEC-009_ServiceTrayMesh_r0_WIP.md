---
document_id: CMN-RUN-SPEC-009
title: Service Tray Mesh Run Specification
revision: r0
status: WIP
document_class: run_spec
owner: CommNet
package_class: SERVICE_TRAY_MESH_READY_WITH_DEBT
---

# Service Tray Mesh Run Specification

[SEC:CMN-RUN-SPEC-009::PURPOSE]
This run turns the Usability HUD package into a more appliance-like CommNet build. It adds a persistent controller window, a default local admin account, stronger notification signals, portal layout repair, BBS structure, RetroWeb social profile features, and a first serious Meshtastic bridge attempt.

[SEC:CMN-RUN-SPEC-009::STARTUP]
The primary launcher is `Start_CommNet.bat`. It opens the CommNet Control Window, starts the local server, monitors `/api/status`, and provides direct buttons for Admin HUD, Portal, Diagnostics, Copy Invite, and Stop Server. `Start_CommNet_Headless.bat` preserves the older launch pattern for diagnostic use.

[SEC:CMN-RUN-SPEC-009::DEFAULT-ADMIN]
Fresh local state shall seed an `admin` account with password `password`. The credential is stored through the same password-hash path as other users. The HUD shall warn while the default password remains active.

[SEC:CMN-RUN-SPEC-009::NOTIFICATIONS]
Pending permission requests, password reset requests, unread admin mail, default-password state, and mesh/device setup warnings shall be summarized centrally and shown as visible HUD badges, attention outlines, or warning cards.

[SEC:CMN-RUN-SPEC-009::PORTAL]
The public Community Portal shall use the same card-grid language as the Admin HUD. Portal apps shall open user-facing portal routes, while management links shall remain explicitly labeled as admin management routes.
