# WOW Modbus Register Map

Protocol: WOW / JK 009 BMS RS485 Modbus RTU.

The WOW decoder follows the PACE-compatible V1.3 register layout used by the
firmware poller. Source map:
`docs/esp32-source-maps/main/protocols/pace_modbus/pace_modbus_registers_map.h`
and `docs/esp32-source-maps/main/protocols/pace_modbus/pace_modbus_registers_map.c`.

- Default slave address: `0x01`
- Supported read functions: `0x03`, `0x04`
- Poll blocks: `0x0000` count `0x000D`, `0x000F` count `0x0016`

## WOW Modbus Runtime Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0000` | `pack_current_10mA` | `i16` | `/100` | `A` |
| `0x0001` | `pack_voltage_10mV` | `u16` | `/100` | `V` |
| `0x0002` | `soc` | `u16 packed` | `1` | `%` |
| `0x0003` | `soh` | `u16 packed` | `1` | `%` |
| `0x0004` | `remaining_capacity_10mAh` | `u16` | `/100` | `Ah` |
| `0x0005` | `full_capacity_10mAh` | `u16` | `/100` | `Ah` |
| `0x0006` | `design_capacity_10mAh` | `u16` | `/100` | `Ah` |
| `0x0007` | `cycle_count` | `u16` | `1` | `cycles` |
| `0x0008` | `runtime_raw_0008` | `u16` | `1` | `raw` |
| `0x0009` | `warning_flags` | `u16 bitfield` | `1` | `flags` |
| `0x000A` | `protection_flags` | `u16 bitfield` | `1` | `flags` |
| `0x000B` | `status_flags` | `u16 bitfield` | `1` | `flags` |
| `0x000C` | `balance_status` | `u16 bitfield` | `1` | `flags` |
| `0x000F..0x001E` | `cell01_mv..cell16_mv` | `u16` | `/1000` | `V` |
| `0x001F` | `temp1_deciC` | `i16` | `/10` | `C` |
| `0x0020` | `temp2_deciC` | `i16` | `/10` | `C` |
| `0x0021` | `temp3_deciC` | `i16` | `/10` | `C` |
| `0x0022` | `temp4_deciC` | `i16` | `/10` | `C` |
| `0x0023` | `mos_temp_deciC` | `i16` | `/10` | `C` |
| `0x0024` | `env_temp_deciC` | `i16` | `/10` | `C` |

## WOW Modbus Status Bits

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x000B bit 8` | `charge` | `flag` | `1` | `state` |
| `0x000B bit 9` | `discharge` | `flag` | `1` | `state` |
| `0x000B bit 10` | `charge_mos` | `flag` | `1` | `state` |
| `0x000B bit 11` | `discharge_mos` | `flag` | `1` | `state` |
