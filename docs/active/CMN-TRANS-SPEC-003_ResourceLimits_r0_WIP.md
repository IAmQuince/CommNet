---
document_id: CMN-TRANS-SPEC-003
title: Communication Resource Limits
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "TRANS", "type": "SPEC", "sequence": "003"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-TRANS-SPEC-002"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/resource_limits.json"]
---
# Communication Resource Limits

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines deterministic resource protections for communication failures. |

## 1. Purpose [SEC:CMN-TRANS-SPEC-003::1]

CommNet shall maximize delivery effort within bounded resource limits. It shall not freeze the UI, exhaust memory, flood networks, or spin indefinitely.

## 2. Required Controls [SEC:CMN-TRANS-SPEC-003::2]

Each communication path shall use bounded queues, bounded worker threads, bounded retry count, retry backoff, send-rate limits, receive polling limits, adapter cooldowns, circuit breakers, payload size limits, and message expiration.

## 3. Low-Bandwidth Controls [SEC:CMN-TRANS-SPEC-003::3]

Low-bandwidth transports such as Meshtastic shall reject or defer large-file payload classes and shall prefer alerts, text, status, manifests, and control notices.

## 4. Emergency Limits [SEC:CMN-TRANS-SPEC-003::4]

Emergency traffic may receive priority and broader replication but shall still use duplicate suppression, TTL or hop controls where available, rate limits, and audit records.
