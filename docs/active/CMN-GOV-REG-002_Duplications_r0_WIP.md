---
document_id: CMN-GOV-REG-002
title: Duplication and Consolidation Register
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
- CMN-GOV-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Duplication and Consolidation Register

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial duplication register. |

## 1. Purpose [SEC:CMN-GOV-REG-002::1]

This register tracks areas where multiple documents describe the same behavior and states which source controls the final design.

## 2. Current Consolidation Areas [SEC:CMN-GOV-REG-002::2]

| ID | Area | Duplicate sources | Controlling source |
|---|---|---|---|
| DUP-001 | Role names | UI, privacy, security docs | CMN-SEC-SPEC-001 |
| DUP-002 | Onboarding tool list | UI spec and registry | registries/onboarding_tools.json plus CMN-UI-SPEC-001 |
| DUP-003 | File registry fields | data spec and metadata spec | CMN-DATA-SPEC-001 |
| DUP-004 | Audit event fields | audit spec and security docs | CMN-AUD-SPEC-002 |
