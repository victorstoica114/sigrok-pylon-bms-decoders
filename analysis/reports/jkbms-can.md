# JKBMS CAN Bridge Capture

Source capture:

```text
examples/bridge/jkbms-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/jkbms-can-raw-capture.sr --protocol jkbms_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,879 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 8.344 s |
| Channel | `CH1` |
| Inverted input | `true` |
| CAN bitrate | 250,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 344 |
| Unique CAN IDs | 12 |
| CAN cycles | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 1 | 9,907,992.715 | 9,907,992.715 | 9,907,992.715 | 9,907,992.715 | 9,907,992.715 |
| `inter_cycle_gap_us` | 0 |  |  |  |  |  |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x1806E5F4` | 20 |
| `0x18E028F4` | 6 |
| `0x18E128F4` | 6 |
| `0x18E228F4` | 6 |
| `0x18E328F4` | 6 |
| `0x18F128F4` | 50 |
| `0x18F228F4` | 10 |
| `0x18F428F4` | 10 |
| `0x18F528F4` | 20 |
| `0x2F4` | 100 |
| `0x4F4` | 100 |
| `0x5F4` | 10 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/jkbms-can-raw-capture.frames.csv
analysis/out/jkbms-can-raw-capture.sequences.csv
analysis/out/jkbms-can-raw-capture.summary.md
```
