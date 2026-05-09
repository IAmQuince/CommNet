---
document_id: CMN-MAIL-SPEC-001
title: Internal CommNet Mail Specification
revision: r0
status: WIP
document_class: app_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Internal CommNet Mail Specification

[SEC:CMN-MAIL-SPEC-001::PURPOSE]
Internal CommNet mail provides local account-to-account messaging, mail-to-admin support, unread counts, sent mail, and admin broadcasts without using public email services.

[SEC:CMN-MAIL-SPEC-001::SCOPE]
The current implementation is local SQLite-backed mail only. SMTP, internet email, attachments, cross-node relay, and encrypted mailbox claims are out of scope for this run.

[SEC:CMN-MAIL-SPEC-001::ADMIN]
Admins can view local mail management pages and send broadcasts to users. HUD mail cards show unread and total counts.

[SEC:CMN-MAIL-SPEC-001::PORTAL]
Logged-in users can read inbox messages, view sent messages, compose messages, and send messages to admin.

