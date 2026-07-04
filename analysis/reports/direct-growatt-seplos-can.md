# Growatt CAN Seplos Direct Capture

Source capture:

```text
examples/direct/growatt-seplos-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/direct/growatt-seplos-can-raw-capture.sr --protocol direct_growatt_seplos_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 1,000,000,047 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 5.000000 s |
| Analysis runtime | 4.125 s |
| Channel | `CH0` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 75.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 65 |
| Unique CAN IDs | 12 |
| CAN cycles | 6 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 6 | 687,125.942 | 129,932.965 | 831,769.225 | 831,762.353 | 831,768.787 |
| `inter_cycle_gap_us` | 5 | 168,228.483 | 168,225.685 | 168,229.680 | 168,229.680 | 168,229.680 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x301` | 10 |
| `0x311` | 5 |
| `0x312` | 5 |
| `0x313` | 5 |
| `0x314` | 5 |
| `0x315` | 5 |
| `0x316` | 5 |
| `0x317` | 5 |
| `0x318` | 5 |
| `0x319` | 5 |
| `0x320` | 5 |
| `0x322` | 5 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/direct-growatt-seplos-can-raw-capture.frames.csv
analysis/out/direct-growatt-seplos-can-raw-capture.sequences.csv
analysis/out/direct-growatt-seplos-can-raw-capture.summary.md
```
