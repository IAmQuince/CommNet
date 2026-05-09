---
document_id: CMN-GOV-STD-001
title: Document Control Standard
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: GOV
  type: STD
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: []
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Document Control Standard

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial CommNet document control standard adapted to the governed package style used in the referenced uDAQ documentation set. |

## 1. Purpose [SEC:CMN-GOV-STD-001::1]

This standard defines how CommNet documents are identified, revised, archived, referenced, and audited. The immediate use is the pre-code baseline package. The same rules are intended to carry into implementation packages and later release candidates.

The control goals are:

- one unambiguous identity for every controlled document
- explicit revision and status on every document
- active and archive separation
- machine-readable registries for documents, requirements, and cross-references
- package audits that can detect missing files, inconsistent metadata, and unsupported implementation claims

## 2. Required Metadata [SEC:CMN-GOV-STD-001::2]

Every controlled document shall begin with YAML front matter containing at least:

| Field | Meaning |
|---|---|
| document_id | Stable machine-readable document identity |
| title | Human-readable title |
| revision | Revision string such as r0 |
| status | WIP, BASELINE, RELEASED, SUPERSEDED, or ARCHIVED |
| document_class | Kind of document |
| package_class | Current package class such as PRECODE_BASELINE |
| classification | domain, type, and sequence fields |
| effective_date | Date of this issue |
| authoring_context | CommNet |
| depends_on | Document dependency list |
| supersedes | Documents superseded by this one |
| superseded_by | Later documents that supersede this one |
| machine_readable_artifacts | Related registry or schema artifacts |

## 3. Section Identifiers [SEC:CMN-GOV-STD-001::3]

Major sections shall include a section identifier of the form `[SEC:DOC-ID::N]`. Subsections may use identifiers such as `[SEC:DOC-ID::2.1]`. These identifiers allow requirements, audits, and future code comments to reference the exact section that governs a behavior.

## 4. Status Lifecycle [SEC:CMN-GOV-STD-001::4]

Allowed document statuses are:

| Status | Meaning |
|---|---|
| WIP | Active working document |
| BASELINE | Accepted as a controlled baseline for the current package |
| RELEASED | Released for external or field use |
| SUPERSEDED | Replaced by a newer controlled document |
| ARCHIVED | Preserved for record or evidence use |

## 5. Active and Archive Rules [SEC:CMN-GOV-STD-001::5]

Active documents live under `docs/active`. Superseded material moves to `docs/archive`. Generated audit reports live under `audit_reports/active` or `audit_reports/archive`. Runtime state is not a controlled document and shall not be committed as source.
