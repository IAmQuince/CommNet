---
document_id: CMN-AUTH-SPEC-001
title: Local Accounts Specification
revision: r0
status: WIP
document_class: security_spec
owner: CommNet
package_class: USABILITY_HUD_READY_WITH_DEBT
---

# Local Accounts Specification

[SEC:CMN-AUTH-SPEC-001::PURPOSE]
CommNet now supports local accounts for a LAN-local demonstrator. The feature separates anonymous visitors, normal users, trusted users, and admins for portal, sharing, mail, and configuration workflows.

[SEC:CMN-AUTH-SPEC-001::CREDENTIALS]
Passwords are not stored in plaintext. The implementation uses per-user salt and PBKDF2-HMAC-SHA256 password hashing through the local identity store. Password hints are stored separately and are length-limited.

[SEC:CMN-AUTH-SPEC-001::SESSIONS]
Session state is stored locally and exposed through HttpOnly cookies. Logout invalidates the session. This is a local-first demonstrator and does not claim public-internet production authentication.

[SEC:CMN-AUTH-SPEC-001::ROLES]
Initial roles are owner, admin, trusted, user, guest, retroweb_user, and suspended. Admin routes continue to be protected by local-client guard and role-aware UI gates.

