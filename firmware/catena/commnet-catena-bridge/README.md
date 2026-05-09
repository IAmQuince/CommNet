# CommNet Catena Bridge

Serial-first firmware for the MCCI Catena 4610 hardware demo path.

This sketch identifies as `commnet-catena-bridge` and implements the `CMN1`
ASCII line protocol expected by the CommNet `catena_serial_lora` adapter plan.
The first build is intentionally serial-only: RF transmit is disabled and every
`TX` acknowledgement means only that the local Catena accepted the command.

## Current Status

- Target board: MCCI Catena 4610
- Arduino FQBN: `mcci:stm32:mcci_catena_4610`
- Serial baud: `115200`
- Protocol prefix: `CMN1`
- RF mode: `disabled`
- Remote delivery: not implemented

## Build

```text
arduino-cli compile --fqbn mcci:stm32:mcci_catena_4610 commnet_catena_bridge
```

## Upload

```text
arduino-cli upload -p COM3 --fqbn mcci:stm32:mcci_catena_4610 commnet_catena_bridge
```

## Basic Test

Open the serial port at `115200` baud and send newline-terminated commands:

```text
CMN1|PING|nonce=12345
CMN1|ID?
CMN1|STATUS?
CMN1|CFG|profile=us915_test|sf=7|bw=125|cr=45|txp=10
CMN1|TX|id=msg_001|class=text_message|to=broadcast|body=SGVsbG8
```

Expected responses include:

```text
CMN1|PONG|nonce=12345|uptime_ms=...
CMN1|ID|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|adapter=catena_serial_lora|rf_mode=disabled
CMN1|ACK|id=msg_001|status=accepted|detail=local_hardware_ack_only|...
```

## Safety Boundary

This firmware is not Meshtastic. It does not claim LoRa mesh delivery. RF
transmit code is not active in this first bridge build.
