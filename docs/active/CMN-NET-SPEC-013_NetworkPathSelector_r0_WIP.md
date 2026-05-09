---
document_id: CMN-NET-SPEC-013
title: Network Path Selector
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Network Path Selector

CommNet shall detect available network interfaces, classify them, and allow the local administrator to choose which path is used for visitor links, share links, peer invites, and LAN setup guidance.

Required behavior:

- list connected and disconnected adapters where detectable;
- show IPv4 address, gateway/router, adapter name, source, classification, and suggested URL;
- classify `169.254.x.x` APIPA addresses as invalid for normal visitor links;
- save the selected path in configuration;
- regenerate copyable links from the selected path.
