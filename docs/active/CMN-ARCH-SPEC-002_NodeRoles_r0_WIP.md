---
document_id: CMN-ARCH-SPEC-002
title: Node Roles Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: ARCH
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-ARCH-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Node Roles Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial logical node role specification. |

## 1. Purpose [SEC:CMN-ARCH-SPEC-002::1]

Node roles define what a device or process does without assuming what hardware it runs on.

## 2. Canonical Node Roles [SEC:CMN-ARCH-SPEC-002::2]

| Role | Description |
|---|---|
| portal_node | Hosts the local community web surface. |
| admin_node | Hosts configuration and policy tools. |
| storage_node | Stores content, registry snapshots, or cache data. |
| gateway_node | Bridges a local deployment to an external network when explicitly enabled. |
| peer_node | Participates in approved peer relationships. |
| client_node | Consumes local services without hosting major services. |
| review_node | Supports moderation, review, audit, or educator/admin review. |
| emergency_node | Hosts outage/emergency resources and notices. |

## 3. Hardware Independence [SEC:CMN-ARCH-SPEC-002::3]

A node role may run on a home PC, school workstation, server, NAS, Raspberry Pi, router-attached appliance, or future device. The product architecture shall not bake hardware type into the logical role model.
