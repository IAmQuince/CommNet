---
document_id: CMN-UI-SPEC-002
title: Launcher Shell Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: UI
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SCM-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Launcher Shell Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial launcher shell specification. |

## 1. Purpose [SEC:CMN-UI-SPEC-002::1]

The launcher shell provides obvious clickable entry points after a user unzips a package.

## 2. Future Launchers [SEC:CMN-UI-SPEC-002::2]

Future product packages may include:

| Launcher | Purpose |
|---|---|
| Start_Here | First-run setup guidance. |
| Open_Admin | Configuration platform. |
| Open_Portal | Community web portal. |
| Run_Diagnostics | Health and support reports. |
| Build_File_Registry | File indexing workflow. |
| Repair_Launchers | Recreate shortcuts after moving the package. |

## 3. Relative Path Rule [SEC:CMN-UI-SPEC-002::3]

Launchers shall use paths relative to the package or install root where practical. This avoids broken shortcuts after unzip.

## 4. Current Package Rule [SEC:CMN-UI-SPEC-002::4]

This pre-code package may include audit launchers. It does not include product launchers that pretend CommNet is implemented.
