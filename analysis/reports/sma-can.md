# SMA CAN Bridge Capture

Source capture:

```text
examples/bridge/sma-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/sma-can-raw-capture.sr --protocol sma_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,001,373 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000007 s |
| Analysis runtime | 7.297 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 60 |
| Unique CAN IDs | 6 |
| CAN cycles | 60 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 60 | 230.733 | 219.400 | 237.400 | 231.400 | 237.400 |
| `inter_cycle_gap_us` | 59 | 166,404.548 | 165,307.740 | 168,241.725 | 165,765.740 | 168,235.921 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 10 |
| `0x355` | 10 |
| `0x356` | 10 |
| `0x35A` | 10 |
| `0x35E` | 10 |
| `0x35F` | 10 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/sma-can-raw-capture.frames.csv
analysis/out/sma-can-raw-capture.sequences.csv
analysis/out/sma-can-raw-capture.summary.md
```
