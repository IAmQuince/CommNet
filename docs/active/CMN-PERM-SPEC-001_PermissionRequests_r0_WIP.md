---
document_id: CMN-PERM-SPEC-001
title: Permission Requests Specification
revision: r0
status: WIP
document_class: policy_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Permission Requests Specification

[SEC:CMN-PERM-SPEC-001::PURPOSE]
Permission requests let guests and users ask for additional access without exposing admin tools. Admins review, approve, deny, or defer requests from the HUD and Users area.

[SEC:CMN-PERM-SPEC-001::REQUEST-STATES]
Request states include pending, approved, denied, needs_info, and cancelled. Approval creates a local grant record. Denial keeps the access blocked.

[SEC:CMN-PERM-SPEC-001::GRANTS]
Grants are scoped to capabilities such as share listing, preview, download, upload, mail use, BBS use, RetroWeb view, and admin-only management rights.

[SEC:CMN-PERM-SPEC-001::AUDIT]
Permission request creation and admin resolution are recorded as local audit-relevant events and included in diagnostics.

