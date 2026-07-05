# Growatt CAN Seplos Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/growatt-seplos-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/growatt-seplos-can-raw-capture.sr --protocol forward_growatt_seplos_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,001,019 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000005 s |
| Analysis runtime | 7.969 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 129 |
| Unique CAN IDs | 12 |
| CAN cycles | 11 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 11 | 755,942.000 | 85,691.125 | 871,814.905 | 834,219.285 | 861,952.157 |
| `inter_cycle_gap_us` | 10 | 160,226.810 | 128,174.720 | 165,777.835 | 165,773.832 | 165,777.835 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 19 |
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
analysis/out/bridge-forward-growatt-seplos-can-raw-capture.frames.csv
analysis/out/bridge-forward-growatt-seplos-can-raw-capture.sequences.csv
analysis/out/bridge-forward-growatt-seplos-can-raw-capture.summary.md
```
