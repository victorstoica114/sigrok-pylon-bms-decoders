# Direct Captures

Use this folder for captures where the inverter communicates directly with the
BMS, without the bridge in the communication path.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS
- Translator mode: Direct cable
- Topology: Growatt inverter <-> JKBMS
- Purpose: baseline traffic for comparing direct inverter/BMS behavior against
  bridge and bridge-forward captures.

## Captures

No direct captures are committed yet.

When adding captures, keep matching `.sr` and `.pvs` files together and use
protocol-prefixed names, for example:

- `growatt-can-raw-capture.sr`
- `growatt-can-pulseview-session.pvs`
