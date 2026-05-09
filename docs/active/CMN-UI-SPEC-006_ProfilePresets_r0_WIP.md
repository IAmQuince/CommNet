---
document_id: CMN-UI-SPEC-006
title: Profile Presets Specification
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
- CMN-PRV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Profile Presets Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial profile preset specification. |

## 1. Purpose [SEC:CMN-UI-SPEC-006::1]

Presets make CommNet usable for different contexts while keeping the same underlying configuration model.

## 2. Initial Presets [SEC:CMN-UI-SPEC-006::2]

| Preset | Default posture |
|---|---|
| home_private | Single household, private local use. |
| home_shared | Household sharing with explicit approval. |
| school_classroom | Strict student privacy and review. |
| school_admin | Administrative management of school deployment. |
| library_public_local | Public local browsing with curated content. |
| makerspace | Shared tools and community resources. |
| neighborhood | Local community directory and shared resources. |
| emergency_outage | Offline notices, resources, and local coordination. |

## 3. Preset Rule [SEC:CMN-UI-SPEC-006::3]

Presets are starting points. They shall be exportable and editable by authorized admins.
