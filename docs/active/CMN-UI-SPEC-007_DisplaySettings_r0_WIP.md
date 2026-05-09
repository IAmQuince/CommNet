---
document_id: CMN-UI-SPEC-007
title: Display Settings Specification
revision: r0
status: WIP
document_class: ui_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Display Settings Specification

[SEC:CMN-UI-SPEC-007::PURPOSE]
The display settings page gives the local admin lightweight control over CommNet appearance without editing source files or JSON by hand.

[SEC:CMN-UI-SPEC-007::SETTINGS]
The first implemented controls include theme, navigation style, card density, color coding, icon mode, advanced card visibility, demo visibility, simulated-device visibility, HUD diagnostics level, default admin page, guest card style, and unavailable-app display behavior.

[SEC:CMN-UI-SPEC-007::PERSISTENCE]
Settings are stored in the local configuration under the ui object and applied through server-rendered layout classes and CSS variables. Restore Defaults returns the UI to a conservative light/hybrid/comfortable layout.

[SEC:CMN-UI-SPEC-007::LIMITS]
The run does not introduce a heavy front-end framework. The page is intentionally simple and local-first.

