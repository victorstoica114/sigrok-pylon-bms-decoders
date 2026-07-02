# Changelog

## Current

### Added

- Standalone PulseView/libsigrokdecode `Pylon CAN` decoder for Pylon-compatible Classic CAN frames.
- PulseView/libsigrokdecode `Pylon RS485` decoder for Pylon-compatible ASCII UART/RS485 frames.
- Pylon CAN input modes for transceiver `RXD`, digitized `CANL`, digitized inverted `CANH`, and digitized `CANH/CANL` captures.
- Windows installer and launcher scripts that keep built-in PulseView decoders visible alongside custom BMS decoders.
- Host-side parser/decoder regression tests.
- README capture examples for decoded Pylon CAN and Pylon RS485 frames.
- Example raw `.sr` captures and matching PulseView `.pvs` sessions for Growatt CAN and Growatt RS485.
- Standalone PulseView/libsigrokdecode `Growatt CAN` decoder for Growatt low-voltage BMS/inverter frames.
- PulseView/libsigrokdecode `Growatt RS485` decoder for Growatt Modbus RTU frames.
- README screenshots for Growatt CAN.
- Automatic custom decoder discovery in the Windows installer and PulseView launcher scripts.
- Example capture folders split by topology: bridge, direct inverter/BMS, and bridge forward mode.
- README screenshots for Growatt RS485 Modbus RTU request, response, status, and cell register blocks.

### Changed

- Removed stale Pylon raw/session files from `examples/` pending extended recapture.
