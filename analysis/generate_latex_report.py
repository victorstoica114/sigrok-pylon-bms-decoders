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

REPORT_TITLE = "Sigrok BMS Protocol Decoder Capture Analysis"
DIRECT_DELTA_THRESHOLD_PERCENT = 40.0

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


def significant_direct_deltas(
    three_mode: list[dict[str, str]],
    min_abs_pct: float = DIRECT_DELTA_THRESHOLD_PERCENT,
) -> list[dict[str, str]]:
    candidates = []
    for row in three_mode:
        pct = percent_from_delta(row.get("direct_vs_bridge", ""))
        if pct is None:
            continue
        abs_pct = abs(pct)
        if abs_pct < min_abs_pct:
            continue
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
) -> str:
    by_group = {row["group"]: row for row in rows}
    coords = []
    for index, group in enumerate(groups, start=1):
        value = chart_value(by_group[group], topology)
        if value is None:
            continue
        coords.append(f"({index},{value * scale:.{decimals}f})")
    return " ".join(coords)


def xtick_labels(groups: list[str]) -> str:
    return ",".join(tex_escape(group) for group in groups)


def bar_axis(
    label: str,
    rows: list[dict[str, str]],
    scale: float = 1.0,
    height: str = "4.8cm",
    bar_width: str = "3.5pt",
    tick_label_width: str = "1.25cm",
    ymode: str = "linear",
    ymin: float | None = None,
    coordinate_decimals: int = 3,
) -> str:
    groups = chart_group_order(rows)
    xticks = ",".join(str(index) for index in range(1, len(groups) + 1))
    xmax = len(groups) + 0.5
    if ymode == "log":
        ymin_value = 0.1 if ymin is None else ymin
        y_options = (
            "    ymode=log,\n"
            "    log basis y=10,\n"
            "    log origin y=infty,\n"
            f"    ymin={ymin_value:.6g},"
        )
    else:
        ymin_value = 0.0 if ymin is None else ymin
        y_options = f"    ymin={ymin_value:.6g},"
    return rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
    ybar,
    width=\textwidth,
    height={height},
    bar width={bar_width},
{y_options}
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
\addplot+[fill=bridge, draw=bridge] coordinates {{{chart_coordinates(rows, groups, "Bridge", scale, coordinate_decimals)}}};
\addplot+[fill=forward, draw=forward] coordinates {{{chart_coordinates(rows, groups, "Bridge Forward", scale, coordinate_decimals)}}};
\addplot+[fill=direct, draw=direct] coordinates {{{chart_coordinates(rows, groups, "Direct cable", scale, coordinate_decimals)}}};
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
                height=str(chart.get("height", "4.8cm")),
                bar_width=str(chart.get("bar_width", "3.5pt")),
                tick_label_width=str(chart.get("tick_label_width", "1.25cm")),
                ymode=str(chart.get("ymode", "linear")),
                ymin=None if ymin_value is None else float(ymin_value),
                coordinate_decimals=int(chart.get("coordinate_decimals", 3)),
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
\begin{{landscape}}
{section_block}

\subsection{{{tex_escape(title)}}}
\scriptsize
\begingroup
\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}>{{\raggedright\arraybackslash}}p{{5.0cm}}>{{\raggedright\arraybackslash}}p{{3.2cm}}rrr>{{\raggedright\arraybackslash}}p{{2.8cm}}>{{\raggedright\arraybackslash}}p{{2.8cm}}>{{\raggedright\arraybackslash}}p{{2.8cm}}@{{}}}}
\toprule
Group & Metric & Bridge & Forward & Direct & Forward vs Bridge & Direct vs Bridge & Direct vs Forward \\
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\endgroup
\end{{landscape}}
"""


def overview_table(
    rows: list[dict[str, str]],
    kind_label: str,
    title: str,
    section_title: str | None = None,
) -> str:
    body = []
    for row in rows:
        target = tex_escape(row["target"].replace("_", " "))
        topology = tex_escape(topology_for_capture(row["capture"]))
        if kind_label == "CAN":
            metrics = [
                tex_int(row.get("frames", "")),
                tex_int(row.get("unique_can_ids", "")),
                tex_int(row.get("can_cycles", "")),
                tex_num(row.get("cycle_duration_min_us", "")),
                tex_num(row.get("cycle_duration_avg_us", "")),
                tex_num(row.get("cycle_duration_max_us", "")),
                tex_num(row.get("cycle_duration_p95_us", "")),
                tex_int(row.get("decode_errors", "")),
            ]
        else:
            metrics = [
                tex_int(row.get("frames", "")),
                tex_int(row.get("complete_sequences", "")),
                tex_int(row.get("incomplete_orphan_rows", "")),
                tex_num(row.get("request_to_response_avg_us", "")),
                tex_num(row.get("request_to_response_p95_us", "")),
                tex_num(row.get("full_exchange_p95_us", "")),
            ]
        body.append(" & ".join([target, topology, *metrics]) + r" \\")

    if kind_label == "CAN":
        header = (
            r"Target & Topology & Frames & IDs & Cycles & Cycle min (us) "
            r"& Cycle avg (us) & Cycle max (us) & Cycle P95 (us) & Errors \\"
        )
        columns = r"p{3.6cm}p{1.8cm}rrrrrrrr"
    else:
        header = (
            r"Target & Topology & Frames & Complete & Incomplete & Req->Rsp avg (us) "
            r"& Req->Rsp P95 (us) & Full P95 (us) \\"
        )
        columns = r"p{4.1cm}p{2.0cm}rrrrrr"

    section_block = rf"\section{{{tex_escape(section_title)}}}" if section_title else ""
    return rf"""
\begin{{landscape}}
{section_block}

\subsection{{{tex_escape(title)}}}
\scriptsize
\begin{{longtable}}{{{columns}}}
\toprule
{header}
\midrule
\endhead
{chr(10).join(body)}
\bottomrule
\end{{longtable}}
\normalsize
\end{{landscape}}
"""


def direct_delta_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in significant_direct_deltas(rows):
        metric, value_scale = display_metric_and_scale(row["metric"])
        body.append(
            " & ".join([
                tex_escape(row["group"]),
                tex_escape(metric),
                tex_delta(row["direct_vs_bridge"], value_scale),
                tex_escape(row["abs_pct"]) + r"\%",
            ])
            + r" \\"
        )
    threshold_label = format_number(DIRECT_DELTA_THRESHOLD_PERCENT)
    return rf"""
\begin{{table}}[htbp]
\centering
\caption{{Direct cable versus Bridge changes with at least {threshold_label}\% absolute difference.}}
\begingroup
\setlength{{\tabcolsep}}{{3pt}}
\begin{{tabular}}{{@{{}}>{{\raggedright\arraybackslash}}p{{5.0cm}}>{{\raggedright\arraybackslash}}p{{4.2cm}}>{{\raggedright\arraybackslash}}p{{3.2cm}}@{{\hspace{{0.15cm}}}}>{{\raggedright\arraybackslash}}p{{2.2cm}}@{{}}}}
\toprule
Group & Metric & Direct vs Bridge & Abs. change \\
\midrule
{chr(10).join(body)}
\bottomrule
\end{{tabular}}
\endgroup
\end{{table}}
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
    can_gap_min_rows = overview_chart_rows(
        overview,
        "CAN",
        "inter_cycle_gap_min_us",
    )
    can_gap_max_rows = overview_chart_rows(
        overview,
        "CAN",
        "inter_cycle_gap_max_us",
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

\begin{{tabularx}}{{\textwidth}}{{XXXX}}
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

{direct_delta_table(three_mode)}

\section{{Protocol Overview Charts}}

These charts include every protocol group available in the overview CSV. Missing
topology modes are intentionally left blank, so a group can have one, two, or three
bars depending on the captures currently available.

CAN cycle duration charts use a logarithmic y-axis because values span multiple
orders of magnitude, from sub-millisecond single-frame cycles to multi-second
capture-length cycles.

{paired_bar_charts(
        "RS485/UART protocol overview charts.",
        [
            {
                "label": "Req->Rsp avg (ms)",
                "rows": rs485_req_rows,
                "scale": 0.001,
                "caption": "Average request-to-response latency for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
            {
                "label": "Full exchange P95 (ms)",
                "rows": rs485_full_rows,
                "scale": 0.001,
                "caption": "P95 full-exchange duration for all available RS485/UART protocol groups.",
                "tick_label_width": "1.05cm",
            },
        ],
    )}

{paired_bar_charts(
        "CAN cycle duration overview charts.",
        [
            {
                "label": "Cycle min (ms)",
                "rows": can_cycle_min_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Minimum CAN cycle duration, log scale, for all available CAN protocol groups.",
                "tick_label_width": "1.3cm",
            },
            {
                "label": "Cycle avg (ms)",
                "rows": can_cycle_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Average CAN cycle duration, log scale, for all available CAN protocol groups.",
                "tick_label_width": "1.3cm",
            },
        ],
    )}

{paired_bar_charts(
        "CAN maximum cycle duration and throughput charts.",
        [
            {
                "label": "Cycle max (ms)",
                "rows": can_cycle_max_rows,
                "scale": 0.001,
                "ymode": "log",
                "ymin": 0.1,
                "caption": "Maximum CAN cycle duration, log scale, for all available CAN protocol groups.",
                "tick_label_width": "1.3cm",
            },
            {
                "label": "Cycles/s",
                "rows": can_rate_rows,
                "scale": 1.0,
                "caption": "CAN cycle rate normalized by capture duration for all available CAN protocol groups.",
                "tick_label_width": "1.3cm",
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
                "label": "Gap max (ms)",
                "rows": can_gap_max_rows,
                "scale": 0.001,
                "caption": "Maximum inter-cycle gap for CAN protocol groups with at least two detected cycles.",
                "tick_label_width": "1.55cm",
            },
        ],
    )}

\clearpage

{three_mode_table(
        serial_three,
        "RS485/UART Three-mode Deltas",
        section_title="Three-mode Delta Tables",
        intro=(
            "The following tables focus only on groups where all three modes are available: "
            "Bridge, Bridge Forward, and Direct cable. Deltas are directional: orange means an "
            "increase, green means a decrease. Timing rows are displayed in milliseconds. "
            "Whether an increase is good depends on the metric."
        ),
    )}

{three_mode_table(can_three, "CAN Three-mode Deltas")}

\clearpage

{overview_table(
        serial_rows,
        "RS485/UART",
        "RS485/UART Capture Overview",
        section_title="Capture Overview",
    )}

{overview_table(can_rows, "CAN", "CAN Capture Overview")}

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
