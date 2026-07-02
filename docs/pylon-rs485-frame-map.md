# Pylon RS485 Frame Map

Protocol scope: Pylon-compatible ASCII protocol over UART/RS485.

This is not a Modbus register map. Frames carry ASCII hex fields with a CID2
command and an INFO payload.

## Pylon RS485 Frame Envelope

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `frame start` | `start_marker` | `ascii` | `1` | `marker` |
| `VER` | `protocol_version` | `hex byte` | `1` | `raw` |
| `ADR` | `address` | `hex byte` | `1` | `address` |
| `CID1` | `command_group` | `hex byte` | `1` | `raw` |
| `CID2` | `command` | `hex byte` | `1` | `command` |
| `LENGTH` | `info_length` | `hex field` | `1` | `nibbles` |
| `INFO` | `info_payload` | `ascii hex` | `1` | `bytes` |
| `CHKSUM` | `checksum` | `hex word` | `1` | `checksum` |
| `frame end` | `end_marker` | `ascii` | `1` | `marker` |

## Pylon RS485 INFO Fields

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `CID2 0x42 INFO[0]` | `pack_count_or_cell_count` | `u8` | `1` | `count` |
| `CID2 0x42 INFO[...]` | `cell_voltage_list` | `u16 be[]` | `1` | `mV` |
| `CID2 0x42 INFO[...]` | `temperature_list` | `u16 be[]` | `1` | `raw` |
| `CID2 0x61 INFO[0..1]` | `pack_voltage` | `u16 be` | `/100` | `V` |
| `CID2 0x61 INFO[2..3]` | `pack_current` | `i16 be` | `/10` | `A` |
| `CID2 0x61 INFO[4]` | `soc` | `u8` | `1` | `%` |
| `CID2 0x61 INFO[5..6]` | `cycles` | `u16 be` | `1` | `cycles` |
| `CID2 0x61 INFO[9]` | `soh` | `u8` | `1` | `%` |
| `CID2 0x61 INFO[11..12]` | `cell_max_mv` | `u16 be` | `1` | `mV` |
| `CID2 0x61 INFO[13..14]` | `cell_max_idx` | `u16 be` | `1` | `cell index` |
| `CID2 0x61 INFO[15..16]` | `cell_min_mv` | `u16 be` | `1` | `mV` |
| `CID2 0x61 INFO[17..18]` | `cell_min_idx` | `u16 be` | `1` | `cell index` |
| `CID2 0x61 INFO[19..20]` | `temp_mos` | `u16 be` | `-2731 then /10` | `C` |
| `CID2 0x61 INFO[21..22]` | `temp_t1` | `u16 be` | `-2731 then /10` | `C` |
| `CID2 0x61 INFO[25..26]` | `temp_t2` | `u16 be` | `-2731 then /10` | `C` |
| `CID2 0x61 INFO[29..30]` | `temp_t4` | `u16 be` | `-2731 then /10` | `C` |
| `CID2 0x61 INFO[31..32]` | `temp_t5` | `u16 be` | `-2731 then /10` | `C` |
| `CID2 0x62 INFO[0..7]` | `status_block` | `u8[8]` | `1` | `raw` |
| `CID2 0x63 INFO[8]` | `status_flags` | `u8 bitfield` | `1` | `flags` |

## Pylon RS485 Supplemental Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `CID2 0x4F INFO[0]` | `protocol_marker` | `u8` | `1` | `raw` |
| `CID2 0x51 INFO[0..9]` | `device_name` | `ascii` | `1` | `text` |
| `CID2 0x51 INFO[10]` | `protocol_revision` | `ascii` | `1` | `text` |
| `CID2 0x51 INFO[11..30]` | `manufacturer` | `ascii` | `1` | `text` |
| `CID2 0x92 INFO[0..1]` | `charge_voltage_limit` | `u16 be` | `/100` | `V` |
| `CID2 0x92 INFO[2..3]` | `minimum_pack_voltage` | `u16 be` | `/100` | `V` |
| `CID2 0x92 INFO[4..5]` | `charge_current_limit` | `u16 be` | `/10` | `A` |
| `CID2 0x92 INFO[6..7]` | `discharge_current_limit` | `u16 be` | `/10` | `A` |
| `CID2 0x92 INFO[8]` | `status_flags` | `u8 bitfield` | `1` | `flags` |
| `CID2 0x44 INFO[0..7]` | `reserved_status` | `u8[8]` | `1` | `raw` |
| `CID2 0x47 INFO[0..23]` | `limits_block` | `u16 be[]` | `mixed` | `raw` |
| `CID2 0x60 INFO[0..9]` | `battery_name` | `ascii` | `1` | `text` |
| `CID2 0x60 INFO[10..29]` | `manufacturer` | `ascii` | `1` | `text` |
| `CID2 0x60 INFO[30..31]` | `model_revision` | `ascii` | `1` | `text` |
