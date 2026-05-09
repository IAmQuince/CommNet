---
document_id: CMN-NET-SPEC-005
title: Reticulum and LXMF Adapter Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "NET", "type": "SPEC", "sequence": "005"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-NET-SPEC-003", "CMN-TRANS-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/backbone_providers.json", "registries/transport_adapters.json"]
---
# Reticulum and LXMF Adapter Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines Reticulum RNS and LXMF backbone profiles. |

## 1. Purpose [SEC:CMN-NET-SPEC-005::1]

Reticulum RNS shall be a first-class resilient backbone option. LXMF shall be a first-class message layer option for Reticulum-based messaging.

## 2. Provider Separation [SEC:CMN-NET-SPEC-005::2]

RNS and LXMF shall be represented as distinct capabilities. RNS represents the network layer and LXMF represents a message-layer service above that network.

## 3. Runtime Checks [SEC:CMN-NET-SPEC-005::3]

Reticulum adapter availability shall be based on dependency presence, configuration presence, interface availability, local identity readiness, and successful probe.

## 4. Store-and-Forward [SEC:CMN-NET-SPEC-005::4]

LXMF shall be considered a preferred path for store-and-forward messages where payload size, privacy policy, and recipient configuration allow.

## 5. Claim Control [SEC:CMN-NET-SPEC-005::5]

The package shall not claim Reticulum interoperability with Meshtastic unless an explicit bridge has been implemented and tested.
