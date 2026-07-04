# Pylon CAN Bridge Capture

Source capture:

```text
examples/bridge/pylon-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/pylon-can-raw-capture.sr --protocol pylon_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,001,251 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000006 s |
| Analysis runtime | 7.734 s |
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
| CAN cycles | 5 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 5 | 1,900,011.264 | 900,275.935 | 2,299,947.265 | 2,299,932.935 | 2,299,945.203 |
| `inter_cycle_gap_us` | 4 | 100,172.068 | 100,163.545 | 100,177.565 | 100,173.580 | 100,176.970 |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 13 |
| `0x355` | 13 |
| `0x356` | 13 |
| `0x359` | 12 |
| `0x35C` | 13 |
| `0x35E` | 12 |
| `0x370` | 12 |
| `0x371` | 12 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/pylon-can-raw-capture.frames.csv
analysis/out/pylon-can-raw-capture.sequences.csv
analysis/out/pylon-can-raw-capture.summary.md
```
