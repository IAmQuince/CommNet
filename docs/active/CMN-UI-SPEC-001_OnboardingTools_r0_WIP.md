---
document_id: CMN-UI-SPEC-001
title: Onboarding Tools Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: UI
  type: SPEC
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-UI-ARCH-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Onboarding Tools Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial complete onboarding tool list for CommNet. |

## 1. Purpose [SEC:CMN-UI-SPEC-001::1]

This specification defines the setup and operations tools that should eventually appear as friendly launchers or entries inside the configuration platform.

## 2. Tool List [SEC:CMN-UI-SPEC-001::2]

| Tool ID | Tool | Purpose | Output |
|---|---|---|---|
| ONB-TOOL-001 | Start Here | First-run guided entry point for nontechnical users and admins. | Creates onboarding session and next-step checklist. |
| ONB-TOOL-002 | Install Check | Checks Python, OS, permissions, disk, and network readiness. | Readiness report. |
| ONB-TOOL-003 | Package Verifier | Confirms package files, hashes, manifest, versions, and path lengths. | Integrity report. |
| ONB-TOOL-004 | Runtime Setup | Creates local runtime folders and separates local state from source packages. | Runtime scaffold. |
| ONB-TOOL-005 | Profile Preset Selector | Selects home, school, library, makerspace, neighborhood, or emergency preset. | Initial policy profile. |
| ONB-TOOL-006 | Node Role Wizard | Defines this machine as portal, storage, admin, gateway, client, peer, or hybrid. | Node role config. |
| ONB-TOOL-007 | Local Identity Wizard | Creates local identities, admin accounts, and recovery artifacts. | Identity record. |
| ONB-TOOL-008 | Visibility Wizard | Controls whether the user or node appears on the community web. | Visibility policy. |
| ONB-TOOL-009 | Privacy Wizard | Sets personal, household, student, staff, public-local, or organization privacy boundaries. | Privacy policy. |
| ONB-TOOL-010 | Sharing Policy Builder | Defines what may be shared, cached, copied, discovered, or published. | Sharing rules. |
| ONB-TOOL-011 | Roles and Permissions Console | Engineers roles, groups, approvals, admin powers, and command boundaries. | Permission matrix. |
| ONB-TOOL-012 | Policy Simulator | Tests who can see or do what before policy changes are applied. | Simulation report. |
| ONB-TOOL-013 | Device Discovery Tool | Finds reachable devices, peers, services, storage nodes, and local interfaces. | Device inventory. |
| ONB-TOOL-014 | Add Device Wizard | Adds router, PC, Pi, NAS, server, peer node, gateway, or storage device. | Device record. |
| ONB-TOOL-015 | Network Setup Assistant | Guides LAN, Wi-Fi, ad hoc, static IP, hostname, and service-discovery setup. | Network config. |
| ONB-TOOL-016 | Mesh and Peer Link Assistant | Adds peer links and verifies connectivity without assuming one transport. | Link records. |
| ONB-TOOL-017 | Gateway Boundary Tool | Configures optional public-internet bridge, firewall, and exposure rules. | Gateway policy. |
| ONB-TOOL-018 | Service Manager | Enables local portal, file registry, directory, forum, wiki, search, and diagnostics services. | Service config. |
| ONB-TOOL-019 | File Registry Builder | Scans selected folders and builds the local registry without publishing by default. | File index. |
| ONB-TOOL-020 | Content Import Tool | Imports files from flash drives or local folders and records provenance. | Import log. |
| ONB-TOOL-021 | Metadata Tagger | Adds tags, descriptions, audience, owner, review status, and visibility flags. | Metadata records. |
| ONB-TOOL-022 | Review and Moderation Queue | Supports review states, restrictions, block decisions, and accountability. | Review decisions. |
| ONB-TOOL-023 | Community Directory Publisher | Publishes only approved public-local or peer-visible entries. | Directory records. |
| ONB-TOOL-024 | Backup and Restore Tool | Creates, verifies, and restores configuration, registry, and content backups. | Backup set. |
| ONB-TOOL-025 | Sync and Replication Planner | Controls which content is cached where and under what trust rules. | Replication policy. |
| ONB-TOOL-026 | Storage Steward Tool | Shows capacity, cache health, replication state, and stale content. | Storage report. |
| ONB-TOOL-027 | Diagnostics Dashboard | Shows service health, network status, registry status, sync state, and errors. | Health report. |
| ONB-TOOL-028 | Audit Log Viewer | Reviews changes, approvals, failures, policy changes, and exports. | Audit view. |
| ONB-TOOL-029 | Security Hardening Checklist | Guides passwords, firewall, local exposure, admin hygiene, and backups. | Security report. |
| ONB-TOOL-030 | Update and Package Installer | Applies future CommNet packages while preserving runtime state. | Update report. |
| ONB-TOOL-031 | Export Support Bundle | Creates a redacted diagnostic bundle for troubleshooting. | Support bundle. |
| ONB-TOOL-032 | Community Web Launcher | Opens the local community portal for browsing, search, and local services. | Portal session. |
| ONB-TOOL-033 | Admin Console Launcher | Opens the powerful configuration platform for owners and admins. | Admin session. |
| ONB-TOOL-034 | Help and Demo Mode | Runs simulated walkthroughs without changing real settings. | Demo state. |
| ONB-TOOL-035 | Emergency and Outage Mode Setup | Configures local notices, emergency resources, and offline operation modes. | Emergency profile. |
| ONB-TOOL-036 | Shortcut and Icon Manager | Creates or repairs clickable launchers relative to the extracted package. | Launcher icons. |

## 3. Common Engine Rule [SEC:CMN-UI-SPEC-001::3]

Home, school, library, makerspace, neighborhood, and emergency deployments should use the same core configuration engine. Presets change defaults and available workflows; they should not create incompatible products.

## 4. Pre-Code Status [SEC:CMN-UI-SPEC-001::4]

This package defines the onboarding tool set and requirements. It does not implement those product tools.
## Backbone Requirements Update [SEC:CMN-UI-SPEC-001::B1]

The onboarding tool set shall include communication profile selection, dependency checks, Meshtastic setup, Reticulum setup, LAN/Wi-Fi peer discovery, Bluetooth profile checks, device adapter status, route diagnostics, queue inspection, and support-bundle export.
