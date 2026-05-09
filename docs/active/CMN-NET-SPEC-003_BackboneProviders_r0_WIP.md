---
document_id: CMN-NET-SPEC-003
title: Backbone Provider Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "NET", "type": "SPEC", "sequence": "003"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-NET-SPEC-001", "CMN-ARCH-SPEC-005"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/backbone_providers.json", "registries/transport_adapters.json"]
---
# Backbone Provider Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines first-class backbone providers. |

## 1. Purpose [SEC:CMN-NET-SPEC-003::1]

CommNet shall route application messages through provider adapters rather than allowing community apps to call transport libraries directly.

## 2. First-Class Providers [SEC:CMN-NET-SPEC-003::2]

| Provider | Role |
|---|---|
| Local HTTP/LAN | First high-bandwidth local path for nearby nodes. |
| Meshtastic | Required LoRa profile for practical off-the-shelf radio mesh devices. |
| Reticulum RNS | General resilient network backbone option. |
| LXMF | Store-and-forward message layer over Reticulum. |
| Bluetooth | Short-range optional adapter profile. |
| Serial | General USB/COM device and radio interface. |
| Storage/custody carriers | Static nodes, phones, removable media, drones, and other store-and-forward carriers. |

## 3. Provider Independence [SEC:CMN-NET-SPEC-003::3]

Meshtastic and Reticulum shall be modeled separately. Similarity of purpose does not imply transparent interoperability. Interoperability shall be treated as a tested bridge, not an assumption.

## 4. Application Boundary [SEC:CMN-NET-SPEC-003::4]

Emergency broadcast, BBS, texting, file transfer, RetroWeb, marketplace, and personal-site tools shall submit envelopes or bundle manifests to the transport manager. They shall not import Meshtastic, RNS, LXMF, Bluetooth, serial, or MQTT libraries directly.
