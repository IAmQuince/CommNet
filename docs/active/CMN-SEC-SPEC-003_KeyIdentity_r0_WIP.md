---
document_id: CMN-SEC-SPEC-003
title: Key Identity and Recovery Specification
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
- CMN-SEC-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Key Identity and Recovery Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial local identity and recovery specification. |

## 1. Purpose [SEC:CMN-SEC-SPEC-003::1]

CommNet identity must work locally and avoid assuming a centralized public authority.

## 2. Identity Principles [SEC:CMN-SEC-SPEC-003::2]

- local identity first
- role is separate from identity
- visibility is separate from identity
- recovery is explicit and auditable
- school or organization authority may be layered on top of local identity

## 3. Recovery Principle [SEC:CMN-SEC-SPEC-003::3]

Recovery must not silently bypass ownership. Future implementation should define local recovery files, backup restore, admin reset policies, and physical-machine authority assumptions.
