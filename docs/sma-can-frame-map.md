# SMA CAN Frame Map

Protocol scope: SMA Sunny Island compatible low-voltage BMS frames over Classic
CAN.

Payload fields are little-endian. This map follows the active
`decoders/sma_can` implementation and the local source map under
`docs/esp32-source-maps/main/protocols/sma`.

## SMA CAN Frames

| Register / Frame | Name | Type | Scale | Unit |
| --- | --- | --- | --- | --- |
| `0x351 bytes 0..1` | `charge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x351 bytes 2..3` | `charge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 4..5` | `discharge_current_limit` | `u16 le` | `/10` | `A` |
| `0x351 bytes 6..7` | `discharge_voltage_limit` | `u16 le` | `/10` | `V` |
| `0x355 bytes 0..1` | `soc` | `u16 le` | `1` | `%` |
| `0x355 bytes 2..3` | `soh` | `u16 le` | `1` | `%` |
| `0x355 bytes 4..7` | `raw_tail` | `u8[4]` | `1` | `raw` |
| `0x356 bytes 0..1` | `pack_voltage` | `u16 le` | `/100` | `V` |
| `0x356 bytes 2..3` | `pack_current` | `i16 le` | `/10` | `A` |
| `0x356 bytes 4..5` | `pack_temperature` | `i16 le` | `/10` | `C` |
| `0x356 bytes 6..7` | `raw_tail` | `u8[2]` | `1` | `raw` |
| `0x359 bytes 0..7` | `alarms_status_raw` | `u8[8]` | `1` | `raw` |
| `0x35A bytes 0..7` | `vendor_raw` | `u8[8]` | `1` | `raw` |
| `0x35E bytes 0..7` | `manufacturer` | `ascii/u8[8]` | `1` | `text / raw` |
| `0x35F bytes 0..7` | `battery_info_raw` | `ascii/u8[8]` | `1` | `text / raw` |
