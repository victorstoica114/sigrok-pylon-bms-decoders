#!/usr/bin/env python3
"""Offline sigrok/PulseView capture analysis.

Current protocol support:
  - china_tower_modbus over UART/RS485

The code is intentionally dependency-free so it can run on a fresh PulseView
workstation with only Python available.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import importlib.util
import re
import statistics
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DECODERS_DIR = REPO_ROOT / "decoders"
CHINA_TOWER_HELPER = DECODERS_DIR / "china_tower_modbus" / "china_tower_modbus.py"

TRANSITION_RE = re.compile(b"\x00\x01|\x01\x00")


def load_helper_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load helper module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


china_tower = load_helper_module("offline_china_tower_modbus", CHINA_TOWER_HELPER)


@dataclass(frozen=True)
class SrMetadata:
    samplerate: int
    unitsize: int
    probes: dict[str, int]


@dataclass(frozen=True)
class UartByte:
    value: int
    start_sample: int
    end_sample: int


@dataclass
class CapturedFrame:
    frame_no: int
    status: str
    frame: dict | None
    raw: bytes
    start_sample: int
    end_sample: int
    summary: str
    decoded: str
    error: str = ""

    @property
    def type(self) -> str:
        if self.frame is None:
            return "invalid"
        return str(self.frame.get("type", "frame"))


@dataclass
class SequenceRow:
    sequence_no: int
    complete: bool
    status: str
    request: CapturedFrame | None
    response: CapturedFrame | None


def parse_samplerate(value: str) -> int:
    text = value.strip().replace(" ", "")
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([kKmMgG]?)[hH][zZ]", text)
    if not match:
        raise ValueError(f"Unsupported samplerate value: {value!r}")

    number = float(match.group(1))
    prefix = match.group(2).lower()
    scale = {"": 1, "k": 1_000, "m": 1_000_000, "g": 1_000_000_000}[prefix]
    return int(round(number * scale))


def read_sr_metadata(sr_path: Path) -> SrMetadata:
    with zipfile.ZipFile(sr_path) as archive:
        metadata_text = archive.read("metadata").decode("utf-8", errors="replace")

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read_string(metadata_text)

    if "device 1" not in parser:
        raise RuntimeError("Capture metadata does not contain [device 1]")

    device = parser["device 1"]
    samplerate = parse_samplerate(device["samplerate"])
    unitsize = int(device["unitsize"])
    total_probes = int(device.get("total probes", "0"))

    probes: dict[str, int] = {}
    for probe_number in range(1, total_probes + 1):
        name = device.get(f"probe{probe_number}", f"CH{probe_number - 1}")
        bit_index = probe_number - 1
        probes[name] = bit_index
        probes[f"CH{probe_number - 1}"] = bit_index

    return SrMetadata(samplerate=samplerate, unitsize=unitsize, probes=probes)


def logic_member_index(name: str) -> int | None:
    match = re.fullmatch(r"logic-1-(\d+)", name)
    if not match:
        return None
    return int(match.group(1))


def iter_logic_members(archive: zipfile.ZipFile) -> Iterable[str]:
    members: list[tuple[int, str]] = []
    for name in archive.namelist():
        index = logic_member_index(name)
        if index is not None:
            members.append((index, name))
    for _index, name in sorted(members, key=lambda item: item[0]):
        yield name


class Uart8n1Decoder:
    def __init__(self, samplerate: int, baud: int, on_byte: Callable[[UartByte], None]):
        self.samplerate = samplerate
        self.baud = baud
        self.bit_time = samplerate / float(baud)
        self.on_byte = on_byte
        self.previous_level: int | None = None
        self.pending: dict | None = None
        self.invalid_start_bits = 0
        self.invalid_stop_bits = 0
        self.decoded_bytes = 0

    def _start_byte(self, start_sample: int) -> None:
        sample_points = [
            int(round(start_sample + ((0.5 + bit_index) * self.bit_time)))
            for bit_index in range(10)
        ]
        self.pending = {
            "start_sample": start_sample,
            "end_sample": int(round(start_sample + (10.0 * self.bit_time))),
            "sample_points": sample_points,
            "levels": [],
        }

    def _finish_pending(self) -> None:
        if self.pending is None:
            return

        levels = self.pending["levels"]
        start_sample = int(self.pending["start_sample"])
        end_sample = int(self.pending["end_sample"])
        self.pending = None

        if len(levels) != 10:
            return
        if levels[0] != 0:
            self.invalid_start_bits += 1
            return
        if levels[9] != 1:
            self.invalid_stop_bits += 1
            return

        value = 0
        for bit_index, level in enumerate(levels[1:9]):
            value |= (int(level) & 1) << bit_index

        self.decoded_bytes += 1
        self.on_byte(UartByte(value=value, start_sample=start_sample, end_sample=end_sample))

    def feed_run(self, start_sample: int, end_sample: int, level: int) -> None:
        if start_sample >= end_sample:
            return

        if self.previous_level is None:
            self.previous_level = level

        if self.pending is None and self.previous_level == 1 and level == 0:
            self._start_byte(start_sample)

        while self.pending is not None:
            levels = self.pending["levels"]
            sample_points = self.pending["sample_points"]
            next_index = len(levels)
            if next_index >= len(sample_points):
                self._finish_pending()
                break

            sample_at = sample_points[next_index]
            if sample_at < start_sample:
                levels.append(level)
                continue
            if sample_at >= end_sample:
                break
            levels.append(level)

            if len(levels) == len(sample_points):
                self._finish_pending()
                break

        self.previous_level = level


class ChinaTowerAssembler:
    def __init__(self, samplerate: int, inter_frame_gap_us: int):
        self.samplerate = samplerate
        self.gap_samples = int((inter_frame_gap_us * samplerate) / 1_000_000)
        self.buf = bytearray()
        self.positions: list[tuple[int, int]] = []
        self.frames: list[CapturedFrame] = []
        self.sequences: list[SequenceRow] = []
        self.pending_requests: dict[tuple[int, int], CapturedFrame] = {}
        self.incomplete_frames = 0
        self.bytes_seen = 0

    def _reset_buffer(self) -> None:
        self.buf = bytearray()
        self.positions = []

    def _pending_request_hint(self, raw: bytes) -> dict | None:
        if len(raw) < 2:
            return None
        key = (raw[0], raw[1] & 0x7F)
        request = self.pending_requests.get(key)
        if request is None or request.frame is None:
            return None
        return {
            "slave": request.frame.get("slave"),
            "func": request.frame.get("func"),
            "start": request.frame.get("start"),
            "count": request.frame.get("count"),
        }

    def _append_sequence(
        self,
        complete: bool,
        status: str,
        request: CapturedFrame | None,
        response: CapturedFrame | None,
    ) -> None:
        self.sequences.append(
            SequenceRow(
                sequence_no=len(self.sequences) + 1,
                complete=complete,
                status=status,
                request=request,
                response=response,
            )
        )

    def _remember_request(self, captured: CapturedFrame) -> None:
        if captured.frame is None:
            return
        key = (int(captured.frame["slave"]), int(captured.frame["func"]))
        previous = self.pending_requests.get(key)
        if previous is not None:
            self._append_sequence(False, "request_replaced", previous, None)
        self.pending_requests[key] = captured

    def _pair_response(self, captured: CapturedFrame) -> None:
        if captured.frame is None:
            return
        key = (int(captured.frame["slave"]), int(captured.frame["func"]))
        request = self.pending_requests.pop(key, None)
        if request is None:
            self._append_sequence(False, "orphan_response", None, captured)
            return
        self._append_sequence(True, "complete", request, captured)

    def _finish_frame(self) -> None:
        if not self.buf:
            return

        raw = bytes(self.buf)
        start_sample = self.positions[0][0]
        end_sample = self.positions[-1][1]

        try:
            frame = china_tower.parse_frame(raw, self._pending_request_hint(raw))
            summary = china_tower.frame_summary(frame)
            decoded = china_tower.describe_frame(frame)
            status = "ok" if frame.get("crc_ok") else "crc_bad"
            error = ""
        except Exception as exc:
            frame = None
            summary = "Invalid China Tower/Modbus frame"
            decoded = ""
            status = "invalid"
            error = str(exc)

        captured = CapturedFrame(
            frame_no=len(self.frames) + 1,
            status=status,
            frame=frame,
            raw=raw,
            start_sample=start_sample,
            end_sample=end_sample,
            summary=summary,
            decoded=decoded,
            error=error,
        )
        self.frames.append(captured)

        if frame is not None:
            if frame.get("type") == "request":
                self._remember_request(captured)
            elif frame.get("type") in ("response", "exception"):
                self._pair_response(captured)

        self._reset_buffer()

    def _flush_incomplete_on_gap(self) -> None:
        if not self.buf:
            return
        self.incomplete_frames += 1
        self._reset_buffer()

    def feed_byte(self, byte: UartByte) -> None:
        self.bytes_seen += 1

        if self.buf and self.gap_samples > 0:
            previous_end = self.positions[-1][1]
            if byte.start_sample - previous_end > self.gap_samples:
                self._flush_incomplete_on_gap()

        self.buf.append(byte.value)
        self.positions.append((byte.start_sample, byte.end_sample))

        if china_tower.frame_complete(self.buf):
            self._finish_frame()

        if len(self.buf) > 260:
            self._flush_incomplete_on_gap()

    def finish(self) -> None:
        if self.buf:
            self._flush_incomplete_on_gap()

        for request in sorted(self.pending_requests.values(), key=lambda item: item.frame_no):
            self._append_sequence(False, "unmatched_request", request, None)
        self.pending_requests.clear()


def make_level_table(bit_in_byte: int, invert: bool) -> bytes:
    invert_bit = 1 if invert else 0
    return bytes((((value >> bit_in_byte) & 1) ^ invert_bit) for value in range(256))


def stream_uart_from_sr(
    sr_path: Path,
    metadata: SrMetadata,
    channel: str,
    invert: bool,
    uart: Uart8n1Decoder,
    max_samples: int | None = None,
    progress: bool = True,
) -> int:
    if channel not in metadata.probes:
        available = ", ".join(sorted(metadata.probes))
        raise ValueError(f"Unknown channel {channel!r}. Available channels: {available}")

    bit_index = metadata.probes[channel]
    byte_index = bit_index // 8
    bit_in_byte = bit_index % 8
    if byte_index >= metadata.unitsize:
        raise ValueError(
            f"Channel {channel!r} maps to bit {bit_index}, beyond unitsize={metadata.unitsize}"
        )

    level_table = make_level_table(bit_in_byte, invert)
    sample_cursor = 0
    last_progress = time.monotonic()
    chunk_size = 4 * 1024 * 1024

    with zipfile.ZipFile(sr_path) as archive:
        members = list(iter_logic_members(archive))
        member_count = len(members)

        for member_index, member_name in enumerate(members, start=1):
            logic_file = archive.open(member_name)
            while True:
                chunk = logic_file.read(chunk_size)
                if not chunk:
                    break

                usable_len = len(chunk) - (len(chunk) % metadata.unitsize)
                if usable_len <= 0:
                    continue
                if usable_len != len(chunk):
                    chunk = chunk[:usable_len]

                selected = chunk[byte_index:usable_len:metadata.unitsize]
                levels = selected.translate(level_table)
                sample_count = len(levels)
                chunk_start = sample_cursor

                if max_samples is not None and chunk_start >= max_samples:
                    return sample_cursor
                if max_samples is not None and chunk_start + sample_count > max_samples:
                    sample_count = max_samples - chunk_start
                    levels = levels[:sample_count]

                if sample_count:
                    run_level = levels[0]
                    run_start_local = 0
                    opposite = b"\x01" if run_level == 0 else b"\x00"
                    first_change = levels.find(opposite)

                    if first_change >= 0:
                        for match in TRANSITION_RE.finditer(levels, max(0, first_change - 1)):
                            edge_local = match.start() + 1
                            uart.feed_run(
                                chunk_start + run_start_local,
                                chunk_start + edge_local,
                                run_level,
                            )
                            run_level = levels[edge_local]
                            run_start_local = edge_local

                    uart.feed_run(
                        chunk_start + run_start_local,
                        chunk_start + sample_count,
                        run_level,
                    )

                sample_cursor += sample_count

                if progress:
                    now = time.monotonic()
                    if now - last_progress >= 2.0:
                        seconds = sample_cursor / metadata.samplerate
                        print(
                            f"scanned {seconds:.3f}s, member {member_index}/{member_count}, "
                            f"uart_bytes={uart.decoded_bytes}",
                            file=sys.stderr,
                        )
                        last_progress = now

                if max_samples is not None and sample_cursor >= max_samples:
                    return sample_cursor

    return sample_cursor


def us_between(start_sample: int, end_sample: int, samplerate: int) -> float:
    return ((end_sample - start_sample) * 1_000_000.0) / samplerate


def sample_to_us(sample: int, samplerate: int) -> float:
    return (sample * 1_000_000.0) / samplerate


def fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}"


def frame_field(frame: CapturedFrame, name: str) -> str:
    if frame.frame is None:
        return ""
    value = frame.frame.get(name)
    if value is None:
        return ""
    if name in ("slave", "func"):
        return f"0x{int(value):02X}"
    if name == "start":
        return f"0x{int(value):04X}"
    return str(value)


def write_frames_csv(path: Path, frames: list[CapturedFrame], samplerate: int) -> None:
    fieldnames = [
        "frame_no",
        "status",
        "type",
        "slave",
        "func",
        "start_reg",
        "count",
        "byte_count",
        "crc_ok",
        "start_sample",
        "end_sample",
        "start_us",
        "end_us",
        "duration_us",
        "gap_from_previous_us",
        "raw_hex",
        "summary",
        "decoded",
        "error",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        previous: CapturedFrame | None = None
        for frame in frames:
            gap_us = None
            if previous is not None:
                gap_us = us_between(previous.end_sample, frame.start_sample, samplerate)
            previous = frame

            writer.writerow(
                {
                    "frame_no": frame.frame_no,
                    "status": frame.status,
                    "type": frame.type,
                    "slave": frame_field(frame, "slave"),
                    "func": frame_field(frame, "func"),
                    "start_reg": frame_field(frame, "start"),
                    "count": frame_field(frame, "count"),
                    "byte_count": frame_field(frame, "byte_count"),
                    "crc_ok": "" if frame.frame is None else str(bool(frame.frame.get("crc_ok"))).lower(),
                    "start_sample": frame.start_sample,
                    "end_sample": frame.end_sample,
                    "start_us": fmt_float(sample_to_us(frame.start_sample, samplerate)),
                    "end_us": fmt_float(sample_to_us(frame.end_sample, samplerate)),
                    "duration_us": fmt_float(us_between(frame.start_sample, frame.end_sample, samplerate)),
                    "gap_from_previous_us": fmt_float(gap_us),
                    "raw_hex": china_tower.hex_bytes(frame.raw),
                    "summary": frame.summary,
                    "decoded": frame.decoded,
                    "error": frame.error,
                }
            )


def sequence_timing(sequence: SequenceRow, samplerate: int) -> dict[str, float | None]:
    request = sequence.request
    response = sequence.response
    if request is None and response is None:
        return {
            "request_start_us": None,
            "request_end_us": None,
            "response_start_us": None,
            "response_end_us": None,
            "request_to_response_us": None,
            "full_exchange_us": None,
        }

    return {
        "request_start_us": None if request is None else sample_to_us(request.start_sample, samplerate),
        "request_end_us": None if request is None else sample_to_us(request.end_sample, samplerate),
        "response_start_us": None if response is None else sample_to_us(response.start_sample, samplerate),
        "response_end_us": None if response is None else sample_to_us(response.end_sample, samplerate),
        "request_to_response_us": None
        if request is None or response is None
        else us_between(request.end_sample, response.start_sample, samplerate),
        "full_exchange_us": None
        if request is None or response is None
        else us_between(request.start_sample, response.end_sample, samplerate),
    }


def write_sequences_csv(path: Path, sequences: list[SequenceRow], samplerate: int) -> None:
    fieldnames = [
        "sequence_no",
        "complete",
        "status",
        "request_frame_no",
        "response_frame_no",
        "slave",
        "func",
        "start_reg",
        "count",
        "request_start_us",
        "request_end_us",
        "response_start_us",
        "response_end_us",
        "request_to_response_us",
        "full_exchange_us",
        "request_summary",
        "response_summary",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for sequence in sequences:
            timing = sequence_timing(sequence, samplerate)
            request = sequence.request
            response = sequence.response
            source = request or response

            writer.writerow(
                {
                    "sequence_no": sequence.sequence_no,
                    "complete": str(sequence.complete).lower(),
                    "status": sequence.status,
                    "request_frame_no": "" if request is None else request.frame_no,
                    "response_frame_no": "" if response is None else response.frame_no,
                    "slave": "" if source is None else frame_field(source, "slave"),
                    "func": "" if source is None else frame_field(source, "func"),
                    "start_reg": "" if request is None else frame_field(request, "start"),
                    "count": "" if request is None else frame_field(request, "count"),
                    "request_start_us": fmt_float(timing["request_start_us"]),
                    "request_end_us": fmt_float(timing["request_end_us"]),
                    "response_start_us": fmt_float(timing["response_start_us"]),
                    "response_end_us": fmt_float(timing["response_end_us"]),
                    "request_to_response_us": fmt_float(timing["request_to_response_us"]),
                    "full_exchange_us": fmt_float(timing["full_exchange_us"]),
                    "request_summary": "" if request is None else request.summary,
                    "response_summary": "" if response is None else response.summary,
                }
            )


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    fraction = index - lower
    return ordered[lower] + ((ordered[upper] - ordered[lower]) * fraction)


def stats_block(label: str, values: list[float]) -> list[str]:
    if not values:
        return [f"- {label}: n=0"]
    return [
        (
            f"- {label}: n={len(values)}, avg={statistics.fmean(values):.3f} us, "
            f"min={min(values):.3f} us, max={max(values):.3f} us, "
            f"p50={percentile(values, 0.50):.3f} us, "
            f"p95={percentile(values, 0.95):.3f} us"
        )
    ]


def write_summary_md(
    path: Path,
    sr_path: Path,
    metadata: SrMetadata,
    total_samples: int,
    assembler: ChinaTowerAssembler,
    uart: Uart8n1Decoder,
    elapsed_s: float,
) -> None:
    frames = assembler.frames
    sequences = assembler.sequences
    complete_sequences = [sequence for sequence in sequences if sequence.complete]
    request_to_response_values = [
        sequence_timing(sequence, metadata.samplerate)["request_to_response_us"]
        for sequence in complete_sequences
    ]
    full_exchange_values = [
        sequence_timing(sequence, metadata.samplerate)["full_exchange_us"]
        for sequence in complete_sequences
    ]
    request_to_response_clean = [float(value) for value in request_to_response_values if value is not None]
    full_exchange_clean = [float(value) for value in full_exchange_values if value is not None]

    request_count = sum(1 for frame in frames if frame.type == "request")
    response_count = sum(1 for frame in frames if frame.type == "response")
    exception_count = sum(1 for frame in frames if frame.type == "exception")
    invalid_count = sum(1 for frame in frames if frame.type == "invalid")
    crc_bad_count = sum(1 for frame in frames if frame.status == "crc_bad")

    lines = [
        f"# Capture Summary: {sr_path.name}",
        "",
        "## Decode Settings",
        "",
        f"- Protocol: china_tower_modbus",
        f"- Samplerate: {metadata.samplerate} Hz",
        f"- Total samples scanned: {total_samples}",
        f"- Capture duration: {total_samples / metadata.samplerate:.6f} s",
        f"- Analysis runtime: {elapsed_s:.3f} s",
        f"- UART bytes decoded: {uart.decoded_bytes}",
        f"- UART invalid start bits: {uart.invalid_start_bits}",
        f"- UART invalid stop bits: {uart.invalid_stop_bits}",
        "",
        "## Frames",
        "",
        f"- Total frames: {len(frames)}",
        f"- Requests: {request_count}",
        f"- Responses: {response_count}",
        f"- Exceptions: {exception_count}",
        f"- CRC bad frames: {crc_bad_count}",
        f"- Invalid frames: {invalid_count}",
        f"- Incomplete frame buffers dropped on gaps: {assembler.incomplete_frames}",
        "",
        "## Sequences",
        "",
        f"- Total sequence rows: {len(sequences)}",
        f"- Complete request/response sequences: {len(complete_sequences)}",
        f"- Incomplete/orphan rows: {len(sequences) - len(complete_sequences)}",
        "",
        "## Timing",
        "",
        *stats_block("request_to_response_us", request_to_response_clean),
        *stats_block("full_exchange_us", full_exchange_clean),
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze sigrok/PulseView captures offline.")
    parser.add_argument("capture", type=Path, help="Path to a .sr capture file.")
    parser.add_argument(
        "--protocol",
        choices=("china_tower_modbus",),
        required=True,
        help="Protocol decoder to run.",
    )
    parser.add_argument("--channel", default="CH0", help="Logic channel/probe name to decode.")
    parser.add_argument("--baud", type=int, default=9600, help="UART baud rate.")
    parser.add_argument(
        "--invert-rx",
        dest="invert_rx",
        action="store_true",
        default=None,
        help="Invert the selected logic channel before UART decoding.",
    )
    parser.add_argument(
        "--no-invert-rx",
        dest="invert_rx",
        action="store_false",
        help="Do not invert the selected logic channel before UART decoding.",
    )
    parser.add_argument(
        "--inter-frame-gap-us",
        type=int,
        default=5000,
        help="Idle gap used to drop incomplete Modbus frame buffers.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "analysis" / "out",
        help="Directory for generated CSV/Markdown files.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Stop after this many samples. Useful for quick debugging.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    capture = args.capture.resolve()
    if not capture.exists():
        print(f"Capture not found: {capture}", file=sys.stderr)
        return 2

    invert_rx = args.invert_rx
    if invert_rx is None:
        invert_rx = args.protocol == "china_tower_modbus"

    metadata = read_sr_metadata(capture)
    assembler = ChinaTowerAssembler(
        samplerate=metadata.samplerate,
        inter_frame_gap_us=args.inter_frame_gap_us,
    )
    uart = Uart8n1Decoder(
        samplerate=metadata.samplerate,
        baud=args.baud,
        on_byte=assembler.feed_byte,
    )

    started = time.monotonic()
    total_samples = stream_uart_from_sr(
        sr_path=capture,
        metadata=metadata,
        channel=args.channel,
        invert=invert_rx,
        uart=uart,
        max_samples=args.max_samples,
        progress=not args.quiet,
    )
    assembler.finish()
    elapsed = time.monotonic() - started

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    output_stem = capture.stem
    frames_path = out_dir / f"{output_stem}.frames.csv"
    sequences_path = out_dir / f"{output_stem}.sequences.csv"
    summary_path = out_dir / f"{output_stem}.summary.md"

    write_frames_csv(frames_path, assembler.frames, metadata.samplerate)
    write_sequences_csv(sequences_path, assembler.sequences, metadata.samplerate)
    write_summary_md(
        summary_path,
        capture,
        metadata,
        total_samples,
        assembler,
        uart,
        elapsed,
    )

    print(f"frames: {frames_path}")
    print(f"sequences: {sequences_path}")
    print(f"summary: {summary_path}")
    print(
        f"decoded {len(assembler.frames)} frames and {len(assembler.sequences)} sequence rows "
        f"in {elapsed:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
