# Growatt RS485 JKBMS Direct Capture

Source capture:

```text
examples/direct/growatt-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/direct/growatt-rs485-raw-capture.sr --protocol direct_growatt_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,000,589 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000003 s |
| Analysis runtime | 23.406 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 2,602 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 100 |
| Requests | 50 |
| Responses | 50 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 50 |
| Complete request/response sequences | 50 |
| Incomplete/orphan rows | 0 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 50 | 5,126.758 | 4,878.360 | 5,675.380 | 5,105.733 | 5,438.647 |
| `full_exchange_us` | 50 | 59,337.414 | 49,671.905 | 75,141.045 | 54,057.872 | 75,000.908 |

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
analysis/out/direct-growatt-rs485-raw-capture.frames.csv
analysis/out/direct-growatt-rs485-raw-capture.sequences.csv
analysis/out/direct-growatt-rs485-raw-capture.summary.md
```
