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
| Total samples scanned | 2,000,001,405 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000007 s |
| Analysis runtime | 9.516 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,029 |
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
| `request_to_response_us` | 25 | 4,759.997 | 4,301.185 | 5,361.060 | 4,643.880 | 5,294.317 |
| `full_exchange_us` | 25 | 49,094.793 | 42,255.805 | 53,555.285 | 50,788.940 | 53,520.070 |

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
