---
document_id: CMN-TRANS-SPEC-002
title: Route Planner Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "TRANS", "type": "SPEC", "sequence": "002"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-TRANS-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/route_policy.json", "registries/payload_classes.json"]
---
# Route Planner Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines deterministic route selection and fallback behavior. |

## 1. Purpose [SEC:CMN-TRANS-SPEC-002::1]

CommNet shall try to communicate through all allowed pathways in a deterministic, bounded, auditable way.

## 2. Delivery Process [SEC:CMN-TRANS-SPEC-002::2]

1. The application creates a message or bundle manifest.
2. The message is classified.
3. The policy gate checks privacy, sharing, and permissions.
4. The transport manager probes available adapters.
5. The route planner scores valid routes.
6. The delivery engine attempts the best route.
7. Failures trigger bounded fallback.
8. If no live route works, the message is deferred if policy allows.
9. Expired or disallowed messages are dropped with reason.
10. Every decision is audited.

## 3. Scoring Inputs [SEC:CMN-TRANS-SPEC-002::3]

Route scoring shall consider payload size, priority, privacy class, latency requirement, deadline, recipient availability, transport availability, estimated bandwidth, estimated latency, reliability, adapter health, queue depth, power cost, and trust level.

## 4. Determinism [SEC:CMN-TRANS-SPEC-002::4]

Equal scores shall be resolved through stable tie-break order defined in `registries/route_policy.json` so repeated decisions are explainable.
