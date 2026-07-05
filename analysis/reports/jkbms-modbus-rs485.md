# JKBMS Modbus RS485 Bridge Capture

Source capture:

```text
examples/bridge/jkbms-modbus-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/jkbms-modbus-rs485-raw-capture.sr --protocol jkbms_modbus --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,255 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000001 s |
| Analysis runtime | 7.953 s |
| Channel | `CH0` |
| Inverted input | `true` |
| UART baud | 115,200 bit/s |
| UART bytes decoded | 1,915 |
| UART invalid start bits | 1 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 78 |
| Requests | 39 |
| Responses | 39 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 39 |
| Complete request/response sequences | 39 |
| Incomplete/orphan rows | 0 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 39 | 4,903.504 | 4,646.325 | 5,585.350 | 4,918.925 | 5,191.553 |
| `full_exchange_us` | 39 | 9,281.989 | 6,283.480 | 13,269.185 | 8,922.580 | 13,115.590 |

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
analysis/out/jkbms-modbus-rs485-raw-capture.frames.csv
analysis/out/jkbms-modbus-rs485-raw-capture.sequences.csv
analysis/out/jkbms-modbus-rs485-raw-capture.summary.md
```
