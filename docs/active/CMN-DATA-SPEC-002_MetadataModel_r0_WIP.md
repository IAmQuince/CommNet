---
document_id: CMN-DATA-SPEC-002
title: Metadata Model Specification
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
- CMN-DATA-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Metadata Model Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial metadata model specification. |

## 1. Purpose [SEC:CMN-DATA-SPEC-002::1]

Metadata gives content meaning without requiring modification of original files.

## 2. Metadata Groups [SEC:CMN-DATA-SPEC-002::2]

| Group | Examples |
|---|---|
| descriptive | title, summary, tags, category |
| provenance | owner, importer, source, date observed |
| integrity | hash, size, observed modification time |
| policy | visibility, sharing policy, review state |
| operational | cache state, replication state, broken/tested state |

## 3. Snapshot Rule [SEC:CMN-DATA-SPEC-002::3]

Metadata shall be exportable in snapshots so settings and review states can be backed up and audited.
