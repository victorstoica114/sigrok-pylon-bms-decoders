#!/usr/bin/env python3
"""Generate an Overleaf-ready LaTeX report from analysis CSV outputs."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "analysis" / "out"
LATEX_DIR = REPO_ROOT / "analysis" / "latex"
MAIN_TEX = LATEX_DIR / "main.tex"

OVERVIEW_CSV = OUT_DIR / "bridge-analysis-overview.csv"
THREE_MODE_CSV = OUT_DIR / "topology-three-mode-comparison.csv"

TOPOLOGY_LABELS = {
    "examples/bridge/": "Bridge",
    "examples/bridge_forward/": "Bridge Forward",
    "examples/direct/": "Direct cable",
}

TOPOLOGY_COLUMNS = {
    "Bridge": "bridge",
    "Bridge Forward": "bridge_forward",
    "Direct cable": "direct_cable",
}

GROUP_LABELS = {
    "china_tower_modbus": "China Tower Modbus RS485",
    "daly_rs485": "Daly RS485",
    "growatt_rs485": "Growatt RS485 JKBMS",
    "forward_growatt_rs485": "Growatt RS485 JKBMS",
    "direct_growatt_rs485": "Growatt RS485 JKBMS",
    "growatt_seplos_rs485": "Growatt RS485 SeplosBMS",
    "forward_growatt_seplos_rs485": "Growatt RS485 SeplosBMS",
    "jkbms_modbus": "JKBMS Modbus RS485",
    "pace_modbus": "PACE Modbus RS485",
    "pylon_rs485": "Pylon RS485",
    "anenji_pylon_rs485": "Anenji Pylon RS485 JKBMS",
    "forward_anenji_pylon_rs485": "Anenji Pylon RS485 JKBMS",
    "direct_anenji_jkbms_pylon_rs485": "Anenji Pylon RS485 JKBMS",
    "forward_anenji_seplos_pylon_rs485": "Anenji Pylon RS485 SeplosBMS",
    "direct_anenji_seplos_pylon_rs485": "Anenji Pylon RS485 SeplosBMS",
    "voltronic_modbus": "Voltronic Modbus RS485",
    "wow_modbus": "WOW Modbus RS485",
    "deye_can": "Deye CAN",
    "goodwe_can": "GoodWe CAN",
    "growatt_can": "Growatt CAN JKBMS",
    "forward_growatt_can": "Growatt CAN JKBMS",
    "direct_growatt_can": "Growatt CAN JKBMS",
    "growatt_seplos_can": "Growatt CAN SeplosBMS",
    "forward_growatt_seplos_can": "Growatt CAN SeplosBMS",
    "direct_growatt_seplos_can": "Growatt CAN SeplosBMS",
    "jkbms_can": "JKBMS CAN",
    "pylon_can": "Pylon CAN",
    "sma_can": "SMA CAN",
    "sofar_can": "Sofar CAN",
    "victron_can": "Victron CAN",
}

CAPTURE_PROTOCOLS = {
    "china_tower_modbus": "China Tower Modbus RS485",
    "daly_rs485": "Daly RS485",
    "growatt_rs485": "Growatt RS485",
    "forward_growatt_rs485": "Growatt RS485",
    "direct_growatt_rs485": "Growatt RS485",
    "growatt_seplos_rs485": "Growatt RS485",
    "forward_growatt_seplos_rs485": "Growatt RS485",
    "jkbms_modbus": "JKBMS Modbus RS485",
    "pace_modbus": "PACE Modbus RS485",
    "pylon_rs485": "Pylon RS485",
    "anenji_pylon_rs485": "Pylon RS485",
    "forward_anenji_pylon_rs485": "Pylon RS485",
    "direct_anenji_jkbms_pylon_rs485": "Pylon RS485",
    "forward_anenji_seplos_pylon_rs485": "Pylon RS485",
    "direct_anenji_seplos_pylon_rs485": "Pylon RS485",
    "voltronic_modbus": "Voltronic Modbus RS485",
    "wow_modbus": "WOW Modbus RS485",
    "deye_can": "Deye CAN",
    "goodwe_can": "GoodWe CAN",
    "growatt_can": "Growatt CAN",
    "forward_growatt_can": "Growatt CAN",
    "direct_growatt_can": "Growatt CAN",
    "growatt_seplos_can": "Growatt CAN",
    "forward_growatt_seplos_can": "Growatt CAN",
    "direct_growatt_seplos_can": "Growatt CAN",
    "jkbms_can": "JKBMS CAN",
    "pylon_can": "Pylon CAN",
    "sma_can": "SMA CAN",
    "sofar_can": "Sofar CAN",
    "victron_can": "Victron CAN",
}

BMS_DEVICES = {
    "daly_rs485": "Daly BMS",
    "goodwe_can": "SeplosBMS",
    "growatt_seplos_rs485": "SeplosBMS",
    "forward_growatt_seplos_rs485": "SeplosBMS",
    "forward_anenji_seplos_pylon_rs485": "SeplosBMS",
    "direct_anenji_seplos_pylon_rs485": "SeplosBMS",
    "growatt_seplos_can": "SeplosBMS",
    "forward_growatt_seplos_can": "SeplosBMS",
    "direct_growatt_seplos_can": "SeplosBMS",
    "sma_can": "SeplosBMS",
    "sofar_can": "SeplosBMS",
    "victron_can": "SeplosBMS",
    "voltronic_modbus": "SeplosBMS",
}

DEVICE_ABBREVIATIONS = {
    "Anenji": "Anj",
    "Daly BMS": "Daly",
    "Easun": "Easun",
    "Growatt": "GW",
    "JKBMS": "JK",
    "SeplosBMS": "Sep",
}

PROTOCOL_ABBREVIATIONS = {
    "Growatt CAN": "GW CAN",
    "Growatt RS485": "GW 485",
    "Pylon CAN": "Py CAN",
    "Pylon RS485": "Py 485",
}

BMS_SIDE_TARGETS = {
    "china_tower_modbus",
    "daly_rs485",
    "jkbms_can",
    "jkbms_modbus",
    "pace_modbus",
    "pylon_can",
    "sma_can",
    "sofar_can",
    "voltronic_modbus",
    "victron_can",
    "wow_modbus",
}

FIXED_INVERTER_PROTOCOLS = {
    "china_tower_modbus": "Pylon CAN",
    "jkbms_can": "Growatt CAN",
    "pylon_can": "Growatt CAN",
    "sma_can": "Growatt CAN",
    "sofar_can": "Growatt CAN",
    "voltronic_modbus": "Pylon RS485",
    "victron_can": "Growatt CAN",
    "wow_modbus": "Pylon RS485",
}

REPORT_TITLE = "Sigrok BMS Protocol Decoder Capture Analysis"

DELTA_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s+\(([-+]?\d+(?:\.\d+)?)%\)\s*$")
DELTA_PERCENT_RE = re.compile(r"\(([-+]\d+(?:\.\d+)?)%\)")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def tex_escape(text: object) -> str:
    value = "" if text is None else str(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def format_number(value: float, max_decimals: int = 2, signed: bool = False) -> str:
    rounded = round(float(value), max_decimals)
    if rounded == 0:
        return "0"

    magnitude = abs(rounded) if signed else rounded
    text = f"{magnitude:.{max_decimals}f}".rstrip("0").rstrip(".")
    if signed:
        return ("+" if rounded > 0 else "-") + text
    return text


def parse_delta(text: str) -> tuple[float, float] | None:
    match = DELTA_RE.match(text)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def format_delta_text(text: str, value_scale: float = 1.0) -> str:
    parsed = parse_delta(text)
    if parsed is None:
        return text
    delta, percent = parsed
    delta *= value_scale
    return (
        f"{format_number(delta, signed=True)} "
        f"({format_number(percent, signed=True)}%)"
    )


def delta_direction(text: str, value_scale: float = 1.0) -> int:
    parsed = parse_delta(text)
    if parsed is None:
        return 0
    rounded_delta = round(parsed[0] * value_scale, 2)
    if rounded_delta > 0:
        return 1
    if rounded_delta < 0:
        return -1
    return 0


def tex_num(text: str, decimals: int = 2) -> str:
    if text == "":
        return "--"
    try:
        return format_number(float(text), decimals)
    except ValueError:
        return tex_escape(text)


def tex_scaled_num(text: str, value_scale: float, decimals: int = 2) -> str:
    if text == "":
        return "--"
    try:
        return format_number(float(text) * value_scale, decimals)
    except ValueError:
        return tex_escape(text)


def tex_int(text: str) -> str:
    if text == "":
        return "--"
    try:
        return f"{int(float(text)):,}"
    except ValueError:
        return tex_escape(text)


def tex_loss_rate(row: dict[str, str]) -> str:
    try:
        total = float(row.get("sequence_rows", "") or 0)
        if total <= 0:
            complete = float(row.get("complete_sequences", "") or 0)
            incomplete = float(row.get("incomplete_orphan_rows", "") or 0)
            total = complete + incomplete
        if total <= 0:
            return "--"
        incomplete = float(row.get("incomplete_orphan_rows", "") or 0)
    except ValueError:
        return "--"
    return rf"{format_number(incomplete * 100.0 / total)}\%"


def tex_delta(text: str, value_scale: float = 1.0) -> str:
    if not text:
        return "--"
    formatted = format_delta_text(text, value_scale)
    escaped = tex_escape(formatted)
    direction = delta_direction(text, value_scale)
    if direction > 0:
        return rf"\increase{{{escaped}}}"
    if direction < 0:
        return rf"\decrease{{{escaped}}}"
    return escaped


def display_metric_details(metric: str) -> tuple[str, float, str]:
    if metric.endswith("(us)"):
        return metric[:-4].rstrip() + " (ms)", 0.001, "ms"
    units = {
        "Complete exchanges/s": "exchanges/s",
        "Cycles/s": "cycles/s",
        "Frames/s": "frames/s",
    }
    return metric, 1.0, units.get(metric, "")


def display_metric_and_scale(metric: str) -> tuple[str, float]:
    display_metric, value_scale, _unit = display_metric_details(metric)
    return display_metric, value_scale


def compact_direct_delta_metric(metric: str) -> str:
    return metric.replace("Inter-cycle gap ", "IC gap ")


def format_metric_delta_text(text: str, metric: str) -> str:
    _display_metric, value_scale, unit = display_metric_details(metric)
    parsed = parse_delta(text)
    if parsed is None:
        return text
    delta, percent = parsed
    unit_text = f" {unit}" if unit else ""
    return (
        f"{format_number(delta * value_scale, signed=True)}{unit_text} "
        f"({format_number(percent, signed=True)}%)"
    )


def topology_for_capture(capture: str) -> str:
    normalized = capture.replace("\\", "/")
    for prefix, label in TOPOLOGY_LABELS.items():
        if normalized.startswith(prefix):
            return label
    return "Bridge"


def topology_column(topology: str) -> str:
    return TOPOLOGY_COLUMNS[topology]


def group_label_for_target(target: str) -> str:
    return GROUP_LABELS.get(target, target.replace("_", " ").title())


def capture_protocol_for_target(target: str) -> str:
    return CAPTURE_PROTOCOLS.get(target, group_label_for_target(target))


def bms_device_for_target(target: str) -> str:
    return BMS_DEVICES.get(target, "JKBMS")


def abbreviate_device(device: str) -> str:
    return DEVICE_ABBREVIATIONS.get(device, device)


def abbreviate_protocol(protocol: str) -> str:
    return PROTOCOL_ABBREVIATIONS.get(protocol, protocol)


def inverter_device_for_capture(capture: str) -> str:
    normalized = capture.replace("\\", "/").lower()
    if "easun" in normalized:
        return "Easun"
    if "anenji" in normalized:
        return "Anenji"
    return "Growatt"


def comparison_inverter_device(group: str) -> str:
    if group.startswith("Anenji"):
        return "Anenji"
    return "Growatt"


def comparison_bms_device(group: str) -> str:
    if "SeplosBMS" in group:
        return "SeplosBMS"
    return "JKBMS"


def comparison_protocol(group: str) -> str:
    if "Growatt CAN" in group:
        return "Growatt CAN"
    if "Growatt RS485" in group:
        return "Growatt RS485"
    if "Pylon RS485" in group:
        return "Pylon RS485"
    if "Pylon CAN" in group:
        return "Pylon CAN"
    return group


def capture_id(capture: str) -> str:
    path = Path(capture.replace("\\", "/"))
    stem = path.stem.replace("-raw-capture", "")
    return f"{path.parent.name}/{stem}"


def captured_side_for_row(row: dict[str, str]) -> str:
    topology = topology_for_capture(row["capture"])
    if topology in {"Bridge Forward", "Direct cable"}:
        return "Shared bus"
    if row["target"] in BMS_SIDE_TARGETS:
        return "BMS side"
    return "Inverter side"


def fixed_inverter_protocol_for_row(row: dict[str, str]) -> str | None:
    target_protocol = FIXED_INVERTER_PROTOCOLS.get(row["target"])
    if target_protocol:
        return target_protocol
    normalized = row["capture"].replace("\\", "/").lower()
    if "easun" in normalized:
        return "Pylon CAN"
    if "anenji" in normalized:
        return "Pylon RS485"
    return None


def inverter_protocol_for_row(row: dict[str, str]) -> str:
    fixed_protocol = fixed_inverter_protocol_for_row(row)
    if fixed_protocol:
        return fixed_protocol
    captured_side = captured_side_for_row(row)
    if captured_side in {"Inverter side", "Shared bus"}:
        return capture_protocol_for_target(row["target"])
    return "not captured"


def bms_protocol_for_row(row: dict[str, str]) -> str:
    captured_side = captured_side_for_row(row)
    if captured_side in {"BMS side", "Shared bus"}:
        return capture_protocol_for_target(row["target"])
    return "not captured"


def fvalue(row: dict[str, str], key: str) -> float | None:
    text = row.get(key, "")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def chart_value(row: dict[str, str], topology: str) -> float | None:
    text = row.get(topology_column(topology), "")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def can_cycles_per_second(row: dict[str, str]) -> float | None:
    cycles = fvalue(row, "can_cycles")
    duration = fvalue(row, "duration_s")
    if cycles is None or duration is None or duration <= 0:
        return None
    return cycles / duration


def complete_exchanges_per_second(row: dict[str, str]) -> float | None:
    complete = fvalue(row, "complete_sequences")
    duration = fvalue(row, "duration_s")
    if complete is None or duration is None or duration <= 0:
        return None
    return complete / duration


def overview_chart_rows(
    overview: list[dict[str, str]],
    kind: str,
    metric_key: str | None = None,
    computed_key=None,
) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, str]] = {}
    order: list[str] = []

    for row in overview:
        is_can = row.get("kind") == "can"
        if kind == "CAN" and not is_can:
            continue
        if kind == "RS485/UART" and is_can:
            continue

        value = computed_key(row) if computed_key else fvalue(row, metric_key or "")
        if value is None:
            continue

        group = group_label_for_target(row["target"])
        if group not in grouped:
            grouped[group] = {
                "group": group,
                "bridge": "",
                "bridge_forward": "",
                "direct_cable": "",
            }
            order.append(group)

        column = topology_column(topology_for_capture(row["capture"]))
        grouped[group][column] = f"{value:.3f}"

    return [
        grouped[group]
        for group in order
        if any(grouped[group][column] for column in TOPOLOGY_COLUMNS.values())
    ]


def find_row(rows: list[dict[str, str]], group: str, metric: str) -> dict[str, str]:
    for row in rows:
        if row.get("group") == group and row.get("metric") == metric:
            return row
    return {}


def metric_rows(rows: list[dict[str, str]], kind: str, metrics: set[str]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("kind") == kind and row.get("metric") in metrics]


def group_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["group"]].append(row)
    return dict(grouped)


def percent_from_delta(text: str) -> float | None:
    match = DELTA_PERCENT_RE.search(text)
    if not match:
        return None
    return float(match.group(1))


def make_observations(three_mode: list[dict[str, str]]) -> list[str]:
    observations = []
    metric = "Req->Rsp avg (us)"
    row = find_row(three_mode, "Anenji Pylon RS485 JKBMS", metric)
    if row:
        observations.append(
            "Anenji Pylon RS485 JKBMS shows the clearest RS485 latency change: "
            f"Direct cable is {format_metric_delta_text(row['direct_vs_bridge'], metric)} "
            "versus Bridge for average request-to-response latency."
        )

    metric = "Full exchange P95 (us)"
    row = find_row(three_mode, "Growatt RS485 JKBMS", metric)
    if row:
        observations.append(
            "Growatt RS485 JKBMS has slower worst-case exchange timing: "
            f"Direct cable is {format_metric_delta_text(row['direct_vs_bridge'], metric)} "
            "versus Bridge for full-exchange P95 latency."
        )

    metric = "Cycle avg (us)"
    row = find_row(three_mode, "Growatt CAN SeplosBMS", metric)
    if row:
        observations.append(
            "Growatt CAN SeplosBMS cycles are shorter in Direct cable mode: "
            f"Direct cable is {format_metric_delta_text(row['direct_vs_bridge'], metric)} "
            "versus Bridge for average CAN cycle duration."
        )

    metric = "Frames/s"
    row = find_row(three_mode, "Growatt CAN JKBMS", metric)
    if row:
        observations.append(
            "Growatt CAN JKBMS frame rate stays effectively flat across modes: "
            f"Direct cable is {format_metric_delta_text(row['direct_vs_bridge'], metric)} "
            "versus Bridge."
        )
    return observations


def direct_deltas(three_mode: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = []
    for row in three_mode:
        pct = percent_from_delta(row.get("direct_vs_bridge", ""))
        if pct is None:
            continue
        abs_pct = abs(pct)
        item = dict(row)
        item["abs_pct_sort"] = abs_pct
        item["abs_pct"] = format_number(abs_pct)
        candidates.append(item)
    candidates.sort(key=lambda item: item["abs_pct_sort"], reverse=True)
    return candidates


def chart_group_order(rows: list[dict[str, str]]) -> list[str]:
    seen = []
    for row in rows:
        group = row["group"]
        if group not in seen:
            seen.append(group)
    return seen


def chart_coordinates(
    rows: list[dict[str, str]],
    groups: list[str],
    topology: str,
    scale: float = 1.0,
    decimals: int = 3,
    label_values: bool = False,
    label_decimals: int = 2,
) -> str:
    by_group = {row["group"]: row for row in rows}
    coords = []
    for index, group in enumerate(groups, start=1):
        value = chart_value(by_group[group], topology)
        if value is None:
            continue
        scaled_value = value * scale
        label = f" [{scaled_value:.{label_decimals}f}]" if label_values else ""
        coords.append(f"({index},{scaled_value:.{decimals}f}){label}")
    return " ".join(coords)


def chart_scaled_max(rows: list[dict[str, str]], groups: list[str], scale: float) -> float | None:
    by_group = {row["group"]: row for row in rows}
    values = []
    for group in groups:
        row = by_group[group]
        for topology in ("Bridge", "Bridge Forward", "Direct cable"):
            value = chart_value(row, topology)
            if value is not None:
                values.append(value * scale)
    return max(values) if values else None


def xtick_labels(groups: list[str]) -> str:
    return ",".join(tex_escape(group) for group in groups)


def bar_axis(
    label: str,
    rows: list[dict[str, str]],
    scale: float = 1.0,
    width: str = r"\textwidth",
    height: str = "4.8cm",
    bar_width: str = "3.5pt",
    tick_label_width: str = "1.25cm",
    ymode: str = "linear",
    ymin: float | None = None,
    coordinate_decimals: int = 3,
    value_labels: bool = False,
    value_label_decimals: int = 2,
    label_headroom: float | None = None,
) -> str:
    groups = chart_group_order(rows)
    xticks = ",".join(str(index) for index in range(1, len(groups) + 1))
    xmax = len(groups) + 0.5
    max_value = chart_scaled_max(rows, groups, scale)
    if ymode == "log":
        ymin_value = 0.1 if ymin is None else ymin
        ymax = ""
        if value_labels and max_value is not None and max_value > 0:
            headroom = 6.0 if label_headroom is None else label_headroom
            ymax_value = max(max_value * headroom, ymin_value * 10)
            ymax = f"\n    ymax={ymax_value:.6g},"
        y_options = (
            "    ymode=log,\n"
            "    log basis y=10,\n"
            "    log origin y=infty,\n"
            "    ytick={0.1,1,10,100,1000,10000},\n"
            "    yticklabels={\\mbox{10\\raisebox{0.55ex}{-1}},\\mbox{10\\raisebox{0.55ex}{0}},\\mbox{10\\raisebox{0.55ex}{1}},\\mbox{10\\raisebox{0.55ex}{2}},\\mbox{10\\raisebox{0.55ex}{3}},\\mbox{10\\raisebox{0.55ex}{4}}},\n"
            f"    ymin={ymin_value:.6g},{ymax}"
        )
    else:
        ymin_value = 0.0 if ymin is None else ymin
        y_options = f"    ymin={ymin_value:.6g},"
    value_label_options = ""
    if value_labels:
        linear_headroom = 0.35 if label_headroom is None else label_headroom
        enlarge_y_limits = (
            "" if ymode == "log" else f"    enlarge y limits={{upper,value={linear_headroom:.3g}}},\n"
        )
        value_label_options = (
            "    point meta=explicit symbolic,\n"
            "    nodes near coords={\\pgfplotspointmeta},\n"
            "    every node near coord/.append style={font=\\tiny, rotate=90, anchor=west, inner sep=1pt},\n"
            f"{enlarge_y_limits}"
            "    clip=false,\n"
        )
    return rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
    ybar,
    width={width},
    height={height},
    bar width={bar_width},
{y_options}
{value_label_options}    scaled y ticks=false,
    xmin=0.5,
    xmax={xmax:.1f},
    enlarge x limits=false,
    ylabel={{{tex_escape(label)}}},
    ylabel style={{font=\small}},
    xtick={{{xticks}}},
    xticklabels={{{xtick_labels(groups)}}},
    x tick label style={{text width={tick_label_width}, align=center, font=\tiny}},
    y tick label style={{font=\scriptsize}},
    legend style={{at={{(0.5,1.04)}}, anchor=south, legend columns=3, font=\scriptsize}},
    grid=both,
    major grid style={{draw=gridline}},
]
\addplot+[fill=bridge, draw=bridge] coordinates {{{chart_coordinates(rows, groups, "Bridge", scale, coordinate_decimals, value_labels, value_label_decimals)}}};
\addplot+[fill=forward, draw=forward] coordinates {{{chart_coordinates(rows, groups, "Bridge Forward", scale, coordinate_decimals, value_labels, value_label_decimals)}}};
\addplot+[fill=direct, draw=direct] coordinates {{{chart_coordinates(rows, groups, "Direct cable", scale, coordinate_decimals, value_labels, value_label_decimals)}}};
\legend{{Bridge, Bridge Forward, Direct cable}}
\end{{axis}}
\end{{tikzpicture}}
"""


def paired_bar_charts(title: str, charts: list[dict[str, object]]) -> str:
    panels = []
    for chart in charts:
        ymin_value = chart.get("ymin")
        panels.append(
            rf"""
\begin{{subfigure}}{{\textwidth}}
\centering
{bar_axis(
                str(chart["label"]),
                chart["rows"],
                scale=float(chart.get("scale", 1.0)),
                width=str(chart.get("width", r"\textwidth")),
                height=str(chart.get("height", "4.8cm")),
                bar_width=str(chart.get("bar_width", "7pt")),
                tick_label_width=str(chart.get("tick_label_width", "1.25cm")),
                ymode=str(chart.get("ymode", "linear")),
                ymin=None if ymin_value is None else float(ymin_value),
                coordinate_decimals=int(chart.get("coordinate_decimals", 3)),
                value_labels=bool(chart.get("value_labels", True)),
                value_label_decimals=int(chart.get("value_label_decimals", 1)),
                label_headroom=(
                    None if chart.get("label_headroom") is None else float(chart["label_headroom"])
                ),
            )}
\caption{{{tex_escape(chart["caption"])}}}
\end{{subfigure}}
"""
        )
    return rf"""
\begin{{figure}}[p]
\centering
{chr(10).join(panels)}
\caption{{{tex_escape(title)}}}
\end{{figure}}
"""


def stacked_single_chart_figures(charts: list[dict[str, object]]) -> str:
    panels = []
    for chart in charts:
        ymin_value = chart.get("ymin")
        panels.append(
            rf"""
\begin{{minipage}}{{\textwidth}}
\centering
{bar_axis(
                str(chart["label"]),
                chart["rows"],
                scale=float(chart.get("scale", 1.0)),
                width=str(chart.get("width", r"\textwidth")),
                height=str(chart.get("height", "4.4cm")),
                bar_width=str(chart.get("bar_width", "7pt")),
                tick_label_width=str(chart.get("tick_label_width", "1.25cm")),
                ymode=str(chart.get("ymode", "linear")),
                ymin=None if ymin_value is None else float(ymin_value),
                coordinate_decimals=int(chart.get("coordinate_decimals", 3)),
                value_labels=bool(chart.get("value_labels", True)),
                value_label_decimals=int(chart.get("value_label_decimals", 1)),
                label_headroom=(
                    None if chart.get("label_headroom") is None else float(chart["label_headroom"])
                ),
            )}
\caption{{{tex_escape(chart["title"])}}}
\end{{minipage}}
"""
        )
    separator = "\n\\vspace{0.65cm}\n"
    return rf"""
\begin{{figure}}[p]
\centering
{separator.join(panels)}
\end{{figure}}
"""


def bar_chart(
    title: str,
    label: str,
    rows: list[dict[str, str]],
    scale: float = 1.0,
    caption: str | None = None,
    landscape: bool = False,
    height: str = "7cm",
    bar_width: str = "8pt",
    tick_label_width: str = "2.7cm",
) -> str:
    groups = chart_group_order(rows)
    xticks = ",".join(str(index) for index in range(1, len(groups) + 1))
    caption_text = caption or title
    width = r"\linewidth" if landscape else r"\textwidth"
    chart = rf"""
\begin{{figure}}[htbp]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
    ybar,
    width={width},
    height={height},
    bar width={bar_width},
    ymin=0,
    ylabel={{{tex_escape(label)}}},
    xtick={{{xticks}}},
    xticklabels={{{xtick_labels(groups)}}},
    x tick label style={{text width={tick_label_width}, align=center, font=\tiny}},
    legend style={{at={{(0.5,-0.28)}}, anchor=north, legend columns=3}},
    grid=both,
    major grid style={{draw=gridline}},
]
\addplot+[fill=bridge, draw=bridge] coordinates {{{chart_coordinates(rows, groups, "Bridge", scale)}}};
\addplot+[fill=forward, draw=forward] coordinates {{{chart_coordinates(rows, groups, "Bridge Forward", scale)}}};
\addplot+[fill=direct, draw=direct] coordinates {{{chart_coordinates(rows, groups, "Direct cable", scale)}}};
\legend{{Bridge, Bridge Forward, Direct cable}}
\end{{axis}}
\end{{tikzpicture}}
\caption{{{tex_escape(caption_text)}}}
\end{{figure}}
"""
    if landscape:
        return rf"""
\begin{{landscape}}
{chart}
\end{{landscape}}
"""
    return chart


def three_mode_table(
    rows: list[dict[str, str]],
    title: str,
    section_title: str | None = None,
    intro: str | None = None,
) -> str:
    return rf"""
\begin{{landscape}}
{three_mode_table_block(rows, title, section_title=section_title, intro=intro)}
\end{{landscape}}
"""


def three_mode_table_block(
    rows: list[dict[str, str]],
    title: str,
    section_title: str | None = None,
    intro: str | None = None,
) -> str:
    body = []
    for row in rows:
        metric, value_scale = display_metric_and_scale(row["metric"])
        body.append(
            " & ".join([
                tex_escape(row["group"]),
                tex_escape(metric),
                tex_scaled_num(row["bridge"], value_scale),
                tex_scaled_num(row["bridge_forward"], value_scale),
                tex_scaled_num(row["direct_cable"], value_scale),
                tex_delta(row["forward_vs_bridge"], value_scale),
                tex_delta(row["direct_vs_bridge"], value_scale),
                tex_delta(row["direct_vs_forward"], value_scale),
            ])
            + r" \\"
        )
    section_lines = []
    if section_title:
        section_lines.append(rf"\section{{{tex_escape(section_title)}}}")
    if intro:
        section_lines.append(tex_escape(intro))
    section_block = "\n\n".join(section_lines)
    return rf"""
{section_block}

\subsection{{{tex_escape(title)}}}
\begingroup
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\setlength{{\LTpre}}{{0.35em}}
\setlength{{\LTpost}}{{0.45em}}
\begin{{longtable}}{{@{{}}L{{5.0cm}}L{{4.0cm}}L{{1.65cm}}L{{1.65cm}}L{{1.65cm}}L{{2.8cm}}L{{2.8cm}}L{{2.8cm}}@{{}}}}
\toprule
Comparison group & Metric & Bridge & Forward & Direct & Forward vs Bridge & Direct vs Bridge & Direct vs Forward \\
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\endgroup
"""


def three_mode_section(
    serial_rows: list[dict[str, str]],
    can_rows: list[dict[str, str]],
) -> str:
    intro = (
        "The following tables focus only on groups where all three modes are available: "
        "Bridge, Bridge Forward, and Direct cable. Deltas are directional: orange means an "
        "increase, green means a decrease. Timing rows are displayed in milliseconds. "
        "Whether an increase is good depends on the metric."
    )
    return rf"""
\begin{{landscape}}
{three_mode_table_block(
        serial_rows,
        "RS485/UART Three-mode Deltas",
        section_title="Three-mode Delta Tables",
        intro=intro,
    )}

{three_mode_table_block(can_rows, "CAN Three-mode Deltas")}
\end{{landscape}}
"""


def overview_table(
    rows: list[dict[str, str]],
    kind_label: str,
    title: str,
    section_title: str | None = None,
) -> str:
    return rf"""
\begin{{landscape}}
{overview_table_block(rows, kind_label, title, section_title=section_title)}
\end{{landscape}}
"""


def overview_table_block(
    rows: list[dict[str, str]],
    kind_label: str,
    title: str,
    section_title: str | None = None,
) -> str:
    body = []
    for row in rows:
        target = tex_escape(capture_protocol_for_target(row["target"]))
        topology = tex_escape(topology_for_capture(row["capture"]))
        if kind_label == "CAN":
            metrics = [
                tex_int(row.get("frames", "")),
                tex_int(row.get("unique_can_ids", "")),
                tex_int(row.get("can_cycles", "")),
                tex_scaled_num(row.get("cycle_duration_min_us", ""), 0.001),
                tex_scaled_num(row.get("cycle_duration_avg_us", ""), 0.001),
                tex_scaled_num(row.get("cycle_duration_max_us", ""), 0.001),
                tex_scaled_num(row.get("cycle_duration_p95_us", ""), 0.001),
                tex_int(row.get("decode_errors", "")),
            ]
        else:
            metrics = [
                tex_int(row.get("frames", "")),
                tex_loss_rate(row),
                tex_scaled_num(row.get("request_to_response_avg_us", ""), 0.001),
                tex_scaled_num(row.get("request_to_response_p95_us", ""), 0.001),
                tex_scaled_num(row.get("full_exchange_p95_us", ""), 0.001),
            ]
        body.append(" & ".join([target, topology, *metrics]) + r" \\")

    if kind_label == "CAN":
        header = (
            r"Captured protocol & Topology & Frames & IDs & Cycles & Cycle min (ms) "
            r"& Cycle avg (ms) & Cycle max (ms) & Cycle P95 (ms) & Errors \\"
        )
        columns = (
            r"@{}L{4.8cm}L{2.35cm}L{1.2cm}L{1.0cm}L{1.2cm}"
            r"L{1.9cm}L{1.9cm}L{1.9cm}L{1.9cm}L{1.1cm}@{}"
        )
    else:
        header = (
            r"Captured protocol & Topology & Frames & Loss rate & Req->Rsp avg (ms) "
            r"& Req->Rsp P95 (ms) & Full P95 (ms) \\"
        )
        columns = (
            r"@{}L{4.8cm}L{2.35cm}L{1.4cm}L{1.5cm}"
            r"L{2.25cm}L{2.25cm}L{2.1cm}@{}"
        )

    section_block = rf"\section{{{tex_escape(section_title)}}}" if section_title else ""
    return rf"""
{section_block}

\subsection{{{tex_escape(title)}}}
\begingroup
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\setlength{{\LTpre}}{{0.35em}}
\setlength{{\LTpost}}{{0.45em}}
\begin{{longtable}}{{{columns}}}
\toprule
{header}
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\endgroup
"""


def overview_section(
    serial_rows: list[dict[str, str]],
    can_rows: list[dict[str, str]],
) -> str:
    return rf"""
\begin{{landscape}}
{overview_table_block(
        serial_rows,
        "RS485/UART",
        "RS485/UART Capture Overview",
        section_title="Capture Overview",
    )}

{overview_table_block(can_rows, "CAN", "CAN Capture Overview")}
\end{{landscape}}
"""


def capture_context_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append(
            " & ".join([
                tex_escape(topology_for_capture(row["capture"])),
                tex_escape(capture_id(row["capture"])),
                tex_escape(captured_side_for_row(row)),
                tex_escape(capture_protocol_for_target(row["target"])),
                tex_escape(inverter_device_for_capture(row["capture"])),
                tex_escape(inverter_protocol_for_row(row)),
                tex_escape(bms_device_for_target(row["target"])),
                tex_escape(bms_protocol_for_row(row)),
            ])
            + r" \\"
        )
    return rf"""
\begin{{landscape}}
\section*{{Capture Context Metadata}}

\small
This table separates the decoded bus from the physical devices used during the
test. Inverter protocol values may come from the captured bus or from fixed
test metadata for inverter models with a single tested protocol. \texttt{{not
captured}} means the opposite-side protocol is not proven by that capture or by
test metadata; it is not inferred from the comparison group name.

\begingroup
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\setlength{{\LTpre}}{{0.45em}}
\setlength{{\LTpost}}{{0.65em}}
\begin{{longtable}}{{@{{}}L{{1.6cm}}L{{3.6cm}}L{{2.2cm}}L{{3.0cm}}L{{2.0cm}}L{{2.8cm}}L{{2.0cm}}L{{3.0cm}}@{{}}}}
\caption{{Capture context metadata.}}\\
\toprule
Mode & Capture & Captured side & Captured protocol & Inverter device & Inverter protocol & BMS device & BMS protocol \\
\midrule
\endfirsthead
\caption[]{{Capture context metadata, continued.}}\\
\toprule
Mode & Capture & Captured side & Captured protocol & Inverter device & Inverter protocol & BMS device & BMS protocol \\
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\endgroup
\end{{landscape}}
"""


def direct_delta_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in direct_deltas(rows):
        metric, value_scale = display_metric_and_scale(row["metric"])
        metric = compact_direct_delta_metric(metric)
        group = row["group"]
        protocol = comparison_protocol(group)
        body.append(
            " & ".join([
                tex_escape(abbreviate_device(comparison_inverter_device(group))),
                tex_escape(abbreviate_protocol(protocol)),
                tex_escape(abbreviate_device(comparison_bms_device(group))),
                tex_escape(abbreviate_protocol(protocol)),
                tex_escape(metric),
                tex_scaled_num(row["direct_cable"], value_scale),
                tex_scaled_num(row["bridge"], value_scale),
                tex_delta(row["direct_vs_bridge"], value_scale),
            ])
            + r" \\"
        )
    return rf"""
\begin{{landscape}}
\begingroup
\setlength{{\tabcolsep}}{{3pt}}
\setlength{{\LTleft}}{{\fill}}
\setlength{{\LTright}}{{\fill}}
\setlength{{\LTpre}}{{0.45em}}
\setlength{{\LTpost}}{{0.65em}}
\small Abbreviations: GW=Growatt, JK=JKBMS, Sep=SeplosBMS, Anj=Anenji, Py=Pylon, IC=inter-cycle.

\begin{{longtable}}{{@{{}}L{{1.6cm}}L{{2.2cm}}L{{1.5cm}}L{{2.2cm}}L{{5.0cm}}L{{1.4cm}}L{{1.4cm}}L{{3.7cm}}@{{}}}}
\caption{{Direct cable versus Bridge values, sorted by absolute percentage difference.}}\\
\toprule
Inv. dev. & Inv. proto. & BMS dev. & BMS proto. & Metric & Direct & Bridge & Diff \\
\midrule
\endfirsthead
\caption[]{{Direct cable versus Bridge values, continued.}}\\
\toprule
Inv. dev. & Inv. proto. & BMS dev. & BMS proto. & Metric & Direct & Bridge & Diff \\
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\endgroup
\end{{landscape}}
"""


def document(overview: list[dict[str, str]], three_mode: list[dict[str, str]]) -> str:
    serial_rows = [row for row in overview if row["kind"] != "can"]
    can_rows = [row for row in overview if row["kind"] == "can"]
    topology_counts: dict[str, int] = defaultdict(int)
    for row in overview:
        topology_counts[topology_for_capture(row["capture"])] += 1

    rs485_req_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "request_to_response_avg_us",
    )
    rs485_full_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "full_exchange_p95_us",
    )
    rs485_full_min_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "full_exchange_min_us",
    )
    rs485_full_max_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "full_exchange_max_us",
    )
    rs485_gap_min_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "inter_cycle_gap_min_us",
    )
    rs485_gap_avg_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "inter_cycle_gap_avg_us",
    )
    rs485_gap_max_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        "inter_cycle_gap_max_us",
    )
    can_cycle_rows = overview_chart_rows(
        overview,
        "CAN",
        "cycle_duration_avg_us",
    )
    can_cycle_min_rows = overview_chart_rows(
        overview,
        "CAN",
        "cycle_duration_min_us",
    )
    can_cycle_max_rows = overview_chart_rows(
        overview,
        "CAN",
        "cycle_duration_max_us",
    )
    can_cycle_p95_rows = overview_chart_rows(
        overview,
        "CAN",
        "cycle_duration_p95_us",
    )
    can_gap_min_rows = overview_chart_rows(
        overview,
        "CAN",
        "inter_cycle_gap_min_us",
    )
    can_gap_avg_rows = overview_chart_rows(
        overview,
        "CAN",
        "inter_cycle_gap_avg_us",
    )
    can_gap_max_rows = overview_chart_rows(
        overview,
        "CAN",
        "inter_cycle_gap_max_us",
    )
    rs485_rate_rows = overview_chart_rows(
        overview,
        "RS485/UART",
        computed_key=complete_exchanges_per_second,
    )
    can_rate_rows = overview_chart_rows(
        overview,
        "CAN",
        computed_key=can_cycles_per_second,
    )

    observations = "\n".join(
        rf"\item {tex_escape(observation)}" for observation in make_observations(three_mode)
    )
    serial_three = [row for row in three_mode if row["kind"] == "RS485/UART"]
    can_three = [row for row in three_mode if row["kind"] == "CAN"]

    return rf"""\documentclass[11pt,a4paper]{{article}}

\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage[margin=1.8cm]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{tabularx}}
\usepackage{{array}}
\usepackage{{pdflscape}}
\usepackage{{subcaption}}
\usepackage[table]{{xcolor}}
\usepackage{{tikz}}
\usepackage{{pgfplots}}
\usepackage{{tcolorbox}}
\usepackage{{hyperref}}
\usepackage{{enumitem}}
\pgfplotsset{{compat=1.18}}

\definecolor{{bridge}}{{HTML}}{{2F6B9A}}
\definecolor{{forward}}{{HTML}}{{2E8B57}}
\definecolor{{direct}}{{HTML}}{{C96C2C}}
\definecolor{{accent}}{{HTML}}{{44546A}}
\definecolor{{panel}}{{HTML}}{{F4F7FA}}
\definecolor{{gridline}}{{HTML}}{{D8DEE8}}
\definecolor{{increasecolor}}{{HTML}}{{A64B2A}}
\definecolor{{decreasecolor}}{{HTML}}{{1F7A66}}

\newcommand{{\increase}}[1]{{\textcolor{{increasecolor}}{{#1}}}}
\newcommand{{\decrease}}[1]{{\textcolor{{decreasecolor}}{{#1}}}}
\newcolumntype{{L}}[1]{{>{{\raggedright\arraybackslash}}p{{#1}}}}
\newcolumntype{{Y}}{{>{{\raggedright\arraybackslash}}X}}
\newcommand{{\statbox}}[2]{{%
  \begin{{tcolorbox}}[colback=panel,colframe=accent,boxrule=0.4pt,arc=1mm,left=1mm,right=1mm,top=1mm,bottom=1mm]
  \centering{{\Large\bfseries #1}}\\[-1mm]{{\scriptsize #2}}
  \end{{tcolorbox}}%
}}

\hypersetup{{
  colorlinks=true,
  linkcolor=accent,
  urlcolor=bridge,
  pdftitle={{{tex_escape(REPORT_TITLE)}}},
}}

\title{{{tex_escape(REPORT_TITLE)}}}
\author{{Generated from offline sigrok/PulseView analysis outputs}}
\date{{}}

\begin{{document}}
\maketitle

\section*{{Executive Summary}}

\begin{{tabularx}}{{\textwidth}}{{YYYY}}
\statbox{{{len(overview)}}}{{total captures}} &
\statbox{{{len(serial_rows)}}}{{RS485/UART captures}} &
\statbox{{{len(can_rows)}}}{{CAN captures}} &
\statbox{{{topology_counts.get("Bridge", 0)} / {topology_counts.get("Bridge Forward", 0)} / {topology_counts.get("Direct cable", 0)}}}{{Bridge / Forward / Direct}} \\
\end{{tabularx}}

\begin{{tcolorbox}}[colback=panel,colframe=accent,title=Key observations]
\begin{{itemize}}[leftmargin=*]
{observations}
\end{{itemize}}
\end{{tcolorbox}}

{capture_context_table(overview)}

{direct_delta_table(three_mode)}

\section{{Protocol Overview Charts}}

These charts include every protocol group available in the overview CSV. Missing
topology modes are intentionally left blank, so a group can have one, two, or three
bars depending on the captures currently available.

For RS485/UART charts, the timing terms are:

\begin{{itemize}}[leftmargin=*]
\item Request-to-response latency: response start minus request end for a
complete paired exchange.
\item Full exchange duration: response end minus request start for a complete
paired exchange. This includes request transmission, turnaround/processing gap,
and response transmission.
\item Inter-exchange gap: response end of one complete exchange to request start
of the next complete exchange.
\item 95th percentile: the value below which 95\% of the measured complete
request/response pairs fall.
\end{{itemize}}

For CAN charts, cycle duration is the time from the first frame in a detected
CAN burst to the last frame in that burst. CAN cycle duration charts use a
logarithmic y-axis because values span multiple orders of magnitude, from
sub-millisecond single-frame cycles to multi-second capture-length cycles. CAN
cycle P95 is the closest counterpart to RS485/UART full-exchange P95 in this
report.

{paired_bar_charts(
        "RS485/UART protocol overview charts.",
        [
            {
                "label": "Request-to-response avg (ms)",
                "rows": rs485_req_rows,
                "scale": 0.001,
                "caption": "Average request-to-response latency for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
            {
                "label": "Full exchange 95th percentile (ms)",
                "rows": rs485_full_rows,
                "scale": 0.001,
                "caption": "P95 full-exchange duration for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
        ],
    )}

{paired_bar_charts(
        "CAN protocol overview charts.",
        [
            {
                "label": "Cycle avg (ms)",
                "rows": can_cycle_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Average CAN cycle duration, log scale.",
                "tick_label_width": "1.3cm",
                "width": r"0.99\textwidth",
                "height": "5.8cm",
                "label_headroom": 12.0,
            },
            {
                "label": "Cycle P95 (ms)",
                "rows": can_cycle_p95_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "95th-percentile CAN cycle duration, log scale.",
                "tick_label_width": "1.3cm",
                "width": r"0.99\textwidth",
                "height": "5.8cm",
                "label_headroom": 12.0,
            },
        ],
    )}

{paired_bar_charts(
        "RS485/UART inter-exchange gap overview charts.",
        [
            {
                "label": "Gap min (ms)",
                "rows": rs485_gap_min_rows,
                "scale": 0.001,
                "caption": "Minimum gap between complete RS485/UART exchanges.",
                "tick_label_width": "1.05cm",
            },
            {
                "label": "Gap avg (ms)",
                "rows": rs485_gap_avg_rows,
                "scale": 0.001,
                "caption": "Average gap between complete RS485/UART exchanges.",
                "tick_label_width": "1.05cm",
            },
            {
                "label": "Gap max (ms)",
                "rows": rs485_gap_max_rows,
                "scale": 0.001,
                "caption": "Maximum gap between complete RS485/UART exchanges.",
                "tick_label_width": "1.05cm",
            },
        ],
    )}

{paired_bar_charts(
        "CAN inter-cycle gap overview charts.",
        [
            {
                "label": "Gap min (ms)",
                "rows": can_gap_min_rows,
                "scale": 0.001,
                "caption": "Minimum inter-cycle gap for CAN protocol groups with at least two detected cycles.",
                "tick_label_width": "1.55cm",
            },
            {
                "label": "Gap avg (ms)",
                "rows": can_gap_avg_rows,
                "scale": 0.001,
                "caption": "Average inter-cycle gap for CAN protocol groups with at least two detected cycles.",
                "tick_label_width": "1.55cm",
            },
            {
                "label": "Gap max (ms)",
                "rows": can_gap_max_rows,
                "scale": 0.001,
                "caption": "Maximum inter-cycle gap for CAN protocol groups with at least two detected cycles.",
                "tick_label_width": "1.55cm",
            },
        ],
    )}

{paired_bar_charts(
        "RS485/UART full-exchange range overview charts.",
        [
            {
                "label": "Full exchange min (ms)",
                "rows": rs485_full_min_rows,
                "scale": 0.001,
                "caption": "Minimum full-exchange duration for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
            {
                "label": "Full exchange max (ms)",
                "rows": rs485_full_max_rows,
                "scale": 0.001,
                "caption": "Maximum full-exchange duration for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
        ],
    )}

{paired_bar_charts(
        "CAN cycle range overview charts.",
        [
            {
                "label": "Cycle min (ms)",
                "rows": can_cycle_min_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Minimum CAN cycle duration, log scale.",
                "tick_label_width": "1.3cm",
                "width": r"0.99\textwidth",
                "height": "5.8cm",
                "label_headroom": 12.0,
            },
            {
                "label": "Cycle max (ms)",
                "rows": can_cycle_max_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Maximum CAN cycle duration, log scale.",
                "tick_label_width": "1.3cm",
                "width": r"0.99\textwidth",
                "height": "5.8cm",
                "label_headroom": 12.0,
            },
        ],
    )}

{stacked_single_chart_figures(
        [
            {
                "title": "RS485/UART exchange rate overview chart.",
                "label": "Complete exchanges/s",
                "rows": rs485_rate_rows,
                "scale": 1.0,
                "tick_label_width": "1.05cm",
            },
            {
                "title": "CAN cycle rate overview chart.",
                "label": "Cycles/s",
                "rows": can_rate_rows,
                "scale": 1.0,
                "tick_label_width": "1.3cm",
            },
        ],
    )}

\clearpage

{three_mode_section(serial_three, can_three)}

\clearpage

{overview_section(serial_rows, can_rows)}

\section*{{Notes}}

\begin{{itemize}}[leftmargin=*]
\item The LaTeX source is generated from committed CSV files under \texttt{{analysis/out/}}.
\item Capture durations are not identical, so normalized rates are included where useful.
\item CAN cycle duration can be dominated by capture length when only one cycle is detected.
\item Compiled PDFs and LaTeX build artifacts should stay out of the repository.
\end{{itemize}}

\end{{document}}
"""


def main() -> int:
    if not OVERVIEW_CSV.exists():
        raise SystemExit(f"Missing overview CSV: {OVERVIEW_CSV}")
    if not THREE_MODE_CSV.exists():
        raise SystemExit(f"Missing three-mode comparison CSV: {THREE_MODE_CSV}")

    overview = read_csv(OVERVIEW_CSV)
    three_mode = read_csv(THREE_MODE_CSV)
    LATEX_DIR.mkdir(parents=True, exist_ok=True)
    MAIN_TEX.write_text(document(overview, three_mode), encoding="utf-8")
    print(f"wrote {MAIN_TEX.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
