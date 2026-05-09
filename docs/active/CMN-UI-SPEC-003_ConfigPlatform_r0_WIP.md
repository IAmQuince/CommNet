---
document_id: CMN-UI-SPEC-003
title: Configuration Platform Specification
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
- CMN-SEC-SPEC-001
- CMN-PRV-SPEC-002
- CMN-DATA-SPEC-003
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Configuration Platform Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial configuration platform specification. |

## 1. Purpose [SEC:CMN-UI-SPEC-003::1]

The configuration platform is the powerful admin surface for engineering permissions, privacy, sharing, security, services, registry settings, devices, and gateway boundaries.

## 2. Required Workspaces [SEC:CMN-UI-SPEC-003::2]

| Workspace | Purpose |
|---|---|
| Overview | Current deployment status, profile, warnings, and next steps. |
| Devices | Discovery, node roles, trust states, and links. |
| Identity | local users, roles, recovery state, and visibility. |
| Privacy | visibility and directory controls. |
| Sharing | content and service policy builder. |
| Registry | file scanning, metadata, review status, and indexing. |
| Services | portal, directory, search, diagnostics, and other local services. |
| Gateway | optional boundary crossing controls. |
| Diagnostics | logs, health, audit reports, support bundle export. |
| Backup | snapshots, restore, and migration. |

## 3. Safety UX [SEC:CMN-UI-SPEC-003::3]

The platform shall distinguish preview, simulate, apply, rollback, and export states. High-impact changes shall be deliberate rather than accidental.
