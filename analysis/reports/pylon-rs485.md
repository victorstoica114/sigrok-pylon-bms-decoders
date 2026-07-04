# Pylon RS485 Bridge Capture

Source capture:

```text
examples/bridge/pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/pylon-rs485-raw-capture.sr --protocol pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 10,000,001,055 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 50.000005 s |
| Analysis runtime | 36.484 s |
| Channel | `CH0` |
| Inverted input | `true` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,634 |
| UART invalid start bits | 2 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 49 |
| Requests | 23 |
| Responses | 18 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 23 |
| Complete request/response sequences | 18 |
| Incomplete/orphan rows | 5 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 18 | 4,817.499 | 4,206.370 | 5,705.760 | 4,761.408 | 5,537.460 |
| `full_exchange_us` | 18 | 88,917.290 | 53,582.340 | 148,836.050 | 64,659.860 | 148,667.742 |

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
analysis/out/pylon-rs485-raw-capture.frames.csv
analysis/out/pylon-rs485-raw-capture.sequences.csv
analysis/out/pylon-rs485-raw-capture.summary.md
```
