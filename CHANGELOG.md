# Changelog

## Current

### Added

- PulseView/libsigrokdecode `China Tower Modbus v2026.07.03a` decoder for validated China Tower / JK 008 RS485 Modbus RTU frames.
- PulseView/libsigrokdecode `Deye CAN v2026.07.03a` decoder for validated Deye-compatible low-voltage CAN frames.
- PulseView/libsigrokdecode `GoodWe CAN v2026.07.03a` decoder for validated GoodWe-compatible low-voltage CAN frames.
- PulseView/libsigrokdecode `Growatt CAN` decoder for Growatt low-voltage Classic CAN frames.
- PulseView/libsigrokdecode `Growatt RS485` decoder for Growatt Modbus RTU frames.
- PulseView/libsigrokdecode `JKBMS Modbus v2026.07.02b` decoder for validated JK BMS RS485 Modbus RTU runtime frames.
- PulseView/libsigrokdecode `JKBMS CAN v2026.07.03a` decoder for validated JK BMS native CAN V2.0 frames.
- PulseView/libsigrokdecode `PACE Modbus v2026.07.04a` decoder for validated PACE BMS RS485 Modbus V1.3 frames.
- PulseView/libsigrokdecode `Pylon CAN v2026.07.03a` decoder for validated Pylon-compatible low-voltage CAN frames.
- PulseView/libsigrokdecode `Pylon RS485 v2026.07.03a` decoder for validated Pylon-compatible RS485 ASCII frames.
- PulseView/libsigrokdecode `SMA CAN v2026.07.04a` decoder for validated SMA Sunny Island compatible low-voltage CAN frames.
- PulseView/libsigrokdecode `Victron CAN v2026.07.03a` decoder for validated Victron-compatible low-voltage CAN frames.
- China Tower Modbus, Deye CAN, GoodWe CAN, Growatt CAN, Growatt RS485, JKBMS CAN, JKBMS Modbus, PACE Modbus, Pylon CAN, Pylon RS485, SMA CAN, and Victron CAN protocol map documentation.
- Windows installer and launcher scripts that keep built-in PulseView decoders visible alongside custom BMS decoders.
- Host-side parser/decoder regression tests for the active decoder set.
- Example capture folders split by topology: bridge, direct inverter/BMS, and bridge forward mode.
- Bridge-mode example capture and PulseView session for China Tower / JK 008 RS485 traffic.
- Bridge-mode example capture and PulseView session for Deye CAN traffic.
- Bridge-mode example capture and PulseView session for GoodWe CAN traffic.
- Bridge-mode example capture and PulseView session for JKBMS CAN traffic.
- Bridge-mode example capture and PulseView session for PACE Modbus RS485 traffic.
- Bridge-mode example capture and PulseView session for Pylon CAN traffic.
- Bridge-mode example capture and PulseView session for Pylon RS485 ASCII traffic.
- Bridge-mode example capture and PulseView session for SMA CAN traffic.
- Bridge-mode example capture and PulseView session for Victron CAN traffic.
- README screenshots for Deye CAN SOC/SOH, pack telemetry, status, identity, and cell extreme frames.
- README screenshots for China Tower Modbus request, status, runtime, and cell register blocks.
- README screenshots for GoodWe CAN limits, SOC/SOH, pack telemetry, and module info frames.
- README screenshots for Growatt RS485 Modbus RTU request, response, status, and cell register blocks.
- README screenshots for JKBMS CAN pack status, cell extremes, temperature, capacity, and raw info/status frames.
- README screenshots for PACE Modbus runtime, cell-voltage, and temperature register blocks.
- README screenshots for Pylon CAN limits, SOC/SOH, pack telemetry, module info, status, identity, and cell extreme frames.
- README screenshots for Pylon RS485 analog telemetry, cell request, alarm/status flags, and charge/discharge status frames.
- README screenshots for SMA CAN limits, pack telemetry, vendor, manufacturer, and battery info frames.
- README screenshots for Victron CAN limits, SOC/SOH, pack telemetry, and vendor raw frames.

### Changed

- Active decoder set is currently limited to validated decoders: `China Tower Modbus`, `Deye CAN`, `GoodWe CAN`, `Growatt CAN`, `Growatt RS485`, `JKBMS CAN`, `JKBMS Modbus`, `PACE Modbus`, `Pylon CAN`, `Pylon RS485`, `SMA CAN`, and `Victron CAN`.
- Updated bridge-mode example capture and PulseView session for Growatt RS485 inverter traffic.
- Updated README screenshots for Growatt RS485 cell-voltage, status/pack telemetry, and limits/cell-extreme response blocks.
- Updated bridge-mode example capture and PulseView session for JKBMS Modbus RS485 runtime polling.
- Updated README screenshots for JKBMS Modbus RTU request, cell, cell-summary, SOC/SOH, and runtime register response blocks.
- Repository rule clarified: decoders still under field test stay out of `decoders/` until they are validated and explicitly promoted.
- README and regression tests now track only the active decoder folders.
- The installer rebuilds `C:\ProgramData\libsigrokdecode\decoders` from built-ins plus active repository decoders, excluding stale custom decoder copies from PulseView's built-in directory.

