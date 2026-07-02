# Pylon CAN Frame Map

Protocol scope: Pylon-compatible CAN profile, including JK/Pylon extension
frames observed in field captures.

Payload words are little-endian unless a decoder explicitly treats a field as
raw bytes or ASCII.

## Pylon CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x351 bytes 0..1` | `charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x351 bytes 2..3` | `charge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 4..5` | `discharge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 6..7` | `discharge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x355 bytes 0..1` | `soc` | `u16 le` | `1` | `%` |
| `0x355 bytes 2..3` | `soh` | `u16 le` | `1` | `%` |
| `0x356 bytes 0..1` | `pack_voltage` | `u16 le` | `/100` | `V` |
| `0x356 bytes 2..3` | `pack_current` | `i16 le` | `/10` | `A` |
| `0x356 bytes 4..5` | `average_temperature` | `u16 le` | `/10` | `C` |
| `0x359 byte 4` | `module_count` | `u8` | `1` | `count` |
| `0x35A bytes 0..7` | `vendor_info` | `u8[8]` | `1` | `raw` |
| `0x35C byte 0` | `status_flags` | `u8 bitfield` | `1` | `flags` |
| `0x35E bytes 0..7` | `ascii_name` | `ascii` | `1` | `text` |
| `0x370 bytes 0..1` | `temperature_max` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 2..3` | `temperature_min` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 4..5` | `cell_max_mv` | `u16 le` | `1` | `mV` |
| `0x370 bytes 6..7` | `cell_min_mv` | `u16 le` | `1` | `mV` |
| `0x371 bytes 0..1` | `temperature_max_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 2..3` | `temperature_min_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 4..5` | `cell_max_idx` | `u16 le` | `1` | `cell index` |
| `0x371 bytes 6..7` | `cell_min_idx` | `u16 le` | `1` | `cell index` |
| `0x372 bytes 0..7` | `misc_372` | `u8[8]` | `1` | `raw` |
| `0x373 bytes 0..1` | `cell_min_mv` | `u16 le` | `1` | `mV` |
| `0x373 bytes 2..3` | `cell_max_mv` | `u16 le` | `1` | `mV` |
| `0x373 bytes 4..5` | `temperature_1` | `u16 le` | `/10` | `C` |
| `0x373 bytes 6..7` | `temperature_2` | `u16 le` | `/10` | `C` |
| `0x374 bytes 0..7` | `ascii_374` | `ascii` | `1` | `text` |
| `0x375 bytes 0..7` | `ascii_375` | `ascii` | `1` | `text` |
| `0x376 bytes 0..7` | `ascii_376` | `ascii` | `1` | `text` |
| `0x377 bytes 0..7` | `ascii_377` | `ascii` | `1` | `text` |
| `0x379 bytes 0..7` | `misc_379` | `u8[8]` | `1` | `raw` |
