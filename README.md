# sigrok-pylon-bms-decoders

PulseView/libsigrokdecode protocol decoders for Pylon-compatible BMS traffic.

This repository currently contains:

- `Pylon RS485`: ASCII Pylon-compatible frames over UART/RS485.
- `Pylon CAN`: Classic CAN Pylon-compatible frames, including field-tested JK/Pylon IDs.

The decoders were built around real captures from LA2016/PulseView sessions and are intended for practical inverter/BMS debugging.

## Layout

```text
decoders/
  pylon_rs485/
  pylon_can/
tests/
install-pulseview-decoders.ps1
start-pulseview.ps1
```

## Quick Start On Windows

For the most reliable PulseView setup, install a combined decoder directory under `C:\ProgramData`:

```powershell
.\install-pulseview-decoders.ps1
```

This copies PulseView's built-in decoders plus these Pylon decoders into:

```text
C:\ProgramData\libsigrokdecode\decoders
```

It also sets the user `SIGROKDECODE_DIR` environment variable and creates a `PulseView Pylon` shortcut on the Desktop and in the Start Menu.

For development, run PulseView with a temporary generated decoder bundle instead:

```powershell
.\start-pulseview.ps1
```

That keeps built-in decoders such as `CAN` visible while adding `Pylon CAN` and `Pylon RS485`.

## Pylon RS485 Decoder

`decoders/pylon_rs485` stacks above the built-in `UART` decoder:

```text
logic -> uart -> pylon_rs485
```

Typical settings:

- baud: `9600`
- data bits: `8`
- parity: `none`
- stop bits: `1`
- bit order: `lsb-first`
- line inversion: depends on the probe point/transceiver output

## Pylon CAN Decoder

`decoders/pylon_can` is a standalone decoder. Add `Pylon CAN` directly from the PulseView decoder selector.

Typical settings:

- nominal bitrate: `500000`
- fast bitrate: unused for Classic CAN; leave at `500000`
- sample point: start with `70%`, then try `75%` or `80%` if needed

Input modes:

- `rx/canl-direct`: use with transceiver `RXD`, or with digitized `CANL` when recessive is `1` and dominant is `0`.
- `canh-inverted`: use with digitized `CANH` when recessive is `0` and dominant is `1`.
- `canh-canl-diff`: use CH0 as `CANH` and optional CH1 as `CANL`; this derives the CAN RX logic level from the digitized wire states.

The decoder currently annotates known Pylon/JK CAN IDs including `0x351`, `0x355`, `0x356`, `0x359`, `0x35C`, `0x35E`, `0x370`, `0x371`, and `0x373`.

## Tests

Run parser/decoder helper tests with:

```powershell
python -m pytest tests -q
```

The tests do not require PulseView to be running, but the package import tests expect a normal PulseView installation at `C:\Program Files\sigrok\PulseView` on Windows.
