---
document_id: CMN-REL-SPEC-001
title: Release Package Composition and Baseline Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: REL
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SCM-STD-001
- CMN-AUD-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Release Package Composition and Baseline Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial release/package composition specification for CommNet. |

## 1. Purpose [SEC:CMN-REL-SPEC-001::1]

This specification defines what must be included in a CommNet send-out package and how the package states its baseline.

## 2. Package Classes [SEC:CMN-REL-SPEC-001::2]

Allowed package classes are:

| Class | Meaning |
|---|---|
| DOC_BASELINE | Documentation-only baseline |
| PRECODE_BASELINE | Controlled requirements, architecture, registries, and audits before product code |
| IMPLEMENTATION_REVIEW | Product code exists and is ready for review |
| RELEASE_CANDIDATE | Functionally complete candidate awaiting acceptance |
| RELEASED_PACKAGE | Accepted package for intended users |

## 3. Required Contents for PRECODE_BASELINE [SEC:CMN-REL-SPEC-001::3]

The package shall include root guidance, active controlled docs, registries, audit tools, audit reports, proof/readiness report, package manifest, and short path report.

## 4. No Product Code Scope [SEC:CMN-REL-SPEC-001::4]

This package class may include governance utilities but shall not claim that CommNet portal, admin console, device onboarding, file registry builder, or policy engine product behavior is implemented.
