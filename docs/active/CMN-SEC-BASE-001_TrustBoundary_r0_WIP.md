---
document_id: CMN-SEC-BASE-001
title: Security and Trust Boundary Baseline
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: SEC
  type: BASE
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Security and Trust Boundary Baseline

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial trust boundary baseline. |

## 1. Purpose [SEC:CMN-SEC-BASE-001::1]

This baseline defines security posture before implementation begins.

## 2. Default Posture [SEC:CMN-SEC-BASE-001::2]

CommNet defaults are:

- private by default
- local-only by default
- invisible by default
- no sharing by default
- no gateway exposure by default
- explicit review before directory publication
- audit records for policy changes

## 3. Trust Boundaries [SEC:CMN-SEC-BASE-001::3]

The following boundaries shall be treated separately:

| Boundary | Risk |
|---|---|
| user to local machine | identity and permissions |
| local machine to LAN | service exposure |
| LAN to approved peer | trust and replication |
| local deployment to public internet | gateway exposure |
| admin console to runtime config | destructive settings |
| file system to portal | unsafe file serving |

## 4. Security Claim Rule [SEC:CMN-SEC-BASE-001::4]

This package defines desired security posture and future requirements. It does not implement the runtime policy engine.
