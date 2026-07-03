# JKBMS CAN Frame Map

Protocol scope: JK BMS native CAN V2.0 profile over Classic CAN.

The ESP32 source map defines the observed JK CAN IDs with node suffix `0x4`.
The PulseView decoder normalizes the low CAN ID nibble so the same command can
be decoded when the node suffix changes.

Payload words are little-endian.

## JKBMS CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x02F4 bytes 0..1` | `pack_voltage` | `u16 le` | `/10` | `V` |
| `0x02F4 bytes 2..3` | `pack_current` | `u16 le` | `/10 - 400` | `A` |
| `0x02F4 byte 4` | `soc` | `u8` | `1` | `%` |
| `0x02F4 bytes 6..7` | `discharge_time` | `u16 le` | `1` | `h` |
| `0x04F4 bytes 0..1` | `cell_max_mv` | `u16 le` | `1` | `mV` |
| `0x04F4 byte 2` | `cell_max_idx` | `u8` | `1` | `cell index` |
| `0x04F4 bytes 3..4` | `cell_min_mv` | `u16 le` | `1` | `mV` |
| `0x04F4 byte 5` | `cell_min_idx` | `u8` | `1` | `cell index` |
| `0x05F4 byte 0` | `temperature_max` | `u8` | `-50` | `C` |
| `0x05F4 byte 1` | `temperature_max_idx` | `u8` | `1` | `sensor index` |
| `0x05F4 byte 2` | `temperature_min` | `u8` | `-50` | `C` |
| `0x05F4 byte 3` | `temperature_min_idx` | `u8` | `1` | `sensor index` |
| `0x05F4 byte 4` | `temperature_avg` | `u8` | `-50` | `C` |
| `0x07F4 bytes 0..3` | `alarm_severity_map` | `u32 le bitfield` | `2 bits per alarm` | `level` |
| `0x18E028F4 bytes 0..7` | `cell01_mv..cell04_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E128F4 bytes 0..7` | `cell05_mv..cell08_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E228F4 bytes 0..7` | `cell09_mv..cell12_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E328F4 bytes 0..7` | `cell13_mv..cell16_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E428F4 bytes 0..7` | `cell17_mv..cell20_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E528F4 bytes 0..7` | `cell21_mv..cell24_mv` | `u16 le x4` | `/1000` | `V` |
| `0x18E628F4 bytes 0..1` | `cell25_mv` | `u16 le` | `/1000` | `V` |
| `0x18F128F4 bytes 0..1` | `remaining_capacity` | `u16 le` | `/10` | `Ah` |
| `0x18F128F4 bytes 2..3` | `rated_capacity` | `u16 le` | `/10` | `Ah` |
| `0x18F128F4 bytes 4..5` | `capacity_reserved` | `u16 le` | `1` | `raw` |
| `0x18F128F4 bytes 6..7` | `cycles` | `u16 le` | `1` | `cycles` |
| `0x18F228F4 byte 0` | `temperature_mask` | `u8 bitfield` | `1` | `flags` |
| `0x18F228F4 bytes 1..5` | `temperature_1..temperature_5` | `u8 x5` | `-50` | `C` |
| `0x18F328F4 bytes 0..7` | `extended_alarms_raw` | `u8[8]` | `1` | `raw` |
| `0x18F428F4 bytes 0..7` | `bms_info_raw` | `u8[8]` | `1` | `raw` |
| `0x18F528F4 bytes 0..7` | `bms_status_raw` | `u8[8]` | `1` | `raw` |
| `0x1806E5F4 bytes 0..1` | `charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x1806E5F4 bytes 2..3` | `charge_current_limit` | `u16 le` | `/10` | `A` |
| `0x1806E5F4 bytes 4..7` | `charge_info_reserved` | `u8[4]` | `1` | `raw` |
