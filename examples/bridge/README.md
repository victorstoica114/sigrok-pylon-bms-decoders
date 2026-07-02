# Bridge Captures

Captures in this folder were taken with traffic passing through the bridge.
The inverter was not connected directly to the BMS during these captures.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS
- Topology: Growatt inverter <-> bridge <-> JKBMS
- Purpose: normal bridge-mediated traffic where the bridge participates in the
  communication path.

## Captures

| File | Bridge mode | Description |
| --- | --- | --- |
| `growatt-can-pulseview-session.pvs` | Normal bridge | PulseView session for the Growatt CAN bridge capture. |
| `growatt-rs485-pulseview-session.pvs` | Normal bridge | PulseView session for the Growatt RS485 bridge capture. |
| `pylon-can-pulseview-session.pvs` | Normal bridge | PulseView session for the JKBMS/Pylon-compatible CAN bridge capture. |
| `pylon-rs485-pulseview-session.pvs` | Normal bridge | PulseView session for the JKBMS/Pylon-compatible RS485 bridge capture. |
| `growatt-can-raw-capture.sr` | Normal bridge | Raw Growatt CAN bridge capture. |
| `growatt-rs485-raw-capture.sr` | Normal bridge | Raw Growatt RS485 bridge capture. |
| `pylon-can-raw-capture.sr` | Normal bridge | Raw JKBMS/Pylon-compatible CAN bridge capture. |
| `pylon-rs485-raw-capture.sr` | Normal bridge | Raw JKBMS/Pylon-compatible RS485 bridge capture. |
