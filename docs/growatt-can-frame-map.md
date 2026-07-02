# Growatt CAN Frame Map

Protocol scope: Growatt low-voltage BMS/inverter CAN profile.

The CAN IDs come from the Growatt protocol map. Payload offsets are the bytes
decoded by the Growatt CAN decoder and bridge implementation.

## Growatt CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x211` | `control_event_trigger` | `frame` | `1` | `event` |
| `0x212` | `control_query` | `frame` | `1` | `query` |
| `0x311 bytes 0..1` | `charge_voltage_limit` | `u16 be` | `/10` | `V` |
| `0x311 bytes 2..3` | `charge_current_limit` | `i16 be` | `/10` | `A` |
| `0x311 bytes 4..5` | `discharge_current_limit` | `i16 be` | `/10` | `A` |
| `0x311 byte 6` | `status_flags` | `u8` | `1` | `flags` |
| `0x311 byte 7` | `discharge_status` | `u8` | `1` | `state` |
| `0x312 byte 0` | `protection_flags_1` | `u8 bitfield` | `1` | `flags` |
| `0x312 byte 1` | `protection_flags_2` | `u8 bitfield` | `1` | `flags` |
| `0x312 byte 2` | `alarm_flags_1` | `u8 bitfield` | `1` | `flags` |
| `0x312 byte 3` | `alarm_flags_2` | `u8 bitfield` | `1` | `flags` |
| `0x312 byte 4` | `pack_count` | `u8` | `1` | `count` |
| `0x312 bytes 5..6` | `power_reduce` | `u16 be` | `1` | `raw` |
| `0x312 byte 7` | `cell_count` | `u8` | `1` | `count` |
| `0x313 bytes 0..1` | `pack_voltage` | `u16 be` | `/100` | `V` |
| `0x313 bytes 2..3` | `pack_current` | `i16 be` | `/10` | `A` |
| `0x313 bytes 4..5` | `average_temperature` | `i16 be` | `/10` | `C` |
| `0x313 byte 6` | `soc` | `u8` | `1` | `%` |
| `0x313 byte 7 bits 0..6` | `soh` | `u7` | `1` | `%` |
| `0x313 byte 7 bit 7` | `life_warning` | `bit` | `1` | `flag` |
| `0x314 bytes 0..1` | `remaining_capacity` | `u16 be` | `/100` | `Ah` |
| `0x314 bytes 2..3` | `full_capacity` | `u16 be` | `/100` | `Ah` |
| `0x314 bytes 4..5` | `cell_delta` | `u16 be` | `1` | `mV` |
| `0x314 bytes 6..7` | `cycles` | `u16 be` | `1` | `cycles` |
| `0x315 bytes 0..7` | `cell01_mv..cell04_mv` | `u16 be x4` | `1` | `mV` |
| `0x316 bytes 0..7` | `cell05_mv..cell08_mv` | `u16 be x4` | `1` | `mV` |
| `0x317 bytes 0..7` | `cell09_mv..cell12_mv` | `u16 be x4` | `1` | `mV` |
| `0x318 bytes 0..7` | `cell13_mv..cell16_mv` | `u16 be x4` | `1` | `mV` |
| `0x319 byte 0` | `charge_state_flags` | `u8 bitfield` | `1` | `flags` |
| `0x319 bytes 1..2` | `cell_max_mv` | `u16 be` | `1` | `mV` |
| `0x319 bytes 3..4` | `cell_min_mv` | `u16 be` | `1` | `mV` |
| `0x319 byte 5` | `cell_max_idx` | `u8` | `1` | `cell index` |
| `0x319 byte 6` | `cell_min_idx` | `u8` | `1` | `cell index` |
| `0x320 bytes 0..1` | `maker` | `ascii` | `1` | `text` |
| `0x320 byte 2` | `hardware_version` | `u8` | `1` | `raw` |
| `0x320 byte 3` | `software_version_low` | `u8` | `1` | `raw` |
| `0x320 byte 4` | `software_version_high_ext` | `u8` | `1` | `raw` |
| `0x320 byte 5` | `compatibility` | `u8` | `1` | `raw` |
| `0x320 byte 6` | `extension` | `u8` | `1` | `raw` |
| `0x321 byte 0` | `upgrade_status` | `u8` | `1` | `state` |
| `0x321 byte 1` | `upgrade_progress` | `u8` | `1` | `%` |
| `0x321 byte 2` | `program_status` | `u8` | `1` | `state` |
| `0x322 bytes 0..1` | `temperature_max` | `i16 be` | `/10` | `C` |
| `0x322 bytes 2..3` | `temperature_min` | `i16 be` | `/10` | `C` |
| `0x322 byte 4` | `temperature_max_idx` | `u8` | `1` | `sensor index` |
| `0x322 byte 5` | `temperature_min_idx` | `u8` | `1` | `sensor index` |
| `0x322 byte 6` | `soc_max` | `u8` | `1` | `%` |
| `0x322 byte 7` | `soc_min` | `u8` | `1` | `%` |
| `0x323 byte 0` | `cell_count` | `u8` | `1` | `count` |
| `0x323 byte 4` | `protection_flags_3` | `u8 bitfield` | `1` | `flags` |
| `0x323 byte 5` | `protection_flags_4` | `u8 bitfield` | `1` | `flags` |
| `0x323 byte 6` | `protection_flags_5` | `u8 bitfield` | `1` | `flags` |
| `0x323 byte 7` | `warning_flags_3` | `u8 bitfield` | `1` | `flags` |
| `0x324` | `extension_1` | `frame` | `1` | `raw` |
| `0x325` | `extension_2` | `frame` | `1` | `raw` |
