# WOW Modbus RS485 Bridge Capture

Source capture:

```text
examples/bridge/wow-modbus-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/wow-modbus-rs485-raw-capture.sr --protocol wow_modbus --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,515 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000003 s |
| Analysis runtime | 12.156 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,881 |
| UART invalid start bits | 0 |
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
| `request_to_response_us` | 39 | 4,799.126 | 4,434.400 | 5,236.035 | 4,798.900 | 5,093.604 |
| `full_exchange_us` | 39 | 56,499.652 | 46,519.095 | 65,824.900 | 65,358.160 | 65,808.754 |

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
analysis/out/wow-modbus-rs485-raw-capture.frames.csv
analysis/out/wow-modbus-rs485-raw-capture.sequences.csv
analysis/out/wow-modbus-rs485-raw-capture.summary.md
```
