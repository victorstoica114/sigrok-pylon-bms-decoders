# Growatt RS485 JKBMS Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/growatt-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/growatt-rs485-raw-capture.sr --protocol forward_growatt_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,213 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000001 s |
| Analysis runtime | 9.829 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,019 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 50 |
| Requests | 25 |
| Responses | 25 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 25 |
| Complete request/response sequences | 25 |
| Incomplete/orphan rows | 0 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 25 | 5,008.099 | 4,253.345 | 5,321.880 | 4,993.570 | 5,293.782 |
| `full_exchange_us` | 25 | 48,926.211 | 42,171.180 | 53,590.030 | 51,386.365 | 53,484.774 |
| `inter_cycle_gap_us` | 24 | 353,210.543 | 349,433.130 | 360,241.285 | 349,894.463 | 360,194.552 |

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
analysis/out/bridge-forward-growatt-rs485-raw-capture.frames.csv
analysis/out/bridge-forward-growatt-rs485-raw-capture.sequences.csv
analysis/out/bridge-forward-growatt-rs485-raw-capture.summary.md
```
