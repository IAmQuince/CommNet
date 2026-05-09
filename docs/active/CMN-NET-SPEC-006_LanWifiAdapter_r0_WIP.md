---
document_id: CMN-NET-SPEC-006
title: LAN and Wi-Fi Adapter Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "NET", "type": "SPEC", "sequence": "006"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-NET-SPEC-003", "CMN-TRANS-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/transport_adapters.json", "registries/route_policy.json"]
---
# LAN and Wi-Fi Adapter Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines high-bandwidth local HTTP/LAN behavior. |

## 1. Purpose [SEC:CMN-NET-SPEC-006::1]

LAN/Wi-Fi shall be the first high-bandwidth local communication path for CommNet nodes on the same local network.

## 2. Scope [SEC:CMN-NET-SPEC-006::2]

The initial LAN/Wi-Fi adapter shall support local HTTP node-to-node communication, manual peer entry, and optional zeroconf discovery. It shall not assume the ability to reconfigure arbitrary routers.

## 3. Payload Suitability [SEC:CMN-NET-SPEC-006::3]

LAN/Wi-Fi may be used for text, directory updates, BBS posts, personal-site updates, file manifests, small files, larger file chunks, RetroWeb bundles, and low-latency local control if health checks pass.

## 4. Resource Rules [SEC:CMN-NET-SPEC-006::4]

LAN/Wi-Fi transfers shall use bounded file chunk sizes, timeouts, retry limits, backpressure, and per-peer queue limits.
