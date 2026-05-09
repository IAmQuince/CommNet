---
document_id: CMN-NET-SPEC-004
title: Meshtastic Adapter Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "NET", "type": "SPEC", "sequence": "004"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-NET-SPEC-003", "CMN-TRANS-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/transport_adapters.json", "registries/resource_limits.json"]
---
# Meshtastic Adapter Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines Meshtastic as first-class LoRa adapter family. |

## 1. Purpose [SEC:CMN-NET-SPEC-004::1]

Meshtastic shall be the first-class off-the-shelf LoRa radio ecosystem supported by CommNet.

## 2. Adapter Modes [SEC:CMN-NET-SPEC-004::2]

CommNet shall model Meshtastic access as multiple adapters: `meshtastic_serial`, `meshtastic_tcp`, `meshtastic_ble`, and `meshtastic_mqtt`.

## 3. Intended Payloads [SEC:CMN-NET-SPEC-004::3]

Meshtastic is intended for emergency alerts, short text, device status, directory deltas, route probes, file manifests, and retrieval instructions. It shall not be used for bulk file transfer except as a control or manifest path.

## 4. Resource Rules [SEC:CMN-NET-SPEC-004::4]

Meshtastic adapters shall use conservative send rates, bounded retries, duplicate suppression, bounded inbound queues, and cooldowns after repeated failures.

## 5. Claim Control [SEC:CMN-NET-SPEC-004::5]

The Meshtastic profile shall be considered available only when the package dependency is installed, the selected interface is configured, compatible hardware or endpoint is present, and a probe succeeds.
