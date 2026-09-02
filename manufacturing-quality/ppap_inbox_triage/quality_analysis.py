from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .models import InboxFile
from .pdf_text import ALL_PAGES, extract_pdf_pages, extract_pdf_text
from .pfmea_ap import (
    AP_RANK,
    benchmark_actions_for_failure_mode,
    compare_table_vs_benchmark,
    pfmea_action_priority,
    pfmea_sort_key,
    split_table_actions,
)
from .pfmea_xlsx import parse_pfmea_xlsx_rows, read_xlsx_rows
from .skill_loader import pfmea_countermeasure_playbook, quality_thresholds

# Bump when capability/MSA/PFMEA parsing rules change — shown in the dashboard sidebar.
QUALITY_PARSER_VERSION = "2026-09-02e"


@dataclass(frozen=True)
class MetricFinding:
    metric: str
    value: float
    threshold: float
    comparison: str
    status: str
    source_file: str
    page_number: int | None = None
    context: str = ""


@dataclass(frozen=True)
class PfmeaRow:
    failure_mode: str
    severity: int
    occurrence: int
    detection: int
    rpn: int
    action_priority: str
    table_actions: tuple[str, ...]
    benchmark_actions: tuple[str, ...]
    comparison_notes: tuple[str, ...]
    source_file: str
    page_number: int | None = None
    rank: int = 0


@dataclass
class QualityAnalysis:
    msa_findings: list[MetricFinding] = field(default_factory=list)
    capability_findings: list[MetricFinding] = field(default_factory=list)
    pfmea_top_ap: list[PfmeaRow] = field(default_factory=list)
    pfmea_benchmark_notes: list[str] = field(default_factory=list)
    pfmea_ranking_method: str = "AIAG/VDA 2019 Action Priority (H → M → L)"
    pfmea_default_practices: list[str] = field(default_factory=list)
    quality_blocking: bool = False
    flags: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        return {
            "parser_version": QUALITY_PARSER_VERSION,
            "msa_findings": [
                {
                    "metric": item.metric,
                    "value": item.value,
                    "threshold": item.threshold,
                    "comparison": item.comparison,
                    "status": item.status,
                    "source_file": item.source_file,
                    "page_number": item.page_number,
                    "context": item.context,
                }
                for item in self.msa_findings
            ],
            "capability_findings": [
                {
                    "metric": item.metric,
                    "value": item.value,
                    "threshold": item.threshold,
                    "comparison": item.comparison,
                    "status": item.status,
                    "source_file": item.source_file,
                    "page_number": item.page_number,
                    "context": item.context,
                }
                for item in self.capability_findings
            ],
            "pfmea_top_ap": [
                {
                    "rank": row.rank,
                    "failure_mode": row.failure_mode,
                    "severity": row.severity,
                    "occurrence": row.occurrence,
                    "detection": row.detection,
                    "rpn": row.rpn,
                    "action_priority": row.action_priority,
                    "table_actions": list(row.table_actions),
                    "benchmark_actions": list(row.benchmark_actions),
                    "comparison_notes": list(row.comparison_notes),
                    "source_file": row.source_file,
                    "page_number": row.page_number,
                }
                for row in self.pfmea_top_ap
            ],
            # Backward-compatible alias for older dashboard sessions.
            "pfmea_top_rpn": [
                {
                    "rank": row.rank,
                    "failure_mode": row.failure_mode,
                    "severity": row.severity,
                    "occurrence": row.occurrence,
                    "detection": row.detection,
                    "rpn": row.rpn,
                    "action_priority": row.action_priority,
                    "table_actions": list(row.table_actions),
                    "benchmark_actions": list(row.benchmark_actions),
                    "comparison_notes": list(row.comparison_notes),
                    "countermeasures": list(row.benchmark_actions),
                    "source_file": row.source_file,
                    "page_number": row.page_number,
                }
                for row in self.pfmea_top_ap
            ],
            "pfmea_benchmark_notes": list(self.pfmea_benchmark_notes),
            "pfmea_ranking_method": self.pfmea_ranking_method,
            "pfmea_default_practices": list(self.pfmea_default_practices),
            "quality_blocking": self.quality_blocking,
            "flags": list(self.flags),
        }


GRR_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:%?\s*grr|gr&r|grr)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%", re.I),
    re.compile(r"(\d+(?:\.\d+)?)\s*%\s*(?:grr|gr&r)", re.I),
    re.compile(r"(?:percent|percentage)\s+grr[^\d]{0,20}(\d+(?:\.\d+)?)", re.I),
    re.compile(r"(?:测量系统|量具).{0,12}(?:grr|重复性).{0,20}(\d+(?:\.\d+)?)\s*%", re.I),
)

CPK_LABELED_PATTERN = re.compile(
    r"\b(?P<label>cpk|ppk)\b\s*[:=]\s*(?P<value>\d+(?:\.\d+)?)",
    re.I,
)
CPK_DECIMAL_AFTER_LABEL = re.compile(
    r"\b(?P<label>cpk|ppk)\b\s+(?P<value>\d+\.\d+)",
    re.I,
)
CPK_DECIMAL_BEFORE_LABEL = re.compile(
    r"(?P<value>\d+\.\d+)\s*\b(?P<label>cpk|ppk)\b",
    re.I,
)
CPK_CHINESE_PATTERN = re.compile(
    r"过程能力指数\s*[:：]?\s*(?P<value>\d+(?:\.\d+)?)",
    re.I,
)

CPK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("labeled", CPK_LABELED_PATTERN),
    ("decimal_after", CPK_DECIMAL_AFTER_LABEL),
    ("decimal_before", CPK_DECIMAL_BEFORE_LABEL),
    ("chinese", CPK_CHINESE_PATTERN),
)

RPN_ROW_PATTERN = re.compile(
    r"(?P<mode>[A-Za-z\u4e00-\u9fff][^\n]{8,120}?)\s+"
    r"(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})\b",
    re.I,
)

LINE_SOD_RPN_PATTERN = re.compile(
    r"^(?P<mode>.{10,90}?)\s+(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})(?:\s+(?P<action>.+))?\s*$",
    re.M,
)

RECOMMENDED_ACTION_PATTERN = re.compile(
    r"(?:recommended\s+actions?|actions?\s+taken|prevention\s+controls?|"
    r"recommended\s+countermeasures?|措施|对策|建议措施)\s*[:：]\s*(?P<action>.{12,220})",
    re.I,
)

SOD_RPN_TUPLE_PATTERN = re.compile(
    r"\b(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})\b",
)

SOD_RPN_AP_INLINE_PATTERN = re.compile(
    r"\b(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})\s+(?P<ap>[HML])\b",
    re.I,
)

EXPLICIT_AP_PATTERN = re.compile(r"\b(?:ap|action\s+priority|行动优先级)\s*[:：]?\s*([HML])\b", re.I)

RPN_INLINE_PATTERN = re.compile(
    r"rpn\s*[:=]?\s*(?P<rpn>\d{2,4})",
    re.I,
)

PFMEA_FILENAME_TOKENS: tuple[str, ...] = (
    "pfmea",
    "dfmea",
    "fmea",
    "过程fmea",
    "過程fmea",
    "过程 fmea",
)

PFMEA_SPREADSHEET_SUFFIXES: tuple[str, ...] = (".xlsx", ".xlsm")


def _normalize_explicit_ap(value: str) -> str:
    cleaned = value.strip().upper()
    if cleaned in AP_RANK:
        return cleaned
    if cleaned and cleaned[0] in AP_RANK:
        return cleaned[0]
    return ""


def _split_action_tail(tail: str) -> tuple[str, str]:
    """Return (explicit_ap, action_text) from text after S/O/D/RPN."""
    stripped = tail.strip()
    if not stripped:
        return "", ""
    ap_match = re.match(r"^(?P<ap>[HML])\b\s*(?P<action>.*)$", stripped, re.I)
    if ap_match:
        return ap_match.group("ap").upper(), ap_match.group("action").strip()
    ap_label = EXPLICIT_AP_PATTERN.search(stripped)
    if ap_label:
        action_text = stripped[ap_label.end() :].strip(" -:;|")
        return ap_label.group(1).upper(), action_text
    return "", stripped


def _is_pfmea_filename(filename: str) -> bool:
    lowered = filename.lower()
    return any(token in lowered for token in PFMEA_FILENAME_TOKENS)


def _is_pfmea_spreadsheet(inbox_file: InboxFile) -> bool:
    return (
        inbox_file.suffix.lower() in PFMEA_SPREADSHEET_SUFFIXES
        and _is_pfmea_filename(inbox_file.name)
    )


def _looks_like_pfmea(text: str) -> bool:
    lowered = text.lower()
    return (
        "pfmea" in lowered
        or "process fmea" in lowered
        or "过程fmea" in lowered
        or "过程 fmea" in lowered
        or "失效模式" in text
        or "fmea" in lowered
    )


def _looks_like_rpn_table(text: str) -> bool:
    if RPN_INLINE_PATTERN.search(text):
        return True
    if len(SOD_RPN_TUPLE_PATTERN.findall(text)) >= 1:
        return True
    if re.search(r"\b(?:sev|severity|严重度)\b", text, re.I) and re.search(
        r"\b(?:occ|occurrence|频度)\b", text, re.I
    ):
        return True
    return False


def _pfmea_scan_needed(
    text: str,
    inbox_file: InboxFile,
    page_number: int | None,
    pfmea_pages_by_file: dict[str, set[int | None]],
) -> bool:
    if _looks_like_pfmea(text) or _looks_like_rpn_table(text):
        return True
    if _is_pfmea_filename(inbox_file.name):
        return True
    pages = pfmea_pages_by_file.get(inbox_file.relative_path)
    if not pages:
        return False
    if None in pages:
        return True
    return page_number in pages


def _valid_sod_rpn(sev: int, occ: int, det: int, rpn: int) -> bool:
    if not (1 <= sev <= 10 and 1 <= occ <= 10 and 1 <= det <= 10):
        return False
    if rpn < 40:
        return False
    if abs(rpn - sev * occ * det) > max(15, rpn * 0.25):
        return False
    return True


def _make_pfmea_row(
    *,
    failure_mode: str,
    severity: int,
    occurrence: int,
    detection: int,
    rpn: int,
    table_actions: tuple[str, ...],
    source_file: str,
    page_number: int | None,
    playbook: dict[str, Any],
    explicit_ap: str = "",
) -> PfmeaRow | None:
    if not table_actions:
        return None
    mode = re.sub(r"\s+", " ", failure_mode).strip(" -:;|")
    if len(mode) < 8:
        mode = f"PFMEA failure mode (RPN {rpn})"
    normalized_ap = _normalize_explicit_ap(explicit_ap)
    if normalized_ap:
        ap = normalized_ap
    elif severity:
        ap = pfmea_action_priority(severity, occurrence, detection)
    else:
        ap = "M"
    benchmark = benchmark_actions_for_failure_mode(mode, playbook)
    return PfmeaRow(
        failure_mode=mode[:120],
        severity=severity,
        occurrence=occurrence,
        detection=detection,
        rpn=rpn,
        action_priority=ap,
        table_actions=table_actions,
        benchmark_actions=benchmark,
        comparison_notes=compare_table_vs_benchmark(
            table_actions=table_actions,
            benchmark_actions=benchmark,
            failure_mode=mode,
            action_priority=ap,
        ),
        source_file=source_file,
        page_number=page_number,
    )


def _is_spurious_capability_reading(label: str, value: float, context: str) -> bool:
    """Reject row labels like 'Cpk 1' (characteristic #1), not Cpk = 1.00."""
    stripped = context.strip()
    if re.match(rf"^{re.escape(label)}\s+\d{{1,2}}$", stripped, re.I):
        return True
    if value == int(value) and 1 <= int(value) <= 9:
        if "." not in stripped and ":" not in stripped and "=" not in stripped:
            return True
    return False


def _extract_grr_values(text: str) -> list[tuple[float, str]]:
    hits: list[tuple[float, str]] = []
    for pattern in GRR_PATTERNS:
        for match in pattern.finditer(text):
            value = float(match.group(1))
            if 0 < value <= 100:
                hits.append((value, match.group(0).strip()[:80]))
    return hits


def _extract_capability_values(text: str) -> list[tuple[str, float, str]]:
    hits: list[tuple[str, float, str]] = []
    seen: set[tuple[str, float, str]] = set()
    for kind, pattern in CPK_PATTERNS:
        for match in pattern.finditer(text):
            if kind == "chinese":
                label = "Cpk"
            else:
                label = "Cpk" if match.group("label").lower() == "cpk" else "Ppk"
            value = float(match.group("value"))
            if not (0 < value <= 5):
                continue
            # Skip "1.05 Ppk" parsed from "Cpk = 1.05 Ppk: 1.08" — value belongs to Cpk.
            if kind == "decimal_before":
                prefix = text[max(0, match.start() - 6) : match.start()]
                if re.search(r"[:=]\s*$", prefix):
                    continue
            context = match.group(0).strip()[:80]
            if _is_spurious_capability_reading(label, value, context):
                continue
            key = (label, value, context)
            if key in seen:
                continue
            seen.add(key)
            hits.append((label, value, context))
    return hits


def _parse_pfmea_rows(text: str, *, source_file: str, page_number: int | None) -> list[PfmeaRow]:
    rows: list[PfmeaRow] = []
    playbook = pfmea_countermeasure_playbook()
    seen: set[tuple[str, int, str]] = set()

    def add_row(
        *,
        failure_mode: str,
        severity: int,
        occurrence: int,
        detection: int,
        rpn: int,
        table_action_text: str = "",
        explicit_ap: str = "",
        from_action_column: bool = False,
    ) -> None:
        if severity or occurrence or detection:
            if not _valid_sod_rpn(severity, occurrence, detection, rpn):
                return
        elif rpn < 40:
            return
        table_actions = split_table_actions(
            table_action_text,
            from_action_column=from_action_column,
        )
        if not table_actions:
            return
        key = (failure_mode.lower()[:60], rpn, table_actions[0][:40])
        if key in seen:
            return
        seen.add(key)
        row = _make_pfmea_row(
            failure_mode=failure_mode,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn,
            table_actions=table_actions,
            source_file=source_file,
            page_number=page_number,
            playbook=playbook,
            explicit_ap=explicit_ap,
        )
        if row:
            rows.append(row)

    for match in RECOMMENDED_ACTION_PATTERN.finditer(text):
        action_text = match.group("action")
        context_start = max(0, match.start() - 120)
        context = text[context_start : match.start()]
        tuple_match = SOD_RPN_TUPLE_PATTERN.search(context)
        if tuple_match:
            mode = context[: tuple_match.start()].strip(" -:;|")
            explicit_ap = ""
            ap_match = EXPLICIT_AP_PATTERN.search(context[tuple_match.end() :])
            if ap_match:
                explicit_ap = ap_match.group(1)
            add_row(
                failure_mode=mode,
                severity=int(tuple_match.group("sev")),
                occurrence=int(tuple_match.group("occ")),
                detection=int(tuple_match.group("det")),
                rpn=int(tuple_match.group("rpn")),
                table_action_text=action_text,
                explicit_ap=explicit_ap,
                from_action_column=True,
            )

    for match in SOD_RPN_AP_INLINE_PATTERN.finditer(text):
        end = match.end()
        tail = text[end : end + 220].split("\n", 1)[0]
        mode = text[max(0, match.start() - 90) : match.start()].strip(" -:;|")
        add_row(
            failure_mode=mode,
            severity=int(match.group("sev")),
            occurrence=int(match.group("occ")),
            detection=int(match.group("det")),
            rpn=int(match.group("rpn")),
            table_action_text=tail,
            explicit_ap=match.group("ap"),
            from_action_column=True,
        )

    for match in RPN_ROW_PATTERN.finditer(text):
        end = match.end()
        tail = text[end : end + 220].split("\n", 1)[0]
        explicit_ap, action_text = _split_action_tail(tail)
        add_row(
            failure_mode=match.group("mode"),
            severity=int(match.group("sev")),
            occurrence=int(match.group("occ")),
            detection=int(match.group("det")),
            rpn=int(match.group("rpn")),
            table_action_text=action_text,
            explicit_ap=explicit_ap,
            from_action_column=bool(explicit_ap),
        )

    for match in LINE_SOD_RPN_PATTERN.finditer(text):
        explicit_ap, action_text = _split_action_tail(match.group("action") or "")
        add_row(
            failure_mode=match.group("mode"),
            severity=int(match.group("sev")),
            occurrence=int(match.group("occ")),
            detection=int(match.group("det")),
            rpn=int(match.group("rpn")),
            table_action_text=action_text,
            explicit_ap=explicit_ap,
            from_action_column=bool(explicit_ap or action_text),
        )

    for line in text.splitlines():
        line = line.strip()
        if len(line) < 12:
            continue
        tuple_match = SOD_RPN_TUPLE_PATTERN.search(line)
        if not tuple_match:
            continue
        mode = line[: tuple_match.start()].strip(" -:;|")
        tail = line[tuple_match.end() :].strip()
        explicit_ap, action_text = _split_action_tail(tail)
        add_row(
            failure_mode=mode,
            severity=int(tuple_match.group("sev")),
            occurrence=int(tuple_match.group("occ")),
            detection=int(tuple_match.group("det")),
            rpn=int(tuple_match.group("rpn")),
            table_action_text=action_text,
            explicit_ap=explicit_ap,
            from_action_column=bool(explicit_ap or action_text),
        )

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    index = 0
    while index + 3 < len(lines):
        try:
            severity = int(lines[index])
            occurrence = int(lines[index + 1])
            detection = int(lines[index + 2])
            rpn = int(lines[index + 3])
        except ValueError:
            index += 1
            continue
        if not _valid_sod_rpn(severity, occurrence, detection, rpn):
            index += 1
            continue
        mode = lines[index - 1] if index > 0 else ""
        cursor = index + 4
        explicit_ap = ""
        if cursor < len(lines) and lines[cursor].upper() in AP_RANK:
            explicit_ap = lines[cursor].upper()
            cursor += 1
        action_parts: list[str] = []
        while cursor < len(lines):
            candidate = lines[cursor]
            if re.fullmatch(r"\d{1,2}", candidate):
                break
            if SOD_RPN_TUPLE_PATTERN.search(candidate):
                break
            action_parts.append(candidate)
            cursor += 1
            if len(" ".join(action_parts)) >= 180:
                break
        add_row(
            failure_mode=mode,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn,
            table_action_text=" ".join(action_parts),
            explicit_ap=explicit_ap,
            from_action_column=True,
        )
        index = cursor

    return rows


def _parse_pfmea_xlsx_file(inbox_file: InboxFile) -> list[PfmeaRow]:
    table = read_xlsx_rows(inbox_file.path)
    if not table:
        return []
    playbook = pfmea_countermeasure_playbook()
    seen: set[tuple[str, int, str]] = set()

    def make_row(
        *,
        failure_mode: str,
        severity: int,
        occurrence: int,
        detection: int,
        rpn: int,
        table_action_text: str = "",
        explicit_ap: str = "",
        from_action_column: bool = False,
    ) -> PfmeaRow | None:
        if severity or occurrence or detection:
            if not _valid_sod_rpn(severity, occurrence, detection, rpn):
                return None
        elif rpn < 40:
            return None
        table_actions = split_table_actions(
            table_action_text,
            from_action_column=from_action_column,
        )
        if not table_actions:
            return None
        key = (failure_mode.lower()[:60], rpn, table_actions[0][:40])
        if key in seen:
            return None
        seen.add(key)
        return _make_pfmea_row(
            failure_mode=failure_mode,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn,
            table_actions=table_actions,
            source_file=inbox_file.relative_path,
            page_number=None,
            playbook=playbook,
            explicit_ap=explicit_ap,
        )

    return parse_pfmea_xlsx_rows(
        table,
        source_file=inbox_file.relative_path,
        make_row=make_row,
    )


def _collect_text_chunks(
    inbox_file: InboxFile,
    *,
    use_pdf_text: bool,
    binder_mode: bool,
) -> list[tuple[int | None, str]]:
    if not use_pdf_text or inbox_file.suffix.lower() != ".pdf":
        return []
    if binder_mode:
        pages = extract_pdf_pages(inbox_file.path, max_pages=ALL_PAGES)
        return [(page, text) for page, text in pages if text.strip()]
    text = extract_pdf_text(inbox_file.path)
    if not text:
        return []
    return [(None, text)]


def analyze_inbox_quality(
    inbox_files: list[InboxFile],
    *,
    use_pdf_text: bool,
    binder_files: set[str],
    pfmea_pages_by_file: dict[str, set[int | None]] | None = None,
) -> QualityAnalysis:
    thresholds = quality_thresholds()
    playbook = pfmea_countermeasure_playbook()
    grr_max = float(thresholds.get("msa_percent_grr_max", 10.0))
    cpk_min = float(thresholds.get("cpk_min", 1.33))
    ppk_min = float(thresholds.get("ppk_min", 1.33))
    top_ap_limit = int(thresholds.get("pfmea_top_ap_limit", thresholds.get("pfmea_top_rpn_limit", 5)))
    pfmea_pages = pfmea_pages_by_file or {}

    analysis = QualityAnalysis()
    analysis.pfmea_benchmark_notes = [
        str(item) for item in thresholds.get("references", []) if item
    ]
    analysis.pfmea_ranking_method = str(
        thresholds.get(
            "pfmea_ranking_method",
            "AIAG/VDA 2019 Action Priority (H → M → L)",
        )
    )
    analysis.pfmea_default_practices = [
        str(item) for item in playbook.get("default_countermeasures", []) if item
    ]
    pfmea_rows: list[PfmeaRow] = []

    for inbox_file in inbox_files:
        if _is_pfmea_spreadsheet(inbox_file):
            pfmea_rows.extend(_parse_pfmea_xlsx_file(inbox_file))
            continue
        if inbox_file.suffix.lower() != ".pdf":
            continue
        binder_mode = inbox_file.relative_path in binder_files
        for page_number, text in _collect_text_chunks(
            inbox_file,
            use_pdf_text=use_pdf_text,
            binder_mode=binder_mode,
        ):
            for value, context in _extract_grr_values(text):
                status = "fail" if value > grr_max else "pass"
                finding = MetricFinding(
                    metric="%GRR",
                    value=value,
                    threshold=grr_max,
                    comparison=">",
                    status=status,
                    source_file=inbox_file.relative_path,
                    page_number=page_number,
                    context=context,
                )
                analysis.msa_findings.append(finding)
                if status == "fail":
                    flag = (
                        f"MSA %GRR {value:.2f}% exceeds AIAG benchmark {grr_max:.0f}% "
                        f"({inbox_file.relative_path}"
                        f"{f', page {page_number}' if page_number else ''})"
                    )
                    analysis.flags.append(flag)
                    analysis.quality_blocking = True
                    analysis.actions.append(
                        "MSA unacceptable: %GRR above 10% — repeat Gage R&R after gauge/fixture "
                        "calibration, operator training, and measurement method review"
                    )

            for label, value, context in _extract_capability_values(text):
                if _is_spurious_capability_reading(label, value, context):
                    continue
                minimum = cpk_min if label == "Cpk" else ppk_min
                status = "fail" if value < minimum else "pass"
                finding = MetricFinding(
                    metric=label,
                    value=value,
                    threshold=minimum,
                    comparison="<",
                    status=status,
                    source_file=inbox_file.relative_path,
                    page_number=page_number,
                    context=context,
                )
                analysis.capability_findings.append(finding)
                if status == "fail":
                    flag = (
                        f"{label} {value:.2f} below automotive benchmark {minimum:.2f} "
                        f"({inbox_file.relative_path}"
                        f"{f', page {page_number}' if page_number else ''})"
                    )
                    analysis.flags.append(flag)
                    analysis.quality_blocking = True
                    analysis.actions.append(
                        f"Process capability gap: {label} {value:.2f} < {minimum:.2f} — "
                        "run special-cause analysis, tighten controls on special characteristics, "
                        "and re-run capability after corrective action"
                    )

            if _pfmea_scan_needed(text, inbox_file, page_number, pfmea_pages):
                pfmea_rows.extend(
                    _parse_pfmea_rows(
                        text,
                        source_file=inbox_file.relative_path,
                        page_number=page_number,
                    )
                )

    pfmea_rows.sort(key=pfmea_sort_key)
    analysis.pfmea_top_ap = []
    for index, row in enumerate(pfmea_rows[:top_ap_limit], start=1):
        analysis.pfmea_top_ap.append(
            PfmeaRow(
                failure_mode=row.failure_mode,
                severity=row.severity,
                occurrence=row.occurrence,
                detection=row.detection,
                rpn=row.rpn,
                action_priority=row.action_priority,
                table_actions=row.table_actions,
                benchmark_actions=row.benchmark_actions,
                comparison_notes=row.comparison_notes,
                source_file=row.source_file,
                page_number=row.page_number,
                rank=index,
            )
        )

    for row in analysis.pfmea_top_ap:
        analysis.flags.append(
            f"PFMEA AP {row.action_priority} #{row.rank}: {row.failure_mode} "
            f"(S={row.severity} O={row.occurrence} D={row.detection}, RPN {row.rpn})"
        )
        if row.action_priority == "H":
            analysis.quality_blocking = True
            analysis.actions.append(
                f"PFMEA Action Priority H (#{row.rank}) — {row.failure_mode}: "
                + "; ".join(row.table_actions[:2])
            )

    # De-duplicate actions while preserving order
    seen_actions: set[str] = set()
    unique_actions: list[str] = []
    for action in analysis.actions:
        if action in seen_actions:
            continue
        seen_actions.add(action)
        unique_actions.append(action)
    analysis.actions = unique_actions

    seen_flags: set[str] = set()
    unique_flags: list[str] = []
    for flag in analysis.flags:
        if flag in seen_flags:
            continue
        seen_flags.add(flag)
        unique_flags.append(flag)
    analysis.flags = unique_flags

    return analysis
