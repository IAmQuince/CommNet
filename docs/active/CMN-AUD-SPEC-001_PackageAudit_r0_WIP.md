---
document_id: CMN-AUD-SPEC-001
title: Package Audit Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: AUD
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-003
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Package Audit Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial package audit specification. |

## 1. Purpose [SEC:CMN-AUD-SPEC-001::1]

The package audit gives the user a way to verify that a delivered zip contains the required structure, docs, registries, reports, and evidence.

## 2. Audit Areas [SEC:CMN-AUD-SPEC-001::2]

The audit shall check:

- required root files and directories
- path length under the intended Windows extraction path
- controlled document metadata
- registry/document consistency
- requirement traceability presence
- overclaiming of implemented product behavior
- package manifest presence

## 3. Audit Outputs [SEC:CMN-AUD-SPEC-001::3]

Audit reports shall be written to `audit_reports/active`. A package is reviewable only when the audit output is readable and gives specific pass/fail results.
