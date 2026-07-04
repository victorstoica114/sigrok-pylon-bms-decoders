# GoodWe CAN Bridge Capture

Source capture:

```text
examples/bridge/goodwe-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/goodwe-can-raw-capture.sr --protocol goodwe_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,373 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000002 s |
| Analysis runtime | 7.703 s |
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
| CAN cycles | 4 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 4 | 2,399,973.046 | 300,245.895 | 7,100,062.150 | 1,099,792.070 | 6,275,024.243 |
| `inter_cycle_gap_us` | 3 | 100,265.227 | 100,259.230 | 100,269.220 | 100,267.230 | 100,269.021 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 13 |
| `0x355` | 13 |
| `0x356` | 12 |
| `0x359` | 13 |
| `0x35C` | 12 |
| `0x35E` | 12 |
| `0x370` | 12 |
| `0x371` | 13 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/goodwe-can-raw-capture.frames.csv
analysis/out/goodwe-can-raw-capture.sequences.csv
analysis/out/goodwe-can-raw-capture.summary.md
```
