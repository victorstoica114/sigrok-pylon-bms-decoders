# Offline Capture Analysis

This folder contains tooling for repeatable, table-oriented analysis of large
PulseView/sigrok captures.

The first supported protocol is `china_tower_modbus` over UART/RS485. The tool
streams a `.sr` file, decodes UART bytes from the selected logic channel, reuses
the existing China Tower Modbus parser, and writes CSV/Markdown outputs.

## China Tower Example

```powershell
python analysis/analyze_capture.py examples/bridge/china-tower-modbus-rs485-raw-capture.sr --protocol china_tower_modbus
```

The bridge China Tower capture uses `CH0`, `9600 8N1`, and inverted RX, so those
are the protocol defaults. Override them when needed:

```powershell
python analysis/analyze_capture.py examples/bridge/china-tower-modbus-rs485-raw-capture.sr --protocol china_tower_modbus --channel CH0 --baud 9600 --invert-rx
```

Outputs are written under `analysis/out/` by default:

- `*.frames.csv` has one row per decoded frame.
- `*.sequences.csv` has request/response pairing and timing.
- `*.summary.md` has quick counts and latency statistics.

## Reports

Committed analysis reports live under `analysis/reports/`:

- [China Tower Modbus RS485 Bridge Capture](reports/china-tower-modbus-rs485.md)

Important timing fields:

- `turnaround_us`: response start minus request end.
- `round_trip_us`: response end minus request start.
- `gap_from_previous_us`: current frame start minus previous frame end.

## Design Notes

The scanner does not loop over every sample in Python. It translates the selected
probe byte to a 0/1 level buffer and finds transitions in C-backed operations,
then the UART decoder only samples scheduled bit centers. That keeps large
captures practical while preserving sample-accurate timing.
