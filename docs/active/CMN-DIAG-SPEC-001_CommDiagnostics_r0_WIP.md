---
document_id: CMN-DIAG-SPEC-001
title: Communication Diagnostics Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "DIAG", "type": "SPEC", "sequence": "001"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-UI-SPEC-005", "CMN-TRANS-SPEC-003"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["audit_reports/active/dependency_report.md", "audit_reports/active/transport_registry_report.md"]
---
# Communication Diagnostics Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines diagnostics needed for multi-path communication troubleshooting. |

## 1. Purpose [SEC:CMN-DIAG-SPEC-001::1]

CommNet shall expose communication status clearly enough for a non-developer to understand what is installed, configured, connected, healthy, degraded, unavailable, or simulated.

## 2. Required Diagnostic Areas [SEC:CMN-DIAG-SPEC-001::2]

Diagnostics shall include dependency status, adapter status, hardware presence, configuration state, queue depth, route decisions, recent failures, cooldowns, circuit-breaker state, deferred messages, and support-bundle export.

## 3. User-Facing Language [SEC:CMN-DIAG-SPEC-001::3]

The UI should use accessible names such as LoRa radio, local Wi-Fi, nearby Bluetooth, local storage cache, delayed delivery, and message queue while retaining precise adapter IDs in advanced details.

## 4. Support Bundle [SEC:CMN-DIAG-SPEC-001::4]

Support bundles shall include redacted config, dependency report, transport registry report, route policy report, resource-limit report, recent audit events, and error logs when implemented.
