---
document_id: CMN-AUD-SPEC-004
title: Documentation Retention Audit
revision: r0
status: WIP
document_class: audit_spec
package_class: CONFIG_READY_WITH_DEBT
effective_date: 2026-05-08
authoring_context: CommNet governed package run 20260508_03_Config
depends_on:
- CMN-GOV-STD-001
- CMN-SCM-STD-001
---
# Documentation Retention Audit

[SEC:CMN-AUD-SPEC-004::1] Purpose

Defines the rule that prior active documentation must not disappear during package evolution unless explicitly archived with a reason.

[SEC:CMN-AUD-SPEC-004::2] Requirements Impact

This document preserves prior CommNet documentation and adds configuration-platform control needed before network adapter implementation.

[SEC:CMN-AUD-SPEC-004::3] Implemented In This Package

- Browser-accessible configuration page or supporting backend model.
- Runtime persistence under `runtime/local`.
- Audit or diagnostic evidence where applicable.

[SEC:CMN-AUD-SPEC-004::4] Explicit Limits

This package does not implement Meshtastic hardware messaging, Reticulum/LXMF messaging, Bluetooth messaging, real peer transfer, or production security.
