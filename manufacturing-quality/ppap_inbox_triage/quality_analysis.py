from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .models import InboxFile
from .pdf_text import ALL_PAGES, extract_pdf_pages, extract_pdf_text
from .skill_loader import pfmea_countermeasure_playbook, quality_thresholds


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


@dataclass
class QualityAnalysis:
    msa_findings: list[MetricFinding] = field(default_factory=list)
    capability_findings: list[MetricFinding] = field(default_factory=list)
    pfmea_top_rpn: list[PfmeaRow] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        return {
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

RPN_INLINE_PATTERN = re.compile(
    r"rpn\s*[:=]?\s*(?P<rpn>\d{2,4})",
    re.I,
)


def _looks_like_pfmea(text: str) -> bool:
    lowered = text.lower()
    return "pfmea" in lowered or "process fmea" in lowered or "过程fmea" in lowered or "过程 fmea" in lowered


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

    for match in RPN_ROW_PATTERN.finditer(text):
        sev = int(match.group("sev"))
        occ = int(match.group("occ"))
        det = int(match.group("det"))
        rpn = int(match.group("rpn"))
        if not (1 <= sev <= 10 and 1 <= occ <= 10 and 1 <= det <= 10):
            continue
        if rpn < 40:
            continue
        if abs(rpn - sev * occ * det) > max(15, rpn * 0.25):
            continue
        mode = re.sub(r"\s+", " ", match.group("mode")).strip(" -:;|")
        if len(mode) < 8:
            continue
        key = (mode.lower()[:60], rpn)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            PfmeaRow(
                failure_mode=mode[:120],
                severity=sev,
                occurrence=occ,
                detection=det,
                rpn=rpn,
                source_file=source_file,
                page_number=page_number,
                countermeasures=_countermeasures_for_failure_mode(mode, playbook),
            )
        )

    # Fallback: lines with explicit RPN labels near PFMEA context
    if not rows and RPN_INLINE_PATTERN.search(text):
        for line in text.splitlines():
            inline = RPN_INLINE_PATTERN.search(line)
            if not inline:
                continue
            rpn = int(inline.group("rpn"))
            if rpn < 40:
                continue
            mode = re.sub(r"\s+", " ", line[: inline.start()]).strip(" -:;|")
            if len(mode) < 8:
                mode = f"PFMEA item (RPN {rpn})"
            rows.append(
                PfmeaRow(
                    failure_mode=mode[:120],
                    severity=0,
                    occurrence=0,
                    detection=0,
                    rpn=rpn,
                    source_file=source_file,
                    page_number=page_number,
                    countermeasures=_countermeasures_for_failure_mode(mode, playbook),
                )
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
) -> QualityAnalysis:
    thresholds = quality_thresholds()
    grr_max = float(thresholds.get("msa_percent_grr_max", 10.0))
    cpk_min = float(thresholds.get("cpk_min", 1.33))
    ppk_min = float(thresholds.get("ppk_min", 1.33))
    top_rpn_limit = int(thresholds.get("pfmea_top_rpn_limit", 5))

    analysis = QualityAnalysis()
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
                    analysis.actions.append(
                        "MSA unacceptable: %GRR above 10% — repeat Gage R&R after gauge/fixture "
                        "calibration, operator training, and measurement method review"
                    )

            for label, value, context in _extract_capability_values(text):
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
                    analysis.actions.append(
                        f"Process capability gap: {label} {value:.2f} < {minimum:.2f} — "
                        "run special-cause analysis, tighten controls on special characteristics, "
                        "and re-run capability after corrective action"
                    )

            if _looks_like_pfmea(text):
                pfmea_rows.extend(
                    _parse_pfmea_rows(
                        text,
                        source_file=inbox_file.relative_path,
                        page_number=page_number,
                    )
                )

    pfmea_rows.sort(key=lambda row: (-row.rpn, row.failure_mode))
    analysis.pfmea_top_rpn = pfmea_rows[:top_rpn_limit]

    for index, row in enumerate(analysis.pfmea_top_rpn, start=1):
        analysis.flags.append(
            f"PFMEA top RPN #{index}: {row.failure_mode} (RPN {row.rpn}, "
            f"S={row.severity} O={row.occurrence} D={row.detection})"
        )
        if row.rpn >= int(thresholds.get("pfmea_action_rpn_min", 100)):
            analysis.actions.append(
                f"PFMEA action required for RPN {row.rpn} — {row.failure_mode}: "
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
