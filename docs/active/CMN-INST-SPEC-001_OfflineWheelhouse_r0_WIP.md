---
document_id: CMN-INST-SPEC-001
title: Offline Wheelhouse Specification
revision: r0
status: WIP
document_class: controlled_doc
package_class: BACKBONE_REQ_BASELINE
classification: {"domain": "INST", "type": "SPEC", "sequence": "001"}
effective_date: 2026-05-08
authoring_context: CommNet
depends_on: ["CMN-SW-REQ-002"]
supersedes: []
superseded_by: []
machine_readable_artifacts: ["requirements/", "wheels/"]
---
# Offline Wheelhouse Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Defines profile-based offline dependency installation. |

## 1. Purpose [SEC:CMN-INST-SPEC-001::1]

CommNet shall support installation from a flash drive without requiring the user to search the internet for libraries during setup.

## 2. Wheelhouse Folders [SEC:CMN-INST-SPEC-001::2]

The package shall define wheelhouse folders for core, Meshtastic, Reticulum, LAN, Bluetooth, diagnostics, and developer profiles.

## 3. False-Claim Control [SEC:CMN-INST-SPEC-001::3]

A package shall not claim offline wheels are included unless wheel files are physically present and listed in a wheel manifest.

## 4. Installer Behavior [SEC:CMN-INST-SPEC-001::4]

Offline installers shall use `python -m pip install --no-index --find-links` against the selected wheelhouse folders. If wheels are missing, the installer shall report the missing package set and continue to allow local documentation and UI where possible.
