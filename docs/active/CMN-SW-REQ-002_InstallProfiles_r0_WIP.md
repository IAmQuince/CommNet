---
document_id: CMN-SW-REQ-002
title: Install Profile Requirements
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "SW", "type": "REQ", "sequence": "002"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-SW-REQ-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/install_profiles.json"]
---
# Install Profile Requirements

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines install profiles for accessible deployment. |

## 1. Purpose [SEC:CMN-SW-REQ-002::1]

Install profiles allow the same CommNet package to serve a local demo user, a LAN/Wi-Fi node, a Meshtastic LoRa node, a Reticulum node, a full experimental node, and a developer without forcing every dependency on every user.

## 2. Profiles [SEC:CMN-SW-REQ-002::2]

| Profile | Intended user | Backbone behavior |
|---|---|---|
| minimal_local_demo | First launch / no hardware | Local UI, loopback messaging, simulated transports. |
| lan_wifi_node | Home/school LAN | Local HTTP transport and mDNS peer discovery. |
| meshtastic_lora_node | LoRa radio user | Meshtastic serial/TCP/BLE/MQTT adapters as available. |
| reticulum_node | Resilient mesh/backbone user | RNS and LXMF adapters. |
| full_experimental_node | Advanced testbed | All practical adapters enabled if dependencies and hardware pass. |
| developer_node | Contributor | Test, lint, audit, packaging, diagnostics tools. |

## 3. Fail-Soft Requirement [SEC:CMN-SW-REQ-002::3]

Missing optional profile dependencies shall disable the corresponding profile features and expose actionable diagnostics. Missing optional dependencies shall not prevent the local admin UI from starting.

## 4. Offline Installer Behavior [SEC:CMN-SW-REQ-002::4]

Profile installers shall install only the selected requirements from local wheelhouse folders. If a wheel is absent, the installer shall report that the wheelhouse is incomplete rather than attempting a hidden internet install.
