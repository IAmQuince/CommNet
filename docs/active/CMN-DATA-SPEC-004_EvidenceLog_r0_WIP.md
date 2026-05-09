---
document_id: CMN-DATA-SPEC-004
title: Evidence Log Specification
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
- CMN-AUD-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Evidence Log Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial evidence log specification. |

## 1. Purpose [SEC:CMN-DATA-SPEC-004::1]

The evidence log records package, audit, support, and operational proof artifacts separately from narrative claims.

## 2. Evidence Types [SEC:CMN-DATA-SPEC-004::2]

| Evidence | Location |
|---|---|
| package audit | audit_reports/active/package_audit.md |
| path report | audit_reports/active/path_length_report.md |
| document control report | audit_reports/active/doc_control_report.md |
| traceability report | audit_reports/active/traceability_report.md |
| readiness report | proof/precode_readiness_report.md |
| source material index | proof/source_refs/source_material_index.md |

## 3. Evidence Rule [SEC:CMN-DATA-SPEC-004::3]

A claim of readiness shall reference generated evidence, not only prose in the README.
