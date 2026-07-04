# Sofar CAN Bridge Capture

Source capture:

```text
examples/bridge/sofar-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/sofar-can-raw-capture.sr --protocol sofar_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,000,351 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000002 s |
| Analysis runtime | 17.641 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 148 |
| Unique CAN IDs | 6 |
| CAN cycles | 148 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 148 | 228.765 | 219.400 | 237.400 | 231.400 | 237.400 |
| `inter_cycle_gap_us` | 147 | 168,953.744 | 124,888.000 | 382,072.265 | 125,773.995 | 377,763.690 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 25 |
| `0x355` | 25 |
| `0x356` | 24 |
| `0x35A` | 25 |
| `0x35E` | 24 |
| `0x35F` | 25 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/sofar-can-raw-capture.frames.csv
analysis/out/sofar-can-raw-capture.sequences.csv
analysis/out/sofar-can-raw-capture.summary.md
```
