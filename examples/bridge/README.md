# Bridge Captures

Captures in this folder were taken with traffic passing through the bridge.
The inverter was not connected directly to the BMS during these captures.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS
- Translator mode: Bridge
- Topology: Growatt inverter <-> bridge <-> JKBMS
- Purpose: normal bridge-mediated traffic where the bridge participates in the
  communication path.

## Captures

| File | Protocol | Translator mode | Description |
| --- | --- | --- | --- |
| `growatt-can-pulseview-session.pvs` | Growatt CAN | Bridge | PulseView session settings. |
| `growatt-rs485-pulseview-session.pvs` | Growatt RS485 | Bridge | PulseView session settings. |
| `pylon-can-pulseview-session.pvs` | JKBMS/Pylon CAN | Bridge | PulseView session settings. |
| `pylon-rs485-pulseview-session.pvs` | JKBMS/Pylon RS485 | Bridge | PulseView session settings. |
| `growatt-can-raw-capture.sr` | Growatt CAN | Bridge | Raw capture. |
| `growatt-rs485-raw-capture.sr` | Growatt RS485 | Bridge | Raw capture. |
| `pylon-can-raw-capture.sr` | JKBMS/Pylon CAN | Bridge | Raw capture. |
| `pylon-rs485-raw-capture.sr` | JKBMS/Pylon RS485 | Bridge | Raw capture. |
