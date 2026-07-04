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
| Total samples scanned | 2,000,000,691 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000003 s |
| Analysis runtime | 7.250 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 237 |
| Unique CAN IDs | 8 |
| CAN cycles | 37 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 37 | 19,950.799 | 221.400 | 100,347.320 | 1,739.195 | 82,038.312 |
| `inter_cycle_gap_us` | 36 | 248,676.040 | 107,484.730 | 398,446.700 | 198,666.805 | 398,264.199 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 20 |
| `0x311` | 33 |
| `0x312` | 33 |
| `0x313` | 33 |
| `0x314` | 33 |
| `0x319` | 33 |
| `0x320` | 33 |
| `0x322` | 19 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/growatt-can-raw-capture.frames.csv
analysis/out/growatt-can-raw-capture.sequences.csv
analysis/out/growatt-can-raw-capture.summary.md
```
