from __future__ import annotations

import html
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from i18n import element_display_name, element_status_label, status_label, ui_text
from ppap_inbox_triage.report import format_console_summary, write_package_reports
from ppap_inbox_triage.skill_loader import skill_element_records, skill_metadata
from ppap_inbox_triage.sqe_checklist import SQE_VERIFICATION_CHECKS, build_binder_page_index, format_page_numbers
from ppap_inbox_triage.triage import triage_packages


def _lang() -> str:
    return str(st.session_state.get("ui_language", "en"))


def _t(key: str) -> str:
    return ui_text(_lang(), key)


def _element_name(element: object) -> str:
    return element_display_name(_lang(), int(getattr(element, "number")), str(getattr(element, "name")))


def _apply_language(code: str) -> None:
    if st.session_state.get("ui_language") == code:
        return
    st.session_state.ui_language = code
    st.rerun()


def _render_language_buttons(key_prefix: str) -> None:
    current = "中文" if _lang() == "zh" else "English"
    choice = st.radio(
        _t("language"),
        ["English", "中文"],
        index=1 if current == "中文" else 0,
        horizontal=True,
        key=f"{key_prefix}_radio",
    )
    _apply_language("zh" if choice == "中文" else "en")


def _match_evidence(match: object) -> tuple[str, ...]:
    """Compatible with older ElementMatch objects that lack an evidence field."""
    raw = getattr(match, "evidence", ())
    if not raw:
        return ()
    return tuple(raw)

DEFAULT_INBOX = (
    r"C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627"
    r"\MIT Applied Agentic\PPAP Agentic\PPAP Inbox"
)
DEFAULT_OUTPUT = str(ROOT / "triage-out")

STATUS_COLORS = {
    "ready_for_review": "#16a34a",
    "incomplete": "#ca8a04",
    "needs_clarification": "#ea580c",
    "blocked": "#dc2626",
}

ELEMENT_STATUS_COLORS = {
    "present": "#16a34a",
    "missing": "#dc2626",
    "duplicate": "#ea580c",
    "review": "#ca8a04",
}


def _widget_prefix(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", name)[:80]


def _run_triage(
    inbox_path: Path,
    output_dir: Path,
    *,
    use_pdf_text: bool,
    layout_mode: str,
) -> list[dict[str, object]]:
    results = triage_packages(
        inbox_path,
        use_pdf_text=use_pdf_text,
        layout_mode=layout_mode,
    )
    return write_package_reports(results, output_dir)


def _render_simple_table(rows: list[dict[str, object]]) -> None:
    """Render a table without pyarrow (blocked on some corporate Windows policies)."""
    if not rows:
        st.info(_t("no_rows"))
        return

    columns = list(rows[0].keys())
    header = "".join(f"<th>{html.escape(str(column))}</th>" for column in columns)
    body_rows = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in columns
        )
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = (
        "<div style='overflow-x:auto;width:100%;'>"
        "<table style='width:100%;border-collapse:collapse;font-size:0.9rem;'>"
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#64748b")
    label = status_label(_lang(), status)
    return (
        f"<span style='background:{color};color:white;padding:4px 10px;"
        f"border-radius:999px;font-weight:600;'>{html.escape(label)}</span>"
    )


def _render_metrics(report) -> None:
    summary = report.summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(_t("completeness"), f"{summary['completeness_pct']}%")
    col2.metric(_t("elements_present"), f"{summary['elements_present']}/18")
    col3.metric(_t("files_scanned"), summary["files_scanned"])
    col4.metric(_t("missing"), summary["elements_missing"])

    st.markdown(
        f"**{_t('submission_layout')}:** `{summary.get('submission_layout', 'discrete')}` &nbsp; "
        f"**{_t('scanned')}:** {report.scanned_at}",
        unsafe_allow_html=True,
    )
    st.markdown(_status_badge(report.status.value), unsafe_allow_html=True)
    skill_title = report.summary.get("skill_title") or "AIAG PPAP 4th Edition"
    st.caption(f"{_t('rules_source')}: **{skill_title}** skill (`{report.summary.get('skill_name', '')}`)")
    skipped = report.summary.get("index_pages_skipped") or []
    if skipped:
        st.caption(
            f"{_t('toc_skipped')}: "
            + ", ".join(str(page) for page in skipped)
            + f". {_t('toc_note')}"
        )


def _render_element_table(report) -> None:
    rows = []
    for triage in report.elements:
        primary = "—"
        if triage.matches:
            unique_files: list[str] = []
            for match in triage.matches:
                path = match.file.relative_path
                if path not in unique_files:
                    unique_files.append(path)
            primary = "; ".join(unique_files[:4])
        evidence: list[str] = []
        for match in triage.matches:
            for item in _match_evidence(match):
                if item not in evidence:
                    evidence.append(item)
        rows.append(
            {
                "#": triage.element.number,
                _t("col_element"): _element_name(triage.element),
                _t("col_status"): element_status_label(_lang(), triage.status),
                _t("col_priority"): triage.element.priority.value,
                _t("col_file"): primary,
                _t("col_pages"): format_page_numbers(triage.matches),
                _t("col_evidence"): ", ".join(evidence[:6]),
                _t("col_rule"): getattr(triage.element, "aiag_rule", "") or "",
                _t("col_notes"): "; ".join(
                    note
                    for note in triage.notes
                    if not note.startswith("AIAG PPAP")
                ),
            }
        )

    _render_simple_table(rows)


def _render_binder_index(report) -> None:
    page_index = build_binder_page_index(report)
    if not page_index:
        st.info(_t("no_binder_pages"))
        return

    rows = [
        {
            _t("col_page"): page,
            _t("col_elements"): ", ".join(f"#{number}" for number in numbers),
        }
        for page, numbers in page_index
    ]
    _render_simple_table(rows)


def _render_sqe_checklist(report, *, key_prefix: str = "pkg") -> None:
    records = {int(item["number"]): item for item in skill_element_records()}
    for triage in report.elements:
        pages = format_page_numbers(triage.matches)
        record = records.get(triage.element.number, {})
        checks = SQE_VERIFICATION_CHECKS.get(triage.element.number, ("Verify element content",))
        with st.expander(
            f"{triage.element.number}. {_element_name(triage.element)} — "
            f"{element_status_label(_lang(), triage.status)} ({_t('pages_label')}: {pages})",
            expanded=triage.status == "missing",
        ):
            st.write(f"**{_t('source_file')}:** `{triage.matches[0].file.relative_path if triage.matches else '—'}`")
            st.write(f"**{_t('priority')}:** {triage.element.priority.value}")
            if record.get("good"):
                st.write(f"**{_t('skill_good')}:** {record['good']}")
            if record.get("watch_outs"):
                st.write(f"**{_t('skill_watch')}:** {record['watch_outs']}")
            if getattr(triage.element, "aiag_rule", ""):
                st.caption(triage.element.aiag_rule)
            if triage.notes:
                st.caption("; ".join(note for note in triage.notes if not note.startswith("AIAG PPAP")))
            for index, check in enumerate(checks):
                st.checkbox(check, key=f"{key_prefix}_sqe_{triage.element.number}_{index}")


def _render_skill_rules() -> None:
    meta = skill_metadata()
    st.subheader(meta["title"])
    st.caption(f"{_t('loaded_from')} `{meta['source_path']}`")
    st.write(
        f"{_t('default_level')} **{meta['default_submission_level']}**. "
        f"{_t('critical_elements')}: {', '.join(f'#{n}' for n in meta['critical_element_numbers'])}."
    )
    binder = meta.get("binder_rules") or {}
    if binder:
        st.markdown(
            "- {skip_toc}: `{skip}`\n"
            "- {title_only}: `{title}`\n"
            "- {psw_only}: `{psw}`\n"
            "- {scan_every}: `{scan}`".format(
                skip_toc=_t("skip_toc"),
                title_only=_t("title_only"),
                psw_only=_t("psw_only"),
                scan_every=_t("scan_every"),
                skip=binder.get("skip_table_of_contents"),
                title=binder.get("title_only_is_not_present"),
                psw=binder.get("psw_checklist_is_element_18_only"),
                scan=binder.get("scan_every_page"),
            )
        )
    rows = []
    for record in skill_element_records():
        rows.append(
            {
                "#": record["number"],
                _t("col_element"): element_display_name(
                    _lang(), int(record["number"]), str(record["name"])
                ),
                _t("col_priority"): record["priority"],
                _t("col_what_good"): record.get("good", ""),
                _t("col_watch_outs"): record.get("watch_outs", ""),
                _t("col_rule"): record.get("aiag_rule", ""),
            }
        )
    _render_simple_table(rows)


def _render_packages_table(items: list[dict[str, object]]) -> None:
    rows = []
    for item in items:
        package = item["package"]
        report = item["report"]
        rows.append(
            {
                _t("col_package"): package.name,
                _t("col_status"): status_label(_lang(), report.status.value),
                _t("completeness"): f"{report.summary['completeness_pct']}%",
                _t("elements_present"): f"{report.summary['elements_present']}/18",
                _t("missing"): report.summary["elements_missing"],
                _t("files_scanned"): report.summary["files_scanned"],
                _t("submission_layout"): report.summary.get("submission_layout", ""),
            }
        )
    _render_simple_table(rows)


def _render_package_detail(item: dict[str, object], *, key_prefix: str, include_skill: bool) -> None:
    report = item["report"]
    outputs = item["outputs"]
    output_dir = item.get("output_dir")
    _render_metrics(report)

    tab_labels = [
        _t("tab_overview"),
        _t("tab_elements"),
        _t("tab_binder"),
        _t("tab_sqe"),
        _t("tab_downloads"),
    ]
    if include_skill:
        tab_labels.insert(4, _t("tab_skill"))
    tabs = st.tabs(tab_labels)
    tab_overview, tab_elements, tab_binder, tab_sqe = tabs[0], tabs[1], tabs[2], tabs[3]
    if include_skill:
        tab_skill = tabs[4]
        tab_downloads = tabs[5]
    else:
        tab_skill = None
        tab_downloads = tabs[4]

    with tab_overview:
        st.subheader(_t("recommended"))
        for index, action in enumerate(report.actions, start=1):
            st.write(f"{index}. {action}")

        binder_files = report.summary.get("binder_files", [])
        if binder_files:
            st.subheader(_t("binder_files"))
            for path in binder_files:
                st.code(path)

        st.subheader(_t("console"))
        st.code(format_console_summary(report))

    with tab_elements:
        _render_element_table(report)

    with tab_binder:
        _render_binder_index(report)

    with tab_sqe:
        st.subheader(_t("sqe_verify"))
        decision = st.radio(
            _t("review_decision"),
            [_t("approve"), _t("approve_conditions"), _t("reject")],
            horizontal=True,
            key=f"{key_prefix}_decision",
        )
        st.text_input(_t("reviewer"), key=f"{key_prefix}_reviewer")
        st.text_input(_t("part_program"), key=f"{key_prefix}_part")
        st.text_input(_t("supplier"), key=f"{key_prefix}_supplier")
        st.text_area(_t("conditions"), key=f"{key_prefix}_conditions")
        _render_sqe_checklist(report, key_prefix=key_prefix)
        st.caption(f"{_t('decision_selected')}: {decision}")

    if tab_skill is not None:
        with tab_skill:
            _render_skill_rules()

    with tab_downloads:
        if outputs:
            for name, path in outputs.items():
                if path.exists():
                    st.download_button(
                        label=f"{_t('download')} {path.name}",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime="application/octet-stream",
                        use_container_width=True,
                        key=f"{key_prefix}_dl_{name}",
                    )
        st.caption(f"{_t('reports_saved')} `{Path(output_dir).resolve() if output_dir else ''}`")


def main() -> None:
    st.set_page_config(
        page_title="PPAP Level 3 Inbox Triage",
        page_icon="📋",
        layout="wide",
    )

    if "ui_language" not in st.session_state:
        st.session_state.ui_language = "en"

    with st.sidebar:
        _render_language_buttons("sidebar_lang")
        st.caption(_t("language_help"))
        st.divider()
        st.header(_t("inbox_settings"))
        inbox_path = st.text_input(_t("inbox_folder"), value=DEFAULT_INBOX)
        output_dir = st.text_input(_t("output_folder"), value=DEFAULT_OUTPUT)
        use_pdf_text = st.toggle(_t("pdf_text"), value=True)
        layout_mode = st.selectbox(
            _t("layout_mode"),
            ["auto", "binder", "discrete"],
            index=0,
            format_func=lambda value: _t(f"layout_{value}"),
        )
        auto_refresh = st.toggle(_t("auto_refresh"), value=False)
        refresh_seconds = st.number_input(_t("refresh_interval"), min_value=5, max_value=300, value=30)

        run_clicked = st.button(_t("run_triage"), type="primary", use_container_width=True)

        st.divider()
        meta = skill_metadata()
        st.markdown(f"**{_t('rules')}:** {meta['title']}")
        st.caption(Path(meta["source_path"]).name if meta["source_path"] else _t("skill_rules_file"))
        st.markdown(f"**Tip:** {_t('tip')}")

    st.title(_t("title"))
    st.caption(_t("caption"))
    st.caption(_t("ocr_note"))

    inbox = Path(inbox_path)
    output = Path(output_dir)

    if "last_packages" not in st.session_state:
        st.session_state.last_packages = None

    wants_scan = run_clicked or (auto_refresh and inbox.exists() and inbox.is_dir())

    if run_clicked:
        if not inbox.exists():
            st.error(f"{_t('inbox_not_exist')}: {inbox}")
            return
        if not inbox.is_dir():
            st.error(f"{_t('inbox_not_dir')}: {inbox}")
            return

    if wants_scan:
        with st.spinner(_t("scanning")):
            try:
                st.session_state.last_packages = _run_triage(
                    inbox,
                    output,
                    use_pdf_text=use_pdf_text,
                    layout_mode=layout_mode,
                )
            except Exception as error:
                st.error(f"{_t('triage_failed')}: {error}")
                return

    items = st.session_state.last_packages

    if not items:
        st.info(_t("configure"))
        if not inbox.exists():
            st.warning(_t("inbox_missing"))
        return

    if len(items) == 1:
        package = items[0]["package"]
        st.caption(f"{_t('col_package')}: `{package.name}`")
        _render_package_detail(
            items[0],
            key_prefix=_widget_prefix(package.name),
            include_skill=True,
        )
    else:
        st.subheader(_t("independent_reviews"))
        st.caption(_t("packages_detected").format(count=len(items)))
        _render_packages_table(items)
        package_tabs = st.tabs([item["package"].name for item in items] + [_t("tab_skill")])
        for tab, item in zip(package_tabs[:-1], items):
            package = item["package"]
            with tab:
                _render_package_detail(
                    item,
                    key_prefix=_widget_prefix(package.name),
                    include_skill=False,
                )
        with package_tabs[-1]:
            _render_skill_rules()

    if auto_refresh and not run_clicked:
        st.caption(f"{_t('auto_refresh_on')} {refresh_seconds}{_t('seconds')}")
        time.sleep(int(refresh_seconds))
        st.rerun()


if __name__ == "__main__":
    main()
