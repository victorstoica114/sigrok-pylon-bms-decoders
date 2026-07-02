# Decoder Implementation Checklist

Use this checklist whenever a new protocol decoder is added or an old decoder
is brought back into the active tree.

## Required For Every Protocol

- Add the decoder package under `decoders/`.
- Add parser/helper tests for the decoded fields.
- Add PulseView package/import tests.
- Add a protocol map under `docs/`.
- Link the protocol map from `README.md`.
- Keep `examples/README.md` aligned when captures are committed.
- Update `CHANGELOG.md`.

## Protocol Map Naming

- CAN payload layout: `<device>-can-frame-map.md`
- RS485 Modbus registers: `<device>-rs485-register-map.md` or `<device>-modbus-register-map.md`
- ASCII/serial frame layout: `<device>-rs485-frame-map.md`

## Protocol Map Table

Use this table shape unless a protocol needs something clearly different:

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |

For CAN, the first column should contain the CAN ID and payload byte range. For
RS485 Modbus, it should contain the register or register range. For ASCII
serial protocols, it should contain the frame command and field range.

Do not add `Direction`, `Source`, `Confidence`, or `Notes` columns unless we
explicitly decide they are needed for that protocol.
