# Changelog

## Current

### Added

- PulseView/libsigrokdecode `JKBMS Modbus` decoder for JK BMS RS485 Modbus RTU frames.
- JKBMS Modbus runtime register map documentation.
- Windows installer and launcher scripts that keep built-in PulseView decoders visible alongside custom BMS decoders.
- Host-side parser/decoder regression tests.
- PulseView/libsigrokdecode `Growatt RS485` decoder for Growatt Modbus RTU frames.
- Example raw `.sr` captures and matching PulseView `.pvs` sessions for Growatt CAN and Growatt RS485.
- Automatic custom decoder discovery in the Windows installer and PulseView launcher scripts.
- Example capture folders split by topology: bridge, direct inverter/BMS, and bridge forward mode.
- README screenshots for Growatt RS485 Modbus RTU request, response, status, and cell register blocks.

### Changed

- Active decoder set is currently focused on `Growatt RS485` and `JKBMS Modbus` while the other protocols are recaptured/reworked.
- README and regression tests now track the active decoder set.
- Removed stale Pylon raw/session files from `examples/` pending extended recapture.

### Removed

- Removed the previous `Pylon RS485`, `Pylon CAN`, and `Growatt CAN` decoder packages from the active tree pending the next implementation pass.
