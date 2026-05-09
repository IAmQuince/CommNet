---
document_id: CMN-NET-SPEC-001
title: Transport Abstraction Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: NET
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-ARCH-SPEC-005
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Transport Abstraction Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial transport abstraction specification. |

## 1. Purpose [SEC:CMN-NET-SPEC-001::1]

Transport abstraction prevents CommNet from depending on a single network method.

## 2. Transport Classes [SEC:CMN-NET-SPEC-001::2]

| Class | Meaning |
|---|---|
| local_loopback | Single-machine testing and use. |
| lan | Wired or wireless local network. |
| manual_transfer | Flash drive or removable media exchange. |
| peer_link | Approved node-to-node relationship. |
| gateway_link | Explicitly configured external boundary crossing. |
| future_mesh | True mesh or routed community network once implemented and verified. |

## 3. Claim Control [SEC:CMN-NET-SPEC-001::3]

A package shall not claim true mesh behavior until routing, discovery, security, failure handling, and performance are implemented and tested for that claim.
## Backbone Requirements Update [SEC:CMN-NET-SPEC-001::B1]

Transport abstraction is elevated from a future concept to a central software requirement. The required transport manager shall include an adapter registry, route planner, policy gate, message queue, bundle store, delivery engine, health monitor, backpressure controller, and audit logger.
