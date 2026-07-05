# Daly RS485 Frame and Register Map

Protocol scope: Daly BMS native RS485 frames and Daly Modbus RTU polling.

This map follows the active `decoders/daly_rs485` implementation.

- Native frame length: `13` bytes
- Native start byte: `0xA5`
- Native BMS address: `0x01`
- Native request addresses: `0x40`, `0x80`
- Modbus request addresses: `0x81`, `0xD2`
- Observed Modbus response address: `0x51`
- Modbus function: `0x03`
- Modbus poll blocks: `0x0000` count `0x007F`, `0x0100` count `0x0078`

## Daly Native Frame Envelope

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `byte 0` | `start_marker` | `u8` | `1` | `raw` |
| `byte 1` | `address` | `u8` | `1` | `address` |
| `byte 2` | `command` | `u8` | `1` | `command` |
| `byte 3` | `payload_length` | `u8` | `1` | `bytes` |
| `bytes 4..11` | `payload` | `u8[8]` | `1` | `raw` |
| `byte 12` | `checksum` | `sum8` | `1` | `checksum` |

## Daly Native Command Payloads

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `cmd 0x50 data[0..3]` | `rated_capacity` | `u32 be` | `/1000` | `Ah` |
| `cmd 0x53 data[0..7]` | `battery_type_info` | `u8[8]` | `1` | `raw` |
| `cmd 0x5A data[0..1]` | `max_pack_voltage` | `u16 be` | `/10` | `V` |
| `cmd 0x5A data[4..5]` | `min_pack_voltage` | `u16 be` | `/10` | `V` |
| `cmd 0x5B data[0..7]` | `current_limits` | `u8[8]` | `1` | `raw` |
| `cmd 0x90 data[0..1]` | `pack_voltage` | `u16 be` | `/10` | `V` |
| `cmd 0x90 data[4..5]` | `pack_current` | `u16 be offset` | `-30000 then /10` | `A` |
| `cmd 0x90 data[6..7]` | `soc` | `u16 be` | `/10` | `%` |
| `cmd 0x91 data[0..1]` | `cell_max_mv` | `u16 be` | `/1000` | `V` |
| `cmd 0x91 data[2]` | `cell_max_index` | `u8` | `1` | `cell index` |
| `cmd 0x91 data[3..4]` | `cell_min_mv` | `u16 be` | `/1000` | `V` |
| `cmd 0x91 data[5]` | `cell_min_index` | `u8` | `1` | `cell index` |
| `cmd 0x92 data[0]` | `temp_max` | `u8 offset` | `-40` | `C` |
| `cmd 0x92 data[1]` | `temp_max_index` | `u8` | `1` | `sensor index` |
| `cmd 0x92 data[2]` | `temp_min` | `u8 offset` | `-40` | `C` |
| `cmd 0x92 data[3]` | `temp_min_index` | `u8` | `1` | `sensor index` |
| `cmd 0x93 data[0]` | `protocol_state` | `u8` | `1` | `state` |
| `cmd 0x93 data[1]` | `charge_enabled` | `u8 flag` | `1` | `state` |
| `cmd 0x93 data[2]` | `discharge_enabled` | `u8 flag` | `1` | `state` |
| `cmd 0x93 data[4..7]` | `remaining_capacity` | `u32 be` | `/1000` | `Ah` |
| `cmd 0x94 data[0]` | `cell_count` | `u8` | `1` | `count` |
| `cmd 0x94 data[1]` | `temp_count` | `u8` | `1` | `count` |
| `cmd 0x94 data[2]` | `charge_enabled` | `u8 flag` | `1` | `state` |
| `cmd 0x94 data[3]` | `discharge_enabled` | `u8 flag` | `1` | `state` |
| `cmd 0x94 data[5..6]` | `cycle_count` | `u16 be` | `1` | `cycles` |
| `cmd 0x95 data[0]` | `cell_voltage_frame_no` | `u8` | `1` | `frame` |
| `cmd 0x95 data[1..6]` | `cell_voltage_triplet` | `u16 be[3]` | `/1000` | `V` |
| `cmd 0x96 data[0]` | `temperature_frame_no` | `u8` | `1` | `frame` |
| `cmd 0x96 data[1..7]` | `temperature_list` | `u8[7] offset` | `-40` | `C` |
| `cmd 0x97 data[0..5]` | `balance_mask` | `u48 be` | `1` | `flags` |
| `cmd 0x98 data[0..3]` | `alarm_mask` | `u32 be` | `1` | `flags` |
| `cmd 0x98 data[4..6]` | `warning_mask` | `u24 be` | `1` | `flags` |

## Daly Modbus Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0000..0x001F` | `cell01_mv..cell32_mv` | `u16` | `/1000` | `V` |
| `0x0030` | `temp_sensor1_raw` | `u16 offset` | `-40` | `C` |
| `0x0031` | `temp_sensor2_raw` | `u16 offset` | `-40` | `C` |
| `0x0032` | `temp_sensor3_raw` | `u16 offset` | `-40` | `C` |
| `0x0033` | `temp_sensor4_raw` | `u16 offset` | `-40` | `C` |
| `0x003A` | `soc_deci_pct` | `u16` | `/10` | `%` |
| `0x003D` | `temp_sensor_count` | `u16` | `1` | `count` |
| `0x005A` | `mos_temp_raw` | `u16 offset` | `-40` | `C` |
| `0x0100..0x0177` | `extended_info_block` | `u16[]` | `mixed` | `raw` |
