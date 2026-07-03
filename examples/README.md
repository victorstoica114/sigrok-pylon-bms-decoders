# Example Captures

This directory separates field captures by communication topology and translator
mode.

## Test Setup

- Inverter side: Growatt
- BMS side: JKBMS

## Translator Power Use

| Translator mode | Runtime | Energy |
| --- | --- | --- |
| Bridge | 2 h 38 min | 3640 mWh |

## Raw Data

Current raw captures:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Deye CAN | `bridge/deye-can-raw-capture.sr` | Deye-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | GoodWe CAN | `bridge/goodwe-can-raw-capture.sr` | GoodWe-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-raw-capture.sr` | Inverter CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-raw-capture.sr` | Inverter RS485 traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS CAN | `bridge/jkbms-can-raw-capture.sr` | JK BMS CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS Modbus RS485 | `bridge/jkbms-modbus-rs485-raw-capture.sr` | JK BMS runtime polling. |

## PulseView Sessions

Current PulseView session files:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Deye CAN | `bridge/deye-can-pulseview-session.pvs` | CAN and Deye decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | GoodWe CAN | `bridge/goodwe-can-pulseview-session.pvs` | CAN and GoodWe decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-pulseview-session.pvs` | CAN decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-pulseview-session.pvs` | UART and Growatt decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS CAN | `bridge/jkbms-can-pulseview-session.pvs` | CAN and JKBMS decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS Modbus RS485 | `bridge/jkbms-modbus-rs485-pulseview-session.pvs` | UART and JKBMS decoder layout. |

No `Forward` or `Direct cable` captures are committed yet.

Open a `.sr` capture in PulseView, then load or recreate the matching `.pvs`
session when you want the same decoder/channel layout used in the screenshots.
