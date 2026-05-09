---
document_id: CMN-HW-GUIDE-002
title: Catena Firmware Team Update
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Catena Firmware Team Update

The flashed `commnet-catena-bridge 0.1.0` firmware passed these acceptance gates:

- BOOT line appears after reset.
- Periodic STATUS heartbeat appears every about 10 seconds.
- PING returns PONG.
- ID? returns device `catena4610`, firmware `commnet-catena-bridge 0.1.0`, adapter `catena_serial_lora`, and `rf_mode=disabled`.
- CFG accepts profile change to `us915_test`.
- STATUS updates profile correctly.
- No errors reported during basic command testing.

Next firmware requests:

1. Keep the firmware serial-first and do not convert it to Meshtastic.
2. Add a stable device identifier if available.
3. Preserve the CMN1 line protocol.
4. Keep ACK semantics explicit.
5. Add future-ready states: `accepted`, `tx_started`, `tx_done`, `RX`, and `REMOTE_ACK`.
6. Continue reporting `rf_mode` honestly.
7. If RF transmit is added, distinguish local RF TX completion from remote receipt.
8. Keep STATUS heartbeat, and make sure every emitted line ends with a clean newline.
9. Document payload and line length limits.
