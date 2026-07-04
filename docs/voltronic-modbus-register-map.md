# Voltronic Modbus Register Map

Protocol: Voltronic Power inverter/BMS RS485 Modbus profile, plus the
JK-007/Voltronic compact runtime map observed by the translator.

This map follows the active `decoders/voltronic_modbus` implementation and the
local source map under `docs/esp32-source-maps/main/protocols/voltronic_modbus`.

- Default slave address: `0x01`
- Supported read functions: `0x03`, `0x04`
- Supported frame prefixes: classic `slave, function` and function-first
  `function, slave`
- Supported response formats: standard byte count, 16-bit byte count, and
  16-bit word count

## Voltronic Public Runtime Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0001` | `protocol_type` | `u16` | `1` | `raw` |
| `0x0002` | `protocol_version` | `u16` | `1` | `raw` |
| `0x0010` | `cell_count` | `u16` | `1` | `cells` |
| `0x0011..0x0024` | `cell01..cell20` | `u16` | `/1000 or normalized` | `V` |
| `0x0025` | `temp_count` | `u16` | `1` | `sensors` |
| `0x0026..0x002F` | `temp01..temp10` | `i16/u16` | `deciK or deciC` | `C` |
| `0x0030` | `charge_current` | `i16` | `/10` | `A` |
| `0x0031` | `discharge_current` | `i16` | `/10` | `A` |
| `0x0032` | `module_voltage` | `u16` | `/10` | `V` |
| `0x0033` | `soc` | `u16` | `1` | `%` |
| `0x0034..0x0035` | `total_capacity` | `u32` | `/1000` | `Ah` |
| `0x0036` | `parallel_packs` | `u16` | `1` | `packs` |
| `0x0037` | `charge_alarm` | `u16 bitfield` | `1` | `flags` |
| `0x0038` | `discharge_alarm` | `u16 bitfield` | `1` | `flags` |
| `0x0039` | `charge_protect` | `u16 bitfield` | `1` | `flags` |
| `0x003A` | `charge_protect2` | `u16 bitfield` | `1` | `flags` |
| `0x003B` | `discharge_protect` | `u16 bitfield` | `1` | `flags` |
| `0x003C` | `discharge_protect2` | `u16 bitfield` | `1` | `flags` |
| `0x003D` | `bms_state` | `u16 bitfield` | `1` | `flags` |
| `0x003E..0x003F` | `design_capacity` | `u32` | `/1000` | `Ah` |
| `0x0040` | `warning_cell_count` | `u16` | `1` | `cells` |
| `0x0041..0x004A` | `cell_state_pair01..cell_state_pair10` | `u16` | `1` | `raw` |
| `0x0050` | `warning_temp_count` | `u16` | `1` | `sensors` |
| `0x0051..0x0055` | `temp_state_pair01..temp_state_pair05` | `u16` | `1` | `raw` |
| `0x0060` | `module_charge_voltage_state` | `u16 bitfield` | `1` | `flags` |
| `0x0061` | `module_discharge_voltage_state` | `u16 bitfield` | `1` | `flags` |
| `0x0062` | `cell_charge_voltage_state` | `u16 bitfield` | `1` | `flags` |
| `0x0063` | `cell_discharge_voltage_state` | `u16 bitfield` | `1` | `flags` |
| `0x0064` | `module_charge_current_state` | `u16 bitfield` | `1` | `flags` |
| `0x0065` | `module_discharge_current_state` | `u16 bitfield` | `1` | `flags` |
| `0x0066` | `module_charge_temperature_state` | `u16 bitfield` | `1` | `flags` |
| `0x0067` | `module_discharge_temperature_state` | `u16 bitfield` | `1` | `flags` |
| `0x0068` | `cell_charge_temperature_state` | `u16 bitfield` | `1` | `flags` |
| `0x0069` | `cell_discharge_temperature_state` | `u16 bitfield` | `1` | `flags` |
| `0x0070` | `charge_voltage_limit` | `u16` | `/10` | `V` |
| `0x0071` | `discharge_voltage_limit` | `u16` | `/10` | `V` |
| `0x0072` | `charge_current_limit` | `i16` | `/10` | `A` |
| `0x0073` | `discharge_current_limit` | `i16` | `/10` | `A` |
| `0x0074` | `charge_discharge_status` | `u16 bitfield` | `1` | `flags` |
| `0x0075` | `runtime_empty` | `u16` | `1` | `min` |
| `0x0076..0x0077` | `remaining_capacity` | `u32` | `/1000` | `Ah` |

## Voltronic JK Runtime Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x106C` | `jk_cell_count` | `u16` | `1` | `cells` |
| `0x106D` | `jk_charge_mos` | `u16` | `1` | `state` |
| `0x106E` | `jk_discharge_mos` | `u16` | `1` | `state` |
| `0x106F` | `jk_balance_active` | `u16` | `1` | `state` |
| `0x1070` | `jk_rated_capacity` | `u16` | `/1000` | `Ah` |
| `0x1200..0x1226`, step `0x0002` | `jk_cell01..jk_cell20` | `u16` | `/1000` | `V` |
| `0x1244` | `jk_cell_avg` | `u16` | `/1000` | `V` |
| `0x1246` | `jk_cell_diff` | `u16` | `1` | `mV` |
| `0x1248` | `jk_cell_idx_raw` | `u16` | `1` | `raw` |
| `0x128A` | `jk_mos_temp` | `i16` | `/10` | `C` |
| `0x1290..0x1291` | `jk_pack_voltage_mV` | `u32` | `/1000` | `V` |
| `0x1294..0x1295` | `jk_pack_power_mW` | `u32` | `/1000` | `W` |
| `0x1298..0x1299` | `jk_pack_current_mA` | `i32` | `/1000` | `A` |
| `0x129C` | `jk_temp1` | `i16` | `/10` | `C` |
| `0x129E` | `jk_temp2` | `i16` | `/10` | `C` |
| `0x12A0..0x12A1` | `jk_alarm` | `u32 bitfield` | `1` | `flags` |
| `0x12A6` | `jk_balance_soc` | `u8x2` | `1` | `state / %` |
| `0x12A8..0x12A9` | `jk_remaining_capacity` | `i32` | `/1000` | `Ah` |
| `0x12AC..0x12AD` | `jk_full_capacity` | `u32` | `/1000` | `Ah` |
| `0x12B0..0x12B1` | `jk_cycles` | `u32` | `1` | `cycles` |
| `0x12B8` | `jk_soh_precharge` | `u8x2` | `1` | `% / state` |

## Voltronic Status Bits

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0074 bit 7` | `charge_enable` | `flag` | `1` | `state` |
| `0x0074 bit 6` | `discharge_enable` | `flag` | `1` | `state` |
| `0x0074 bit 5` | `charge_now` | `flag` | `1` | `state` |
| `0x0074 bit 4` | `charge_now2` | `flag` | `1` | `state` |
| `0x0074 bit 3` | `full_charge_request` | `flag` | `1` | `state` |
