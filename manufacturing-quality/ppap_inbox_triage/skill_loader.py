from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

SKILL_FOLDER_NAME = "aiag-ppap-4th-edition"
RULES_FILENAME = "rules.json"


def _candidate_rule_paths() -> list[Path]:
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    package_root = here.parents[1]
    return [
        repo_root / ".cursor" / "skills" / SKILL_FOLDER_NAME / RULES_FILENAME,
        package_root / "skills" / SKILL_FOLDER_NAME / RULES_FILENAME,
        Path.cwd() / ".cursor" / "skills" / SKILL_FOLDER_NAME / RULES_FILENAME,
        Path.cwd() / "skills" / SKILL_FOLDER_NAME / RULES_FILENAME,
    ]


def find_skill_rules_path() -> Path:
    for path in _candidate_rule_paths():
        if path.is_file():
            return path
    searched = "\n".join(f"  - {path}" for path in _candidate_rule_paths())
    raise FileNotFoundError(
        "AIAG PPAP skill rules.json not found. Looked in:\n" + searched
    )


@lru_cache(maxsize=1)
def load_skill_rules() -> dict[str, Any]:
    path = find_skill_rules_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Skill rules must be a JSON object: {path}")
    elements = payload.get("elements")
    if not isinstance(elements, list) or len(elements) != 18:
        raise ValueError(f"Skill rules must define 18 PPAP elements: {path}")
    payload["_source_path"] = str(path)
    return payload


def skill_metadata() -> dict[str, Any]:
    rules = load_skill_rules()
    return {
        "skill_name": rules.get("skill_name", SKILL_FOLDER_NAME),
        "title": rules.get("title", "AIAG PPAP 4th Edition"),
        "default_submission_level": rules.get("default_submission_level", 3),
        "critical_element_numbers": list(rules.get("critical_element_numbers", [6, 7, 18])),
        "physical_artifact_numbers": list(rules.get("physical_artifact_numbers", [14, 15, 16])),
        "binder_rules": dict(rules.get("binder_rules") or {}),
        "triage_statuses": dict(rules.get("triage_statuses") or {}),
        "source_path": rules.get("_source_path", ""),
        "skill_markdown": str(Path(rules.get("_source_path", "")).with_name("SKILL.md")),
    }


def skill_element_records() -> list[dict[str, Any]]:
    return list(load_skill_rules()["elements"])


def sqe_checks_by_element() -> dict[int, tuple[str, ...]]:
    checks: dict[int, tuple[str, ...]] = {}
    for record in skill_element_records():
        number = int(record["number"])
        raw = record.get("sqe_checks") or ("Verify element content",)
        checks[number] = tuple(str(item) for item in raw)
    return checks


def quality_thresholds() -> dict[str, Any]:
    rules = load_skill_rules()
    defaults = {
        "msa_percent_grr_max": 10.0,
        "cpk_min": 1.33,
        "ppk_min": 1.33,
        "pfmea_top_ap_limit": 5,
        "pfmea_top_rpn_limit": 5,
        "pfmea_ranking_method": "AIAG/VDA 2019 Action Priority (H → M → L)",
        "pfmea_reduction_order": "Severity → Occurrence → Detection within each AP band",
    }
    payload = dict(rules.get("quality_thresholds") or {})
    merged = {**defaults, **payload}
    return merged


def pfmea_countermeasure_playbook() -> dict[str, Any]:
    rules = load_skill_rules()
    return dict(rules.get("pfmea_countermeasure_playbook") or {})
