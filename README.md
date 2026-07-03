# sigrok-pylon-bms-decoders

PulseView/libsigrokdecode protocol decoders for validated BMS/inverter captures.

Active decoders:

- `Growatt RS485`: Growatt Modbus RTU frames over UART/RS485.
- `Growatt CAN`: Growatt low-voltage BMS/inverter frames over Classic CAN.
- `JKBMS Modbus`: JK BMS RS485 Modbus RTU runtime frames.

Rule for this repository: `decoders/` contains only decoders that were validated
on captures and explicitly accepted for publication. Decoders that are still in
field test stay in the firmware/workbench repository until they are confirmed
again together, then copied here and installed.

Older screenshots and map notes can remain under `pictures/` and `docs/` while
those protocols are being reworked, but they are not active unless their decoder
folder exists under `decoders/`.

## Layout

```text
decoders/
  growatt_can/
  growatt_rs485/
  jkbms_modbus/
docs/
  decoder-implementation-checklist.md
  growatt-can-frame-map.md
  growatt-rs485-register-map.md
  jkbms-modbus-register-map.md
  pylon-can-frame-map.md
  pylon-rs485-frame-map.md
examples/
  README.md
  bridge/
  direct/
  bridge_forward/
pictures/
  growatt_can/
  growatt_rs485/
  jkbms_modbus/
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

This copies PulseView's built-in decoders plus all validated custom decoders
from `decoders/` into:

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

Active maps:

- [Growatt CAN Frame Map](docs/growatt-can-frame-map.md)
- [Growatt RS485 Register Map](docs/growatt-rs485-register-map.md)
- [JKBMS Modbus Register Map](docs/jkbms-modbus-register-map.md)

Staging/reference maps currently present for future promotion:

- [Pylon CAN Frame Map](docs/pylon-can-frame-map.md)
- [Pylon RS485 Frame Map](docs/pylon-rs485-frame-map.md)

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

## Growatt CAN Decoder

`decoders/growatt_can` is a standalone decoder. Add `Growatt CAN` directly from
the PulseView decoder selector.

Typical settings:

- nominal bitrate: `500000`
- fast bitrate: unused for Classic CAN; leave at `500000`
- sample point: start with `70%`; try `75%` or `80%` if annotations are unstable
- input mode:
  - `rx/canl-direct` for transceiver `RXD` or digitized `CANL`
  - `canh-inverted` for digitized `CANH` when recessive/dominant are inverted
  - `canh-canl-diff` with CH0 as `CANH` and CH1 as `CANL`

The decoder covers the Growatt low-voltage CAN frame IDs used by the bridge,
including pack telemetry, limits, status/alarms, cell extremes, temperatures,
and metadata frames.

## JKBMS Modbus Decoder

`decoders/jkbms_modbus` stacks above the built-in `UART` decoder:

```text
logic -> uart -> jkbms_modbus
```

Typical logic-level UART settings:

- baud: `115200` for JK app profile `001 - JK BMS RS485 Modbus V1.0`
- baud: `9600` for JK app profile `013 - (9600) JK BMS RS485 Modbus V1.0`
- data bits: `8`
- parity: `none`
- stop bits: `1`
- bit order: `lsb-first`
- line inversion: depends on the probe point/transceiver output

For direct digital probing of RS485 A/B with the LA2016, validate both
polarities. The current field capture was checked with `115200 8N1`; the best
offline pass used `CH1`, RX invert `no`, and a UART sample point around `30%`.

The current published decoder is visible in PulseView as
`JKBMS Modbus v2026.07.02b`. It handles Modbus RTU requests, responses,
exceptions, CRC checks, and the JK runtime register map used by the bridge:
cell-voltage blocks, cell average/delta/index registers, MOS/battery
temperatures, pack voltage/current, SOC/SOH, capacities, cycles, and candidate
alarm/status fields.

## JKBMS Modbus Capture Screenshots

The current screenshots use a Growatt inverter, a JK BMS, RS485 through the
translator bridge, a Kingst LA2016 logic analyzer, and
`JKBMS Modbus v2026.07.02b`.

![JKBMS Modbus request for 0x1230](pictures/jkbms_modbus/jkbms-modbus-0x1230-request.png)

![JKBMS Modbus response for 0x1230](pictures/jkbms_modbus/jkbms-modbus-0x1230-response.png)

![JKBMS Modbus response for 0x1244](pictures/jkbms_modbus/jkbms-modbus-0x1244-response.png)

![JKBMS Modbus response for 0x1200](pictures/jkbms_modbus/jkbms-modbus-0x1200-response.png)

## Tests

Run parser/decoder helper tests with:

```powershell
python -m pytest tests -q
```

The tests do not require PulseView to be running.
