# PACE Modbus RS485 Bridge Capture

Source capture:

```text
examples/bridge/pace-modbus-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/pace-modbus-rs485-raw-capture.sr --protocol pace_modbus --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,831 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 11.969 s |
| Channel | `CH0` |
| Inverted input | `true` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,894 |
| UART invalid start bits | 4 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 79 |
| Requests | 40 |
| Responses | 39 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 40 |
| Complete request/response sequences | 39 |
| Incomplete/orphan rows | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 39 | 4,987.736 | 4,396.025 | 5,385.960 | 4,991.105 | 5,260.878 |
| `full_exchange_us` | 39 | 56,207.464 | 46,480.715 | 66,221.520 | 47,356.220 | 66,064.784 |

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
analysis/out/pace-modbus-rs485-raw-capture.frames.csv
analysis/out/pace-modbus-rs485-raw-capture.sequences.csv
analysis/out/pace-modbus-rs485-raw-capture.summary.md
```
