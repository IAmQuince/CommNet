---
document_id: CMN-NET-SPEC-008
title: Storage Node and Data Mule Model
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "NET", "type": "SPEC", "sequence": "008"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-SYNC-SPEC-001", "CMN-DATA-SPEC-001"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["registries/payload_classes.json", "registries/route_policy.json"]
---
# Storage Node and Data Mule Model

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Unifies static storage, phone caches, removable media, and drones under custody-based bundle transfer. |

## 1. Purpose [SEC:CMN-NET-SPEC-008::1]

Storage nodes, phone storage silos, removable media, and future drones or vehicle-based data mules shall be represented as custody carriers for bundles.

## 2. Custody Bundle Fields [SEC:CMN-NET-SPEC-008::2]

A custody bundle shall include bundle ID, sender, recipient or group, payload class, privacy class, size, content hash, chunk manifest, allowed carriers, custody history, expiration, delivery status, and audit chain.

## 3. Static Storage Nodes [SEC:CMN-NET-SPEC-008::3]

Static storage nodes may cache approved bundles for homes, schools, libraries, makerspaces, neighborhoods, or emergency operations.

## 4. Mobile Carriers [SEC:CMN-NET-SPEC-008::4]

Phone caches, removable media, drones, and future mobile carriers shall only accept custody when policy permits and when payload privacy, size, expiration, and trust requirements are satisfied.

## 5. Implementation Status [SEC:CMN-NET-SPEC-008::5]

In the backbone requirements package, this model is specified but not implemented.
