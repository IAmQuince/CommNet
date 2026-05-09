# Known Limits

- This firmware is not Meshtastic.
- RF transmit is disabled in version `0.1.0`.
- `ACK status=accepted` is a local hardware acknowledgement only.
- Remote RF delivery is not implemented.
- LoRaWAN is not implemented.
- Raw LoRa peer-to-peer is not implemented.
- Serial input is intentionally bounded; oversized lines are rejected.
