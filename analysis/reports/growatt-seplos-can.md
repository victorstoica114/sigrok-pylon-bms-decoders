# Growatt CAN Seplos Bridge Capture

Source capture:

```text
examples/bridge/growatt-seplos-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/growatt-seplos-can-raw-capture.sr --protocol growatt_seplos_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,411 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000002 s |
| Analysis runtime | 8.047 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 130 |
| Unique CAN IDs | 12 |
| CAN cycles | 10 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 10 | 851,373.724 | 251,234.865 | 1,496,223.985 | 834,224.170 | 1,221,318.481 |
| `inter_cycle_gap_us` | 9 | 155,493.468 | 114,668.755 | 165,777.835 | 165,773.835 | 165,776.235 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 20 |
| `0x311` | 10 |
| `0x312` | 10 |
| `0x313` | 10 |
| `0x314` | 10 |
| `0x315` | 10 |
| `0x316` | 10 |
| `0x317` | 10 |
| `0x318` | 10 |
| `0x319` | 10 |
| `0x320` | 10 |
| `0x322` | 10 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/growatt-seplos-can-raw-capture.frames.csv
analysis/out/growatt-seplos-can-raw-capture.sequences.csv
analysis/out/growatt-seplos-can-raw-capture.summary.md
```
