---
document_id: CMN-GOV-STD-002
title: Semantic Precedence and Term Usage Standard
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: GOV
  type: STD
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Semantic Precedence and Term Usage Standard

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial standard for canonical CommNet terminology. |

## 1. Purpose [SEC:CMN-GOV-STD-002::1]

CommNet uses terms that can easily drift: community web, community internet, local internet, mesh, peer link, gateway, registry, node, visibility, and sharing. This standard controls those terms so product design does not rely on ambiguous language.

## 2. Precedence [SEC:CMN-GOV-STD-002::2]

When documents conflict, the following precedence applies for this pre-code package:

1. safety, privacy, and trust-boundary documents
2. requirements registry
3. architecture specifications
4. UI specifications
5. concept narratives and source references

## 3. Canonical Terms [SEC:CMN-GOV-STD-002::3]

| Term | Controlled meaning |
|---|---|
| CommNet | The governed project name for the hardware- and software-agnostic community internet platform. |
| Community web | The local portal experience presented to users. |
| Local-first | Useful without public internet and private by default. |
| Node | A logical participant in the system, independent of physical hardware type. |
| Peer link | A configured relationship between nodes. It does not by itself imply true mesh routing. |
| Gateway | Optional bridge beyond the local trust boundary, disabled by default. |
| Visibility | Whether an identity, node, service, or content item can be discovered. |
| Sharing | Whether a content item, service, or metadata record can be accessed or copied by others. |

## 4. Design Rule [SEC:CMN-GOV-STD-002::4]

Documents shall not use mesh, internet, public, visible, shared, or published as casual synonyms. If a behavior crosses a trust boundary, that boundary shall be named.
