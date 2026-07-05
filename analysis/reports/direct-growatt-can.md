# Growatt CAN JKBMS Direct Capture

Source capture:

```text
examples/direct/growatt-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/direct/growatt-can-raw-capture.sr --protocol direct_growatt_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 1,000,000,191 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 5.000001 s |
| Analysis runtime | 6.500 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 75.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 260 |
| Unique CAN IDs | 10 |
| CAN cycles | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 1 | 4,980,232.085 | 4,980,232.085 | 4,980,232.085 | 4,980,232.085 | 4,980,232.085 |
| `inter_cycle_gap_us` | 0 |  |  |  |  |  |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 10 |
| `0x311` | 28 |
| `0x312` | 28 |
| `0x313` | 28 |
| `0x314` | 28 |
| `0x319` | 28 |
| `0x320` | 28 |
| `0x321` | 28 |
| `0x322` | 27 |
| `0x323` | 27 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/direct-growatt-can-raw-capture.frames.csv
analysis/out/direct-growatt-can-raw-capture.sequences.csv
analysis/out/direct-growatt-can-raw-capture.summary.md
```
