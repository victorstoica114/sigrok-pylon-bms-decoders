# Anenji Pylon RS485 JKBMS Direct Capture

Source capture:

```text
examples/direct/anenji-jkbms-pylon-rs485-raw-capture.sr
```

Analysis command:

```powershell
python analysis/analyze_capture.py examples/direct/anenji-jkbms-pylon-rs485-raw-capture.sr --protocol direct_anenji_jkbms_pylon_rs485 --quiet
```

## Decode Summary

| Metric | Value |
| --- | ---: |
| Total samples scanned | 5,000,001,513 |
| Samplerate | 200,000,000 Hz |
| Capture duration | 25.000008 s |
| Analysis runtime | 24.453 s |
| Channel | `CH0` |
| Inverted input | `false` |
| UART baud | 9,600 bit/s |
| UART bytes decoded | 3,238 |
| UART invalid start bits | 0 |
| UART invalid stop bits | 0 |

## Frame Counts

| Metric | Count |
| --- | ---: |
| Total frames | 61 |
| Requests | 31 |
| Responses | 30 |
| Exceptions | 0 |
| Bad/invalid frames | 0 |

## Sequence Counts

| Metric | Count |
| --- | ---: |
| Total sequence rows | 41 |
| Complete request/response sequences | 20 |
| Incomplete/orphan rows | 21 |

## Timing Statistics

| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `request_to_response_us` | 20 | 5,124.941 | 4,290.195 | 5,893.365 | 5,137.235 | 5,692.958 |
| `full_exchange_us` | 20 | 102,917.894 | 60,414.530 | 145,354.945 | 102,904.783 | 145,154.533 |

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
analysis/out/direct-anenji-jkbms-pylon-rs485-raw-capture.frames.csv
analysis/out/direct-anenji-jkbms-pylon-rs485-raw-capture.sequences.csv
analysis/out/direct-anenji-jkbms-pylon-rs485-raw-capture.summary.md
```
