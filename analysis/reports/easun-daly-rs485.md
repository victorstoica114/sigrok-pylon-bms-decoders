# Daly RS485 Bridge Capture

Source capture:

```text
examples/bridge/easun-daly-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/easun-daly-rs485-raw-capture.sr --protocol daly_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,000,701 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000004 s |
| Analysis runtime | 45.171 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 11,748 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 88 |
| Requests | 44 |
| Responses | 44 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 44 |
| Complete request/response sequences | 44 |
| Incomplete/orphan rows | 0 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 44 | 14,458.976 | 11,987.095 | 18,095.990 | 14,048.380 | 18,060.297 |
| `full_exchange_us` | 44 | 294,045.479 | 291,573.595 | 297,682.490 | 293,634.883 | 297,646.802 |
| `inter_cycle_gap_us` | 43 | 271,066.451 | 269,414.240 | 272,681.260 | 270,570.460 | 272,393.405 |

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
analysis/out/easun-daly-rs485-raw-capture.frames.csv
analysis/out/easun-daly-rs485-raw-capture.sequences.csv
analysis/out/easun-daly-rs485-raw-capture.summary.md
```
