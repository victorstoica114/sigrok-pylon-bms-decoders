# Growatt CAN Bridge Capture

Source capture:

```text
examples/bridge/growatt-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/growatt-can-raw-capture.sr --protocol growatt_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,717 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 13.172 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 519 |
| Unique CAN IDs | 10 |
| CAN cycles | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 1 | 9,980,699.265 | 9,980,699.265 | 9,980,699.265 | 9,980,699.265 | 9,980,699.265 |
| `inter_cycle_gap_us` | 0 |  |  |  |  |  |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 19 |
| `0x311` | 55 |
| `0x312` | 55 |
| `0x313` | 55 |
| `0x314` | 56 |
| `0x319` | 56 |
| `0x320` | 56 |
| `0x321` | 56 |
| `0x322` | 56 |
| `0x323` | 55 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/growatt-can-raw-capture.frames.csv
analysis/out/growatt-can-raw-capture.sequences.csv
analysis/out/growatt-can-raw-capture.summary.md
```
