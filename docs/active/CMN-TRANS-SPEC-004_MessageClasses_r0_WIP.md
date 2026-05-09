---
document_id: CMN-TRANS-SPEC-004
title: Message and Payload Classes
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "TRANS", "type": "SPEC", "sequence": "004"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-TRANS-SPEC-002"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/payload_classes.json", "registries/route_policy.json"]
---
# Message and Payload Classes

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines message classes for routing and policy decisions. |

## 1. Purpose [SEC:CMN-TRANS-SPEC-004::1]

Every outbound item shall be classified before route planning.

## 2. Required Classes [SEC:CMN-TRANS-SPEC-004::2]

Required classes include emergency alert, text message, BBS post, directory update, site update, file manifest, small file, large file, RetroWeb bundle, concert control, marketplace listing, device status, route probe, config snapshot, and support-bundle notice.

## 3. Required Fields [SEC:CMN-TRANS-SPEC-004::3]

Each class shall define priority, typical size, privacy sensitivity, latency requirement, delivery deadline behavior, allowed transports, disallowed transports, and audit requirements.

## 4. Route Enforcement [SEC:CMN-TRANS-SPEC-004::4]

The route planner shall use message class policy before transport scoring. A high transport score shall not override class-level disallow rules.
