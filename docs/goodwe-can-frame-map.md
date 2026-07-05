# GoodWe CAN Frame Map

Protocol scope: GoodWe-compatible low-voltage BMS CAN frames, including the
JK/Pylon compatibility dialect observed in the current GoodWe bridge capture.

This map documents the native GoodWe `0x453..0x458` frames. The PulseView
decoder also recognizes the JK/Pylon-compatible `0x351..0x371` frames used by
the validated capture.

Payload words are little-endian.

## GoodWe CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x351 bytes 0..1` | `jk_pylon_charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x351 bytes 2..3` | `jk_pylon_charge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 4..5` | `jk_pylon_discharge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 6..7` | `jk_pylon_discharge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x355 bytes 0..1` | `jk_pylon_soc` | `u16 le` | `1` | `%` |
| `0x355 bytes 2..3` | `jk_pylon_soh` | `u16 le` | `1` | `%` |
| `0x356 bytes 0..1` | `jk_pylon_pack_voltage` | `u16 le` | `/100` | `V` |
| `0x356 bytes 2..3` | `jk_pylon_pack_current` | `i16 le` | `/10` | `A` |
| `0x356 bytes 4..5` | `jk_pylon_pack_temperature` | `i16 le` | `/10` | `C` |
| `0x359 byte 4` | `jk_pylon_module_count` | `u8` | `1` | `count` |
| `0x359 bytes 5..7` | `jk_pylon_module_tag` | `ascii/raw` | `1` | `text` |
| `0x35C byte 0 bit 7` | `jk_pylon_charge_enabled` | `bit` | `1` | `state` |
| `0x35C byte 0 bit 6` | `jk_pylon_discharge_enabled` | `bit` | `1` | `state` |
| `0x35C byte 0 bit 5` | `jk_pylon_balance_enabled` | `bit` | `1` | `state` |
| `0x35C bytes 0..7` | `jk_pylon_status_raw` | `u8[8]` | `1` | `raw` |
| `0x35E bytes 0..7` | `jk_pylon_identity` | `ascii/raw` | `1` | `text` |
| `0x370 bytes 0..1` | `jk_pylon_temperature_max` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 2..3` | `jk_pylon_temperature_min` | `u16 le` | `raw or /10` | `C` |
| `0x370 bytes 4..5` | `jk_pylon_cell_max_mv` | `u16 le` | `/1000` | `V` |
| `0x370 bytes 6..7` | `jk_pylon_cell_min_mv` | `u16 le` | `/1000` | `V` |
| `0x371 bytes 0..1` | `jk_pylon_temperature_max_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 2..3` | `jk_pylon_temperature_min_sensor_idx` | `u16 le` | `1` | `sensor index` |
| `0x371 bytes 4..5` | `jk_pylon_cell_max_idx` | `u16 le` | `1` | `cell index` |
| `0x371 bytes 6..7` | `jk_pylon_cell_min_idx` | `u16 le` | `1` | `cell index` |
| `0x453 bytes 0..7` | `goodwe_modules_raw` | `u8[8]` | `1` | `raw` |
| `0x455 bytes 0..7` | `goodwe_alarms_raw` | `u8[8]` | `1` | `raw` |
| `0x456 bytes 0..1` | `goodwe_charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x456 bytes 2..3` | `goodwe_charge_current_limit` | `i16 le` | `/10` | `A` |
| `0x456 bytes 4..5` | `goodwe_discharge_current_limit` | `i16 le` | `/10` | `A` |
| `0x456 bytes 6..7` | `goodwe_discharge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x457 bytes 0..1` | `goodwe_soc` | `u16 le` | `/10` | `%` |
| `0x457 bytes 2..3` | `goodwe_soh` | `u16 le` | `/10` | `%` |
| `0x458 bytes 0..1` | `goodwe_pack_voltage` | `u16 le` | `/10` | `V` |
| `0x458 bytes 2..3` | `goodwe_pack_current` | `i16 le` | `/10` | `A` |
| `0x458 bytes 4..5` | `goodwe_pack_temperature` | `i16 le` | `/10` | `C` |
