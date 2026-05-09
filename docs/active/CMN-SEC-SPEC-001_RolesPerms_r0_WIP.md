---
document_id: CMN-SEC-SPEC-001
title: Roles Permissions and Authorization Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: SEC
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SEC-BASE-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Roles Permissions and Authorization Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial roles, permissions, and authorization specification. |

## 1. Purpose [SEC:CMN-SEC-SPEC-001::1]

This specification defines role classes and the policy principle that permissions must be enforced by backend policy logic.

## 2. Canonical Roles [SEC:CMN-SEC-SPEC-001::2]

| Role | Typical capability |
|---|---|
| anonymous_visitor | Browse explicitly public-local resources when allowed. |
| registered_user | Use local portal under assigned profile. |
| trusted_contributor | Submit content or metadata for review. |
| moderator | Review, restrict, and label content under policy. |
| administrator | Configure services, roles, privacy, and sharing. |
| auditor_reviewer | Review audit logs and support bundles without broad content-control authority. |
| guardian_teacher | Apply dependent/student/household rules in applicable deployments. |
| system_maintainer | Maintain software, packages, backups, and diagnostics. |

## 3. Authorization Rule [SEC:CMN-SEC-SPEC-001::3]

The UI may guide users, but authorization decisions shall be made by policy checks that can be tested outside the UI.

## 4. Policy Simulation [SEC:CMN-SEC-SPEC-001::4]

A future policy simulator shall answer questions such as: as this role, can this actor discover, open, copy, edit, moderate, publish, replicate, or delete this target?
