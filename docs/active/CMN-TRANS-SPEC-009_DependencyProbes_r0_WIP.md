---
document_id: CMN-TRANS-SPEC-009
title: Dependency Probes
revision: r0
status: WIP
document_class: network_spec
owner: CommNet
package_class: NETWORK_READY_WITH_DEBT
---

# Dependency Probes

[SEC:CMN-TRANS-SPEC-009::1]

This controlled document was added in package `20260508_04_Network`.

## Scope

[SEC:CMN-TRANS-SPEC-009::2]

This run implements local loopback delivery, manual peer registration, LAN HTTP handshake/test delivery for reachable peers, optional dependency probing, deterministic route-decision records, bounded queue defaults, network diagnostics, and delivery audit evidence.

## Safe boundary

[SEC:CMN-TRANS-SPEC-009::3]

Meshtastic, Reticulum/LXMF, Bluetooth, storage nodes, phone caches, removable media, and drone/data-mule carriers remain specified or dependency-aware only unless a later package explicitly implements and verifies them.

## Requirements linkage

[SEC:CMN-TRANS-SPEC-009::4]

This document supports the `CMN-REQ-NET-*`, `CMN-REQ-TRANS-*`, `CMN-REQ-DEP-*`, and `CMN-REQ-AUD-DEL-*` requirements added for the network foundation run.
