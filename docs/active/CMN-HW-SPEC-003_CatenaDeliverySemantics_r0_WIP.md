---
document_id: CMN-HW-SPEC-003
title: Catena Delivery Semantics
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Catena Delivery Semantics

Catena ACK responses have scoped meaning:

- `accepted`: local hardware accepted the command.
- `tx_started`: local RF transmit started.
- `tx_done`: local RF transmit completed.
- `RX`: inbound RF evidence.
- `REMOTE_ACK`: remote receiver confirmed receipt.

CommNet shall not mark remote delivery based only on local ACK.
