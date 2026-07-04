# Growatt RS485 Bridge Capture

Source capture:

```text
examples/bridge/growatt-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/growatt-rs485-raw-capture.sr --protocol growatt_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,623 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000003 s |
| Analysis runtime | 9.625 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,027 |
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
| `request_to_response_us` | 25 | 4,656.807 | 4,320.610 | 5,394.950 | 4,589.795 | 5,282.182 |
| `full_exchange_us` | 25 | 48,908.271 | 42,251.070 | 53,729.940 | 50,759.735 | 53,501.203 |

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
analysis/out/growatt-rs485-raw-capture.frames.csv
analysis/out/growatt-rs485-raw-capture.sequences.csv
analysis/out/growatt-rs485-raw-capture.summary.md
```
