---
document_id: CMN-RISK-REG-001
title: Risk and Mitigation Register
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: RISK
  type: REG
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-REQ-MAT-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Risk and Mitigation Register

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial CommNet risk and mitigation register. |

## 1. Purpose [SEC:CMN-RISK-REG-001::1]

This register documents project risks and mitigations for the pre-code baseline and future onboarding/configuration platform.

## 2. Risk Register [SEC:CMN-RISK-REG-001::2]

| Risk ID | Severity | Risk | Mitigation |
|---|---|---|---|
| CMN-RISK-001 | High | Overbuilding before architecture is controlled | Keep this package PRECODE_BASELINE; product code waits for readiness gate. |
| CMN-RISK-002 | High | False implementation claims | Audit for overclaiming; mark this package as no product implementation scope. |
| CMN-RISK-003 | High | Path length failures | Short package root, short filenames, automated path audit. |
| CMN-RISK-004 | High | File loss during packaging | Manifest, tree report, hash manifest, and package audit before zip. |
| CMN-RISK-005 | High | Documentation drift | Registry sync and traceability audits. |
| CMN-RISK-006 | Medium | Home and school divergence | One policy/config engine with different presets. |
| CMN-RISK-007 | High | Privacy exposure by default | Private/local-only/invisible/no-sharing defaults. |
| CMN-RISK-008 | High | UI-only security | Backend policy enforcement required by specification. |
| CMN-RISK-009 | High | Confusing permissions | Policy simulator, plain-language labels, novice/advanced modes. |
| CMN-RISK-010 | High | Unreviewed content availability | Review states and explicit publishing rules. |
| CMN-RISK-011 | High | Registry integrity problems | Stable IDs, content hashes, provenance, snapshots. |
| CMN-RISK-012 | Medium | Metadata separation failure | Central registry and exportable snapshots. |
| CMN-RISK-013 | High | Irreversible config mistakes | Snapshot before apply, rollback plan, audit entry. |
| CMN-RISK-014 | Medium | Noisy audit logs | Controlled event types and required audit fields. |
| CMN-RISK-015 | High | Sensitive log leakage | Redaction levels and inclusion manifest. |
| CMN-RISK-016 | High | Mesh claims exceed implementation | Separate LAN, peer, replication, gateway, and mesh terms. |
| CMN-RISK-017 | Medium | Hardware lock-in | Node roles and adapter abstraction. |
| CMN-RISK-018 | Medium | Python installation friction | Install Check, offline installer guidance, eventual bundled runtime option. |
| CMN-RISK-019 | Medium | Shortcut breakage | Relative launchers and launcher repair tool requirement. |
| CMN-RISK-020 | Medium | Admin tool overload | Mode separation and guided first-run flows. |
| CMN-RISK-021 | High | Gateway exposure risk | Disabled by default, warning, audit, dedicated gateway boundary tool. |
| CMN-RISK-022 | High | Replication spreads private content | Dry-run replication plans and trust-aware cache policy. |
| CMN-RISK-023 | Medium | Ambiguous deletion | Controlled deletion types and confirmation language. |
| CMN-RISK-024 | Medium | Moderation accountability gaps | Reason codes, actor IDs, timestamps, and appeal hooks. |
| CMN-RISK-025 | Medium | Lost admin access | Recovery artifact and restore flow requirements. |
| CMN-RISK-026 | High | Malformed input | Length limits, character allowlists, path normalization, safe rendering. |
| CMN-RISK-027 | High | Unsafe file serving | Serve only registered approved content from controlled roots. |
| CMN-RISK-028 | High | Overscanning private files | Explicit folder selection, preview, exclude patterns, confirmation. |
| CMN-RISK-029 | Medium | Weak hardware performance | Lightweight core, incremental indexing, no heavy base dependencies. |
| CMN-RISK-030 | High | Incomplete offline operation | Offline-first tests and optional external integrations. |
| CMN-RISK-031 | High | Updates overwrite local policy | Separate source from runtime, backup before migration. |
| CMN-RISK-032 | High | Runtime artifacts committed | runtime excluded by gitignore and audit scan. |
| CMN-RISK-033 | Medium | Tests grow without scope | Sprint-specific test plan tied to claims. |
| CMN-RISK-034 | High | No acceptance gate | PRECODE_READY gate with debt register. |
| CMN-RISK-035 | Medium | Legal/policy uncertainty | Deployment owner responsibility and policy hooks. |
| CMN-RISK-036 | Medium | Concept expansion | Scope register and staged milestones. |

## 3. Highest Priority Risk [SEC:CMN-RISK-REG-001::3]

The highest priority risk is making the concept look more implemented, secure, or governed than it is. The mitigation is explicit package class labeling, generated audits, and refusal to claim product behavior before code and tests exist.
