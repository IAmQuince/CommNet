---
document_id: CMN-POLICY-SPEC-001
title: Privacy Gate
revision: r0
status: WIP
document_class: policy_spec
package_class: CONFIG_READY_WITH_DEBT
effective_date: 2026-05-08
authoring_context: CommNet governed package run 20260508_03_Config
depends_on:
- CMN-GOV-STD-001
- CMN-SCM-STD-001
---
# Privacy Gate

[SEC:CMN-POLICY-SPEC-001::1] Purpose

Defines private-by-default behavior and the rule that registered file roots do not imply publication.

[SEC:CMN-POLICY-SPEC-001::2] Requirements Impact

This document preserves prior CommNet documentation and adds configuration-platform control needed before network adapter implementation.

[SEC:CMN-POLICY-SPEC-001::3] Implemented In This Package

- Browser-accessible configuration page or supporting backend model.
- Runtime persistence under `runtime/local`.
- Audit or diagnostic evidence where applicable.

[SEC:CMN-POLICY-SPEC-001::4] Explicit Limits

This package does not implement Meshtastic hardware messaging, Reticulum/LXMF messaging, Bluetooth messaging, real peer transfer, or production security.
