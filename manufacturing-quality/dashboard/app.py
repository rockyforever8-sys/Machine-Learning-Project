from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ppap_inbox_triage.report import format_console_summary, report_to_dict, write_all_reports
from ppap_inbox_triage.sqe_checklist import SQE_VERIFICATION_CHECKS, build_binder_page_index
from ppap_inbox_triage.triage import triage_inbox

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


def _run_triage(
    inbox_path: Path,
    output_dir: Path,
    *,
    use_pdf_text: bool,
    layout_mode: str,
) -> dict[str, Path]:
    report = triage_inbox(
        inbox_path,
        use_pdf_text=use_pdf_text,
        layout_mode=layout_mode,
    )
    outputs = write_all_reports(report, output_dir)
    return {"report": report, "outputs": outputs}


def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#64748b")
    label = status.replace("_", " ").title()
    return (
        f"<span style='background:{color};color:white;padding:4px 10px;"
        f"border-radius:999px;font-weight:600;'>{label}</span>"
    )


def _render_metrics(report) -> None:
    summary = report.summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completeness", f"{summary['completeness_pct']}%")
    col2.metric("Elements present", f"{summary['elements_present']}/18")
    col3.metric("Files scanned", summary["files_scanned"])
    col4.metric("Missing", summary["elements_missing"])

    st.markdown(
        f"**Submission layout:** `{summary.get('submission_layout', 'discrete')}` &nbsp; "
        f"**Scanned:** {report.scanned_at}",
        unsafe_allow_html=True,
    )
    st.markdown(_status_badge(report.status.value), unsafe_allow_html=True)


def _render_element_table(report) -> None:
    rows = []
    for triage in report.elements:
        primary = triage.matches[0].file.relative_path if triage.matches else "—"
        pages = "—"
        if triage.matches:
            page_numbers = sorted(
                {match.page_number for match in triage.matches if match.page_number is not None}
            )
            if page_numbers:
                pages = ", ".join(str(page) for page in page_numbers)

        rows.append(
            {
                "#": triage.element.number,
                "Element": triage.element.name,
                "Status": triage.status.upper(),
                "Priority": triage.element.priority.value,
                "File": primary,
                "Pages": pages,
                "Notes": "; ".join(triage.notes) if triage.notes else "",
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_binder_index(report) -> None:
    page_index = build_binder_page_index(report)
    if not page_index:
        st.info("No binder page references detected. Run with PDF text enabled for binder submissions.")
        return

    rows = [
        {"Page": page, "Elements": ", ".join(f"#{number}" for number in numbers)}
        for page, numbers in page_index
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_sqe_checklist(report) -> None:
    for triage in report.elements:
        pages = "—"
        if triage.matches:
            page_numbers = sorted(
                {match.page_number for match in triage.matches if match.page_number is not None}
            )
            if page_numbers:
                pages = ", ".join(str(page) for page in page_numbers)

        checks = SQE_VERIFICATION_CHECKS.get(triage.element.number, ("Verify element content",))
        with st.expander(
            f"{triage.element.number}. {triage.element.name} — {triage.status.upper()} (pages: {pages})",
            expanded=triage.status == "missing",
        ):
            st.write(f"**Source file:** `{triage.matches[0].file.relative_path if triage.matches else '—'}`")
            st.write(f"**Priority:** {triage.element.priority.value}")
            if triage.notes:
                st.caption("; ".join(triage.notes))
            for index, check in enumerate(checks):
                st.checkbox(check, key=f"sqe_{triage.element.number}_{index}")


def main() -> None:
    st.set_page_config(
        page_title="PPAP Level 3 Inbox Triage",
        page_icon="📋",
        layout="wide",
    )

    st.title("PPAP Level 3 Inbox Triage")
    st.caption("Local SQE dashboard for OneDrive supplier submission folders")

    with st.sidebar:
        st.header("Inbox settings")
        inbox_path = st.text_input("PPAP inbox folder", value=DEFAULT_INBOX)
        output_dir = st.text_input("Output folder", value=DEFAULT_OUTPUT)
        use_pdf_text = st.toggle("PDF text extraction", value=True)
        layout_mode = st.selectbox("Layout mode", ["auto", "binder", "discrete"], index=0)
        auto_refresh = st.toggle("Auto-refresh inbox", value=False)
        refresh_seconds = st.number_input("Refresh interval (seconds)", min_value=5, max_value=300, value=30)

        run_clicked = st.button("Run triage now", type="primary", use_container_width=True)

        st.divider()
        st.markdown(
            "**Tip:** Point the inbox path at your OneDrive `PPAP Inbox` folder. "
            "The dashboard writes reports to the output folder and displays binder page references."
        )

    inbox = Path(inbox_path)
    output = Path(output_dir)

    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "last_outputs" not in st.session_state:
        st.session_state.last_outputs = None

    wants_scan = run_clicked or (auto_refresh and inbox.exists() and inbox.is_dir())

    if run_clicked:
        if not inbox.exists():
            st.error(f"Inbox path does not exist: {inbox}")
            return
        if not inbox.is_dir():
            st.error(f"Inbox path is not a directory: {inbox}")
            return

    if wants_scan:
        with st.spinner("Scanning inbox and classifying PPAP elements..."):
            try:
                result = _run_triage(
                    inbox,
                    output,
                    use_pdf_text=use_pdf_text,
                    layout_mode=layout_mode,
                )
                st.session_state.last_run = result["report"]
                st.session_state.last_outputs = result["outputs"]
            except Exception as error:
                st.error(f"Triage failed: {error}")
                return

    report = st.session_state.last_run
    outputs = st.session_state.last_outputs

    if report is None:
        st.info("Configure your OneDrive inbox path in the sidebar, then click **Run triage now**.")
        if not inbox.exists():
            st.warning("The inbox path does not exist yet. Check the path or sync OneDrive first.")
        return

    _render_metrics(report)

    tab_overview, tab_elements, tab_binder, tab_sqe, tab_downloads = st.tabs(
        ["Overview", "Elements", "Binder pages", "SQE checklist", "Downloads"]
    )

    with tab_overview:
        st.subheader("Recommended actions")
        for index, action in enumerate(report.actions, start=1):
            st.write(f"{index}. {action}")

        binder_files = report.summary.get("binder_files", [])
        if binder_files:
            st.subheader("Binder files")
            for path in binder_files:
                st.code(path)

        st.subheader("Console summary")
        st.code(format_console_summary(report))

    with tab_elements:
        _render_element_table(report)

    with tab_binder:
        _render_binder_index(report)

    with tab_sqe:
        st.subheader("SQE element verification")
        decision = st.radio("Review decision", ["Approve", "Approve with conditions", "Reject"], horizontal=True)
        st.text_input("Reviewer")
        st.text_input("Part / Program")
        st.text_input("Supplier")
        st.text_area("Conditions / notes")
        _render_sqe_checklist(report)
        st.caption(f"Decision selected: {decision}")

    with tab_downloads:
        if outputs:
            for name, path in outputs.items():
                if path.exists():
                    st.download_button(
                        label=f"Download {path.name}",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime="application/octet-stream",
                        use_container_width=True,
                    )
        st.caption(f"Reports saved to `{output.resolve()}`")

    if auto_refresh and not run_clicked:
        st.caption(f"Auto-refresh enabled — next scan in {refresh_seconds}s")
        time.sleep(int(refresh_seconds))
        st.rerun()


if __name__ == "__main__":
    main()
