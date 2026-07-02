# sigrok-pylon-bms-decoders

PulseView/libsigrokdecode protocol decoders for the current JKBMS and Growatt
test bench.

Active decoders:

- `Growatt RS485`: Growatt Modbus RTU frames over UART/RS485.
- `JKBMS Modbus`: JK BMS RS485 Modbus RTU runtime frames.

Older screenshots remain under `pictures/` until those protocols are brought
back into the active decoder set.

## Layout

```text
decoders/
  growatt_rs485/
  jkbms_modbus/
docs/
  decoder-implementation-checklist.md
  jkbms-modbus-register-map.md
examples/
  README.md
  bridge/
  direct/
  bridge_forward/
pictures/
tests/
install-pulseview-decoders.ps1
start-pulseview.ps1
```

## Quick Start On Windows

For the most reliable PulseView setup, install a combined decoder directory
under `C:\ProgramData`:

```powershell
.\install-pulseview-decoders.ps1
```

This copies PulseView's built-in decoders plus all custom decoders from
`decoders/` into:

```text
C:\ProgramData\libsigrokdecode\decoders
```

It also sets the user `SIGROKDECODE_DIR` environment variable and creates
PulseView shortcuts.

For development, run PulseView with a temporary generated decoder bundle
instead:

```powershell
.\start-pulseview.ps1
```

That keeps built-in decoders such as `UART` and `CAN` visible while adding the
custom BMS decoders from this repo.

## Example Captures

The `examples/` directory separates field captures by communication topology
and translator mode. See `examples/README.md` for the current raw data and
PulseView session tables.

## Protocol Maps

Every active protocol decoder must have a matching map document under `docs/`.
Use [Decoder Implementation Checklist](docs/decoder-implementation-checklist.md)
before adding or merging a new decoder.

- [JKBMS Modbus Register Map](docs/jkbms-modbus-register-map.md)

## Growatt RS485 Decoder

`decoders/growatt_rs485` stacks above the built-in `UART` decoder:

```text
logic -> uart -> growatt_rs485
```

Typical settings:

- baud: `9600`
- data bits: `8`
- parity: `none`
- stop bits: `1`
- bit order: `lsb-first`
- line inversion: depends on the probe point/transceiver output

The decoder handles Growatt Modbus RTU requests, responses, exceptions, CRC
checks, and known BMS register blocks including status, protection flags, SOC,
pack voltage/current, cell extremes, and cell voltage registers.

## JKBMS Modbus Decoder

`decoders/jkbms_modbus` stacks above the built-in `UART` decoder:

```text
logic -> uart -> jkbms_modbus
```

Typical settings:

- baud: `115200` for JK app profile `001`
- baud: `9600` for JK app profile `013`
- data bits: `8`
- parity: `none`
- stop bits: `1`
- bit order: `lsb-first`
- line inversion: depends on the probe point/transceiver output

The decoder handles Modbus RTU requests, responses, exceptions, CRC checks, and
the JKBMS runtime register map used by the current Growatt/JKBMS bridge tests.

## Tests

Run parser/decoder helper tests with:

```powershell
python -m pytest tests -q
```

The tests do not require PulseView to be running.
