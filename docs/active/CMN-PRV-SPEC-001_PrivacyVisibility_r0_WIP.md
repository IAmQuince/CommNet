---
document_id: CMN-PRV-SPEC-001
title: Privacy and Visibility Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: PRV
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SEC-BASE-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Privacy and Visibility Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial privacy and visibility specification. |

## 1. Purpose [SEC:CMN-PRV-SPEC-001::1]

This specification separates privacy from visibility and makes opt-in visibility a core rule.

## 2. Visibility Levels [SEC:CMN-PRV-SPEC-001::2]

| Level | Meaning |
|---|---|
| private_local | Visible only to the owner/admin context. |
| device_local | Visible on the same machine to authorized users. |
| local_network | Discoverable to authorized users on the local deployment. |
| approved_peer | Discoverable to approved peer nodes under policy. |
| gateway_exposed | Exposed beyond local boundary by explicit gateway policy. |

## 3. Opt-In Rule [SEC:CMN-PRV-SPEC-001::3]

Users, nodes, services, and content items are not visible in the community directory unless explicitly enabled.
