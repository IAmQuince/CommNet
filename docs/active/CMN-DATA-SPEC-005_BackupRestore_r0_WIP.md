---
document_id: CMN-DATA-SPEC-005
title: Backup and Restore Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: DATA
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-DATA-SPEC-003
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Backup and Restore Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial backup and restore specification. |

## 1. Purpose [SEC:CMN-DATA-SPEC-005::1]

CommNet deployments need predictable backup and restore of policies, identities, registry metadata, logs, and selected content.

## 2. Backup Classes [SEC:CMN-DATA-SPEC-005::2]

| Class | Content |
|---|---|
| config_only | policies, profiles, services, roles, nodes |
| registry_metadata | file registry and metadata without content files |
| evidence_bundle | audit reports and support diagnostics |
| content_backup | selected content according to policy |
| full_local_backup | deployment state defined by the owner/admin |

## 3. Restore Rule [SEC:CMN-DATA-SPEC-005::3]

Restore operations shall preview consequences, preserve a pre-restore snapshot, and write audit events.
