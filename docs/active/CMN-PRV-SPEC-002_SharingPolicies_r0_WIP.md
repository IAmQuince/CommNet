---
document_id: CMN-PRV-SPEC-002
title: Sharing Policy Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: PRV
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-PRV-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Sharing Policy Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial sharing policy specification. |

## 1. Purpose [SEC:CMN-PRV-SPEC-002::1]

Sharing policy controls access, copying, caching, replication, and publishing. A file being indexed does not mean it is shared.

## 2. Sharing Decisions [SEC:CMN-PRV-SPEC-002::2]

A sharing decision shall consider owner/source, role, group, content class, review state, visibility level, replication policy, gateway boundary, and retention rule.

## 3. Policy Profiles [SEC:CMN-PRV-SPEC-002::3]

Initial profiles are home_private, home_shared, school_classroom, school_admin, library_public_local, makerspace, neighborhood, and emergency_outage.

## 4. Preview Rule [SEC:CMN-PRV-SPEC-002::4]

Future sharing tools shall preview what will become visible, accessible, copyable, or replicated before applying a change.
