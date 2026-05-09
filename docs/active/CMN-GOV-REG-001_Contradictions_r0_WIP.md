---
document_id: CMN-GOV-REG-001
title: Contradiction and Reconciliation Register
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: GOV
  type: REG
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Contradiction and Reconciliation Register

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial contradiction register for CommNet. |

## 1. Purpose [SEC:CMN-GOV-REG-001::1]

This register records unresolved contradictions, ambiguous concepts, and decisions that need reconciliation before implementation.

## 2. Active Items [SEC:CMN-GOV-REG-001::2]

| ID | Topic | Conflict | Current resolution |
|---|---|---|---|
| CON-001 | Mesh terminology | Mesh can mean routing, peer sync, or local portal access. | Use specific terms: LAN, peer link, replication, gateway, true mesh. |
| CON-002 | Community web visibility | A user may read the portal without being listed in the directory. | Separate portal access from identity visibility. |
| CON-003 | School vs home defaults | School mode needs stricter privacy and review than home mode. | Use one policy engine with different presets. |
| CON-004 | File registry vs file server | Indexed files are not automatically shared. | Registry, visibility, review, and sharing are separate states. |

## 3. Reconciliation Rule [SEC:CMN-GOV-REG-001::3]

A contradiction is closed only when the governing document and related registry entries are both updated.
