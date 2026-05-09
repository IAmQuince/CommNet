---
document_id: CMN-RETROWEB-SPEC-002
title: RetroWeb Profile Social Icon Portal Specification
revision: r0
status: WIP
document_class: portal_spec
owner: CommNet
package_class: SERVICE_TRAY_MESH_READY_WITH_DEBT
---

# RetroWeb Profile, Social, and Icon Portal Specification

[SEC:CMN-RETROWEB-SPEC-002::PURPOSE]
RetroWeb is treated as a separate local portal app reached through CommNet. Users enter through `/portal`, then open `/retroweb` if permitted. This run retains the profile creation, generated user icon, and local social-network direction from the RetroWeb concept package.

[SEC:CMN-RETROWEB-SPEC-002::PROFILES]
Logged-in users may create or update a RetroWeb profile with handle, display name, about text, and a generated icon. The generated icon is represented by local palette, shape, glyph, and pattern values rather than external image dependencies.

[SEC:CMN-RETROWEB-SPEC-002::SOCIAL]
RetroWeb users may see a local user gallery, publish short posts, view a feed, and comment on each other's posts. These features are intentionally local-first and are separate from public internet social networking.

[SEC:CMN-RETROWEB-SPEC-002::BOUNDARY]
The RetroWeb shell shall be visually distinct from the Admin HUD and general Community Portal. Admin management remains under `/admin/apps/retroweb`; user interaction remains under `/retroweb`.
