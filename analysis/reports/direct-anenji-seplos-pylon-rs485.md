# Anenji Pylon RS485 Seplos Direct Capture

Source capture:

```text
examples/direct/anenji-seplos-pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/direct/anenji-seplos-pylon-rs485-raw-capture.sr --protocol direct_anenji_seplos_pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,000,307 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000002 s |
| Analysis runtime | 21.328 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 2,060 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 50 |
| Requests | 30 |
| Responses | 20 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 30 |
| Complete request/response sequences | 20 |
| Incomplete/orphan rows | 10 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 20 | 9,887.208 | 9,069.430 | 12,153.795 | 9,731.057 | 12,043.433 |
| `full_exchange_us` | 20 | 107,676.065 | 65,191.905 | 151,609.075 | 107,414.997 | 151,498.699 |
| `inter_cycle_gap_us` | 19 | 1,106,892.711 | 650,603.640 | 1,614,699.315 | 734,596.865 | 1,614,094.519 |

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
analysis/out/direct-anenji-seplos-pylon-rs485-raw-capture.frames.csv
analysis/out/direct-anenji-seplos-pylon-rs485-raw-capture.sequences.csv
analysis/out/direct-anenji-seplos-pylon-rs485-raw-capture.summary.md
```
