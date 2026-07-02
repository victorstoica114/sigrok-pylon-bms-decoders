# Bridge Forward Captures

Use this folder for captures where traffic passes through the bridge in forward
mode.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS
- Topology: Growatt inverter <-> bridge in forward mode <-> JKBMS
- Purpose: forward-mode traffic for comparing bridge forwarding behavior against
  direct and normal bridge captures.

## Captures

No bridge-forward captures are committed yet.

When adding captures, keep matching `.sr` and `.pvs` files together and use
protocol-prefixed names, for example:

- `growatt-can-raw-capture.sr`
- `growatt-can-pulseview-session.pvs`
