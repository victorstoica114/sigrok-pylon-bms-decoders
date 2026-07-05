# Growatt CAN JKBMS Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/growatt-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/growatt-can-raw-capture.sr --protocol forward_growatt_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,571 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000003 s |
| Analysis runtime | 13.250 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 520 |
| Unique CAN IDs | 10 |
| CAN cycles | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 1 | 9,980,680.500 | 9,980,680.500 | 9,980,680.500 | 9,980,680.500 | 9,980,680.500 |
| `inter_cycle_gap_us` | 0 |  |  |  |  |  |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 20 |
| `0x311` | 55 |
| `0x312` | 56 |
| `0x313` | 56 |
| `0x314` | 56 |
| `0x319` | 56 |
| `0x320` | 56 |
| `0x321` | 55 |
| `0x322` | 55 |
| `0x323` | 55 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/bridge-forward-growatt-can-raw-capture.frames.csv
analysis/out/bridge-forward-growatt-can-raw-capture.sequences.csv
analysis/out/bridge-forward-growatt-can-raw-capture.summary.md
```
