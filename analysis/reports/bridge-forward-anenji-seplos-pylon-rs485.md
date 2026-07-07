# Anenji Pylon RS485 Seplos Bridge Forward Capture

Source capture:

```text
examples/bridge_forward/anenji-seplos-pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/bridge_forward/anenji-seplos-pylon-rs485-raw-capture.sr --protocol forward_anenji_seplos_pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 2,000,001,191 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 10.000006 s |
| Analysis runtime | 8.625 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 824 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 20 |
| Requests | 12 |
| Responses | 8 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 12 |
| Complete request/response sequences | 8 |
| Incomplete/orphan rows | 4 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 8 | 9,469.731 | 9,141.200 | 9,978.710 | 9,427.405 | 9,877.579 |
| `full_exchange_us` | 8 | 110,927.388 | 68,932.450 | 153,102.775 | 110,919.262 | 153,001.644 |
| `inter_cycle_gap_us` | 7 | 1,072,162.129 | 646,655.530 | 1,611,293.610 | 731,028.125 | 1,586,190.683 |

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
analysis/out/bridge-forward-anenji-seplos-pylon-rs485-raw-capture.frames.csv
analysis/out/bridge-forward-anenji-seplos-pylon-rs485-raw-capture.sequences.csv
analysis/out/bridge-forward-anenji-seplos-pylon-rs485-raw-capture.summary.md
```
