---
document_id: CMN-ARCH-SPEC-004
title: Gateway Boundary Specification
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
- CMN-ARCH-SPEC-001
- CMN-SEC-BASE-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Gateway Boundary Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial optional gateway boundary specification. |

## 1. Purpose [SEC:CMN-ARCH-SPEC-004::1]

The gateway boundary defines what changes when a CommNet deployment connects beyond the local trust area.

## 2. Default [SEC:CMN-ARCH-SPEC-004::2]

Gateway behavior is disabled by default. A deployment may be useful without a public internet gateway.

## 3. Required Gateway Controls [SEC:CMN-ARCH-SPEC-004::3]

Any future gateway tool shall provide:

- explicit enablement
- visible warning and consequence preview
- policy simulation
- audit event
- rollback path where practical
- service-by-service exposure controls
- firewall and listening-interface review
- support bundle redaction awareness

## 4. Non-Equivalence Rule [SEC:CMN-ARCH-SPEC-004::4]

Local-network visibility, approved-peer visibility, and public gateway exposure are separate states and shall not be collapsed into a single public/private switch.
