---
document_id: CMN-IMP-PLAN-001
title: Implementation Transition and Coding Gate Plan
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: IMP
  type: PLAN
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-REL-SPEC-001
- CMN-RISK-REG-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Implementation Transition and Coding Gate Plan

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial plan for moving from pre-code baseline to first coding sprint. |

## 1. Purpose [SEC:CMN-IMP-PLAN-001::1]

This plan defines what must be true before CommNet product coding begins.

## 2. Coding Gate [SEC:CMN-IMP-PLAN-001::2]

Coding can begin after:

- root structure passes audit
- document metadata and document IDs pass audit
- path length report passes threshold
- requirements and onboarding tools are registered
- privacy/security model exists
- file registry/data integrity model exists
- UI shell/configuration platform specs exist
- risk and debt registers exist
- readiness report states `PRECODE_READY` or `PRECODE_READY_WITH_DEBT`

## 3. First Coding Sprint Recommendation [SEC:CMN-IMP-PLAN-001::3]

The first coding sprint should not attempt the full network. It should build a local-only skeleton with a launcher, install check, local runtime setup, package verifier, settings file, and diagnostics export. That creates a safe executable foundation before adding portal, registry, device discovery, or policy engine complexity.
