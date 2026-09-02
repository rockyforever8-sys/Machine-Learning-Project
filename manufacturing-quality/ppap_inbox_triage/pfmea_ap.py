from __future__ import annotations

import re
from typing import Any

AP_RANK = {"H": 0, "M": 1, "L": 2}

ACTION_VERB_TOKENS: tuple[str, ...] = (
    "install",
    "implement",
    "monitor",
    "inspect",
    "control",
    "train",
    "calibrat",
    "verify",
    "audit",
    "add",
    "revise",
    "update",
    "poka",
    "mistake",
    "reduce",
    "prevent",
    "check",
    "maintain",
    "replace",
    "standard",
    "escalat",
    "实施",
    "监控",
    "检查",
    "培训",
    "校准",
    "防错",
)


def pfmea_action_priority(severity: int, occurrence: int, detection: int) -> str:
    """AIAG & VDA FMEA Handbook (2019) Process FMEA Action Priority approximation."""
    if not (1 <= severity <= 10 and 1 <= occurrence <= 10 and 1 <= detection <= 10):
        return "L"
    s, o, d = severity, occurrence, detection
    if s >= 9:
        if o >= 4:
            return "H"
        if o >= 2:
            return "M" if d >= 6 else "L"
        return "L"
    if s >= 7:
        if o >= 6:
            return "H"
        if o >= 4:
            return "M" if d >= 4 else "L"
        if o >= 2:
            return "M" if d >= 8 else "L"
        return "L"
    if s >= 4:
        if o >= 8 and d >= 6:
            return "H"
        if o >= 6:
            return "M"
        if o >= 4 and d >= 8:
            return "M"
        return "L"
    if s >= 2 and o >= 8 and d >= 8:
        return "M"
    return "L"


def split_table_actions(text: str) -> tuple[str, ...]:
    """Split supplier PFMEA recommended-action text from a table row."""
    cleaned = re.sub(r"\s+", " ", text).strip(" -:;|")
    if len(cleaned) < 12:
        return ()
    if not _looks_like_action_text(cleaned):
        return ()
    parts = re.split(r"\s*;\s*|\s*\|\s*", cleaned)
    actions = [part.strip() for part in parts if len(part.strip()) >= 12]
    if not actions:
        actions = [cleaned]
    return tuple(actions[:5])


def _looks_like_action_text(text: str) -> bool:
    lowered = text.lower()
    if re.search(r"\b(?:action|recommend|prevent|control|countermeasure|措施|对策|建议)\b", lowered):
        return True
    return any(token in lowered for token in ACTION_VERB_TOKENS)


def benchmark_actions_for_failure_mode(failure_mode: str, playbook: dict[str, Any]) -> tuple[str, ...]:
    """Industrial best-practice counter-measures from the skill playbook (pattern-specific only)."""
    lowered = failure_mode.lower()
    measures: list[str] = []
    for entry in playbook.get("failure_mode_patterns", []):
        keywords = [str(keyword).lower() for keyword in entry.get("keywords", [])]
        if any(keyword in lowered for keyword in keywords):
            for action in entry.get("countermeasures", []):
                text = str(action)
                if text not in measures:
                    measures.append(text)
    limit = int(playbook.get("countermeasure_limit", 5))
    return tuple(measures[:limit])


def compare_table_vs_benchmark(
    *,
    table_actions: tuple[str, ...],
    benchmark_actions: tuple[str, ...],
    failure_mode: str,
    action_priority: str,
) -> tuple[str, ...]:
    """Reason about supplier PFMEA actions vs industrial best practices."""
    notes: list[str] = []
    notes.append(
        f"Action Priority {action_priority} — rank H before M before L per AIAG/VDA 2019 PFMEA."
    )
    if action_priority == "H":
        notes.append(
            "High AP: verify supplier actions reduce Severity first, then Occurrence, then Detection."
        )
    elif action_priority == "M":
        notes.append(
            "Medium AP: confirm actions are tracked to completion with effectiveness verification."
        )

    if not table_actions:
        notes.append("No supplier recommended actions were captured from the PFMEA table row.")
        return tuple(notes)

    table_blob = " ".join(table_actions).lower()
    if not benchmark_actions:
        notes.append(
            "Supplier documented actions in PFMEA; no failure-mode keyword match in industrial playbook — "
            "review manually against Control Plan and customer CSR."
        )
        return tuple(notes)

    for bench in benchmark_actions:
        keywords = _benchmark_keywords(bench)
        if keywords and any(keyword in table_blob for keyword in keywords):
            notes.append(f"Aligned: PFMEA action covers industrial practice — {bench}")
        else:
            notes.append(
                f"Gap: consider adding — {bench} — not evident in supplier PFMEA recommended actions."
            )

    aligned_count = sum(
        1
        for bench in benchmark_actions
        if any(keyword in table_blob for keyword in _benchmark_keywords(bench))
    )
    if benchmark_actions and aligned_count == len(benchmark_actions):
        notes.append("Overall: supplier PFMEA actions align well with industrial best-practice themes.")

    return tuple(notes)


def _benchmark_keywords(benchmark: str) -> tuple[str, ...]:
    lowered = benchmark.lower()
    tokens = re.findall(r"[a-z\u4e00-\u9fff]{4,}", lowered)
    stop = {"with", "from", "that", "this", "after", "before", "through", "their", "into"}
    return tuple(token for token in tokens if token not in stop)[:6]


def pfmea_sort_key(row: object) -> tuple[int, int, int, int, str]:
    ap = getattr(row, "action_priority", "L")
    return (
        AP_RANK.get(str(ap), 9),
        -int(getattr(row, "severity", 0)),
        -int(getattr(row, "occurrence", 0)),
        -int(getattr(row, "detection", 0)),
        str(getattr(row, "failure_mode", "")),
    )
