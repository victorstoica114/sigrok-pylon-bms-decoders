# Changelog

## Current

### Added

- PulseView/libsigrokdecode `Growatt CAN` decoder for Growatt low-voltage Classic CAN frames.
- PulseView/libsigrokdecode `Growatt RS485` decoder for Growatt Modbus RTU frames.
- PulseView/libsigrokdecode `JKBMS Modbus v2026.07.02b` decoder for validated JK BMS RS485 Modbus RTU runtime frames.
- PulseView/libsigrokdecode `JKBMS CAN v2026.07.03a` decoder for validated JK BMS native CAN V2.0 frames.
- Growatt CAN, Growatt RS485, JKBMS CAN, and JKBMS Modbus protocol map documentation.
- Windows installer and launcher scripts that keep built-in PulseView decoders visible alongside custom BMS decoders.
- Host-side parser/decoder regression tests for the active decoder set.
- Example capture folders split by topology: bridge, direct inverter/BMS, and bridge forward mode.
- Bridge-mode example capture and PulseView session for JKBMS Modbus RS485 runtime polling.
- README screenshots for Growatt RS485 Modbus RTU request, response, status, and cell register blocks.
- README screenshots for JKBMS CAN pack status, cell extremes, temperature, capacity, and raw info/status frames.
- README screenshots for JKBMS Modbus RTU request and runtime register response blocks.

### Changed

- Active decoder set is currently limited to validated decoders: `Growatt CAN`, `Growatt RS485`, `JKBMS CAN`, and `JKBMS Modbus`.
- Repository rule clarified: decoders still under field test stay out of `decoders/` until they are validated and explicitly promoted.
- README and regression tests now track only the active decoder folders.
- The installer rebuilds `C:\ProgramData\libsigrokdecode\decoders` from built-ins plus active repository decoders, excluding stale custom decoder copies from PulseView's built-in directory.

### Removed

- Removed stale Pylon decoder packages from the active tree pending the next validated implementation pass.

