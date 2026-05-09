---
document_id: CMN-ARCH-SPEC-003
title: Service Model Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: ARCH
  type: SPEC
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
# Service Model Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial service model for CommNet. |

## 1. Purpose [SEC:CMN-ARCH-SPEC-003::1]

The service model defines what kinds of local services CommNet may expose and how those services relate to privacy, roles, and audit.

## 2. Candidate Services [SEC:CMN-ARCH-SPEC-003::2]

| Service | Default | Notes |
|---|---|---|
| portal | off until configured | User-facing local community web. |
| admin_console | local admin only | Configuration platform. |
| file_registry | private | Indexes selected folders; does not publish by default. |
| directory | private | Publishes approved visible entries only. |
| search | private | May search local approved registry items. |
| forum | off | Requires moderation rules. |
| wiki_pages | off | Requires authoring and review policy. |
| media_library | off | Requires review state and content rules. |
| diagnostics | admin only | Health, logs, reports, support bundle. |

## 3. Enablement Rule [SEC:CMN-ARCH-SPEC-003::3]

Service enablement shall be explicit, auditable, and snapshot-backed. Enabling a service shall not automatically expose private content.
