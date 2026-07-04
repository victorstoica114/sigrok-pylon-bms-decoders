# Deye CAN Bridge Capture

Source capture:

```text
examples/bridge/deye-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/deye-can-raw-capture.sr --protocol deye_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,885 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 7.781 s |
| Channel | `CH1` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 100 |
| Unique CAN IDs | 8 |
| CAN cycles | 9 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 9 | 1,011,013.334 | 599,848.765 | 1,599,872.420 | 799,820.930 | 1,599,871.234 |
| `inter_cycle_gap_us` | 8 | 100,194.479 | 100,185.535 | 100,203.535 | 100,195.520 | 100,202.133 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 12 |
| `0x355` | 13 |
| `0x356` | 13 |
| `0x359` | 12 |
| `0x35C` | 13 |
| `0x35E` | 13 |
| `0x370` | 12 |
| `0x371` | 12 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/deye-can-raw-capture.frames.csv
analysis/out/deye-can-raw-capture.sequences.csv
analysis/out/deye-can-raw-capture.summary.md
```
