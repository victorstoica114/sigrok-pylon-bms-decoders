# Deye CAN Frame Map

Protocol scope: Deye-compatible low-voltage BMS CAN dialect observed in the
JK-BMS bridge captures.

Many frame IDs overlap the Pylon CAN profile, but the field meanings and units
can differ by payload byte.

Payload words are little-endian.

## Deye CAN Frames

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
| `0x356 bytes 4..5` | `pack_temperature` | `i16 le` | `/10` | `C` |
| `0x359 byte 4` | `module_count` | `u8` | `1` | `count` |
| `0x359 bytes 5..7` | `module_tag` | `ascii/raw` | `1` | `text` |
| `0x35C byte 0 bit 7` | `charge_enabled` | `bit` | `1` | `state` |
| `0x35C byte 0 bit 6` | `discharge_enabled` | `bit` | `1` | `state` |
| `0x35C byte 0 bit 5` | `balance_enabled` | `bit` | `1` | `state` |
| `0x35C bytes 0..7` | `status_raw` | `u8[8]` | `1` | `raw` |
| `0x35E bytes 0..7` | `identity` | `ascii/raw` | `1` | `text` |
| `0x370 bytes 0..1` | `temperature_max` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 2..3` | `temperature_min` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 4..5` | `cell_max_mv` | `u16 le` | `/1000` | `V` |
| `0x370 bytes 6..7` | `cell_min_mv` | `u16 le` | `/1000` | `V` |
| `0x371 bytes 0..1` | `temperature_max_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 2..3` | `temperature_min_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 4..5` | `cell_max_idx` | `u16 le` | `1` | `cell index` |
| `0x371 bytes 6..7` | `cell_min_idx` | `u16 le` | `1` | `cell index` |
