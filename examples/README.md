# Example Captures

This directory separates field captures by communication topology and translator
mode.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS

## Raw Data

Current committed raw captures:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-raw-capture.sr` | Raw capture. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-raw-capture.sr` | Raw capture. |

## PulseView Sessions

Current committed PulseView session files:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-pulseview-session.pvs` | PulseView session settings. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-pulseview-session.pvs` | PulseView session settings. |

No `Forward` or `Direct cable` captures are committed yet.

Open a `.sr` capture in PulseView, then load or recreate the matching `.pvs`
session when you want the same decoder/channel layout used in the screenshots.
