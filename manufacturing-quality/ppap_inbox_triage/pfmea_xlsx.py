from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

MODE_HEADERS = ("failure mode", "failure mode/effect", "失效模式", "过程功能", "process step", "potential failure mode")
SEV_HEADERS = ("s", "sev", "severity", "严重度", "严重度(s)")
OCC_HEADERS = ("o", "occ", "occurrence", "频度", "发生度", "occurrence (o)")
DET_HEADERS = ("d", "det", "detection", "探测度", "detection (d)")
AP_HEADERS = ("ap", "action priority", "行动优先级", "行动优先度", "priority")
RPN_HEADERS = ("rpn",)
ACTION_HEADERS = (
    "recommended action",
    "recommended actions",
    "action",
    "actions",
    "prevention",
    "detection controls",
    "recommended countermeasure",
    "建议措施",
    "现行措施",
    "措施",
    "对策",
    "recommended actions taken",
)


def _col_name(index: int) -> str:
    name = ""
    value = index + 1
    while value:
        value, rem = divmod(value - 1, 26)
        name = chr(65 + rem) + name
    return name


def _col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch.upper()) - 64)
    return index - 1


def read_xlsx_rows(path: Path, *, sheet_path: str = "xl/worksheets/sheet1.xml") -> list[list[str]]:
    if not path.exists():
        return []
    rows: dict[int, dict[int, str]] = {}
    try:
        archive_ctx = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return []
    with archive_ctx as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall(".//m:si", NS):
                parts = [node.text or "" for node in item.findall(".//m:t", NS)]
                shared.append("".join(parts))
        if sheet_path not in archive.namelist():
            return []
        sheet_root = ET.fromstring(archive.read(sheet_path))
        for row in sheet_root.findall(".//m:sheetData/m:row", NS):
            row_number = int(row.get("r", "0") or 0)
            for cell in row.findall("m:c", NS):
                ref = cell.get("r", "")
                if not ref:
                    continue
                col_number = _col_index(ref)
                value = ""
                cell_type = cell.get("t")
                if cell_type == "inlineStr":
                    value = "".join(node.text or "" for node in cell.findall(".//m:t", NS))
                else:
                    node = cell.find("m:v", NS)
                    if node is not None and node.text is not None:
                        value = node.text
                        if cell_type == "s":
                            value = shared[int(value)]
                rows.setdefault(row_number, {})[col_number] = str(value).strip()
    if not rows:
        return []
    max_row = max(rows)
    max_col = max(max(cols) for cols in rows.values())
    table: list[list[str]] = []
    for row_number in range(1, max_row + 1):
        cells = rows.get(row_number, {})
        table.append([cells.get(col, "") for col in range(max_col + 1)])
    return table


def write_simple_xlsx(path: Path, rows: list[list[str]]) -> None:
    """Write a minimal XLSX workbook (stdlib only) for tests and fixtures."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_rows: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells: list[str] = []
        for col_index, value in enumerate(row):
            ref = f"{_col_name(col_index)}{row_index}"
            escaped = (
                str(value)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{escaped}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(sheet_rows)}</sheetData></worksheet>"
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="PFMEA" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/></Relationships>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def _header_map(header_row: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for index, raw in enumerate(header_row):
        label = re.sub(r"\s+", " ", raw).strip().lower()
        if not label:
            continue
        if any(label == item or label.endswith(item) for item in MODE_HEADERS):
            mapping.setdefault("mode", index)
        elif label in SEV_HEADERS:
            mapping.setdefault("sev", index)
        elif label in OCC_HEADERS:
            mapping.setdefault("occ", index)
        elif label in DET_HEADERS:
            mapping.setdefault("det", index)
        elif label in AP_HEADERS:
            mapping.setdefault("ap", index)
        elif label in RPN_HEADERS:
            mapping.setdefault("rpn", index)
        elif any(item in label for item in ACTION_HEADERS):
            mapping.setdefault("action", index)
    return mapping


def parse_pfmea_xlsx_rows(
    table: list[list[str]],
    *,
    source_file: str,
    make_row: Any,
) -> list[Any]:
    if not table:
        return []
    header_index = 0
    for index, row in enumerate(table[:8]):
        joined = " ".join(cell.lower() for cell in row if cell)
        if "failure mode" in joined or "失效模式" in joined or joined.count("severity") >= 1:
            header_index = index
            break
    headers = _header_map(table[header_index])
    if "action" not in headers or not {"sev", "occ", "det"} <= headers.keys():
        return []
    rows: list[Any] = []
    for row in table[header_index + 1 :]:
        if not any(cell.strip() for cell in row):
            continue
        try:
            severity = int(float(row[headers["sev"]]))
            occurrence = int(float(row[headers["occ"]]))
            detection = int(float(row[headers["det"]]))
        except (KeyError, ValueError, IndexError):
            continue
        mode = row[headers["mode"]].strip() if "mode" in headers and headers["mode"] < len(row) else ""
        action_text = row[headers["action"]].strip() if "action" in headers and headers["action"] < len(row) else ""
        if not action_text:
            continue
        explicit_ap = ""
        if "ap" in headers and headers["ap"] < len(row):
            explicit_ap = row[headers["ap"]].strip().upper()
        rpn = severity * occurrence * detection
        if "rpn" in headers and headers["rpn"] < len(row) and row[headers["rpn"]].strip():
            try:
                rpn = int(float(row[headers["rpn"]]))
            except ValueError:
                pass
        row_obj = make_row(
            failure_mode=mode,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn,
            table_action_text=action_text,
            explicit_ap=explicit_ap,
            from_action_column=True,
        )
        if row_obj:
            rows.append(row_obj)
    return rows
