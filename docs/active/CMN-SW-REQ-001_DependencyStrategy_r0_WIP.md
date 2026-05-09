---
document_id: CMN-SW-REQ-001
title: Software Dependency Strategy
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "SW", "type": "REQ", "sequence": "001"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-GOV-STD-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/dependencies.json", "requirements/requirements_core.txt"]
---
# Software Dependency Strategy

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines dependency tiers and communication-library profiles. |

## 1. Purpose [SEC:CMN-SW-REQ-001::1]

CommNet shall remain accessible to a non-developer receiving a flash-drive package while still supporting real communication backbones such as Meshtastic, Reticulum/LXMF, LAN/Wi-Fi, Bluetooth, serial, and future custody carriers.

## 2. Dependency Doctrine [SEC:CMN-SW-REQ-001::2]

1. The local configuration interface shall launch with Python and the packaged codebase even when optional hardware libraries are missing.
2. External libraries shall be grouped into install profiles instead of being forced into one global dependency set.
3. Hardware-specific imports shall be isolated inside adapter modules.
4. An unavailable dependency shall produce a structured adapter state, not an application crash.
5. Offline installation shall use a wheelhouse and requirements files stored in the package.

## 3. Required Baseline [SEC:CMN-SW-REQ-001::3]

The baseline local demonstrator shall use Python standard library services, SQLite through `sqlite3`, static HTML/CSS/JavaScript, and a vendored Bottle-compatible web layer. Waitress may be used when present for a more robust local WSGI server.

## 4. Backbone Libraries [SEC:CMN-SW-REQ-001::4]

Meshtastic is required for the Meshtastic LoRa profile. Reticulum RNS and LXMF are required for the Reticulum profile. PySerial is required for serial radio access. Paho-MQTT is required for Meshtastic MQTT bridging. Zeroconf is recommended for LAN discovery. Bleak is required only for Bluetooth profiles.

## 5. Claim Control [SEC:CMN-SW-REQ-001::5]

A package shall not claim Meshtastic, Reticulum, Bluetooth, or Wi-Fi communication capability unless the dependency, configuration, hardware presence, and adapter health checks pass.
