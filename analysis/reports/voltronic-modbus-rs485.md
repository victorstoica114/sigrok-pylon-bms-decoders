# Voltronic Modbus RS485 Bridge Capture

Source capture:

```text
examples/bridge/voltronic-modbus-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/voltronic-modbus-rs485-raw-capture.sr --protocol voltronic_modbus --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,877 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000004 s |
| Analysis runtime | 8.953 s |
| Channel | `CH1` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 624 |
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
| `request_to_response_us` | 39 | 99,796.750 | 99,374.265 | 104,836.495 | 99,490.160 | 101,837.191 |
| `full_exchange_us` | 39 | 117,921.656 | 117,499.170 | 122,961.420 | 117,615.085 | 119,962.102 |

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
analysis/out/voltronic-modbus-rs485-raw-capture.frames.csv
analysis/out/voltronic-modbus-rs485-raw-capture.sequences.csv
analysis/out/voltronic-modbus-rs485-raw-capture.summary.md
```
