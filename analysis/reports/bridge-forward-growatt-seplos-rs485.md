# Growatt RS485 Seplos Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/growatt-seplos-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/growatt-seplos-rs485-raw-capture.sr --protocol forward_growatt_seplos_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,077 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000000 s |
| Analysis runtime | 9.344 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 818 |
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
| `request_to_response_us` | 24 | 49,604.182 | 49,370.515 | 51,956.015 | 49,464.700 | 50,490.317 |
| `full_exchange_us` | 24 | 86,131.735 | 64,375.440 | 98,205.740 | 95,728.305 | 97,846.399 |

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
analysis/out/bridge-forward-growatt-seplos-rs485-raw-capture.frames.csv
analysis/out/bridge-forward-growatt-seplos-rs485-raw-capture.sequences.csv
analysis/out/bridge-forward-growatt-seplos-rs485-raw-capture.summary.md
```
