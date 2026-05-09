---
document_id: CMN-MESH-SPEC-001
title: Meshtastic Bridge Specification
revision: r0
status: WIP
document_class: transport_spec
owner: CommNet
package_class: SERVICE_TRAY_MESH_READY_WITH_DEBT
---

# Meshtastic Bridge Specification

[SEC:CMN-MESH-SPEC-001::PURPOSE]
The Meshtastic bridge provides a low-bandwidth, resilient side channel for short CommNet messages. It is not a file sharing, media, preview, or full web-page transport.

[SEC:CMN-MESH-SPEC-001::MODES]
The first implementation supports dependency detection, candidate serial-port listing, fake adapter smoke testing, serial probe attempts, short test text transmission, and a local transcript of events. TCP and BLE remain future extensions.

[SEC:CMN-MESH-SPEC-001::STATES]
The UI shall distinguish missing dependency, no ports detected, candidate ports found, configured unverified, connected, send failed, receive active, failed, and simulated states. A device row or HUD card shall not claim connected status without a successful probe or send result.

[SEC:CMN-MESH-SPEC-001::SAFETY]
CommNet shall not send passwords, password hints, session tokens, file contents, RetroWeb media, or large JSON payloads over Meshtastic. The first payloads are short test messages and future compact notices such as ping, bulletin, mail notice, request-access notice, and node beacon.

[SEC:CMN-MESH-SPEC-001::INSTALL-HELP]
If the required Python packages are missing, the admin page shall show copyable setup instructions and continue to let the rest of CommNet run normally.
