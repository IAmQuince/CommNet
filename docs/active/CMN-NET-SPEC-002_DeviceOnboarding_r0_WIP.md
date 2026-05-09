---
document_id: CMN-NET-SPEC-002
title: Device Onboarding Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: NET
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-ARCH-SPEC-002
- CMN-SEC-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Device Onboarding Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial device onboarding specification. |

## 1. Purpose [SEC:CMN-NET-SPEC-002::1]

Device onboarding adds local devices or peer nodes to a deployment without treating discovery as trust.

## 2. Onboarding Stages [SEC:CMN-NET-SPEC-002::2]

1. discover candidate device or accept manual entry
2. display capabilities and risks
3. assign node role
4. choose trust level
5. apply privacy and service rules
6. verify connectivity
7. create audit event and snapshot

## 3. Trust Rule [SEC:CMN-NET-SPEC-002::3]

A discovered device is not trusted by discovery alone. Trust must be assigned by policy and recorded.
## Backbone Requirements Update [SEC:CMN-NET-SPEC-002::B1]

Device onboarding shall identify what communication profiles a device can support, including LAN/Wi-Fi, Meshtastic serial/TCP/BLE/MQTT, Reticulum/LXMF, Bluetooth, generic serial, removable media, storage node, phone cache, or future data-mule behavior. Missing dependencies or hardware shall be represented as adapter status, not as setup failure for the whole system.
