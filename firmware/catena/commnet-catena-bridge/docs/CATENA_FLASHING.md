# Catena Flashing Notes

## Board

- Hardware: MCCI Catena 4610
- Arduino core: `mcci:stm32`
- FQBN: `mcci:stm32:mcci_catena_4610`
- Serial port observed on this machine: `COM3`
- Upload method used on this machine: STM32 DFU bootloader

## Arduino CLI Setup

The MCCI board manager URL is:

```text
https://github.com/mcci-catena/arduino-boards/raw/master/BoardManagerFiles/package_mcci_index.json
```

The required core is:

```text
mcci:stm32
```

## Upload Command

```text
arduino-cli upload -p COM3 --fqbn mcci:stm32:mcci_catena_4610 commnet_catena_bridge
```

If upload waits for bootloader/reset, press the Catena reset button when
requested or when the upload tool begins trying to connect.

## Windows DFU Driver Note

On this machine, the Catena runtime USB serial device appeared as `COM3`, but
DFU upload initially failed because Windows had the STM32 ROM bootloader in an
error state:

```text
STM32 BOOTLOADER
USB\VID_0483&PID_DF11
```

The fix was to bind `STM32 BOOTLOADER` / `0483 DF11` to the WinUSB driver using
Zadig. Do not replace the driver for the Catena runtime serial device
`VID_040E&PID_00A1`.
