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
| Samplerate | 200 MHz |
| Capture duration | 10.000002 s |
| Analysis runtime | 11.250 s |
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
| CRC bad frames | 0 |
| Invalid frames | 0 |
| Incomplete frame buffers dropped on gaps | 1 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 40 |
| Complete request/response sequences | 39 |
| Incomplete/orphan rows | 1 |

The final sequence is an unmatched request at the end of the capture, so it is
expected to be incomplete if the recording stopped before the response arrived.

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 39 | 5,015.035 | 4,286.525 | 5,549.810 | 5,038.930 | 5,337.927 |
| `full_exchange_us` | 39 | 42,238.361 | 25,536.900 | 53,654.395 | 47,129.775 | 53,525.724 |

Definitions:

```text
request start ---- request end    response start ---- response end
              <-- request_to_response -->
<---------------------- full_exchange ----------------->
```

- `request_to_response_us`: response start minus request end.
- `full_exchange_us`: response end minus request start.
- `n`: number of complete request/response sequences included.
- `avg`: arithmetic mean across those sequences.
- `min`: fastest observed value.
- `max`: slowest observed value.
- `p50`: median value; half of the observations are below this value.
- `p95`: 95th percentile; 95% of observations are below this value.

## Generated Tables

The detailed generated CSV files are tracked in Git and can also be recreated at
any time:

```text
analysis/out/china-tower-modbus-rs485-raw-capture.frames.csv
analysis/out/china-tower-modbus-rs485-raw-capture.sequences.csv
analysis/out/china-tower-modbus-rs485-raw-capture.summary.md
```
