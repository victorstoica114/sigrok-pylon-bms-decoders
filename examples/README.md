# Example Captures

This directory separates field captures by communication topology and translator
mode.

## Test Setup

- Inverter side: Growatt, Anenji, or Easun, as listed in each capture row
- BMS side: JKBMS, SeplosBMS, or Daly BMS, as listed in each capture row

## Translator Power Use

| Translator mode | Runtime | Energy |
| --- | --- | --- |
| Bridge | 2 h 38 min | 3640 mWh |

## Raw Data

Current raw captures:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | China Tower Modbus RS485 | `bridge/china-tower-modbus-rs485-raw-capture.sr` | China Tower / JK 008 RS485 polling. |
| Bridge | Easun inverter <-> bridge <-> Daly BMS | Daly RS485 | `bridge/easun-daly-rs485-raw-capture.sr` | Daly BMS RS485 traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Deye CAN | `bridge/deye-can-raw-capture.sr` | Deye-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | GoodWe CAN | `bridge/goodwe-can-raw-capture.sr` | GoodWe-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-raw-capture.sr` | Inverter CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Growatt CAN | `bridge/growatt-seplos-can-raw-capture.sr` | Inverter CAN traffic. |
| Direct cable | Growatt inverter <-> direct cable <-> JKBMS | Growatt CAN | `direct/growatt-can-raw-capture.sr` | Inverter CAN traffic. |
| Direct cable | Growatt inverter <-> direct cable <-> SeplosBMS | Growatt CAN | `direct/growatt-seplos-can-raw-capture.sr` | Inverter CAN traffic. |
| Forward | Growatt inverter <-> bridge in forward mode <-> JKBMS | Growatt CAN | `bridge_forward/growatt-can-raw-capture.sr` | Inverter CAN traffic in forward mode. |
| Forward | Growatt inverter <-> bridge in forward mode <-> SeplosBMS | Growatt CAN | `bridge_forward/growatt-seplos-can-raw-capture.sr` | Inverter CAN traffic in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-raw-capture.sr` | Inverter RS485 traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Growatt RS485 | `bridge/growatt-seplos-rs485-raw-capture.sr` | Inverter RS485 traffic. |
| Direct cable | Growatt inverter <-> direct cable <-> JKBMS | Growatt RS485 | `direct/growatt-rs485-raw-capture.sr` | Inverter RS485 traffic. |
| Forward | Growatt inverter <-> bridge in forward mode <-> JKBMS | Growatt RS485 | `bridge_forward/growatt-rs485-raw-capture.sr` | Inverter RS485 traffic in forward mode. |
| Forward | Growatt inverter <-> bridge in forward mode <-> SeplosBMS | Growatt RS485 | `bridge_forward/growatt-seplos-rs485-raw-capture.sr` | Inverter RS485 traffic in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS CAN | `bridge/jkbms-can-raw-capture.sr` | JK BMS CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS Modbus RS485 | `bridge/jkbms-modbus-rs485-raw-capture.sr` | JK BMS runtime polling. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | PACE Modbus RS485 | `bridge/pace-modbus-rs485-raw-capture.sr` | PACE BMS RS485 polling. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Pylon CAN | `bridge/pylon-can-raw-capture.sr` | Pylon-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Pylon RS485 | `bridge/pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic. |
| Bridge | Anenji inverter <-> bridge <-> JKBMS | Pylon RS485 | `bridge/anenji-pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic. |
| Direct cable | Anenji inverter <-> direct cable <-> JKBMS | Pylon RS485 | `direct/anenji-jkbms-pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic. |
| Direct cable | Anenji inverter <-> direct cable <-> SeplosBMS | Pylon RS485 | `direct/anenji-seplos-pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic. |
| Forward | Anenji inverter <-> bridge in forward mode <-> JKBMS | Pylon RS485 | `bridge_forward/anenji-pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic in forward mode. |
| Forward | Anenji inverter <-> bridge in forward mode <-> SeplosBMS | Pylon RS485 | `bridge_forward/anenji-seplos-pylon-rs485-raw-capture.sr` | Pylon-compatible RS485 ASCII traffic in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | SMA CAN | `bridge/sma-can-raw-capture.sr` | SMA-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Sofar CAN | `bridge/sofar-can-raw-capture.sr` | Sofar-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Victron CAN | `bridge/victron-can-raw-capture.sr` | Victron-compatible CAN traffic. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Voltronic Modbus RS485 | `bridge/voltronic-modbus-rs485-raw-capture.sr` | Voltronic/JK-007 RS485 polling. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | WOW Modbus RS485 | `bridge/wow-modbus-rs485-raw-capture.sr` | WOW / JK 009 RS485 polling. |

## PulseView Sessions

Current PulseView session files:

| Translator mode | Test topology | Protocol | File | Description |
| --- | --- | --- | --- | --- |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | China Tower Modbus RS485 | `bridge/china-tower-modbus-rs485-pulseview-session.pvs` | UART and China Tower decoder layout. |
| Bridge | Easun inverter <-> bridge <-> Daly BMS | Daly RS485 | `bridge/easun-daly-rs485-pulseview-session.pvs` | UART and Daly decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Deye CAN | `bridge/deye-can-pulseview-session.pvs` | CAN and Deye decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | GoodWe CAN | `bridge/goodwe-can-pulseview-session.pvs` | CAN and GoodWe decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt CAN | `bridge/growatt-can-pulseview-session.pvs` | CAN decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Growatt CAN | `bridge/growatt-seplos-can-pulseview-session.pvs` | CAN and Growatt decoder layout. |
| Direct cable | Growatt inverter <-> direct cable <-> JKBMS | Growatt CAN | `direct/growatt-can-pulseview-session.pvs` | CAN and Growatt decoder layout. |
| Direct cable | Growatt inverter <-> direct cable <-> SeplosBMS | Growatt CAN | `direct/growatt-seplos-can-pulseview-session.pvs` | CAN and Growatt decoder layout. |
| Forward | Growatt inverter <-> bridge in forward mode <-> JKBMS | Growatt CAN | `bridge_forward/growatt-can-pulseview-session.pvs` | CAN and Growatt decoder layout in forward mode. |
| Forward | Growatt inverter <-> bridge in forward mode <-> SeplosBMS | Growatt CAN | `bridge_forward/growatt-seplos-can-pulseview-session.pvs` | CAN and Growatt decoder layout in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Growatt RS485 | `bridge/growatt-rs485-pulseview-session.pvs` | UART and Growatt decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Growatt RS485 | `bridge/growatt-seplos-rs485-pulseview-session.pvs` | UART and Growatt decoder layout. |
| Direct cable | Growatt inverter <-> direct cable <-> JKBMS | Growatt RS485 | `direct/growatt-rs485-pulseview-session.pvs` | UART and Growatt decoder layout. |
| Forward | Growatt inverter <-> bridge in forward mode <-> JKBMS | Growatt RS485 | `bridge_forward/growatt-rs485-pulseview-session.pvs` | UART and Growatt decoder layout in forward mode. |
| Forward | Growatt inverter <-> bridge in forward mode <-> SeplosBMS | Growatt RS485 | `bridge_forward/growatt-seplos-rs485-pulseview-session.pvs` | UART and Growatt decoder layout in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS CAN | `bridge/jkbms-can-pulseview-session.pvs` | CAN and JKBMS decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | JKBMS Modbus RS485 | `bridge/jkbms-modbus-rs485-pulseview-session.pvs` | UART and JKBMS decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | PACE Modbus RS485 | `bridge/pace-modbus-rs485-pulseview-session.pvs` | UART and PACE decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Pylon CAN | `bridge/pylon-can-pulseview-session.pvs` | CAN and Pylon decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | Pylon RS485 | `bridge/pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout. |
| Bridge | Anenji inverter <-> bridge <-> JKBMS | Pylon RS485 | `bridge/anenji-pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout. |
| Direct cable | Anenji inverter <-> direct cable <-> JKBMS | Pylon RS485 | `direct/anenji-jkbms-pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout. |
| Direct cable | Anenji inverter <-> direct cable <-> SeplosBMS | Pylon RS485 | `direct/anenji-seplos-pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout. |
| Forward | Anenji inverter <-> bridge in forward mode <-> JKBMS | Pylon RS485 | `bridge_forward/anenji-pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout in forward mode. |
| Forward | Anenji inverter <-> bridge in forward mode <-> SeplosBMS | Pylon RS485 | `bridge_forward/anenji-seplos-pylon-rs485-pulseview-session.pvs` | UART and Pylon decoder layout in forward mode. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | SMA CAN | `bridge/sma-can-pulseview-session.pvs` | CAN and SMA decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Sofar CAN | `bridge/sofar-can-pulseview-session.pvs` | CAN and Sofar decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Victron CAN | `bridge/victron-can-pulseview-session.pvs` | CAN and Victron decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> SeplosBMS | Voltronic Modbus RS485 | `bridge/voltronic-modbus-rs485-pulseview-session.pvs` | UART and Voltronic decoder layout. |
| Bridge | Growatt inverter <-> bridge <-> JKBMS | WOW Modbus RS485 | `bridge/wow-modbus-rs485-pulseview-session.pvs` | UART and WOW decoder layout. |

Open a `.sr` capture in PulseView, then load or recreate the matching `.pvs`
session when you want the same decoder/channel layout used in the screenshots.
