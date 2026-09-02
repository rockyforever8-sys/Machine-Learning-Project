from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .models import InboxFile
from .pdf_text import ALL_PAGES, extract_pdf_pages, extract_pdf_text
from .skill_loader import pfmea_countermeasure_playbook, quality_thresholds

# Bump when capability/MSA/PFMEA parsing rules change — shown in the dashboard sidebar.
QUALITY_PARSER_VERSION = "2026-09-02c"


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
    source_file: str
    page_number: int | None = None
    countermeasures: tuple[str, ...] = ()
    rank: int = 0


@dataclass
class QualityAnalysis:
    msa_findings: list[MetricFinding] = field(default_factory=list)
    capability_findings: list[MetricFinding] = field(default_factory=list)
    pfmea_top_rpn: list[PfmeaRow] = field(default_factory=list)
    pfmea_benchmark_notes: list[str] = field(default_factory=list)
    pfmea_reduction_order: str = "Severity → Occurrence → Detection"
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
            "pfmea_top_rpn": [
                {
                    "rank": row.rank,
                    "failure_mode": row.failure_mode,
                    "severity": row.severity,
                    "occurrence": row.occurrence,
                    "detection": row.detection,
                    "rpn": row.rpn,
                    "source_file": row.source_file,
                    "page_number": row.page_number,
                    "countermeasures": list(row.countermeasures),
                }
                for row in self.pfmea_top_rpn
            ],
            "pfmea_benchmark_notes": list(self.pfmea_benchmark_notes),
            "pfmea_reduction_order": self.pfmea_reduction_order,
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
    r"^(?P<mode>.{10,110}?)\s+(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})\s*$",
    re.M,
)

SOD_RPN_TUPLE_PATTERN = re.compile(
    r"\b(?P<sev>\d{1,2})\s+(?P<occ>\d{1,2})\s+(?P<det>\d{1,2})\s+(?P<rpn>\d{2,4})\b",
)

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


def _is_pfmea_filename(filename: str) -> bool:
    lowered = filename.lower()
    return any(token in lowered for token in PFMEA_FILENAME_TOKENS)


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
    source_file: str,
    page_number: int | None,
    playbook: dict[str, Any],
) -> PfmeaRow:
    mode = re.sub(r"\s+", " ", failure_mode).strip(" -:;|")
    if len(mode) < 8:
        mode = f"PFMEA failure mode (RPN {rpn})"
    return PfmeaRow(
        failure_mode=mode[:120],
        severity=severity,
        occurrence=occurrence,
        detection=detection,
        rpn=rpn,
        source_file=source_file,
        page_number=page_number,
        countermeasures=_countermeasures_for_failure_mode(mode, playbook),
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
    seen: set[tuple[str, int]] = set()

    def add_row(
        *,
        failure_mode: str,
        severity: int,
        occurrence: int,
        detection: int,
        rpn: int,
    ) -> None:
        if severity or occurrence or detection:
            if not _valid_sod_rpn(severity, occurrence, detection, rpn):
                return
        elif rpn < 40:
            return
        key = (failure_mode.lower()[:60], rpn)
        if key in seen:
            return
        seen.add(key)
        rows.append(
            _make_pfmea_row(
                failure_mode=failure_mode,
                severity=severity,
                occurrence=occurrence,
                detection=detection,
                rpn=rpn,
                source_file=source_file,
                page_number=page_number,
                playbook=playbook,
            )
        )

    for match in RPN_ROW_PATTERN.finditer(text):
        add_row(
            failure_mode=match.group("mode"),
            severity=int(match.group("sev")),
            occurrence=int(match.group("occ")),
            detection=int(match.group("det")),
            rpn=int(match.group("rpn")),
        )

    for match in LINE_SOD_RPN_PATTERN.finditer(text):
        add_row(
            failure_mode=match.group("mode"),
            severity=int(match.group("sev")),
            occurrence=int(match.group("occ")),
            detection=int(match.group("det")),
            rpn=int(match.group("rpn")),
        )

    for line in text.splitlines():
        line = line.strip()
        if len(line) < 12:
            continue
        tuple_match = SOD_RPN_TUPLE_PATTERN.search(line)
        if not tuple_match:
            continue
        mode = line[: tuple_match.start()].strip(" -:;|")
        add_row(
            failure_mode=mode,
            severity=int(tuple_match.group("sev")),
            occurrence=int(tuple_match.group("occ")),
            detection=int(tuple_match.group("det")),
            rpn=int(tuple_match.group("rpn")),
        )

    if not rows and RPN_INLINE_PATTERN.search(text):
        for line in text.splitlines():
            inline = RPN_INLINE_PATTERN.search(line)
            if not inline:
                continue
            rpn = int(inline.group("rpn"))
            if rpn < 40:
                continue
            mode = re.sub(r"\s+", " ", line[: inline.start()]).strip(" -:;|")
            add_row(
                failure_mode=mode,
                severity=0,
                occurrence=0,
                detection=0,
                rpn=rpn,
            )

    return rows


def _countermeasures_for_failure_mode(failure_mode: str, playbook: dict[str, Any]) -> tuple[str, ...]:
    lowered = failure_mode.lower()
    measures: list[str] = []
    for entry in playbook.get("failure_mode_patterns", []):
        keywords = [str(keyword).lower() for keyword in entry.get("keywords", [])]
        if any(keyword in lowered for keyword in keywords):
            for action in entry.get("countermeasures", []):
                if action not in measures:
                    measures.append(str(action))
    for action in playbook.get("default_countermeasures", []):
        if action not in measures:
            measures.append(str(action))
    top_n = int(playbook.get("countermeasure_limit", 5))
    return tuple(measures[:top_n])


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
    top_rpn_limit = int(thresholds.get("pfmea_top_rpn_limit", 5))
    pfmea_pages = pfmea_pages_by_file or {}

    analysis = QualityAnalysis()
    analysis.pfmea_benchmark_notes = [
        str(item) for item in thresholds.get("references", []) if item
    ]
    analysis.pfmea_reduction_order = str(
        thresholds.get(
            "pfmea_reduction_order",
            "Severity → Occurrence → Detection (AIAG FMEA priority)",
        )
    )
    analysis.pfmea_default_practices = [
        str(item) for item in playbook.get("default_countermeasures", []) if item
    ]
    pfmea_rows: list[PfmeaRow] = []

    for inbox_file in inbox_files:
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

    pfmea_rows.sort(key=lambda row: (-row.rpn, row.failure_mode))
    analysis.pfmea_top_rpn = []
    for index, row in enumerate(pfmea_rows[:top_rpn_limit], start=1):
        analysis.pfmea_top_rpn.append(
            PfmeaRow(
                failure_mode=row.failure_mode,
                severity=row.severity,
                occurrence=row.occurrence,
                detection=row.detection,
                rpn=row.rpn,
                source_file=row.source_file,
                page_number=row.page_number,
                countermeasures=row.countermeasures,
                rank=index,
            )
        )

    if pfmea_pages and not analysis.pfmea_top_rpn:
        pass  # Dashboard shows default PFMEA best practices when rows are not parseable.

    for row in analysis.pfmea_top_rpn:
        analysis.flags.append(
            f"PFMEA top RPN #{row.rank}: {row.failure_mode} (RPN {row.rpn}, "
            f"S={row.severity} O={row.occurrence} D={row.detection})"
        )
        if row.rpn >= int(thresholds.get("pfmea_action_rpn_min", 100)):
            analysis.quality_blocking = True
            analysis.actions.append(
                f"PFMEA RPN {row.rpn} (#{row.rank}) — reduce per AIAG priority "
                f"({analysis.pfmea_reduction_order}): "
                + "; ".join(row.countermeasures[:3])
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
