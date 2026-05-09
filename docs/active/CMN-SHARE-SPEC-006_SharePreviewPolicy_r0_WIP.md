---
document_id: CMN-SHARE-SPEC-006
title: Share Preview Policy Specification
revision: r0
status: WIP
document_class: security_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Share Preview Policy Specification

[SEC:CMN-SHARE-SPEC-006::PURPOSE]
Share preview policy gives admins more control than a single download-or-not setting. Shares can be invisible, count-only, list-only, preview-only, download-enabled, upload-inbox, or admin-only.

[SEC:CMN-SHARE-SPEC-006::SAFE-PREVIEW]
Safe preview is allowlist-based. Text, markdown, CSV previews, and common images are supported. HTML and JavaScript are not executed. Unknown binary content is blocked or shown as metadata only.

[SEC:CMN-SHARE-SPEC-006::ROOT-SELECTION]
Admins can create shares from detected root candidates and a server-side folder-selection workflow, with warnings for broad paths such as whole drives.

[SEC:CMN-SHARE-SPEC-006::GUEST-VIEW]
The guest view reflects the share behavior: hidden, count only, list only, preview, or download. Path traversal protection remains required.

