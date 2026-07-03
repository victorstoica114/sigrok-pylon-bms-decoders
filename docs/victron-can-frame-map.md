# Victron CAN Frame Map

Protocol scope: Victron-compatible low-voltage BMS CAN profile as emitted by
the Seplos/Victron bridge profile.

The observed payload is little-endian and follows a shared low-voltage BMS CAN
layout.

## Victron CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x351 bytes 0..1` | `charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x351 bytes 2..3` | `charge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 4..5` | `discharge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 6..7` | `discharge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x355 bytes 0..1` | `soc` | `u16 le` | `1` | `%` |
| `0x355 bytes 2..3` | `soh` | `u16 le` | `1` | `%` |
| `0x355 bytes 4..7` | `soc_soh_tail_raw` | `u8[4]` | `1` | `raw` |
| `0x356 bytes 0..1` | `pack_voltage` | `u16 le` | `/100` | `V` |
| `0x356 bytes 2..3` | `pack_current` | `i16 le` | `/10` | `A` |
| `0x356 bytes 4..5` | `pack_temperature` | `i16 le` | `/10` | `C` |
| `0x356 bytes 6..7` | `pack_tail_raw` | `u8[2]` | `1` | `raw` |
| `0x359 bytes 0..7` | `alarms_status_raw` | `u8[8]` | `1` | `raw` |
| `0x35A bytes 0..7` | `vendor_raw` | `u8[8]` | `1` | `raw` |
| `0x35E bytes 0..7` | `manufacturer` | `ascii/raw` | `1` | `text` |
| `0x35F bytes 0..7` | `battery_raw_words` | `u16 le x4` | `1` | `raw` |
| `0x360 bytes 0..7` | `status_raw` | `u8[8]` | `1` | `raw` |
| `0x370 bytes 0..7` | `ascii_or_raw_370` | `ascii/raw` | `1` | `text` |
| `0x371 bytes 0..7` | `raw_371` | `u8[8]` | `1` | `raw` |
| `0x372 bytes 0..7` | `raw_372` | `u8[8]` | `1` | `raw` |
| `0x373 bytes 0..1` | `cell_min_mv_candidate` | `u16 le` | `/1000` | `V` |
| `0x373 bytes 2..3` | `cell_max_mv_candidate` | `u16 le` | `/1000` | `V` |
| `0x373 bytes 4..5` | `temperature_1_candidate` | `u16 le` | `raw or /10` | `C` |
| `0x373 bytes 6..7` | `temperature_2_candidate` | `u16 le` | `raw or /10` | `C` |
| `0x374 bytes 0..7` | `ascii_segment_374` | `ascii/raw` | `1` | `text` |
| `0x375 bytes 0..7` | `ascii_segment_375` | `ascii/raw` | `1` | `text` |
| `0x376 bytes 0..7` | `ascii_segment_376` | `ascii/raw` | `1` | `text` |
| `0x377 bytes 0..7` | `ascii_segment_377` | `ascii/raw` | `1` | `text` |
| `0x378 bytes 0..7` | `raw_378` | `u8[8]` | `1` | `raw` |
| `0x379 bytes 0..7` | `raw_379` | `u8[8]` | `1` | `raw` |
| `0x380 bytes 0..7` | `ascii_segment_380` | `ascii/raw` | `1` | `text` |
| `0x381 bytes 0..7` | `ascii_segment_381` | `ascii/raw` | `1` | `text` |
