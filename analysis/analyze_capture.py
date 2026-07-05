#!/usr/bin/env python3
"""Offline sigrok/PulseView capture analysis.

The analyzer is dependency-free and streams `.sr` ZIP captures directly. It can
decode UART/RS485 captures into protocol frames and Classic CAN captures into
CAN packets, then writes CSV tables, generated summaries, and readable reports.
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DECODERS_DIR = REPO_ROOT / "decoders"
EXAMPLES_BRIDGE_DIR = REPO_ROOT / "examples" / "bridge"
EXAMPLES_FORWARD_DIR = REPO_ROOT / "examples" / "bridge_forward"
EXAMPLES_DIRECT_DIR = REPO_ROOT / "examples" / "direct"
DEFAULT_OUT_DIR = REPO_ROOT / "analysis" / "out"
DEFAULT_REPORT_DIR = REPO_ROOT / "analysis" / "reports"
DEFAULT_README = REPO_ROOT / "analysis" / "README.md"
README_REPORTS_BEGIN = "<!-- BEGIN GENERATED CONSOLIDATED REPORTS -->"
README_REPORTS_END = "<!-- END GENERATED CONSOLIDATED REPORTS -->"

TRANSITION_RE = re.compile(b"\x00\x01|\x01\x00")


@dataclass(frozen=True)
class ProtocolConfig:
    protocol: str
    title: str
    helper_path: Path
    kind: str
    capture: Path
    channel: str
    invert: bool
    baud: int | None = None
    bitrate: int | None = None
    sample_point_pct: float = 70.0
    inter_frame_gap_us: int = 5000
    cycle_gap_us: int = 100000


@dataclass(frozen=True)
class TopologyComparisonGroup:
    name: str
    target_protocols: tuple[str, ...]


PROTOCOL_CONFIGS: dict[str, ProtocolConfig] = {
    "china_tower_modbus": ProtocolConfig(
        "china_tower_modbus",
        "China Tower Modbus RS485",
        DECODERS_DIR / "china_tower_modbus" / "china_tower_modbus.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "china-tower-modbus-rs485-raw-capture.sr",
        "CH0",
        True,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "daly_rs485": ProtocolConfig(
        "daly_rs485",
        "Daly RS485",
        DECODERS_DIR / "daly_rs485" / "daly_rs485.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "easun-daly-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "growatt_rs485": ProtocolConfig(
        "growatt_rs485",
        "Growatt RS485",
        DECODERS_DIR / "growatt_rs485" / "growatt.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "growatt-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "growatt_seplos_rs485": ProtocolConfig(
        "growatt_seplos_rs485",
        "Growatt RS485 Seplos",
        DECODERS_DIR / "growatt_rs485" / "growatt.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "growatt-seplos-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "direct_growatt_rs485": ProtocolConfig(
        "direct_growatt_rs485",
        "Growatt RS485 JKBMS",
        DECODERS_DIR / "growatt_rs485" / "growatt.py",
        "modbus",
        EXAMPLES_DIRECT_DIR / "growatt-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "forward_growatt_rs485": ProtocolConfig(
        "forward_growatt_rs485",
        "Growatt RS485 JKBMS",
        DECODERS_DIR / "growatt_rs485" / "growatt.py",
        "modbus",
        EXAMPLES_FORWARD_DIR / "growatt-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "forward_growatt_seplos_rs485": ProtocolConfig(
        "forward_growatt_seplos_rs485",
        "Growatt RS485 Seplos",
        DECODERS_DIR / "growatt_rs485" / "growatt.py",
        "modbus",
        EXAMPLES_FORWARD_DIR / "growatt-seplos-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "jkbms_modbus": ProtocolConfig(
        "jkbms_modbus",
        "JKBMS Modbus RS485",
        DECODERS_DIR / "jkbms_modbus" / "jkbms_modbus.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "jkbms-modbus-rs485-raw-capture.sr",
        "CH0",
        True,
        baud=115200,
        inter_frame_gap_us=2000,
    ),
    "pace_modbus": ProtocolConfig(
        "pace_modbus",
        "PACE Modbus RS485",
        DECODERS_DIR / "pace_modbus" / "pace_modbus.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "pace-modbus-rs485-raw-capture.sr",
        "CH0",
        True,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "pylon_rs485": ProtocolConfig(
        "pylon_rs485",
        "Pylon RS485",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_BRIDGE_DIR / "pylon-rs485-raw-capture.sr",
        "CH0",
        True,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "anenji_pylon_rs485": ProtocolConfig(
        "anenji_pylon_rs485",
        "Anenji Pylon RS485",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_BRIDGE_DIR / "anenji-pylon-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "direct_anenji_jkbms_pylon_rs485": ProtocolConfig(
        "direct_anenji_jkbms_pylon_rs485",
        "Anenji Pylon RS485 JKBMS",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_DIRECT_DIR / "anenji-jkbms-pylon-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "direct_anenji_seplos_pylon_rs485": ProtocolConfig(
        "direct_anenji_seplos_pylon_rs485",
        "Anenji Pylon RS485 Seplos",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_DIRECT_DIR / "anenji-seplos-pylon-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "forward_anenji_pylon_rs485": ProtocolConfig(
        "forward_anenji_pylon_rs485",
        "Anenji Pylon RS485 JKBMS",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_FORWARD_DIR / "anenji-pylon-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "forward_anenji_seplos_pylon_rs485": ProtocolConfig(
        "forward_anenji_seplos_pylon_rs485",
        "Anenji Pylon RS485 Seplos",
        DECODERS_DIR / "pylon_rs485" / "pylon.py",
        "pylon_rs485",
        EXAMPLES_FORWARD_DIR / "anenji-seplos-pylon-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "voltronic_modbus": ProtocolConfig(
        "voltronic_modbus",
        "Voltronic Modbus RS485",
        DECODERS_DIR / "voltronic_modbus" / "voltronic_modbus.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "voltronic-modbus-rs485-raw-capture.sr",
        "CH1",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "wow_modbus": ProtocolConfig(
        "wow_modbus",
        "WOW Modbus RS485",
        DECODERS_DIR / "wow_modbus" / "wow_modbus.py",
        "modbus",
        EXAMPLES_BRIDGE_DIR / "wow-modbus-rs485-raw-capture.sr",
        "CH0",
        False,
        baud=9600,
        inter_frame_gap_us=5000,
    ),
    "deye_can": ProtocolConfig(
        "deye_can",
        "Deye CAN",
        DECODERS_DIR / "deye_can" / "deye_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "deye-can-raw-capture.sr",
        "CH1",
        True,
        bitrate=500000,
    ),
    "goodwe_can": ProtocolConfig(
        "goodwe_can",
        "GoodWe CAN",
        DECODERS_DIR / "goodwe_can" / "goodwe_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "goodwe-can-raw-capture.sr",
        "CH1",
        True,
        bitrate=500000,
    ),
    "growatt_can": ProtocolConfig(
        "growatt_can",
        "Growatt CAN",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "growatt-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "growatt_seplos_can": ProtocolConfig(
        "growatt_seplos_can",
        "Growatt CAN Seplos",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "growatt-seplos-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "direct_growatt_can": ProtocolConfig(
        "direct_growatt_can",
        "Growatt CAN JKBMS",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_DIRECT_DIR / "growatt-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
        sample_point_pct=75.0,
    ),
    "direct_growatt_seplos_can": ProtocolConfig(
        "direct_growatt_seplos_can",
        "Growatt CAN Seplos",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_DIRECT_DIR / "growatt-seplos-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
        sample_point_pct=75.0,
    ),
    "forward_growatt_can": ProtocolConfig(
        "forward_growatt_can",
        "Growatt CAN JKBMS",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_FORWARD_DIR / "growatt-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "forward_growatt_seplos_can": ProtocolConfig(
        "forward_growatt_seplos_can",
        "Growatt CAN Seplos",
        DECODERS_DIR / "growatt_can" / "growatt_can.py",
        "can",
        EXAMPLES_FORWARD_DIR / "growatt-seplos-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "jkbms_can": ProtocolConfig(
        "jkbms_can",
        "JKBMS CAN",
        DECODERS_DIR / "jkbms_can" / "jkbms_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "jkbms-can-raw-capture.sr",
        "CH1",
        True,
        bitrate=250000,
    ),
    "pylon_can": ProtocolConfig(
        "pylon_can",
        "Pylon CAN",
        DECODERS_DIR / "pylon_can" / "pylon_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "pylon-can-raw-capture.sr",
        "CH1",
        True,
        bitrate=500000,
    ),
    "sma_can": ProtocolConfig(
        "sma_can",
        "SMA CAN",
        DECODERS_DIR / "sma_can" / "sma_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "sma-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "sofar_can": ProtocolConfig(
        "sofar_can",
        "Sofar CAN",
        DECODERS_DIR / "sofar_can" / "sofar_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "sofar-can-raw-capture.sr",
        "CH0",
        True,
        bitrate=500000,
    ),
    "victron_can": ProtocolConfig(
        "victron_can",
        "Victron CAN",
        DECODERS_DIR / "victron_can" / "victron_can.py",
        "can",
        EXAMPLES_BRIDGE_DIR / "victron-can-raw-capture.sr",
        "CH1",
        True,
        bitrate=500000,
    ),
}


TOPOLOGY_COMPARISON_GROUPS: tuple[TopologyComparisonGroup, ...] = (
    TopologyComparisonGroup(
        "Growatt CAN JKBMS",
        ("growatt_can", "forward_growatt_can", "direct_growatt_can"),
    ),
    TopologyComparisonGroup(
        "Growatt CAN SeplosBMS",
        ("growatt_seplos_can", "forward_growatt_seplos_can", "direct_growatt_seplos_can"),
    ),
    TopologyComparisonGroup(
        "Growatt RS485 JKBMS",
        ("growatt_rs485", "forward_growatt_rs485", "direct_growatt_rs485"),
    ),
    TopologyComparisonGroup(
        "Growatt RS485 SeplosBMS",
        ("growatt_seplos_rs485", "forward_growatt_seplos_rs485"),
    ),
    TopologyComparisonGroup(
        "Anenji Pylon RS485 JKBMS",
        ("anenji_pylon_rs485", "forward_anenji_pylon_rs485", "direct_anenji_jkbms_pylon_rs485"),
    ),
    TopologyComparisonGroup(
        "Anenji Pylon RS485 SeplosBMS",
        ("forward_anenji_seplos_pylon_rs485", "direct_anenji_seplos_pylon_rs485"),
    ),
)


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
    frame: dict
    raw: bytes
    start_sample: int
    end_sample: int
    summary: str
    decoded: str
    error: str = ""

    @property
    def type(self) -> str:
        return str(self.frame.get("type", "frame"))


@dataclass
class SequenceRow:
    sequence_no: int
    complete: bool
    status: str
    request: CapturedFrame | None
    response: CapturedFrame | None


@dataclass
class CycleRow:
    sequence_no: int
    frames: list[CapturedFrame]
    gap_from_previous_us: float | None


@dataclass
class AnalysisResult:
    config: ProtocolConfig
    metadata: SrMetadata
    total_samples: int
    elapsed_s: float
    frames: list[CapturedFrame]
    sequences: list[SequenceRow] = field(default_factory=list)
    cycles: list[CycleRow] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class OverviewRecord:
    config: ProtocolConfig
    metrics: dict[str, str]


@dataclass(frozen=True)
class ThreeModeMetric:
    name: str
    label: str


def load_helper_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load helper module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def helper_for(config: ProtocolConfig):
    return load_helper_module(f"offline_{config.protocol}", config.helper_path)


def parse_samplerate(value: str) -> int:
    text = value.strip().replace(" ", "")
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([kKmMgG]?)[hH][zZ]", text)
    if not match:
        raise ValueError(f"Unsupported samplerate value: {value!r}")
    number = float(match.group(1))
    scale = {"": 1, "k": 1_000, "m": 1_000_000, "g": 1_000_000_000}[match.group(2).lower()]
    return int(round(number * scale))


def read_sr_metadata(sr_path: Path) -> SrMetadata:
    with zipfile.ZipFile(sr_path) as archive:
        metadata_text = archive.read("metadata").decode("utf-8", errors="replace")

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read_string(metadata_text)
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
    return int(match.group(1)) if match else None


def iter_logic_members(archive: zipfile.ZipFile) -> Iterable[str]:
    members = []
    for name in archive.namelist():
        index = logic_member_index(name)
        if index is not None:
            members.append((index, name))
    for _index, name in sorted(members, key=lambda item: item[0]):
        yield name


def make_level_table(bit_in_byte: int, invert: bool) -> bytes:
    invert_bit = 1 if invert else 0
    return bytes((((value >> bit_in_byte) & 1) ^ invert_bit) for value in range(256))


def stream_logic_runs_from_sr(
    sr_path: Path,
    metadata: SrMetadata,
    channel: str,
    invert: bool,
    on_run: Callable[[int, int, int], None],
    max_samples: int | None = None,
    progress_label: str = "",
    progress: bool = True,
) -> int:
    if channel not in metadata.probes:
        available = ", ".join(sorted(metadata.probes))
        raise ValueError(f"Unknown channel {channel!r}. Available channels: {available}")

    bit_index = metadata.probes[channel]
    byte_index = bit_index // 8
    bit_in_byte = bit_index % 8
    if byte_index >= metadata.unitsize:
        raise ValueError(f"Channel {channel!r} maps beyond unitsize={metadata.unitsize}")

    level_table = make_level_table(bit_in_byte, invert)
    sample_cursor = 0
    last_progress = time.monotonic()
    chunk_size = 4 * 1024 * 1024

    with zipfile.ZipFile(sr_path) as archive:
        members = list(iter_logic_members(archive))
        member_count = len(members)
        for member_index, member_name in enumerate(members, start=1):
            with archive.open(member_name) as logic_file:
                while True:
                    chunk = logic_file.read(chunk_size)
                    if not chunk:
                        break

                    usable_len = len(chunk) - (len(chunk) % metadata.unitsize)
                    if usable_len <= 0:
                        continue
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
                                on_run(chunk_start + run_start_local, chunk_start + edge_local, run_level)
                                run_level = levels[edge_local]
                                run_start_local = edge_local
                        on_run(chunk_start + run_start_local, chunk_start + sample_count, run_level)

                    sample_cursor += sample_count
                    if progress:
                        now = time.monotonic()
                        if now - last_progress >= 2.0:
                            seconds = sample_cursor / metadata.samplerate
                            suffix = f", {progress_label}" if progress_label else ""
                            print(
                                f"scanned {seconds:.3f}s, member {member_index}/{member_count}{suffix}",
                                file=sys.stderr,
                            )
                            last_progress = now

                    if max_samples is not None and sample_cursor >= max_samples:
                        return sample_cursor

    return sample_cursor


def sample_to_us(sample: int, samplerate: int) -> float:
    return (sample * 1_000_000.0) / samplerate


def us_between(start_sample: int, end_sample: int, samplerate: int) -> float:
    return ((end_sample - start_sample) * 1_000_000.0) / samplerate


def fmt_float(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def hex_bytes(data: Iterable[int]) -> str:
    return " ".join(f"{value & 0xFF:02X}" for value in data)


class Uart8n1Decoder:
    def __init__(self, samplerate: int, baud: int, on_byte: Callable[[UartByte], None]):
        self.samplerate = samplerate
        self.baud = baud
        self.bit_time = samplerate / float(baud)
        self.on_byte = on_byte
        self.previous_level: int | None = None
        self.pending: dict | None = None
        self.decoded_bytes = 0
        self.invalid_start_bits = 0
        self.invalid_stop_bits = 0

    def _start_byte(self, start_sample: int) -> None:
        self.pending = {
            "start_sample": start_sample,
            "end_sample": int(round(start_sample + 10.0 * self.bit_time)),
            "sample_points": [
                int(round(start_sample + ((0.5 + bit_index) * self.bit_time)))
                for bit_index in range(10)
            ],
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
        self.on_byte(UartByte(value, start_sample, end_sample))

    def feed_run(self, start_sample: int, end_sample: int, level: int) -> None:
        if start_sample >= end_sample:
            return
        if self.previous_level is None:
            self.previous_level = level
        if self.pending is None and self.previous_level == 1 and level == 0:
            self._start_byte(start_sample)

        while self.pending is not None:
            levels = self.pending["levels"]
            points = self.pending["sample_points"]
            next_index = len(levels)
            if next_index >= len(points):
                self._finish_pending()
                break
            sample_at = points[next_index]
            if sample_at < start_sample:
                levels.append(level)
                continue
            if sample_at >= end_sample:
                break
            levels.append(level)
            if len(levels) == len(points):
                self._finish_pending()
                break

        self.previous_level = level


class ModbusAssembler:
    def __init__(self, config: ProtocolConfig, helper, samplerate: int):
        self.config = config
        self.helper = helper
        self.samplerate = samplerate
        self.gap_samples = int((config.inter_frame_gap_us * samplerate) / 1_000_000)
        self.buf = bytearray()
        self.positions: list[tuple[int, int]] = []
        self.frames: list[CapturedFrame] = []
        self.sequences: list[SequenceRow] = []
        self.pending: dict[tuple[int, int], CapturedFrame] = {}
        self.incomplete_frames = 0
        self.bytes_seen = 0

    def _reset_buffer(self) -> None:
        self.buf = bytearray()
        self.positions = []

    def _request_hint(self, captured: CapturedFrame) -> dict:
        return {
            "slave": captured.frame.get("slave"),
            "func": captured.frame.get("func"),
            "start": captured.frame.get("start"),
            "count": captured.frame.get("count"),
        }

    def _parse_frame(self, raw: bytes) -> dict:
        for request in list(self.pending.values()):
            try:
                return self.helper.parse_frame(raw, self._request_hint(request))
            except Exception:
                pass
        return self.helper.parse_frame(raw, None)

    def _append_sequence(
        self,
        complete: bool,
        status: str,
        request: CapturedFrame | None,
        response: CapturedFrame | None,
    ) -> None:
        self.sequences.append(SequenceRow(len(self.sequences) + 1, complete, status, request, response))

    def _remember_request(self, captured: CapturedFrame) -> None:
        key = (int(captured.frame.get("slave", 0)), int(captured.frame.get("func", 0)))
        previous = self.pending.get(key)
        if previous is not None:
            self._append_sequence(False, "request_replaced", previous, None)
        self.pending[key] = captured

    def _pair_response(self, captured: CapturedFrame) -> None:
        key = (int(captured.frame.get("slave", 0)), int(captured.frame.get("func", 0)))
        request = self.pending.pop(key, None)
        if request is None:
            func = int(captured.frame.get("func", 0))
            candidates = [
                pending
                for pending in self.pending.values()
                if int(pending.frame.get("func", 0)) == func
            ]
            if candidates:
                request = min(candidates, key=lambda item: item.frame_no)
                fallback_key = (
                    int(request.frame.get("slave", 0)),
                    int(request.frame.get("func", 0)),
                )
                self.pending.pop(fallback_key, None)
        if request is None:
            self._append_sequence(False, "orphan_response", None, captured)
            return
        self._append_sequence(True, "complete", request, captured)

    def _finish_frame(self) -> None:
        raw = bytes(self.buf)
        start_sample = self.positions[0][0]
        end_sample = self.positions[-1][1]
        try:
            frame = self._parse_frame(raw)
            summary = self.helper.frame_summary(frame)
            describe = getattr(self.helper, "describe_frame", None)
            decoded = describe(frame) if describe else summary
            status = "ok" if frame.get("crc_ok", True) else "crc_bad"
            error = ""
        except Exception as exc:
            frame = {"type": "invalid"}
            summary = f"Invalid {self.config.title} frame"
            decoded = ""
            status = "invalid"
            error = str(exc)

        captured = CapturedFrame(len(self.frames) + 1, status, frame, raw, start_sample, end_sample, summary, decoded, error)
        self.frames.append(captured)

        if frame.get("type") == "request":
            self._remember_request(captured)
        elif frame.get("type") in ("response", "exception"):
            self._pair_response(captured)

        self._reset_buffer()

    def _flush_incomplete(self) -> None:
        if self.buf:
            self.incomplete_frames += 1
            self._reset_buffer()

    def feed_byte(self, byte: UartByte) -> None:
        self.bytes_seen += 1
        if self.buf and self.gap_samples > 0 and byte.start_sample - self.positions[-1][1] > self.gap_samples:
            self._flush_incomplete()

        self.buf.append(byte.value)
        self.positions.append((byte.start_sample, byte.end_sample))
        if self.helper.frame_complete(self.buf):
            self._finish_frame()
        elif len(self.buf) > 320:
            self._flush_incomplete()

    def finish(self) -> None:
        self._flush_incomplete()
        for request in sorted(self.pending.values(), key=lambda item: item.frame_no):
            self._append_sequence(False, "unmatched_request", request, None)
        self.pending.clear()


class PylonRs485Assembler:
    def __init__(self, config: ProtocolConfig, helper):
        self.config = config
        self.helper = helper
        self.buf = bytearray()
        self.positions: list[tuple[int, int]] = []
        self.frames: list[CapturedFrame] = []
        self.sequences: list[SequenceRow] = []
        self.pending: dict[int, CapturedFrame] = {}
        self.incomplete_frames = 0
        self.bytes_seen = 0

    def _reset_buffer(self) -> None:
        self.buf = bytearray()
        self.positions = []

    def _append_sequence(
        self,
        complete: bool,
        status: str,
        request: CapturedFrame | None,
        response: CapturedFrame | None,
    ) -> None:
        self.sequences.append(SequenceRow(len(self.sequences) + 1, complete, status, request, response))

    def _pending_cid2(self, frame: dict) -> int | None:
        pending = self.pending.get(int(frame.get("addr", 0)))
        if pending is None:
            return None
        return int(pending.frame.get("code", 0))

    def _finish_frame(self) -> None:
        raw = bytes(self.buf)
        start_sample = self.positions[0][0]
        end_sample = self.positions[-1][1]
        try:
            frame = self.helper.parse_frame(raw)
            pending_cid2 = self._pending_cid2(frame)
            is_request = bool(self.helper.is_request(frame))
            is_response = frame.get("cid1") == 0x46 and frame.get("code") == 0x00
            frame["type"] = "request" if is_request else "response" if is_response else "frame"
            summary = self.helper.frame_summary(frame, pending_cid2=pending_cid2)
            decoded = self.helper.describe_info(frame, pending_cid2)
            status = "ok" if frame.get("checksum_ok") and frame.get("length_ok") else "checksum_bad"
            error = ""
        except Exception as exc:
            frame = {"type": "invalid"}
            summary = "Invalid Pylon RS485 frame"
            decoded = ""
            status = "invalid"
            error = str(exc)
            pending_cid2 = None

        captured = CapturedFrame(len(self.frames) + 1, status, frame, raw, start_sample, end_sample, summary, decoded, error)
        self.frames.append(captured)

        if frame.get("type") == "request":
            addr = int(frame.get("addr", 0))
            previous = self.pending.get(addr)
            if previous is not None:
                self._append_sequence(False, "request_replaced", previous, None)
            self.pending[addr] = captured
        elif frame.get("type") == "response":
            addr = int(frame.get("addr", 0))
            request = self.pending.pop(addr, None)
            if request is None:
                self._append_sequence(False, "orphan_response", None, captured)
            else:
                self._append_sequence(True, "complete", request, captured)

        self._reset_buffer()

    def feed_byte(self, byte: UartByte) -> None:
        self.bytes_seen += 1
        if byte.value == ord("~"):
            self.buf = bytearray([byte.value])
            self.positions = [(byte.start_sample, byte.end_sample)]
            return
        if not self.buf:
            return
        self.buf.append(byte.value)
        self.positions.append((byte.start_sample, byte.end_sample))
        if byte.value == ord("\r"):
            self._finish_frame()
        elif len(self.buf) > 260:
            self.incomplete_frames += 1
            self._reset_buffer()

    def finish(self) -> None:
        if self.buf:
            self.incomplete_frames += 1
            self._reset_buffer()
        for request in sorted(self.pending.values(), key=lambda item: item.frame_no):
            self._append_sequence(False, "unmatched_request", request, None)
        self.pending.clear()


def bits_to_int(bits: list[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | (bit & 1)
    return value


class ClassicCanDecoder:
    def __init__(
        self,
        config: ProtocolConfig,
        helper,
        samplerate: int,
        on_frame: Callable[[CapturedFrame], None],
    ):
        self.config = config
        self.helper = helper
        self.samplerate = samplerate
        self.bit_time = samplerate / float(config.bitrate or 500000)
        self.sample_point = config.sample_point_pct / 100.0
        self.on_frame = on_frame
        self.previous_level: int | None = None
        self.reset()
        self.frames_seen = 0
        self.stuff_errors = 0
        self.decode_errors = 0

    def reset(self) -> None:
        self.in_frame = False
        self.sof_sample = 0
        self.next_bit_index = 0
        self.raw_bits: list[int] = []
        self.raw_samples: list[int] = []
        self.destuffed_bits: list[int] = []
        self.destuffed_samples: list[int] = []
        self.last_destuffed: int | None = None
        self.run_len = 0
        self.skip_next_stuff = False
        self.destuff_active = True
        self.expected_destuffed: int | None = None
        self.tail_bits_after_crc = 0

    def _start_frame(self, start_sample: int) -> None:
        self.reset()
        self.in_frame = True
        self.sof_sample = start_sample

    def _sample_at(self, bit_index: int) -> int:
        return int(round(self.sof_sample + ((bit_index + self.sample_point) * self.bit_time)))

    def _expected_destuffed_bits(self) -> int | None:
        bits = self.destuffed_bits
        if len(bits) < 19 or bits[0] != 0:
            return None
        ide = bits[13]
        if ide == 0:
            dlc = bits_to_int(bits[15:19])
            if dlc > 8:
                return None
            return 19 + (dlc * 8) + 15
        if len(bits) < 39:
            return None
        dlc = bits_to_int(bits[35:39])
        if dlc > 8:
            return None
        return 39 + (dlc * 8) + 15

    def _packet_from_bits(self) -> tuple[str, int, str, int, list[int]]:
        bits = self.destuffed_bits
        if bits[13] == 0:
            can_id = bits_to_int(bits[1:12])
            rtr = "remote" if bits[12] else "data"
            dlc = bits_to_int(bits[15:19])
            data_start = 19
            frame_type = "standard"
        else:
            base_id = bits_to_int(bits[1:12])
            ext_id = bits_to_int(bits[14:32])
            can_id = (base_id << 18) | ext_id
            rtr = "remote" if bits[32] else "data"
            dlc = bits_to_int(bits[35:39])
            data_start = 39
            frame_type = "extended"

        payload = []
        for pos in range(data_start, data_start + min(dlc, 8) * 8, 8):
            payload.append(bits_to_int(bits[pos:pos + 8]))
        return frame_type, can_id, rtr, dlc, payload

    def _accept_destuffed_bit(self, bit: int, sample: int) -> None:
        self.destuffed_bits.append(bit)
        self.destuffed_samples.append(sample)
        if self.last_destuffed is None or bit != self.last_destuffed:
            self.last_destuffed = bit
            self.run_len = 1
        else:
            self.run_len += 1
            if self.run_len == 5:
                self.skip_next_stuff = True

        expected = self._expected_destuffed_bits()
        if expected is not None:
            self.expected_destuffed = expected
            if len(self.destuffed_bits) >= expected:
                self.destuff_active = False

    def _accept_raw_bit(self, bit: int, sample: int) -> None:
        self.raw_bits.append(bit)
        self.raw_samples.append(sample)

        if self.destuff_active:
            if self.skip_next_stuff:
                if bit == self.last_destuffed:
                    self.stuff_errors += 1
                self.skip_next_stuff = False
                self.run_len = 0
                return
            self._accept_destuffed_bit(bit, sample)
            return

        self.tail_bits_after_crc += 1
        if self.tail_bits_after_crc >= 10:
            self._finish_frame(sample)

    def _finish_frame(self, end_sample: int) -> None:
        try:
            packet = self._packet_from_bits()
            frame_type, can_id, rtr_type, dlc, payload = packet
            summary = self.helper.frame_summary(packet)
            decoded = self.helper.describe_packet(packet)
            raw = bytes(payload)
            status = "ok"
            error = ""
            frame = {
                "type": "can",
                "frame_type": frame_type,
                "can_id": can_id,
                "rtr_type": rtr_type,
                "dlc": dlc,
                "data": payload,
            }
        except Exception as exc:
            self.decode_errors += 1
            raw = b""
            status = "invalid"
            error = str(exc)
            summary = f"Invalid {self.config.title} frame"
            decoded = ""
            frame = {"type": "invalid"}

        if status == "ok":
            self.frames_seen += 1
            captured = CapturedFrame(
                self.frames_seen,
                status,
                frame,
                raw,
                self.sof_sample,
                end_sample,
                summary,
                decoded,
                error,
            )
            self.on_frame(captured)
        self.reset()

    def feed_run(self, start_sample: int, end_sample: int, level: int) -> None:
        if start_sample >= end_sample:
            return
        if self.previous_level is None:
            self.previous_level = level
        if not self.in_frame and self.previous_level == 1 and level == 0:
            self._start_frame(start_sample)

        while self.in_frame:
            sample_at = self._sample_at(self.next_bit_index)
            if sample_at < start_sample:
                self.next_bit_index += 1
                continue
            if sample_at >= end_sample:
                break
            self._accept_raw_bit(level, sample_at)
            self.next_bit_index += 1
            if self.next_bit_index > 260:
                self.decode_errors += 1
                self.reset()
                break

        self.previous_level = level


def group_can_cycles(frames: list[CapturedFrame], samplerate: int, gap_us: int) -> list[CycleRow]:
    cycles: list[CycleRow] = []
    current: list[CapturedFrame] = []
    previous_end: int | None = None
    previous_cycle_end: int | None = None
    gap_samples = int((gap_us * samplerate) / 1_000_000)

    for frame in frames:
        if current and previous_end is not None and frame.start_sample - previous_end > gap_samples:
            gap = None if previous_cycle_end is None else us_between(previous_cycle_end, current[0].start_sample, samplerate)
            cycles.append(CycleRow(len(cycles) + 1, current, gap))
            previous_cycle_end = current[-1].end_sample
            current = []
        current.append(frame)
        previous_end = frame.end_sample

    if current:
        gap = None if previous_cycle_end is None else us_between(previous_cycle_end, current[0].start_sample, samplerate)
        cycles.append(CycleRow(len(cycles) + 1, current, gap))
    return cycles


def analyze_serial_capture(
    config: ProtocolConfig,
    helper,
    metadata: SrMetadata,
    max_samples: int | None,
    progress: bool,
) -> tuple[int, list[CapturedFrame], list[SequenceRow], dict[str, int]]:
    if config.kind == "pylon_rs485":
        assembler = PylonRs485Assembler(config, helper)
    else:
        assembler = ModbusAssembler(config, helper, metadata.samplerate)
    uart = Uart8n1Decoder(metadata.samplerate, int(config.baud or 9600), assembler.feed_byte)
    total_samples = stream_logic_runs_from_sr(
        config.capture,
        metadata,
        config.channel,
        config.invert,
        uart.feed_run,
        max_samples=max_samples,
        progress_label=f"uart_bytes={uart.decoded_bytes}",
        progress=progress,
    )
    assembler.finish()
    counters = {
        "uart_bytes": uart.decoded_bytes,
        "uart_invalid_start_bits": uart.invalid_start_bits,
        "uart_invalid_stop_bits": uart.invalid_stop_bits,
        "incomplete_frames": assembler.incomplete_frames,
        "bytes_seen": assembler.bytes_seen,
    }
    return total_samples, assembler.frames, assembler.sequences, counters


def analyze_can_capture(
    config: ProtocolConfig,
    helper,
    metadata: SrMetadata,
    max_samples: int | None,
    progress: bool,
) -> tuple[int, list[CapturedFrame], list[CycleRow], dict[str, int]]:
    frames: list[CapturedFrame] = []
    decoder = ClassicCanDecoder(config, helper, metadata.samplerate, frames.append)
    total_samples = stream_logic_runs_from_sr(
        config.capture,
        metadata,
        config.channel,
        config.invert,
        decoder.feed_run,
        max_samples=max_samples,
        progress_label=f"can_frames={len(frames)}",
        progress=progress,
    )
    cycles = group_can_cycles(frames, metadata.samplerate, config.cycle_gap_us)
    counters = {
        "can_frames": len(frames),
        "can_stuff_errors": decoder.stuff_errors,
        "can_decode_errors": decoder.decode_errors,
    }
    return total_samples, frames, cycles, counters


def analyze_capture(
    config: ProtocolConfig,
    max_samples: int | None = None,
    progress: bool = True,
) -> AnalysisResult:
    helper = helper_for(config)
    metadata = read_sr_metadata(config.capture)
    started = time.monotonic()

    if config.kind == "can":
        total_samples, frames, cycles, counters = analyze_can_capture(config, helper, metadata, max_samples, progress)
        result = AnalysisResult(config, metadata, total_samples, time.monotonic() - started, frames, cycles=cycles, counters=counters)
    else:
        total_samples, frames, sequences, counters = analyze_serial_capture(config, helper, metadata, max_samples, progress)
        result = AnalysisResult(config, metadata, total_samples, time.monotonic() - started, frames, sequences=sequences, counters=counters)
    return result


def frame_value(frame: CapturedFrame, name: str) -> str:
    value = frame.frame.get(name)
    if value is None:
        return ""
    if name in ("slave", "func"):
        return f"0x{int(value):02X}"
    if name == "start":
        return f"0x{int(value):04X}"
    if name == "can_id":
        width = 8 if frame.frame.get("frame_type") == "extended" else 3
        return f"0x{int(value):0{width}X}"
    if name == "data":
        return hex_bytes(value)
    return str(value)


def write_frames_csv(path: Path, result: AnalysisResult) -> None:
    if result.config.kind == "can":
        fieldnames = [
            "frame_no",
            "status",
            "frame_type",
            "can_id",
            "rtr_type",
            "dlc",
            "start_sample",
            "end_sample",
            "start_us",
            "end_us",
            "duration_us",
            "gap_from_previous_us",
            "data_hex",
            "summary",
            "decoded",
            "error",
        ]
    else:
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
        for frame in result.frames:
            gap_us = None if previous is None else us_between(previous.end_sample, frame.start_sample, result.metadata.samplerate)
            previous = frame
            common = {
                "frame_no": frame.frame_no,
                "status": frame.status,
                "start_sample": frame.start_sample,
                "end_sample": frame.end_sample,
                "start_us": fmt_float(sample_to_us(frame.start_sample, result.metadata.samplerate)),
                "end_us": fmt_float(sample_to_us(frame.end_sample, result.metadata.samplerate)),
                "duration_us": fmt_float(us_between(frame.start_sample, frame.end_sample, result.metadata.samplerate)),
                "gap_from_previous_us": fmt_float(gap_us),
                "summary": frame.summary,
                "decoded": frame.decoded,
                "error": frame.error,
            }
            if result.config.kind == "can":
                common.update({
                    "frame_type": frame_value(frame, "frame_type"),
                    "can_id": frame_value(frame, "can_id"),
                    "rtr_type": frame_value(frame, "rtr_type"),
                    "dlc": frame_value(frame, "dlc"),
                    "data_hex": frame_value(frame, "data"),
                })
            else:
                common.update({
                    "type": frame.type,
                    "slave": frame_value(frame, "slave") or frame_value(frame, "addr"),
                    "func": frame_value(frame, "func") or frame_value(frame, "code"),
                    "start_reg": frame_value(frame, "start"),
                    "count": frame_value(frame, "count"),
                    "byte_count": frame_value(frame, "byte_count"),
                    "crc_ok": str(bool(frame.frame.get("crc_ok", frame.frame.get("checksum_ok", True)))).lower()
                    if frame.type != "invalid" else "",
                    "raw_hex": hex_bytes(frame.raw),
                })
            writer.writerow(common)


def sequence_timing(sequence: SequenceRow, samplerate: int) -> dict[str, float | None]:
    request = sequence.request
    response = sequence.response
    return {
        "request_start_us": None if request is None else sample_to_us(request.start_sample, samplerate),
        "request_end_us": None if request is None else sample_to_us(request.end_sample, samplerate),
        "response_start_us": None if response is None else sample_to_us(response.start_sample, samplerate),
        "response_end_us": None if response is None else sample_to_us(response.end_sample, samplerate),
        "request_to_response_us": None
        if request is None or response is None else us_between(request.end_sample, response.start_sample, samplerate),
        "full_exchange_us": None
        if request is None or response is None else us_between(request.start_sample, response.end_sample, samplerate),
    }


def write_serial_sequences_csv(path: Path, result: AnalysisResult) -> None:
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
        for sequence in result.sequences:
            request = sequence.request
            response = sequence.response
            source = request or response
            timing = sequence_timing(sequence, result.metadata.samplerate)
            writer.writerow({
                "sequence_no": sequence.sequence_no,
                "complete": str(sequence.complete).lower(),
                "status": sequence.status,
                "request_frame_no": "" if request is None else request.frame_no,
                "response_frame_no": "" if response is None else response.frame_no,
                "slave": "" if source is None else (frame_value(source, "slave") or frame_value(source, "addr")),
                "func": "" if source is None else (frame_value(source, "func") or frame_value(source, "code")),
                "start_reg": "" if request is None else frame_value(request, "start"),
                "count": "" if request is None else frame_value(request, "count"),
                "request_start_us": fmt_float(timing["request_start_us"]),
                "request_end_us": fmt_float(timing["request_end_us"]),
                "response_start_us": fmt_float(timing["response_start_us"]),
                "response_end_us": fmt_float(timing["response_end_us"]),
                "request_to_response_us": fmt_float(timing["request_to_response_us"]),
                "full_exchange_us": fmt_float(timing["full_exchange_us"]),
                "request_summary": "" if request is None else request.summary,
                "response_summary": "" if response is None else response.summary,
            })


def write_can_sequences_csv(path: Path, result: AnalysisResult) -> None:
    fieldnames = [
        "sequence_no",
        "frame_count",
        "start_us",
        "end_us",
        "duration_us",
        "gap_from_previous_us",
        "unique_can_ids",
        "first_frame_no",
        "last_frame_no",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cycle in result.cycles:
            start = cycle.frames[0].start_sample
            end = cycle.frames[-1].end_sample
            ids = sorted({frame_value(frame, "can_id") for frame in cycle.frames})
            writer.writerow({
                "sequence_no": cycle.sequence_no,
                "frame_count": len(cycle.frames),
                "start_us": fmt_float(sample_to_us(start, result.metadata.samplerate)),
                "end_us": fmt_float(sample_to_us(end, result.metadata.samplerate)),
                "duration_us": fmt_float(us_between(start, end, result.metadata.samplerate)),
                "gap_from_previous_us": fmt_float(cycle.gap_from_previous_us),
                "unique_can_ids": " ".join(ids),
                "first_frame_no": cycle.frames[0].frame_no,
                "last_frame_no": cycle.frames[-1].frame_no,
            })


def write_sequences_csv(path: Path, result: AnalysisResult) -> None:
    if result.config.kind == "can":
        write_can_sequences_csv(path, result)
    else:
        write_serial_sequences_csv(path, result)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + ((ordered[upper] - ordered[lower]) * (index - lower))


def stats_line(label: str, values: list[float]) -> str:
    if not values:
        return f"- {label}: n=0"
    return (
        f"- {label}: n={len(values)}, avg={statistics.fmean(values):.3f} us, "
        f"min={min(values):.3f} us, max={max(values):.3f} us, "
        f"p50={percentile(values, 0.50):.3f} us, "
        f"p95={percentile(values, 0.95):.3f} us"
    )


def serial_timing_values(result: AnalysisResult, key: str) -> list[float]:
    values = []
    for sequence in result.sequences:
        if not sequence.complete:
            continue
        value = sequence_timing(sequence, result.metadata.samplerate)[key]
        if value is not None:
            values.append(float(value))
    return values


def can_cycle_values(result: AnalysisResult, mode: str) -> list[float]:
    values = []
    for cycle in result.cycles:
        if mode == "duration":
            values.append(us_between(cycle.frames[0].start_sample, cycle.frames[-1].end_sample, result.metadata.samplerate))
        elif mode == "gap" and cycle.gap_from_previous_us is not None:
            values.append(float(cycle.gap_from_previous_us))
    return values


def topology_label_for(config: ProtocolConfig) -> str:
    parent = config.capture.parent.name
    if parent == "bridge_forward":
        return "Bridge Forward"
    if parent == "direct":
        return "Direct"
    return "Bridge"


def output_stem_for(config: ProtocolConfig) -> str:
    stem = config.capture.stem
    parent = config.capture.parent.name
    if parent == "bridge_forward":
        return f"bridge-forward-{stem}"
    if parent == "direct":
        return f"direct-{stem}"
    return stem


def display_title_for(config: ProtocolConfig) -> str:
    return f"{config.title} {topology_label_for(config)}"


def report_name_for(config: ProtocolConfig) -> str:
    stem = output_stem_for(config).replace("-raw-capture", "")
    return f"{stem}.md"


def write_summary_md(path: Path, result: AnalysisResult) -> None:
    lines = [
        f"# Capture Summary: {result.config.capture.name}",
        "",
        "## Decode Settings",
        "",
        f"- Protocol: {result.config.protocol}",
        f"- Samplerate: {result.metadata.samplerate} Hz",
        f"- Total samples scanned: {result.total_samples}",
        f"- Capture duration: {result.total_samples / result.metadata.samplerate:.6f} s",
        f"- Analysis runtime: {result.elapsed_s:.3f} s",
        f"- Channel: {result.config.channel}",
        f"- Inverted input: {str(result.config.invert).lower()}",
    ]

    if result.config.kind == "can":
        lines.extend([
            f"- CAN bitrate: {result.config.bitrate}",
            f"- CAN sample point: {result.config.sample_point_pct:.1f}%",
            f"- CAN stuff errors: {result.counters.get('can_stuff_errors', 0)}",
            f"- CAN decode errors: {result.counters.get('can_decode_errors', 0)}",
            "",
            "## Frames",
            "",
            f"- Total CAN frames: {len(result.frames)}",
            f"- Unique CAN IDs: {len({frame.frame.get('can_id') for frame in result.frames})}",
            "",
            "## Sequences",
            "",
            f"- CAN cycles: {len(result.cycles)}",
            f"- Cycle gap threshold: {result.config.cycle_gap_us} us",
            "",
            "## Timing",
            "",
            stats_line("cycle_duration_us", can_cycle_values(result, "duration")),
            stats_line("inter_cycle_gap_us", can_cycle_values(result, "gap")),
        ])
    else:
        request_count = sum(1 for frame in result.frames if frame.type == "request")
        response_count = sum(1 for frame in result.frames if frame.type == "response")
        exception_count = sum(1 for frame in result.frames if frame.type == "exception")
        invalid_count = sum(1 for frame in result.frames if frame.type == "invalid")
        bad_count = sum(1 for frame in result.frames if frame.status not in ("ok",))
        complete_count = sum(1 for sequence in result.sequences if sequence.complete)
        lines.extend([
            f"- UART baud: {result.config.baud}",
            f"- UART bytes decoded: {result.counters.get('uart_bytes', 0)}",
            f"- UART invalid start bits: {result.counters.get('uart_invalid_start_bits', 0)}",
            f"- UART invalid stop bits: {result.counters.get('uart_invalid_stop_bits', 0)}",
            "",
            "## Frames",
            "",
            f"- Total frames: {len(result.frames)}",
            f"- Requests: {request_count}",
            f"- Responses: {response_count}",
            f"- Exceptions: {exception_count}",
            f"- Bad/invalid frames: {bad_count}",
            f"- Invalid frames: {invalid_count}",
            f"- Incomplete frame buffers dropped on gaps: {result.counters.get('incomplete_frames', 0)}",
            "",
            "## Sequences",
            "",
            f"- Total sequence rows: {len(result.sequences)}",
            f"- Complete request/response sequences: {complete_count}",
            f"- Incomplete/orphan rows: {len(result.sequences) - complete_count}",
            "",
            "## Timing",
            "",
            stats_line("request_to_response_us", serial_timing_values(result, "request_to_response_us")),
            stats_line("full_exchange_us", serial_timing_values(result, "full_exchange_us")),
        ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_stats(values: list[float]) -> list[str]:
    if not values:
        return ["0", "", "", "", "", ""]
    return [
        str(len(values)),
        f"{statistics.fmean(values):,.3f}",
        f"{min(values):,.3f}",
        f"{max(values):,.3f}",
        f"{percentile(values, 0.50):,.3f}",
        f"{percentile(values, 0.95):,.3f}",
    ]


def overview_stat(values: list[float], mode: str) -> str:
    if not values:
        return ""
    if mode == "avg":
        value = statistics.fmean(values)
    elif mode == "min":
        value = min(values)
    elif mode == "max":
        value = max(values)
    elif mode == "p95":
        value = percentile(values, 0.95)
    else:
        raise ValueError(f"unknown overview stat mode: {mode}")
    return "" if value is None else f"{value:.3f}"


def write_report_md(path: Path, result: AnalysisResult) -> None:
    lines = [
        f"# {display_title_for(result.config)} Capture",
        "",
        "Source capture:",
        "",
        "```text",
        str(result.config.capture.relative_to(REPO_ROOT)).replace("\\", "/"),
        "```",
        "",
        "Analysis command:",
        "",
        "```powershell",
        f"python analysis/analyze_capture.py {str(result.config.capture.relative_to(REPO_ROOT)).replace(chr(92), '/')} --protocol {result.config.protocol} --quiet",
        "```",
        "",
        "## Decode Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total samples scanned | {result.total_samples:,} |",
        f"| Samplerate | {result.metadata.samplerate:,} Hz |",
        f"| Capture duration | {result.total_samples / result.metadata.samplerate:.6f} s |",
        f"| Analysis runtime | {result.elapsed_s:.3f} s |",
        f"| Channel | `{result.config.channel}` |",
        f"| Inverted input | `{str(result.config.invert).lower()}` |",
    ]

    if result.config.kind == "can":
        id_counts: dict[str, int] = {}
        for frame in result.frames:
            can_id = frame_value(frame, "can_id")
            id_counts[can_id] = id_counts.get(can_id, 0) + 1
        lines.extend([
            f"| CAN bitrate | {result.config.bitrate:,} bit/s |",
            f"| CAN sample point | {result.config.sample_point_pct:.1f}% |",
            f"| CAN stuff errors | {result.counters.get('can_stuff_errors', 0)} |",
            f"| CAN decode errors | {result.counters.get('can_decode_errors', 0)} |",
            "",
            "## Frame Counts",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| Total CAN frames | {len(result.frames)} |",
            f"| Unique CAN IDs | {len(id_counts)} |",
            f"| CAN cycles | {len(result.cycles)} |",
            "",
            "## Timing Statistics",
            "",
            "| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            "| `cycle_duration_us` | " + " | ".join(table_stats(can_cycle_values(result, "duration"))) + " |",
            "| `inter_cycle_gap_us` | " + " | ".join(table_stats(can_cycle_values(result, "gap"))) + " |",
            "",
            "## CAN IDs",
            "",
            "| CAN ID | Frames |",
            "| --- | ---: |",
        ])
        for can_id, count in sorted(id_counts.items()):
            lines.append(f"| `{can_id}` | {count} |")
        lines.extend([
            "",
            "Definitions:",
            "",
            "- `cycle_duration_us`: time from the first frame in a CAN burst to the last frame in that burst.",
            "- `inter_cycle_gap_us`: time between the end of one CAN burst and the start of the next burst.",
        ])
    else:
        complete_count = sum(1 for sequence in result.sequences if sequence.complete)
        lines.extend([
            f"| UART baud | {result.config.baud:,} bit/s |",
            f"| UART bytes decoded | {result.counters.get('uart_bytes', 0):,} |",
            f"| UART invalid start bits | {result.counters.get('uart_invalid_start_bits', 0)} |",
            f"| UART invalid stop bits | {result.counters.get('uart_invalid_stop_bits', 0)} |",
            "",
            "## Frame Counts",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| Total frames | {len(result.frames)} |",
            f"| Requests | {sum(1 for frame in result.frames if frame.type == 'request')} |",
            f"| Responses | {sum(1 for frame in result.frames if frame.type == 'response')} |",
            f"| Exceptions | {sum(1 for frame in result.frames if frame.type == 'exception')} |",
            f"| Bad/invalid frames | {sum(1 for frame in result.frames if frame.status != 'ok')} |",
            "",
            "## Sequence Counts",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| Total sequence rows | {len(result.sequences)} |",
            f"| Complete request/response sequences | {complete_count} |",
            f"| Incomplete/orphan rows | {len(result.sequences) - complete_count} |",
            "",
            "## Timing Statistics",
            "",
            "| Measurement | n | Avg (us) | Min (us) | Max (us) | P50 (us) | P95 (us) |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            "| `request_to_response_us` | " + " | ".join(table_stats(serial_timing_values(result, "request_to_response_us"))) + " |",
            "| `full_exchange_us` | " + " | ".join(table_stats(serial_timing_values(result, "full_exchange_us"))) + " |",
            "",
            "Definitions:",
            "",
            "```text",
            "request start ---- request end    response start ---- response end",
            "              <-- request_to_response -->",
            "<---------------------- full_exchange ----------------->",
            "```",
            "",
            "- `request_to_response_us`: response start minus request end.",
            "- `full_exchange_us`: response end minus request start.",
        ])

    lines.extend([
        "",
        "## Generated Tables",
        "",
        "```text",
        f"analysis/out/{output_stem_for(result.config)}.frames.csv",
        f"analysis/out/{output_stem_for(result.config)}.sequences.csv",
        f"analysis/out/{output_stem_for(result.config)}.summary.md",
        "```",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(result: AnalysisResult, out_dir: Path, report_dir: Path) -> tuple[Path, Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(result.config)
    frames_path = out_dir / f"{stem}.frames.csv"
    sequences_path = out_dir / f"{stem}.sequences.csv"
    summary_path = out_dir / f"{stem}.summary.md"
    report_path = report_dir / report_name_for(result.config)
    write_frames_csv(frames_path, result)
    write_sequences_csv(sequences_path, result)
    write_summary_md(summary_path, result)
    write_report_md(report_path, result)
    return frames_path, sequences_path, summary_path, report_path


def overview_csv_row(result: AnalysisResult) -> dict[str, str | int]:
    duration_s = result.total_samples / result.metadata.samplerate
    request_to_response = serial_timing_values(result, "request_to_response_us")
    full_exchange = serial_timing_values(result, "full_exchange_us")
    cycle_duration = can_cycle_values(result, "duration")
    inter_cycle_gap = can_cycle_values(result, "gap")
    complete_count = sum(1 for sequence in result.sequences if sequence.complete)
    can_ids = {frame_value(frame, "can_id") for frame in result.frames} if result.config.kind == "can" else set()
    decode_errors = (
        result.counters.get("can_stuff_errors", 0)
        + result.counters.get("can_decode_errors", 0)
        + result.counters.get("uart_invalid_start_bits", 0)
        + result.counters.get("uart_invalid_stop_bits", 0)
    )
    return {
        "target": result.config.protocol,
        "kind": result.config.kind,
        "capture": str(result.config.capture.relative_to(REPO_ROOT)).replace("\\", "/"),
        "duration_s": f"{duration_s:.6f}",
        "runtime_s": f"{result.elapsed_s:.3f}",
        "frames": len(result.frames),
        "requests": sum(1 for frame in result.frames if frame.type == "request"),
        "responses": sum(1 for frame in result.frames if frame.type == "response"),
        "sequence_rows": len(result.sequences),
        "complete_sequences": complete_count,
        "incomplete_orphan_rows": len(result.sequences) - complete_count,
        "can_cycles": len(result.cycles),
        "unique_can_ids": len(can_ids),
        "bad_or_invalid_frames": sum(1 for frame in result.frames if frame.status != "ok"),
        "decode_errors": decode_errors,
        "request_to_response_avg_us": overview_stat(request_to_response, "avg"),
        "request_to_response_p95_us": overview_stat(request_to_response, "p95"),
        "full_exchange_avg_us": overview_stat(full_exchange, "avg"),
        "full_exchange_p95_us": overview_stat(full_exchange, "p95"),
        "cycle_duration_avg_us": overview_stat(cycle_duration, "avg"),
        "cycle_duration_min_us": overview_stat(cycle_duration, "min"),
        "cycle_duration_max_us": overview_stat(cycle_duration, "max"),
        "cycle_duration_p95_us": overview_stat(cycle_duration, "p95"),
        "inter_cycle_gap_min_us": overview_stat(inter_cycle_gap, "min"),
        "inter_cycle_gap_max_us": overview_stat(inter_cycle_gap, "max"),
        "inter_cycle_gap_avg_us": overview_stat(inter_cycle_gap, "avg"),
        "inter_cycle_gap_p95_us": overview_stat(inter_cycle_gap, "p95"),
    }


def write_overview_csv(path: Path, results: list[AnalysisResult]) -> None:
    fieldnames = [
        "target",
        "kind",
        "capture",
        "duration_s",
        "runtime_s",
        "frames",
        "requests",
        "responses",
        "sequence_rows",
        "complete_sequences",
        "incomplete_orphan_rows",
        "can_cycles",
        "unique_can_ids",
        "bad_or_invalid_frames",
        "decode_errors",
        "request_to_response_avg_us",
        "request_to_response_p95_us",
        "full_exchange_avg_us",
        "full_exchange_p95_us",
        "cycle_duration_avg_us",
        "cycle_duration_min_us",
        "cycle_duration_max_us",
        "cycle_duration_p95_us",
        "inter_cycle_gap_min_us",
        "inter_cycle_gap_max_us",
        "inter_cycle_gap_avg_us",
        "inter_cycle_gap_p95_us",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(overview_csv_row(result))


def write_overview_md(path: Path, results: list[AnalysisResult]) -> None:
    serial_results = [result for result in results if result.config.kind != "can"]
    can_results = [result for result in results if result.config.kind == "can"]
    lines = [
        "# Capture Analysis Overview",
        "",
        "Generated by:",
        "",
        "```powershell",
        "python analysis/analyze_capture.py --all-captures --quiet",
        "```",
        "",
        "## RS485/UART Captures",
        "",
        "| Target | Frames | Complete | Incomplete | Req->Rsp avg (us) | Req->Rsp P95 (us) | Full avg (us) | Full P95 (us) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in serial_results:
        request_to_response = serial_timing_values(result, "request_to_response_us")
        full_exchange = serial_timing_values(result, "full_exchange_us")
        complete_count = sum(1 for sequence in result.sequences if sequence.complete)
        report_link = report_name_for(result.config)
        lines.append(
            f"| [{display_title_for(result.config)}]({report_link}) "
            f"| {len(result.frames)} "
            f"| {complete_count} "
            f"| {len(result.sequences) - complete_count} "
            f"| {overview_stat(request_to_response, 'avg')} "
            f"| {overview_stat(request_to_response, 'p95')} "
            f"| {overview_stat(full_exchange, 'avg')} "
            f"| {overview_stat(full_exchange, 'p95')} |"
        )

    lines.extend([
        "",
        "## CAN Captures",
        "",
        "| Target | Frames | CAN IDs | Cycles | Cycle min (us) | Cycle avg (us) | Cycle max (us) | Cycle P95 (us) | Gap min (us) | Gap avg (us) | Gap max (us) | Gap P95 (us) | Decode errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for result in can_results:
        cycle_duration = can_cycle_values(result, "duration")
        inter_cycle_gap = can_cycle_values(result, "gap")
        can_ids = {frame_value(frame, "can_id") for frame in result.frames}
        decode_errors = result.counters.get("can_stuff_errors", 0) + result.counters.get("can_decode_errors", 0)
        report_link = report_name_for(result.config)
        lines.append(
            f"| [{display_title_for(result.config)}]({report_link}) "
            f"| {len(result.frames)} "
            f"| {len(can_ids)} "
            f"| {len(result.cycles)} "
            f"| {overview_stat(cycle_duration, 'min')} "
            f"| {overview_stat(cycle_duration, 'avg')} "
            f"| {overview_stat(cycle_duration, 'max')} "
            f"| {overview_stat(cycle_duration, 'p95')} "
            f"| {overview_stat(inter_cycle_gap, 'min')} "
            f"| {overview_stat(inter_cycle_gap, 'avg')} "
            f"| {overview_stat(inter_cycle_gap, 'max')} "
            f"| {overview_stat(inter_cycle_gap, 'p95')} "
            f"| {decode_errors} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def overview_record_from_result(result: AnalysisResult) -> OverviewRecord:
    return OverviewRecord(
        result.config,
        {key: str(value) for key, value in overview_csv_row(result).items()},
    )


def read_overview_records(path: Path) -> list[OverviewRecord]:
    records = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            config = PROTOCOL_CONFIGS.get(row.get("target", ""))
            if config is None:
                continue
            records.append(OverviewRecord(config, dict(row)))
    return records


def comparison_topology_label_for(config: ProtocolConfig) -> str:
    parent = config.capture.parent.name
    if parent == "bridge_forward":
        return "Bridge Forward"
    if parent == "direct":
        return "Direct cable"
    return "Bridge"


def comparison_kind_label_for(config: ProtocolConfig) -> str:
    return "CAN" if config.kind == "can" else "RS485/UART"


def metric_text(record: OverviewRecord, name: str) -> str:
    return record.metrics.get(name, "")


def metric_number(record: OverviewRecord, name: str) -> float | None:
    text = metric_text(record, name)
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fixed_metric(record: OverviewRecord, name: str, decimals: int = 3) -> str:
    value = metric_number(record, name)
    return "" if value is None else f"{value:.{decimals}f}"


def rate_metric(record: OverviewRecord, numerator_name: str) -> str:
    numerator = metric_number(record, numerator_name)
    duration_s = metric_number(record, "duration_s")
    if numerator is None or duration_s is None or duration_s <= 0:
        return ""
    return f"{numerator / duration_s:.3f}"


def comparison_groups(records: list[OverviewRecord]) -> list[tuple[TopologyComparisonGroup, list[OverviewRecord]]]:
    by_target = {record.config.protocol: record for record in records}
    groups = []
    for group in TOPOLOGY_COMPARISON_GROUPS:
        group_records = [by_target[target] for target in group.target_protocols if target in by_target]
        if len(group_records) >= 2:
            groups.append((group, group_records))
    return groups


TOPOLOGY_ORDER = ("Bridge", "Bridge Forward", "Direct cable")

SERIAL_THREE_MODE_METRICS = (
    ThreeModeMetric("complete_sequences_per_s", "Complete exchanges/s"),
    ThreeModeMetric("request_to_response_avg_us", "Req->Rsp avg (us)"),
    ThreeModeMetric("request_to_response_p95_us", "Req->Rsp P95 (us)"),
    ThreeModeMetric("full_exchange_avg_us", "Full exchange avg (us)"),
    ThreeModeMetric("full_exchange_p95_us", "Full exchange P95 (us)"),
)

CAN_THREE_MODE_METRICS = (
    ThreeModeMetric("frames_per_s", "Frames/s"),
    ThreeModeMetric("can_cycles_per_s", "Cycles/s"),
    ThreeModeMetric("cycle_duration_min_us", "Cycle min (us)"),
    ThreeModeMetric("cycle_duration_avg_us", "Cycle avg (us)"),
    ThreeModeMetric("cycle_duration_max_us", "Cycle max (us)"),
    ThreeModeMetric("cycle_duration_p95_us", "Cycle P95 (us)"),
    ThreeModeMetric("inter_cycle_gap_min_us", "Inter-cycle gap min (us)"),
    ThreeModeMetric("inter_cycle_gap_avg_us", "Inter-cycle gap avg (us)"),
    ThreeModeMetric("inter_cycle_gap_max_us", "Inter-cycle gap max (us)"),
    ThreeModeMetric("inter_cycle_gap_p95_us", "Inter-cycle gap P95 (us)"),
)


def records_by_topology(records: list[OverviewRecord]) -> dict[str, OverviewRecord]:
    return {comparison_topology_label_for(record.config): record for record in records}


def is_three_mode_group(records: list[OverviewRecord]) -> bool:
    labels = set(records_by_topology(records))
    return all(label in labels for label in TOPOLOGY_ORDER)


def three_mode_groups(
    groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]],
) -> list[tuple[TopologyComparisonGroup, list[OverviewRecord]]]:
    return [(group, records) for group, records in groups if is_three_mode_group(records)]


def partial_mode_groups(
    groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]],
) -> list[tuple[TopologyComparisonGroup, list[OverviewRecord]]]:
    return [(group, records) for group, records in groups if not is_three_mode_group(records)]


def report_link_for_record(record: OverviewRecord) -> str:
    return f"[details]({report_name_for(record.config)})"


def three_mode_metric_value(records: list[OverviewRecord], topology: str, metric: ThreeModeMetric) -> float | None:
    record = records_by_topology(records).get(topology)
    if record is None:
        return None
    if metric.name == "frames_per_s":
        frames = metric_number(record, "frames")
        duration_s = metric_number(record, "duration_s")
        return None if frames is None or duration_s is None or duration_s <= 0 else frames / duration_s
    if metric.name == "complete_sequences_per_s":
        complete = metric_number(record, "complete_sequences")
        duration_s = metric_number(record, "duration_s")
        return None if complete is None or duration_s is None or duration_s <= 0 else complete / duration_s
    if metric.name == "can_cycles_per_s":
        cycles = metric_number(record, "can_cycles")
        duration_s = metric_number(record, "duration_s")
        return None if cycles is None or duration_s is None or duration_s <= 0 else cycles / duration_s
    return metric_number(record, metric.name)


def format_metric_value(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def format_delta(base: float | None, value: float | None) -> str:
    if base is None or value is None:
        return ""
    diff = value - base
    if base == 0:
        return f"{diff:+.3f}"
    return f"{diff:+.3f} ({(diff / base) * 100.0:+.1f}%)"


def three_mode_metric_rows(
    groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]],
    metrics: tuple[ThreeModeMetric, ...],
) -> list[dict[str, str]]:
    rows = []
    for group, records in groups:
        for metric in metrics:
            bridge = three_mode_metric_value(records, "Bridge", metric)
            forward = three_mode_metric_value(records, "Bridge Forward", metric)
            direct = three_mode_metric_value(records, "Direct cable", metric)
            if bridge is None or forward is None or direct is None:
                continue
            rows.append({
                "group": group.name,
                "kind": comparison_kind_label_for(records[0].config),
                "metric": metric.label,
                "bridge": format_metric_value(bridge),
                "bridge_forward": format_metric_value(forward),
                "direct_cable": format_metric_value(direct),
                "forward_vs_bridge": format_delta(bridge, forward),
                "direct_vs_bridge": format_delta(bridge, direct),
                "direct_vs_forward": format_delta(forward, direct),
            })
    return rows


def comparison_csv_row(group: TopologyComparisonGroup, record: OverviewRecord) -> dict[str, str]:
    return {
        "group": group.name,
        "topology": comparison_topology_label_for(record.config),
        "target": record.config.protocol,
        "kind": comparison_kind_label_for(record.config),
        "capture": metric_text(record, "capture"),
        "duration_s": metric_text(record, "duration_s"),
        "frames": metric_text(record, "frames"),
        "frames_per_s": rate_metric(record, "frames"),
        "complete_sequences": metric_text(record, "complete_sequences"),
        "complete_sequences_per_s": rate_metric(record, "complete_sequences"),
        "incomplete_orphan_rows": metric_text(record, "incomplete_orphan_rows"),
        "can_cycles": metric_text(record, "can_cycles"),
        "can_cycles_per_s": rate_metric(record, "can_cycles"),
        "unique_can_ids": metric_text(record, "unique_can_ids"),
        "bad_or_invalid_frames": metric_text(record, "bad_or_invalid_frames"),
        "decode_errors": metric_text(record, "decode_errors"),
        "request_to_response_avg_us": metric_text(record, "request_to_response_avg_us"),
        "request_to_response_p95_us": metric_text(record, "request_to_response_p95_us"),
        "full_exchange_avg_us": metric_text(record, "full_exchange_avg_us"),
        "full_exchange_p95_us": metric_text(record, "full_exchange_p95_us"),
        "cycle_duration_avg_us": metric_text(record, "cycle_duration_avg_us"),
        "cycle_duration_min_us": metric_text(record, "cycle_duration_min_us"),
        "cycle_duration_max_us": metric_text(record, "cycle_duration_max_us"),
        "cycle_duration_p95_us": metric_text(record, "cycle_duration_p95_us"),
        "inter_cycle_gap_min_us": metric_text(record, "inter_cycle_gap_min_us"),
        "inter_cycle_gap_max_us": metric_text(record, "inter_cycle_gap_max_us"),
        "inter_cycle_gap_avg_us": metric_text(record, "inter_cycle_gap_avg_us"),
        "inter_cycle_gap_p95_us": metric_text(record, "inter_cycle_gap_p95_us"),
    }


def write_comparison_csv(path: Path, records: list[OverviewRecord]) -> None:
    fieldnames = [
        "group",
        "topology",
        "target",
        "kind",
        "capture",
        "duration_s",
        "frames",
        "frames_per_s",
        "complete_sequences",
        "complete_sequences_per_s",
        "incomplete_orphan_rows",
        "can_cycles",
        "can_cycles_per_s",
        "unique_can_ids",
        "bad_or_invalid_frames",
        "decode_errors",
        "request_to_response_avg_us",
        "request_to_response_p95_us",
        "full_exchange_avg_us",
        "full_exchange_p95_us",
        "cycle_duration_avg_us",
        "cycle_duration_min_us",
        "cycle_duration_max_us",
        "cycle_duration_p95_us",
        "inter_cycle_gap_min_us",
        "inter_cycle_gap_max_us",
        "inter_cycle_gap_avg_us",
        "inter_cycle_gap_p95_us",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for group, group_records in comparison_groups(records):
            for record in group_records:
                writer.writerow(comparison_csv_row(group, record))


def write_three_mode_comparison_csv(path: Path, records: list[OverviewRecord]) -> None:
    groups = three_mode_groups(comparison_groups(records))
    fieldnames = [
        "group",
        "kind",
        "metric",
        "bridge",
        "bridge_forward",
        "direct_cable",
        "forward_vs_bridge",
        "direct_vs_bridge",
        "direct_vs_forward",
    ]
    rows = [
        *three_mode_metric_rows(
            [(group, rows) for group, rows in groups if rows[0].config.kind != "can"],
            SERIAL_THREE_MODE_METRICS,
        ),
        *three_mode_metric_rows(
            [(group, rows) for group, rows in groups if rows[0].config.kind == "can"],
            CAN_THREE_MODE_METRICS,
        ),
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def comparison_highlight_rows(
    groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]],
    metric_name: str,
) -> list[str]:
    rows = []
    for group, group_records in groups:
        candidates = [
            (record, metric_number(record, metric_name))
            for record in group_records
            if metric_number(record, metric_name) is not None
        ]
        if len(candidates) < 2:
            continue
        fastest = min(candidates, key=lambda item: item[1] or 0.0)
        slowest = max(candidates, key=lambda item: item[1] or 0.0)
        fastest_value = fastest[1] or 0.0
        slowest_value = slowest[1] or 0.0
        rows.append(
            f"| {group.name} "
            f"| {comparison_topology_label_for(fastest[0].config)} "
            f"| {fastest_value:.3f} "
            f"| {comparison_topology_label_for(slowest[0].config)} "
            f"| {slowest_value:.3f} "
            f"| {slowest_value - fastest_value:.3f} |"
        )
    return rows


def write_serial_comparison_group(lines: list[str], group: TopologyComparisonGroup, records: list[OverviewRecord]) -> None:
    lines.extend([
        "",
        f"### {group.name}",
        "",
        "| Topology | Report | Duration (s) | Frames | Frames/s | Complete | Complete/s | Incomplete | Bad/invalid | Req->Rsp avg (us) | Req->Rsp P95 (us) | Full avg (us) | Full P95 (us) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for record in records:
        lines.append(
            f"| {comparison_topology_label_for(record.config)} "
            f"| {report_link_for_record(record)} "
            f"| {fixed_metric(record, 'duration_s')} "
            f"| {metric_text(record, 'frames')} "
            f"| {rate_metric(record, 'frames')} "
            f"| {metric_text(record, 'complete_sequences')} "
            f"| {rate_metric(record, 'complete_sequences')} "
            f"| {metric_text(record, 'incomplete_orphan_rows')} "
            f"| {metric_text(record, 'bad_or_invalid_frames')} "
            f"| {metric_text(record, 'request_to_response_avg_us')} "
            f"| {metric_text(record, 'request_to_response_p95_us')} "
            f"| {metric_text(record, 'full_exchange_avg_us')} "
            f"| {metric_text(record, 'full_exchange_p95_us')} |"
        )


def write_can_comparison_group(lines: list[str], group: TopologyComparisonGroup, records: list[OverviewRecord]) -> None:
    lines.extend([
        "",
        f"### {group.name}",
        "",
        "| Topology | Report | Duration (s) | Frames | Frames/s | CAN IDs | Cycles | Cycles/s | Decode errors | Cycle min (us) | Cycle avg (us) | Cycle max (us) | Cycle P95 (us) | Gap min (us) | Gap avg (us) | Gap max (us) | Gap P95 (us) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for record in records:
        lines.append(
            f"| {comparison_topology_label_for(record.config)} "
            f"| {report_link_for_record(record)} "
            f"| {fixed_metric(record, 'duration_s')} "
            f"| {metric_text(record, 'frames')} "
            f"| {rate_metric(record, 'frames')} "
            f"| {metric_text(record, 'unique_can_ids')} "
            f"| {metric_text(record, 'can_cycles')} "
            f"| {rate_metric(record, 'can_cycles')} "
            f"| {metric_text(record, 'decode_errors')} "
            f"| {metric_text(record, 'cycle_duration_min_us')} "
            f"| {metric_text(record, 'cycle_duration_avg_us')} "
            f"| {metric_text(record, 'cycle_duration_max_us')} "
            f"| {metric_text(record, 'cycle_duration_p95_us')} "
            f"| {metric_text(record, 'inter_cycle_gap_min_us')} "
            f"| {metric_text(record, 'inter_cycle_gap_avg_us')} "
            f"| {metric_text(record, 'inter_cycle_gap_max_us')} "
            f"| {metric_text(record, 'inter_cycle_gap_p95_us')} |"
        )


def write_three_mode_pivot_section(
    lines: list[str],
    title: str,
    groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]],
    metrics: tuple[ThreeModeMetric, ...],
) -> None:
    lines.extend([
        "",
        title,
        "",
        "| Group | Metric | Bridge | Bridge Forward | Direct cable | Forward vs Bridge | Direct vs Bridge | Direct vs Forward |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    rows = three_mode_metric_rows(groups, metrics)
    if not rows:
        lines.append("| No complete three-mode groups |  |  |  |  |  |  |  |")
        return
    for row in rows:
        lines.append(
            f"| {row['group']} "
            f"| {row['metric']} "
            f"| {row['bridge']} "
            f"| {row['bridge_forward']} "
            f"| {row['direct_cable']} "
            f"| {row['forward_vs_bridge']} "
            f"| {row['direct_vs_bridge']} "
            f"| {row['direct_vs_forward']} |"
        )


def write_partial_mode_coverage(lines: list[str], groups: list[tuple[TopologyComparisonGroup, list[OverviewRecord]]]) -> None:
    lines.extend([
        "",
        "## Partial Topology Coverage",
        "",
        "These groups are still useful, but they do not have all three modes captured yet.",
        "",
        "| Group | Available modes | Missing modes |",
        "| --- | --- | --- |",
    ])
    if not groups:
        lines.append("| None |  |  |")
        return
    for group, records in groups:
        labels = set(records_by_topology(records))
        available = ", ".join(label for label in TOPOLOGY_ORDER if label in labels)
        missing = ", ".join(label for label in TOPOLOGY_ORDER if label not in labels)
        lines.append(f"| {group.name} | {available} | {missing} |")


def write_comparison_md(path: Path, records: list[OverviewRecord]) -> None:
    grouped = comparison_groups(records)
    three_groups = three_mode_groups(grouped)
    partial_groups = partial_mode_groups(grouped)
    serial_three_groups = [(group, rows) for group, rows in three_groups if rows[0].config.kind != "can"]
    can_three_groups = [(group, rows) for group, rows in three_groups if rows[0].config.kind == "can"]
    serial_groups = [(group, rows) for group, rows in grouped if rows[0].config.kind != "can"]
    can_groups = [(group, rows) for group, rows in grouped if rows[0].config.kind == "can"]

    lines = [
        "# Topology Comparison Report",
        "",
        "Generated by the full analysis run, or refreshed from an existing overview CSV:",
        "",
        "```powershell",
        "python analysis/analyze_capture.py --all-captures --quiet",
        "python analysis/analyze_capture.py --comparison-only",
        "```",
        "",
        "This report compares captures that share the same inverter, protocol, and BMS side across Bridge, Bridge Forward, and Direct cable topologies.",
        "",
        "Notes:",
        "",
        "- Capture durations are not identical; `frames/s`, `complete/s`, and `cycles/s` normalize counts by capture duration.",
        "- RS485/UART latency columns use complete request/response pairs only.",
        "- CAN cycle duration can be dominated by capture length when only one cycle is detected.",
        "- The first comparison tables include only groups where Bridge, Bridge Forward, and Direct cable all exist.",
    ]

    write_three_mode_pivot_section(
        lines,
        "## Three-mode RS485/UART Deltas",
        serial_three_groups,
        SERIAL_THREE_MODE_METRICS,
    )
    write_three_mode_pivot_section(
        lines,
        "## Three-mode CAN Deltas",
        can_three_groups,
        CAN_THREE_MODE_METRICS,
    )

    lines.extend([
        "",
        "## Three-mode RS485/UART Highlights",
        "",
        "| Group | Lowest Req->Rsp avg topology | Lowest Req->Rsp avg (us) | Highest Req->Rsp avg topology | Highest Req->Rsp avg (us) | Spread (us) |",
        "| --- | --- | ---: | --- | ---: | ---: |",
    ])
    highlight_rows = comparison_highlight_rows(serial_three_groups, "request_to_response_avg_us")
    lines.extend(highlight_rows or ["| No comparable RS485/UART groups |  |  |  |  |  |"])

    lines.extend([
        "",
        "## Three-mode CAN Highlights",
        "",
        "| Group | Lowest cycle avg topology | Lowest cycle avg (us) | Highest cycle avg topology | Highest cycle avg (us) | Spread (us) |",
        "| --- | --- | ---: | --- | ---: | ---: |",
    ])
    highlight_rows = comparison_highlight_rows(can_three_groups, "cycle_duration_avg_us")
    lines.extend(highlight_rows or ["| No comparable CAN groups |  |  |  |  |  |"])

    write_partial_mode_coverage(lines, partial_groups)

    lines.extend([
        "",
        "## RS485/UART Comparisons",
    ])
    for group, rows in serial_groups:
        write_serial_comparison_group(lines, group, rows)

    lines.extend([
        "",
        "## CAN Comparisons",
    ])
    for group, rows in can_groups:
        write_can_comparison_group(lines, group, rows)

    lines.extend([
        "",
        "## Generated Tables",
        "",
        "```text",
        "analysis/out/topology-comparison.csv",
        "analysis/out/topology-three-mode-comparison.csv",
        "```",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_comparison_outputs(records: list[OverviewRecord], out_dir: Path, report_dir: Path) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "topology-comparison.csv"
    three_mode_csv_path = out_dir / "topology-three-mode-comparison.csv"
    md_path = report_dir / "topology-comparison.md"
    write_comparison_csv(csv_path, records)
    write_three_mode_comparison_csv(three_mode_csv_path, records)
    write_comparison_md(md_path, records)
    return csv_path, three_mode_csv_path, md_path


def shifted_report_text(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.startswith("#"):
            lines.append(f"###{line}")
        else:
            lines.append(line)
    return lines


def consolidated_reports_block(readme_path: Path, report_dir: Path) -> str:
    lines = [
        README_REPORTS_BEGIN,
        "",
        "## Consolidated Reports",
        "",
        "This section is generated from every Markdown file under `analysis/reports/`.",
        "",
    ]
    for report_path in sorted(report_dir.glob("*.md")):
        try:
            report_link = report_path.resolve().relative_to(readme_path.parent.resolve()).as_posix()
        except ValueError:
            report_link = report_path.as_posix()
        lines.extend([
            f"### [{report_path.stem}]({report_link})",
            "",
            *shifted_report_text(report_path),
            "",
        ])
    lines.append(README_REPORTS_END)
    return "\n".join(lines)


def update_readme_reports(readme_path: Path, report_dir: Path) -> None:
    text = readme_path.read_text(encoding="utf-8")
    block = consolidated_reports_block(readme_path, report_dir)
    begin = text.find(README_REPORTS_BEGIN)
    end = text.find(README_REPORTS_END)
    if begin == -1 or end == -1:
        updated = text.rstrip() + "\n\n" + block
    else:
        end += len(README_REPORTS_END)
        updated = text[:begin].rstrip() + "\n\n" + block + text[end:].rstrip()
    readme_path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def write_overview_outputs(results: list[AnalysisResult], out_dir: Path, report_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "bridge-analysis-overview.csv"
    md_path = report_dir / "bridge-analysis-overview.md"
    write_overview_csv(csv_path, results)
    write_overview_md(md_path, results)
    return csv_path, md_path


def infer_config_for_capture(capture: Path) -> ProtocolConfig | None:
    resolved = capture.resolve()
    for config in PROTOCOL_CONFIGS.values():
        if config.capture.resolve() == resolved:
            return config
    matches = [config for config in PROTOCOL_CONFIGS.values() if config.capture.name == capture.name]
    if len(matches) == 1:
        return matches[0]
    return None


def target_configs(args) -> list[ProtocolConfig]:
    if args.all_captures or args.all_bridge:
        return list(PROTOCOL_CONFIGS.values())

    if args.capture is None:
        raise SystemExit("capture is required unless --all-captures is used")

    capture = args.capture.resolve()
    base = infer_config_for_capture(capture)
    if args.protocol:
        config = PROTOCOL_CONFIGS[args.protocol]
    elif base is not None:
        config = base
    else:
        raise SystemExit("Could not infer protocol; pass --protocol")

    return [ProtocolConfig(
        config.protocol,
        config.title,
        config.helper_path,
        config.kind,
        capture,
        args.channel or config.channel,
        config.invert if args.invert is None else args.invert,
        baud=args.baud or config.baud,
        bitrate=args.bitrate or config.bitrate,
        sample_point_pct=args.sample_point if args.sample_point is not None else config.sample_point_pct,
        inter_frame_gap_us=args.inter_frame_gap_us or config.inter_frame_gap_us,
        cycle_gap_us=args.cycle_gap_us or config.cycle_gap_us,
    )]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze sigrok/PulseView captures offline.")
    parser.add_argument("capture", nargs="?", type=Path, help="Path to a .sr capture file.")
    parser.add_argument("--all-captures", action="store_true", help="Analyze every known example capture.")
    parser.add_argument("--all-bridge", action="store_true", help="Compatibility alias for --all-captures.")
    parser.add_argument("--list-targets", action="store_true", help="List built-in bridge targets and exit.")
    parser.add_argument("--protocol", choices=sorted(PROTOCOL_CONFIGS), help="Protocol decoder to run.")
    parser.add_argument("--channel", help="Logic channel/probe name to decode.")
    parser.add_argument("--baud", type=int, help="UART baud rate.")
    parser.add_argument("--bitrate", type=int, help="CAN bitrate.")
    parser.add_argument("--sample-point", type=float, help="CAN sample point percent.")
    parser.add_argument("--invert", dest="invert", action="store_true", default=None, help="Invert selected input.")
    parser.add_argument("--no-invert", dest="invert", action="store_false", help="Do not invert selected input.")
    parser.add_argument("--inter-frame-gap-us", type=int, help="Serial idle gap for incomplete frame flush.")
    parser.add_argument("--cycle-gap-us", type=int, help="CAN gap threshold for cycle grouping.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Directory for generated CSV/summary files.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR, help="Directory for readable reports.")
    parser.add_argument("--comparison-only", action="store_true", help="Write topology comparison reports from an existing overview CSV.")
    parser.add_argument("--overview-csv", type=Path, help="Overview CSV to use with --comparison-only.")
    parser.add_argument("--update-readme-reports", action="store_true", help="Refresh the consolidated reports section in analysis/README.md.")
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="README file updated by --update-readme-reports.")
    parser.add_argument("--max-samples", type=int, help="Stop after this many samples.")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress messages.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.list_targets:
        for config in PROTOCOL_CONFIGS.values():
            print(f"{config.protocol}: {config.capture.relative_to(REPO_ROOT)}")
        return 0

    if args.comparison_only:
        overview_csv = args.overview_csv or args.out_dir / "bridge-analysis-overview.csv"
        if not overview_csv.exists():
            print(f"Overview CSV not found: {overview_csv}", file=sys.stderr)
            return 2
        records = read_overview_records(overview_csv)
        if not records:
            print(f"No known targets found in: {overview_csv}", file=sys.stderr)
            return 2
        comparison_csv_path, three_mode_csv_path, comparison_md_path = write_comparison_outputs(records, args.out_dir, args.report_dir)
        print(f"comparison_csv: {comparison_csv_path}")
        print(f"three_mode_comparison_csv: {three_mode_csv_path}")
        print(f"comparison_report: {comparison_md_path}")
        if args.update_readme_reports:
            update_readme_reports(args.readme, args.report_dir)
            print(f"readme: {args.readme}")
        return 0

    if args.update_readme_reports and args.capture is None and not args.all_captures and not args.all_bridge:
        update_readme_reports(args.readme, args.report_dir)
        print(f"readme: {args.readme}")
        return 0

    configs = target_configs(args)
    results = []
    for config in configs:
        if not config.capture.exists():
            print(f"Capture not found: {config.capture}", file=sys.stderr)
            return 2
        print(f"analyzing {config.protocol}: {config.capture}", flush=True)
        result = analyze_capture(config, max_samples=args.max_samples, progress=not args.quiet)
        results.append(result)
        frames_path, sequences_path, summary_path, report_path = write_outputs(result, args.out_dir, args.report_dir)
        print(f"frames: {frames_path}")
        print(f"sequences: {sequences_path}")
        print(f"summary: {summary_path}")
        print(f"report: {report_path}")
        if result.config.kind == "can":
            print(f"decoded {len(result.frames)} CAN frames and {len(result.cycles)} cycles in {result.elapsed_s:.3f}s")
        else:
            print(f"decoded {len(result.frames)} frames and {len(result.sequences)} sequence rows in {result.elapsed_s:.3f}s")

    if args.all_captures or args.all_bridge:
        overview_csv_path, overview_md_path = write_overview_outputs(results, args.out_dir, args.report_dir)
        print(f"overview_csv: {overview_csv_path}")
        print(f"overview_report: {overview_md_path}")
        comparison_csv_path, three_mode_csv_path, comparison_md_path = write_comparison_outputs(
            [overview_record_from_result(result) for result in results],
            args.out_dir,
            args.report_dir,
        )
        print(f"comparison_csv: {comparison_csv_path}")
        print(f"three_mode_comparison_csv: {three_mode_csv_path}")
        print(f"comparison_report: {comparison_md_path}")

    if args.update_readme_reports:
        update_readme_reports(args.readme, args.report_dir)
        print(f"readme: {args.readme}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
