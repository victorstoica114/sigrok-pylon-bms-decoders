# Growatt RS485 Seplos Bridge Capture

Source capture:

```text
examples/bridge/growatt-seplos-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/growatt-seplos-rs485-raw-capture.sr --protocol growatt_seplos_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,991 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000005 s |
| Analysis runtime | 8.859 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 820 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 49 |
| Requests | 25 |
| Responses | 16 |
| Exceptions | 8 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 25 |
| Complete request/response sequences | 24 |
| Incomplete/orphan rows | 1 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 24 | 49,517.093 | 49,022.880 | 51,760.200 | 49,430.690 | 49,863.536 |
| `full_exchange_us` | 24 | 86,044.643 | 64,022.775 | 97,822.885 | 95,682.337 | 97,806.109 |

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
analysis/out/growatt-seplos-rs485-raw-capture.frames.csv
analysis/out/growatt-seplos-rs485-raw-capture.sequences.csv
analysis/out/growatt-seplos-rs485-raw-capture.summary.md
```
