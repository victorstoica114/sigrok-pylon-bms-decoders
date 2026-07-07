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
| Total samples scanned | 2,000,000,539 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000003 s |
| Analysis runtime | 8.891 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 824 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 20 |
| Requests | 12 |
| Responses | 8 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 12 |
| Complete request/response sequences | 8 |
| Incomplete/orphan rows | 4 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 8 | 9,706.670 | 9,219.085 | 9,922.345 | 9,828.750 | 9,912.793 |
| `full_exchange_us` | 8 | 111,164.319 | 69,059.730 | 153,046.400 | 111,014.717 | 153,034.215 |
| `inter_cycle_gap_us` | 7 | 1,059,938.776 | 647,998.470 | 1,527,191.470 | 730,394.285 | 1,527,126.174 |

Definitions:

```text
request start ---- request end    response start ---- response end
              <-- request_to_response -->
<---------------------- full_exchange ----------------->
```

- `request_to_response_us`: response start minus request end.
- `full_exchange_us`: response end minus request start.
- `inter_cycle_gap_us`: time between the response end of one complete exchange and the request start of the next complete exchange.

## Generated Tables

```text
analysis/out/anenji-pylon-rs485-raw-capture.frames.csv
analysis/out/anenji-pylon-rs485-raw-capture.sequences.csv
analysis/out/anenji-pylon-rs485-raw-capture.summary.md
```
