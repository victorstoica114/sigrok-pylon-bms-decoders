# JKBMS Modbus Register Map

Protocol: Ji Kong BMS RS485 Modbus Universal Protocol V1.1.

This map is limited to the runtime register area used by
`decoders/jkbms_modbus` for the current Growatt/JKBMS bridge tests.

- Default slave address: `0x01`
- Supported read functions: `0x03`, `0x04`
- Runtime base: `0x1200`

## JKBMS Modbus Runtime Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x1200..0x123E`, step `0x0002` | `cell01_mv..cell32_mv` | `u16` | `/1000` | `V` |
| `0x1244` | `cell_avg_mv` | `u16` | `/1000` | `V` |
| `0x1246` | `cell_diff_max_mv` | `u16` | `1` | `mV` |
| `0x1248` | `max_min_cell_idx` | `u8x2` | `1` | `cell index` |
| `0x128A` | `temp_mos_deciC` | `i16` | `/10` | `C` |
| `0x1290..0x1291` | `pack_voltage_mV` | `u32` | `/1000` | `V` |
| `0x1294..0x1295` | `pack_power_mW` | `u32` | `/1000` | `W` |
| `0x1298..0x1299` | `pack_current_mA` | `i32` | `/1000` | `A` |
| `0x129C` | `temp_bat1_deciC` | `i16` | `/10` | `C` |
| `0x129E` | `temp_bat2_deciC` | `i16` | `/10` | `C` |
| `0x12A0..0x12A1` | `alarm` | `u32 bitfield` | `1` | `flags` |
| `0x12A4` | `balance_current_mA` | `i16` | `/1000` | `A` |
| `0x12A6` | `balance_soc` | `u8x2` | `1` | `state / %` |
| `0x12A8..0x12A9` | `remaining_capacity_mAh` | `i32` | `/1000` | `Ah` |
| `0x12AC..0x12AD` | `full_capacity_mAh` | `u32` | `/1000` | `Ah` |
| `0x12B0..0x12B1` | `cycles` | `u32` | `1` | `cycles` |
| `0x12B8` | `soh_precharge` | `u8x2` | `1` | `% / state` |
