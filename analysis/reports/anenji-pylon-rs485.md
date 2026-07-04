# Anenji Pylon RS485 Bridge Capture

Source capture:

```text
examples/bridge/anenji-pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/anenji-pylon-rs485-raw-capture.sr --protocol anenji_pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,001,053 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000005 s |
| Analysis runtime | 24.844 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 3,274 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 62 |
| Requests | 31 |
| Responses | 31 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 41 |
| Complete request/response sequences | 21 |
| Incomplete/orphan rows | 20 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 21 | 5,057.951 | 4,284.055 | 5,876.660 | 5,059.785 | 5,729.205 |
| `full_exchange_us` | 21 | 104,535.490 | 64,077.220 | 149,007.030 | 65,112.695 | 148,859.575 |

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
analysis/out/anenji-pylon-rs485-raw-capture.frames.csv
analysis/out/anenji-pylon-rs485-raw-capture.sequences.csv
analysis/out/anenji-pylon-rs485-raw-capture.summary.md
```
