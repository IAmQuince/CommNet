---
document_id: CMN-ARCH-SPEC-005
title: Hardware and Software Agnostic Model Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: ARCH
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-ARCH-NAR-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Hardware and Software Agnostic Model Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial universality specification for CommNet. |

## 1. Purpose [SEC:CMN-ARCH-SPEC-005::1]

CommNet shall be designed around logical capabilities rather than specific hardware brands, router models, operating systems, or transport layers.

## 2. Abstraction Areas [SEC:CMN-ARCH-SPEC-005::2]

| Area | Abstract concept |
|---|---|
| identity | local identity, role, trust level |
| node | logical role and advertised capabilities |
| transport | LAN, Wi-Fi, peer link, manual transfer, future mesh |
| storage | local folder, removable drive, NAS, server, cache |
| service | portal, registry, directory, search, diagnostics |
| policy | visibility, sharing, permissions, moderation, gateway |
| evidence | audit event, snapshot, manifest, report |

## 3. Implementation Rule [SEC:CMN-ARCH-SPEC-005::3]

Future code may include adapters for specific platforms, but the core domain model shall not assume one device type as mandatory.
## Backbone Requirements Update [SEC:CMN-ARCH-SPEC-005::B1]

Hardware/software agnosticism is implemented through provider and adapter boundaries. Application tools shall not depend on Meshtastic, RNS, LXMF, Bluetooth, serial, LAN, or storage-node libraries directly. New communication paths shall be added as transport adapters with structured status, capability, estimate, send, receive, health, and shutdown behavior.
