# Anenji Pylon RS485 JKBMS Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/anenji-pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/anenji-pylon-rs485-raw-capture.sr --protocol forward_anenji_pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,887 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 9.766 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,288 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 24 |
| Requests | 12 |
| Responses | 12 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 16 |
| Complete request/response sequences | 8 |
| Incomplete/orphan rows | 8 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 8 | 5,488.619 | 5,085.285 | 6,362.195 | 5,321.738 | 6,190.079 |
| `full_exchange_us` | 8 | 106,950.364 | 64,878.425 | 149,492.540 | 106,878.750 | 149,320.428 |

Definitions:

```text
request start ---- request end    response start ---- response end
              <-- request_to_response -->
<---------------------- full_exchange ----------------->
```

- `request_to_response_us`: response start minus request end.
- `full_exchange_us`: response end minus request start.

## Generated Tables

```text
analysis/out/bridge-forward-anenji-pylon-rs485-raw-capture.frames.csv
analysis/out/bridge-forward-anenji-pylon-rs485-raw-capture.sequences.csv
analysis/out/bridge-forward-anenji-pylon-rs485-raw-capture.summary.md
```
