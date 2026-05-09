---
document_id: CMN-DEV-SPEC-002
title: Device Verification UX Specification
revision: r0
status: WIP
document_class: hardware_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Device Verification UX Specification

[SEC:CMN-DEV-SPEC-002::PURPOSE]
Device rows must distinguish configuration from verification. Adding a device row is not the same as proving that hardware is connected and responding.

[SEC:CMN-DEV-SPEC-002::STATES]
Device states include not_configured, candidate, configured, connected, failed, simulated, and unverified. Catena fake mode is always labeled Simulated.

[SEC:CMN-DEV-SPEC-002::CATENA]
Catena pages show selected serial port, fake/real mode, last attempted handshake, last result, and transcript access. A local ACK is not remote RF delivery confirmation.

[SEC:CMN-DEV-SPEC-002::DIAGNOSTICS]
Device diagnostics export explicit results suitable for copy/paste review.

