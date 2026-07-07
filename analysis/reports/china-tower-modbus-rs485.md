# China Tower Modbus RS485 Bridge Capture

Source capture:

```text
examples/bridge/china-tower-modbus-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge/china-tower-modbus-rs485-raw-capture.sr --protocol china_tower_modbus --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,000,421 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000002 s |
| Analysis runtime | 10.625 s |
| Channel | `CH0` |
| Inverted input | `true` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 1,356 |
| UART invalid start bits | 3 |
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
| `request_to_response_us` | 39 | 5,015.035 | 4,286.525 | 5,549.810 | 5,038.930 | 5,337.927 |
| `full_exchange_us` | 39 | 42,238.361 | 25,536.900 | 53,654.395 | 47,129.775 | 53,525.724 |
| `inter_cycle_gap_us` | 38 | 210,161.634 | 196,255.520 | 233,716.280 | 206,433.860 | 225,931.406 |

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
analysis/out/china-tower-modbus-rs485-raw-capture.frames.csv
analysis/out/china-tower-modbus-rs485-raw-capture.sequences.csv
analysis/out/china-tower-modbus-rs485-raw-capture.summary.md
```
