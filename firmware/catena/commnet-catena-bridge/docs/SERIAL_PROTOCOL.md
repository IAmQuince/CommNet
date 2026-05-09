# Catena Serial Protocol

## Scope

This protocol is a conservative ASCII line protocol for CommNet-to-Catena USB
serial control. It intentionally avoids JSON and dynamic parsing libraries.

## Line Format

- Line ending: `\n`
- Carriage return: tolerated and ignored
- Prefix: `CMN1`
- Field separator: `|`
- Key/value separator: `=`
- Maximum input line buffer: 319 visible bytes plus null terminator
- Maximum decoded payload body: 180 bytes

## Host to Catena

```text
CMN1|PING|nonce=12345
CMN1|ID?
CMN1|STATUS?
CMN1|CFG|profile=us915_test|sf=7|bw=125|cr=45|txp=10
CMN1|TX|id=msg_001|class=text_message|to=broadcast|body=SGVsbG8
```

`body` is base64url text. The serial-only firmware validates character set and
payload size, but does not decode or transmit RF.

## Catena to Host

```text
CMN1|BOOT|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|baud=115200|rf_mode=disabled
CMN1|PONG|nonce=12345|uptime_ms=123456
CMN1|ID|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|adapter=catena_serial_lora|rf_mode=disabled
CMN1|STATUS|uptime_ms=123456|tx=3|rx=0|err=0|last_error=none|last_msg_id=msg_001|profile=us915_test|rf_mode=disabled
CMN1|ACK|id=msg_001|status=accepted|detail=local_hardware_ack_only|class=text_message|to=broadcast|bytes=5
CMN1|ERR|id=msg_002|code=payload_too_large|detail=max_180
```

## Delivery Semantics

`ACK status=accepted` means the local Catena firmware accepted the serial
command. It does not mean remote RF delivery. Future RF-capable firmware must
emit separate `tx_started`, `tx_done`, `RX`, or `REMOTE_ACK` status before a
host application may claim RF progress or remote delivery.
