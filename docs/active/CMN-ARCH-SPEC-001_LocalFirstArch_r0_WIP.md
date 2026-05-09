---
document_id: CMN-ARCH-SPEC-001
title: Local-First Architecture Specification
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
- CMN-ARCH-NAR-001
- CMN-SEC-BASE-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Local-First Architecture Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial local-first architecture specification. |

## 1. Purpose [SEC:CMN-ARCH-SPEC-001::1]

This specification defines the local-first architecture expectations for CommNet.

## 2. Required Properties [SEC:CMN-ARCH-SPEC-001::2]

CommNet shall be designed so that:

- local setup can proceed without public internet where installers and dependencies are already present
- local portal use can work on a LAN or single machine
- private state remains local unless explicitly shared
- external gateway behavior is optional and separately governed
- backups and configuration snapshots can be created locally

## 3. Local Services [SEC:CMN-ARCH-SPEC-001::3]

Candidate local services include portal, directory, file registry, search, wiki/pages, bulletin board, forum, media library, diagnostics dashboard, and admin console. Services should be enabled intentionally and recorded in configuration snapshots.

## 4. Trust Boundary [SEC:CMN-ARCH-SPEC-001::4]

Local-only does not mean risk-free. The architecture shall still treat users, processes, devices, files, peer nodes, and gateways as separate trust surfaces.
## Backbone Requirements Update [SEC:CMN-ARCH-SPEC-001::B1]

Local-first remains the default, but local does not mean isolated. The local node shall be capable of exchanging approved messages and bundles through available transport adapters when policy allows. Public internet access remains optional and separately governed.
