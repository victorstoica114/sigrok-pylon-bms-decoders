# Sofar CAN Frame Map

Protocol scope: Sofar-compatible low-voltage BMS frames over Classic CAN.

Payload fields are little-endian. This map follows the active
`decoders/sofar_can` implementation.

## Sofar CAN Frames

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
| `0x359 bytes 0..7` | `module_info` | `u8[8]` | `mixed` | `raw / text` |
| `0x35C bytes 0..7` | `status` | `u8[8]` | `1` | `flags / raw` |
| `0x35E bytes 0..7` | `brand` | `ascii/u8[8]` | `1` | `text / raw` |
| `0x35F bytes 0..7` | `module_raw` | `ascii/u16 le[4]` | `1` | `text / raw` |
| `0x370 bytes 0..1` | `temperature_max` | `u16 le` | `mixed` | `C` |
| `0x370 bytes 2..3` | `temperature_min` | `u16 le` | `mixed` | `C` |
| `0x370 bytes 4..5` | `cell_voltage_max` | `u16 le` | `/1000` | `V` |
| `0x370 bytes 6..7` | `cell_voltage_min` | `u16 le` | `/1000` | `V` |
| `0x371 bytes 0..1` | `temperature_max_sensor` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 2..3` | `temperature_min_sensor` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 4..5` | `cell_voltage_max_index` | `u16 le` | `1` | `cell index` |
| `0x371 bytes 6..7` | `cell_voltage_min_index` | `u16 le` | `1` | `cell index` |
