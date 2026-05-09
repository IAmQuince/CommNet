---
document_id: CMN-ARCH-NAR-001
title: System Narrative
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: ARCH
  type: NAR
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# System Narrative

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial CommNet system narrative derived from the community internet concept. |

## 1. Purpose [SEC:CMN-ARCH-NAR-001::1]

CommNet is a local-first community internet platform intended to let homes, schools, libraries, makerspaces, neighborhoods, and similar groups host useful local services without assuming dependence on the public internet.

## 2. Product Intent [SEC:CMN-ARCH-NAR-001::2]

A user may receive a flash drive, unzip a package, install Python if needed, and use clear launchers to configure the local system. Setup includes device discovery, local identity, privacy, visibility, file registry, sharing policy, services, diagnostics, backup, and entry into the community web.

## 3. Local-First Principle [SEC:CMN-ARCH-NAR-001::3]

The public internet is optional. Core setup and local portal use must remain valuable even when the public internet is unavailable. A gateway may exist later, but it is not the default model.

## 4. Universal Deployment Principle [SEC:CMN-ARCH-NAR-001::4]

The same underlying configuration platform should serve home, school, library, makerspace, and neighborhood deployments. The difference should be profile presets, roles, and policies rather than incompatible toolchains.

## 5. Pre-Code Boundary [SEC:CMN-ARCH-NAR-001::5]

This package defines the governed baseline. It does not include the executable CommNet portal, admin console, registry builder, network discovery tool, policy engine, or mesh transport implementation.
## Backbone Requirements Update [SEC:CMN-ARCH-NAR-001::B1]

The CommNet narrative is updated by package 20260508_00_BackboneReqs to make the communication layer central. CommNet is not merely a local portal with optional networking; it is a local-first community system whose applications submit messages and bundles to a universal transport manager. Meshtastic, Reticulum/LXMF, LAN/Wi-Fi, Bluetooth, serial, and custody carriers are modeled as adapters under one deterministic route-planning and resource-control doctrine.
