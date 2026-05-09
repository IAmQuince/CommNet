---
document_id: CMN-NET-SPEC-014
title: Address Classification
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Address Classification

CommNet classifies network addresses before presenting them as visitor links.

- Recommended: private LAN IPv4 with gateway/router.
- Warning: private IPv4 without gateway, VPN/virtual/unknown adapter, or public-looking address.
- Invalid: loopback, media disconnected, no IPv4, and self-assigned/APIPA `169.254.x.x`.

CommNet shall not recommend APIPA addresses for normal visitor links unless an advanced override exists in a later package.
