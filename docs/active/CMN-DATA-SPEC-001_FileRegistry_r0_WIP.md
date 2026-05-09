---
document_id: CMN-DATA-SPEC-001
title: File Registry Specification
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
- CMN-PRV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# File Registry Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial file registry specification. |

## 1. Purpose [SEC:CMN-DATA-SPEC-001::1]

The file registry is the controlled index of content known to a CommNet deployment. It is not automatically a sharing or publishing mechanism.

## 2. Minimum Fields [SEC:CMN-DATA-SPEC-001::2]

| Field | Meaning |
|---|---|
| content_id | Stable registry identity. |
| source_path | Original or current local path reference. |
| content_hash | Hash of file contents when available. |
| size_bytes | File size. |
| created_at | Registry creation timestamp. |
| observed_mtime | File modification time observed at scan. |
| owner_id | Owner or source identity. |
| importer_id | Actor or process that imported the item. |
| tags | Controlled or freeform tags. |
| review_state | Moderation state. |
| visibility_level | Visibility level. |
| sharing_policy_id | Policy controlling access. |
| provenance_note | Source and import context. |

## 3. Registry Principle [SEC:CMN-DATA-SPEC-001::3]

Files are selected, indexed, reviewed, and shared as separate actions. A registry scan shall not imply publication.
## Backbone Requirements Update [SEC:CMN-DATA-SPEC-001::B1]

The file registry shall support bundle manifests for store-and-forward transfer. Bulk files shall move through high-bandwidth or custody carriers while low-bandwidth transports such as Meshtastic carry manifests, notices, or small control payloads when policy allows.
