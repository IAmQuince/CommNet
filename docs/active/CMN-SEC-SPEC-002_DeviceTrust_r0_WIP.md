---
document_id: CMN-SEC-SPEC-002
title: Device Trust Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: SEC
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SEC-BASE-001
- CMN-NET-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Device Trust Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial device trust model. |

## 1. Purpose [SEC:CMN-SEC-SPEC-002::1]

Device trust defines how discovered or manually added devices become part of a deployment.

## 2. Trust States [SEC:CMN-SEC-SPEC-002::2]

| State | Meaning |
|---|---|
| discovered | Seen by the system but not trusted. |
| pending_review | Waiting for admin decision. |
| trusted_local | Approved for local service interaction. |
| trusted_peer | Approved for peer-link behavior. |
| restricted | Allowed only limited interaction. |
| blocked | Not allowed. |

## 3. Trust Assignment [SEC:CMN-SEC-SPEC-002::3]

Trust assignment shall be explicit and auditable. A device may have a role without broad access to files or services.
