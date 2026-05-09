---
document_id: CMN-UI-ARCH-001
title: UI Functional Architecture
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: UI
  type: ARCH
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SEC-SPEC-001
- CMN-PRV-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# UI Functional Architecture

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial UI architecture for CommNet onboarding and configuration. |

## 1. Purpose [SEC:CMN-UI-ARCH-001::1]

The CommNet UI architecture defines how users move from flash-drive setup to local configuration, diagnostics, and community web entry.

## 2. Shell Concepts [SEC:CMN-UI-ARCH-001::2]

Future UI surfaces shall support:

- clear first-run entry point
- separated portal and admin modes
- dockable/reconfigurable panels where useful
- persistent status strip
- settings persistence
- autosave/restore of local scenario/config state
- logs and diagnostic export
- novice and advanced modes

## 3. Consequence Preview [SEC:CMN-UI-ARCH-001::3]

High-impact actions such as publishing, sharing, gateway exposure, role escalation, and destructive changes shall provide a consequence preview before apply.
