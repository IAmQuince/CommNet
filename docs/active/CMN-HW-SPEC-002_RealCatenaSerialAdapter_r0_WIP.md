---
document_id: CMN-HW-SPEC-002
title: Real Catena Serial Adapter
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Real Catena Serial Adapter

CommNet shall support a real Catena USB serial adapter using pyserial when available. Missing pyserial shall not prevent the local UI from starting.

The adapter supports PING, ID?, STATUS?, CFG, and TX commands using the CMN1 protocol. It must tolerate unsolicited STATUS heartbeat lines while waiting for command responses.
