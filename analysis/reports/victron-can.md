# Victron CAN Bridge Capture

Source capture:

```text
examples/bridge/victron-can-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/victron-can-raw-capture.sr --protocol victron_can --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,241 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000001 s |
| Analysis runtime | 9.625 s |
| Channel | `CH1` |
| Inverted input | `true` |
| CAN bitrate | 500,000 bit/s |
| CAN sample point | 70.0% |
| CAN stuff errors | 0 |
| CAN decode errors | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total CAN frames | 250 |
| Unique CAN IDs | 19 |
| CAN cycles | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cycle_duration_us` | 1 | 9,960,725.835 | 9,960,725.835 | 9,960,725.835 | 9,960,725.835 | 9,960,725.835 |
| `inter_cycle_gap_us` | 0 |  |  |  |  |  |

## CAN IDs

| CAN ID | Frames |
| --- | ---: |
| `0x351` | 13 |
| `0x355` | 13 |
| `0x356` | 13 |
| `0x35A` | 13 |
| `0x35E` | 13 |
| `0x35F` | 13 |
| `0x360` | 13 |
| `0x370` | 13 |
| `0x371` | 13 |
| `0x372` | 13 |
| `0x373` | 13 |
| `0x374` | 13 |
| `0x375` | 14 |
| `0x376` | 14 |
| `0x377` | 14 |
| `0x378` | 13 |
| `0x379` | 13 |
| `0x380` | 13 |
| `0x381` | 13 |

Definitions:

- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.
- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.

## Generated Tables

```text
analysis/out/victron-can-raw-capture.frames.csv
analysis/out/victron-can-raw-capture.sequences.csv
analysis/out/victron-can-raw-capture.summary.md
```
