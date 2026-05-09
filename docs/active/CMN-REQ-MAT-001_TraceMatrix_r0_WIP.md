---
document_id: CMN-REQ-MAT-001
title: Requirements Traceability Matrix
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: REQ
  type: MAT
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Requirements Traceability Matrix

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial machine-readable and human-readable requirements matrix. |

## 1. Purpose [SEC:CMN-REQ-MAT-001::1]

This matrix lists current CommNet pre-code requirements and their verification path. The machine-readable source is `registries/requirements.json`.

## 2. Requirements [SEC:CMN-REQ-MAT-001::2]

| Requirement ID | Status | Requirement | Verification |
|---|---|---|---|
| CMN-REQ-GOV-001 | READY_FOR_REVIEW | Every controlled document shall have a unique document_id, revision, status, classification, and package_class metadata block. | check_doc_ids.py |
| CMN-REQ-GOV-002 | READY_FOR_REVIEW | Every controlled document shall use stable section identifiers in the form [SEC:DOC-ID::N]. | check_doc_ids.py |
| CMN-REQ-GOV-003 | READY_FOR_REVIEW | The package shall include active and archive areas for documents and audit reports. | check_package_shape.py |
| CMN-REQ-GOV-004 | READY_FOR_REVIEW | The package shall include a machine-readable document registry matching active controlled documents. | check_registry_sync.py |
| CMN-REQ-GOV-005 | READY_FOR_REVIEW | The package shall state its package class and shall not claim implemented product behavior in a pre-code baseline. | audit_package.py |
| CMN-REQ-PATH-001 | READY_FOR_REVIEW | Package paths should remain short enough for Windows extraction under C:\Users\iaq16\Documents\Code\CommNet. | check_paths.py |
| CMN-REQ-AUD-001 | READY_FOR_REVIEW | The package shall include audit scripts for package shape, path length, document metadata, registries, and implementation-claim scanning. | audit_package.py |
| CMN-REQ-AUD-002 | READY_FOR_REVIEW | Audit reports shall be generated under audit_reports/active and proof evidence under proof/. | audit_package.py |
| CMN-REQ-ARCH-001 | READY_FOR_REVIEW | CommNet shall be local-first and shall remain useful without public internet access. | architecture review and future offline functional tests |
| CMN-REQ-ARCH-002 | READY_FOR_REVIEW | CommNet shall be hardware- and software-agnostic at the core model level. | adapter architecture review |
| CMN-REQ-ARCH-003 | READY_FOR_REVIEW | CommNet shall distinguish node roles from physical hardware types. | node role registry review |
| CMN-REQ-ARCH-004 | READY_FOR_REVIEW | CommNet shall separate local portal, local services, peer links, replication, and optional public gateway exposure. | architecture review |
| CMN-REQ-ARCH-005 | READY_FOR_REVIEW | Public internet gateway exposure shall be optional and disabled by default. | security review and future config tests |
| CMN-REQ-SEC-001 | READY_FOR_REVIEW | All privacy and permission decisions shall be enforced by backend policy, not only by UI visibility. | future policy engine tests |
| CMN-REQ-SEC-002 | READY_FOR_REVIEW | Default setup shall be private, local-only, invisible, and non-sharing until the user explicitly changes it. | future first-run tests |
| CMN-REQ-SEC-003 | READY_FOR_REVIEW | Role definitions shall distinguish visitor, user, contributor, moderator, administrator, auditor, guardian, and maintainer capabilities. | roles registry review |
| CMN-REQ-SEC-004 | READY_FOR_REVIEW | The system shall support recovery from lost admin access without silently bypassing ownership rules. | future recovery design review |
| CMN-REQ-SEC-005 | READY_FOR_REVIEW | High-impact actions shall require preview, confirmation, audit entry, and rollback path when practical. | future UI and policy tests |
| CMN-REQ-PRV-001 | READY_FOR_REVIEW | A user or node shall not appear in the community directory unless visibility is explicitly enabled. | future visibility tests |
| CMN-REQ-PRV-002 | READY_FOR_REVIEW | Visibility labels shall distinguish private local, device-local, local-network, approved-peer, and gateway-exposed states. | future UX review |
| CMN-REQ-PRV-003 | READY_FOR_REVIEW | Policy profiles shall be exportable, importable, and reviewable before apply. | future profile tests |
| CMN-REQ-DATA-001 | READY_FOR_REVIEW | The file registry shall use stable IDs, content hashes, source attribution, timestamps, owner/source fields, paths, tags, review state, and visibility flags. | schema review and future registry tests |
| CMN-REQ-DATA-002 | READY_FOR_REVIEW | Metadata shall remain separable from original files and shall be snapshot/export capable. | future registry export tests |
| CMN-REQ-DATA-003 | READY_FOR_REVIEW | Configuration changes shall create versioned snapshots and audit entries. | future config tests |
| CMN-REQ-DATA-004 | READY_FOR_REVIEW | Destructive actions shall distinguish hide, local delete, cache purge, registry removal, tombstone, and takedown request. | future policy and UX tests |
| CMN-REQ-DATA-005 | READY_FOR_REVIEW | Support bundles shall redact sensitive values by default and shall declare what was included. | future support bundle tests |
| CMN-REQ-UI-001 | READY_FOR_REVIEW | CommNet shall provide one obvious first-run entry point. | future launcher tests |
| CMN-REQ-UI-002 | READY_FOR_REVIEW | Configuration tools shall share one common policy engine and differ by profile, not by incompatible implementations. | future architecture tests |
| CMN-REQ-UI-003 | READY_FOR_REVIEW | The admin configuration platform shall support novice and advanced modes. | future UX review |
| CMN-REQ-UI-004 | READY_FOR_REVIEW | The UI shall expose policy consequences before applying privacy, sharing, gateway, and role changes. | future policy simulator tests |
| CMN-REQ-UI-005 | READY_FOR_REVIEW | The UI design shall support dockable panels, persistent status, settings persistence, diagnostic export, and logs. | future UI acceptance tests |
| CMN-REQ-UI-006 | READY_FOR_REVIEW | The community web portal and admin console shall be separate entry points. | future launcher tests |
| CMN-REQ-ONB-001 | READY_FOR_REVIEW | CommNet onboarding shall define the Start Here as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-002 | READY_FOR_REVIEW | CommNet onboarding shall define the Install Check as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-003 | READY_FOR_REVIEW | CommNet onboarding shall define the Package Verifier as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-004 | READY_FOR_REVIEW | CommNet onboarding shall define the Runtime Setup as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-005 | READY_FOR_REVIEW | CommNet onboarding shall define the Profile Preset Selector as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-006 | READY_FOR_REVIEW | CommNet onboarding shall define the Node Role Wizard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-007 | READY_FOR_REVIEW | CommNet onboarding shall define the Local Identity Wizard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-008 | READY_FOR_REVIEW | CommNet onboarding shall define the Visibility Wizard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-009 | READY_FOR_REVIEW | CommNet onboarding shall define the Privacy Wizard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-010 | READY_FOR_REVIEW | CommNet onboarding shall define the Sharing Policy Builder as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-011 | READY_FOR_REVIEW | CommNet onboarding shall define the Roles and Permissions Console as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-012 | READY_FOR_REVIEW | CommNet onboarding shall define the Policy Simulator as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-013 | READY_FOR_REVIEW | CommNet onboarding shall define the Device Discovery Tool as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-014 | READY_FOR_REVIEW | CommNet onboarding shall define the Add Device Wizard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-015 | READY_FOR_REVIEW | CommNet onboarding shall define the Network Setup Assistant as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-016 | READY_FOR_REVIEW | CommNet onboarding shall define the Mesh and Peer Link Assistant as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-017 | READY_FOR_REVIEW | CommNet onboarding shall define the Gateway Boundary Tool as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-018 | READY_FOR_REVIEW | CommNet onboarding shall define the Service Manager as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-019 | READY_FOR_REVIEW | CommNet onboarding shall define the File Registry Builder as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-020 | READY_FOR_REVIEW | CommNet onboarding shall define the Content Import Tool as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-021 | READY_FOR_REVIEW | CommNet onboarding shall define the Metadata Tagger as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-022 | READY_FOR_REVIEW | CommNet onboarding shall define the Review and Moderation Queue as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-023 | READY_FOR_REVIEW | CommNet onboarding shall define the Community Directory Publisher as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-024 | READY_FOR_REVIEW | CommNet onboarding shall define the Backup and Restore Tool as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-025 | READY_FOR_REVIEW | CommNet onboarding shall define the Sync and Replication Planner as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-026 | READY_FOR_REVIEW | CommNet onboarding shall define the Storage Steward Tool as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-027 | READY_FOR_REVIEW | CommNet onboarding shall define the Diagnostics Dashboard as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-028 | READY_FOR_REVIEW | CommNet onboarding shall define the Audit Log Viewer as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-029 | READY_FOR_REVIEW | CommNet onboarding shall define the Security Hardening Checklist as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-030 | READY_FOR_REVIEW | CommNet onboarding shall define the Update and Package Installer as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-031 | READY_FOR_REVIEW | CommNet onboarding shall define the Export Support Bundle as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-032 | READY_FOR_REVIEW | CommNet onboarding shall define the Community Web Launcher as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-033 | READY_FOR_REVIEW | CommNet onboarding shall define the Admin Console Launcher as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-034 | READY_FOR_REVIEW | CommNet onboarding shall define the Help and Demo Mode as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-035 | READY_FOR_REVIEW | CommNet onboarding shall define the Emergency and Outage Mode Setup as a first-class setup or operations tool. | onboarding_tools.json review |
| CMN-REQ-ONB-036 | READY_FOR_REVIEW | CommNet onboarding shall define the Shortcut and Icon Manager as a first-class setup or operations tool. | onboarding_tools.json review |

## 3. Coding Gate [SEC:CMN-REQ-MAT-001::3]

Coding may begin when the pre-code readiness report is `PRECODE_READY` or `PRECODE_READY_WITH_DEBT`, and when remaining debt is explicitly listed.

## Backbone Requirement Addendum [SEC:CMN-REQ-MAT-001::B1]

| Requirement | Source Document | Verification |
|---|---|---|
| CMN-REQ-TRANS-001 | CMN-TRANS-SPEC-001 | transport registry and adapter API review |
| CMN-REQ-TRANS-002 | CMN-TRANS-SPEC-001 | adapter architecture review |
| CMN-REQ-TRANS-003 | CMN-TRANS-SPEC-004 | payload class registry audit |
| CMN-REQ-TRANS-004 | CMN-TRANS-SPEC-002 | route policy audit |
| CMN-REQ-TRANS-005 | CMN-TRANS-SPEC-003 | resource limits audit |
| CMN-REQ-TRANS-006 | CMN-TRANS-SPEC-002 | future queue tests and route policy review |
| CMN-REQ-TRANS-007 | CMN-DIAG-SPEC-001 | diagnostics spec review |
| CMN-REQ-MESH-001 | CMN-NET-SPEC-004 | dependency/profile/adapter registry audit |
| CMN-REQ-MESH-002 | CMN-NET-SPEC-005 | dependency/profile/adapter registry audit |
| CMN-REQ-MESH-003 | CMN-NET-SPEC-005 | dependency/profile/adapter registry audit |
| CMN-REQ-LAN-001 | CMN-NET-SPEC-006 | transport registry audit |
| CMN-REQ-BT-001 | CMN-NET-SPEC-007 | transport registry audit |
| CMN-REQ-STORE-001 | CMN-NET-SPEC-008 | storage/mule registry and spec review |
| CMN-REQ-INST-001 | CMN-INST-SPEC-001 | wheelhouse audit |
| CMN-REQ-INST-002 | CMN-SW-REQ-002 | future import isolation tests |
| CMN-REQ-DIAG-001 | CMN-DIAG-SPEC-001 | diagnostic registry and future UI test |
