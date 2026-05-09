---
document_id: CMN-UI-SPEC-005
title: Diagnostics UX Specification
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
- CMN-DATA-SPEC-004
- CMN-AUD-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Diagnostics UX Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial diagnostics UX specification. |

## 1. Purpose [SEC:CMN-UI-SPEC-005::1]

Diagnostics should help users and reviewers understand what happened without exposing private content unnecessarily.

## 2. Diagnostic Areas [SEC:CMN-UI-SPEC-005::2]

| Area | Examples |
|---|---|
| install | Python version, OS, permissions, package path |
| package | manifest, hashes, version, audit state |
| network | local interfaces, services, peer links |
| services | portal, directory, registry, diagnostics |
| registry | scan state, hash errors, missing files |
| security | privacy defaults, gateway state, role policy |
| logs | warnings, errors, audit events |

## 3. Support Bundle Rule [SEC:CMN-UI-SPEC-005::3]

Support bundles shall describe included files, redact private data by default, and allow the user/admin to inspect before sending.
