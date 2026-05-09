---
document_id: CMN-TRANS-SPEC-001
title: Transport Adapter API Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "TRANS", "type": "SPEC", "sequence": "001"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-NET-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/transport_adapters.json"]
---
# Transport Adapter API Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines the common communication adapter contract. |

## 1. Purpose [SEC:CMN-TRANS-SPEC-001::1]

CommNet shall isolate all communication pathways behind a universal transport adapter interface so application tools remain independent of hardware and network method.

## 2. Required Adapter Methods [SEC:CMN-TRANS-SPEC-001::2]

Each transport adapter shall provide bounded implementations of: `probe()`, `capabilities()`, `estimate(message)`, `send(message)`, `receive()`, `health()`, and `shutdown()`.

## 3. Required Status Fields [SEC:CMN-TRANS-SPEC-001::3]

Each adapter shall report installed, configured, hardware present, available, healthy, last error, queue depth, bandwidth estimate, latency estimate, payload limit, broadcast support, direct-message support, bundle support, emergency support, and implementation status.

## 4. Failure Behavior [SEC:CMN-TRANS-SPEC-001::4]

Adapter failures shall be returned as structured status and delivery results. Adapters shall not terminate the CommNet process for ordinary dependency, hardware, or connectivity failures.

## 5. Application Boundary [SEC:CMN-TRANS-SPEC-001::5]

Application modules shall use the transport manager. They shall not call adapter libraries directly.
