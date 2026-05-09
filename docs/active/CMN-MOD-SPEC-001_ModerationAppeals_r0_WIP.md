---
document_id: CMN-MOD-SPEC-001
title: Moderation and Appeals Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: MOD
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-AUD-SPEC-002
- CMN-PRV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Moderation and Appeals Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial moderation and appeals specification. |

## 1. Purpose [SEC:CMN-MOD-SPEC-001::1]

Local community systems need content review without assuming one policy fits every home, school, library, or neighborhood.

## 2. Review States [SEC:CMN-MOD-SPEC-001::2]

| State | Meaning |
|---|---|
| unreviewed | Indexed or imported but not approved. |
| reviewed_ok | Approved under current policy. |
| restricted | Available only to certain roles or contexts. |
| blocked | Not available through the portal. |
| broken | Item does not function or cannot be opened. |
| admin_review | Needs administrator decision. |

## 3. Accountability [SEC:CMN-MOD-SPEC-001::3]

Moderation actions should include actor, reason code, target, result, timestamp, and review context. Appeals may be enabled by deployment profile.
