---
document_id: CMN-AUD-SPEC-002
title: Audit Log Field Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: AUD
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-SEC-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Audit Log Field Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial future runtime audit event field specification. |

## 1. Purpose [SEC:CMN-AUD-SPEC-002::1]

CommNet runtime tools will need structured audit events for setup, privacy, permission, sharing, gateway, registry, review, and backup actions.

## 2. Required Runtime Audit Fields [SEC:CMN-AUD-SPEC-002::2]

| Field | Meaning |
|---|---|
| event_id | Stable event ID |
| timestamp_utc | Event time in UTC |
| actor_id | User, service, or process that initiated the action |
| actor_role | Role at time of action |
| action | Controlled action name |
| target_type | Identity, node, service, content, config, policy, or gateway |
| target_id | Stable target ID |
| old_value_hash | Hash or reference to prior state when applicable |
| new_value_hash | Hash or reference to new state when applicable |
| result | success, denied, failed, simulated, or rolled_back |
| reason_code | Controlled reason code |
| source_tool | Tool that caused the event |
| redaction_level | none, normal, support_bundle, or private_admin |

## 3. Logging Principle [SEC:CMN-AUD-SPEC-002::3]

Audit logs should be useful without being reckless. Support exports must not leak private content by default.
