# Acceptance Test

## Serial-Only Acceptance

1. Compile for `mcci:stm32:mcci_catena_4610`.
2. Upload to the Catena on `COM3`.
3. Open serial at `115200`.
4. Confirm boot banner:

```text
CMN1|BOOT|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|baud=115200|rf_mode=disabled
```

5. Send:

```text
CMN1|PING|nonce=12345
```

Expected:

```text
CMN1|PONG|nonce=12345|uptime_ms=...
```

6. Send:

```text
CMN1|ID?
CMN1|STATUS?
CMN1|TX|id=msg_001|class=text_message|to=broadcast|body=SGVsbG8
```

Expected:

```text
CMN1|ID|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|adapter=catena_serial_lora|rf_mode=disabled
CMN1|STATUS|...
CMN1|ACK|id=msg_001|status=accepted|detail=local_hardware_ack_only|...
```

## Pass Criteria

- Firmware boots cleanly.
- PING/PONG works.
- ID reports `commnet-catena-bridge`.
- TX returns local hardware ACK.
- No RF success or Meshtastic claims are emitted.

## 2026-05-08 Result

Result: PASS

Board and toolchain:

```text
Board: MCCI Catena 4610
FQBN: mcci:stm32:mcci_catena_4610
Port after upload: COM3
Arduino CLI: 1.4.1
Firmware: commnet-catena-bridge 0.1.0
RF mode: disabled
```

Observed responses:

```text
CMN1|BOOT|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|baud=115200|rf_mode=disabled
CMN1|PONG|nonce=12345|uptime_ms=20977
CMN1|ID|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|adapter=catena_serial_lora|rf_mode=disabled
CMN1|STATUS|uptime_ms=21697|tx=0|rx=0|err=0|last_error=none|last_msg_id=none|profile=serial_only|rf_mode=disabled
CMN1|ACK|id=cfg|status=accepted|profile=us915_test|rf_mode=disabled
CMN1|ACK|id=msg_001|status=accepted|detail=local_hardware_ack_only|class=text_message|to=broadcast|bytes=5
```
