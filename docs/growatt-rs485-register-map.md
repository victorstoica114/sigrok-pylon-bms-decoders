# Growatt RS485 Register Map

Protocol scope: Growatt Modbus RTU BMS/inverter profile over RS485.

- Default slave address: `0x01`
- Supported read functions: `0x03`, `0x04`

## Growatt RS485 Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0001..0x000F` | `device_info` | `u16[]` | `1` | `raw` |
| `0x0013` | `status_flags` | `u16 bitfield` | `1` | `flags` |
| `0x0014` | `error_or_protection_code` | `u16 bitfield` | `1` | `flags` |
| `0x0015` | `soc` | `u16` | `1` | `%` |
| `0x0016` | `pack_voltage` | `u16` | `/100` | `V` |
| `0x0017` | `pack_current_abs` | `u16` | `/100` | `A` |
| `0x0018` | `pack_temperature` | `i16` | `1` | `C` |
| `0x0019` | `max_charge_discharge_current` | `u16` | `/100` | `A` |
| `0x001A` | `remaining_capacity` | `u16` | `/100` | `Ah` |
| `0x001B` | `full_capacity` | `u16` | `/100` | `Ah` |
| `0x001E` | `cycles` | `u16` | `1` | `cycles` |
| `0x0020` | `soh` | `u16` | `1` | `%` |
| `0x0021` | `charge_voltage_target` | `u16` | `/100` | `V` |
| `0x0022` | `warning_code` | `u16 bitfield` | `1` | `flags` |
| `0x0023` | `discharge_current_limit` | `u16` | `/100` | `A` |
| `0x0024` | `extended_error_code` | `u16 bitfield` | `1` | `flags` |
| `0x0025` | `cell_max_mv` | `u16` | `1` | `mV` |
| `0x0026` | `cell_min_mv` | `u16` | `1` | `mV` |
| `0x0027` | `cell_max_idx` | `u16` | `1` | `cell index` |
| `0x0028` | `cell_min_idx` | `u16` | `1` | `cell index` |
| `0x0070` | `cell_header` | `u16` | `1` | `raw` |
| `0x0071..0x0080` | `cell01_mv..cell16_mv` | `u16[]` | `1` | `mV` |

## Growatt RS485 Poll Blocks

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0001..0x000F` | `device_info_poll` | `u16[15]` | `1` | `raw` |
| `0x0010..0x0017` | `main_status_poll_1` | `u16[8]` | `1` | `raw` |
| `0x0018..0x001F` | `main_status_poll_2` | `u16[8]` | `1` | `raw` |
| `0x0020..0x002A` | `main_status_poll_3` | `u16[11]` | `1` | `raw` |
| `0x0071..0x0080` | `cell_voltage_poll` | `u16[16]` | `1` | `mV` |
