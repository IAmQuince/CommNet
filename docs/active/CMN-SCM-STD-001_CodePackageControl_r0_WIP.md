---
document_id: CMN-SCM-STD-001
title: Code and Package Version Control Scheme
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: SCM
  type: STD
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-003
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Code and Package Version Control Scheme

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial CommNet source/package control scheme. |

## 1. Purpose [SEC:CMN-SCM-STD-001::1]

This scheme controls package naming, extraction, source boundaries, and implementation claims.

## 2. Package Naming [SEC:CMN-SCM-STD-001::2]

Package names shall use the format `YYYYMMDD_00_Description`. One-word descriptions are preferred when they prevent path-length problems. This package is `20260508_00_CommNetPrecode`.

## 3. Extraction Location [SEC:CMN-SCM-STD-001::3]

Packages are intended to be extracted under:

```text
C:\Users\iaq16\Documents\Code\CommNet
```

## 4. Source Boundary [SEC:CMN-SCM-STD-001::4]

`src/commnet` is reserved for future product code. This pre-code package contains only source boundary markers. Audit and package tools under `tools/` are package governance utilities, not CommNet product behavior.

## 5. Implementation Claim Rule [SEC:CMN-SCM-STD-001::5]

A package shall not describe a tool, service, UI, security control, or network function as implemented unless the corresponding code and verification evidence are included.
