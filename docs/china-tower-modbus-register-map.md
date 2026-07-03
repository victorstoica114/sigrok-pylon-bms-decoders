# China Tower Modbus Register Map

Protocol: China Tower shared battery cabinet RS485 profile used by JK UART
protocol `008`.

This map follows the live JK app layout validated with
`decoders/china_tower_modbus` for the current Growatt/JKBMS bridge tests.

- Default slave address: `0x01`
- Supported read functions: `0x03`, `0x04`
- Poll blocks: `0x0000` count `0x000D`, `0x0009` count `16`,
  `0x0019` count `3`

## China Tower Modbus Runtime Registers

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x0000` | `pack_voltage_10mV` | `u16` | `/100` | `V` |
| `0x0001` | `cell_count` | `u16` | `1` | `cells` |
| `0x0002` | `soc` | `u16 packed` | `1` | `%` |
| `0x0003` | `runtime_raw_0003` | `u16` | `1` | `raw` |
| `0x0004` | `runtime_raw_0004` | `u16` | `1` | `raw` |
| `0x0005` | `runtime_raw_0005` | `u16` | `1` | `raw` |
| `0x0006` | `temp1` | `i16` | `1` | `C` |
| `0x0007` | `temp2` | `i16` | `1` | `C` |
| `0x0008` | `mos_temp` | `i16` | `1` | `C` |
| `0x0009..0x0018` | `cell01_mv..cell16_mv` | `u16` | `/1000` | `V` |
| `0x0019` | `warning_flags` | `u16 bitfield` | `1` | `flags` |
| `0x001A` | `protection_flags` | `u16 bitfield` | `1` | `flags` |
| `0x001B` | `status_flags` | `u16 bitfield` | `1` | `flags` |
| `0x001C` | `temp_dup1` | `i16` | `1` | `C` |
| `0x001D` | `temp_dup2` | `i16` | `1` | `C` |

## China Tower Modbus Status Bits

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x001B bit 8` | `charge` | `flag` | `1` | `state` |
| `0x001B bit 9` | `discharge` | `flag` | `1` | `state` |
| `0x001B bit 10` | `charge_mos` | `flag` | `1` | `state` |
| `0x001B bit 11` | `discharge_mos` | `flag` | `1` | `state` |
