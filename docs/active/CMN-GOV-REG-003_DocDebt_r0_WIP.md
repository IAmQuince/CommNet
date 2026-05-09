---
document_id: CMN-GOV-REG-003
title: Documentation Update Debt Register
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
# Documentation Update Debt Register

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial documentation debt register. |

## 1. Purpose [SEC:CMN-GOV-REG-003::1]

This register records useful but incomplete documentation work so the package can stay honest without blocking every future task.

## 2. Open Debt [SEC:CMN-GOV-REG-003::2]

| Debt ID | Item | Impact | Planned handling |
|---|---|---|---|
| DEBT-001 | Detailed schemas are currently represented as JSON registry field conventions rather than full JSON Schema files. | Medium | Add formal schemas in the first implementation planning sprint. |
| DEBT-002 | UI mockups are specifications only; no executable GUI exists in this package. | Low | Build UI proof in a later sprint after the coding gate. |
| DEBT-003 | Networking implementation choices are not selected. | Medium | Decide after transport abstraction and first local-only portal proof. |
| DEBT-004 | Legal/policy review is not performed. | Medium | Keep school/library deployments in review posture until local policy is checked. |
