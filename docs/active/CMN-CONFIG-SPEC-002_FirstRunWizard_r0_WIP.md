---
document_id: CMN-CONFIG-SPEC-002
title: First Run Wizard
revision: r0
status: WIP
document_class: configuration_spec
package_class: CONFIG_READY_WITH_DEBT
effective_date: 2026-05-08
authoring_context: CommNet governed package run 20260508_03_Config
depends_on:
- CMN-GOV-STD-001
- CMN-SCM-STD-001
---
# First Run Wizard

[SEC:CMN-CONFIG-SPEC-002::1] Purpose

Defines the accessible browser setup workflow from launcher to applied local node configuration.

[SEC:CMN-CONFIG-SPEC-002::2] Requirements Impact

This document preserves prior CommNet documentation and adds configuration-platform control needed before network adapter implementation.

[SEC:CMN-CONFIG-SPEC-002::3] Implemented In This Package

- Browser-accessible configuration page or supporting backend model.
- Runtime persistence under `runtime/local`.
- Audit or diagnostic evidence where applicable.

[SEC:CMN-CONFIG-SPEC-002::4] Explicit Limits

This package does not implement Meshtastic hardware messaging, Reticulum/LXMF messaging, Bluetooth messaging, real peer transfer, or production security.
