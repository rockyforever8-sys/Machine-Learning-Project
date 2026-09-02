#!/usr/bin/env python3
"""Merge Simplified/Traditional Chinese PPAP markers into skill rules.json files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE_PATHS = [
    ROOT / ".cursor" / "skills" / "aiag-ppap-4th-edition" / "rules.json",
    ROOT / "manufacturing-quality" / "skills" / "aiag-ppap-4th-edition" / "rules.json",
]

BINDER_INDEX_PHRASES = [
    "目录",
    "目錄",
    "目次",
    "文件清单",
    "文件清單",
    "表格内容",
    "表格內容",
    "提交目录",
    "提交目錄",
    "附件清单",
    "附件清單",
]

BINDER_PSW_MARKERS = [
    "零件提交保证书",
    "零件提交保證書",
    "供应商授权签字",
    "供應商授權簽字",
    "提交等级",
    "提交等級",
    "声明",
    "聲明",
]

CHINESE: dict[int, dict[str, list[str]]] = {
    1: {
        "aliases": ["设计记录", "設計記錄", "图纸", "圖紙", "工程图", "工程圖"],
        "content_markers": ["图号", "圖號", "图纸编号", "标题栏", "標題欄", "版次", "材料规格", "材料規格", "公差", "工程图", "工程圖"],
        "unique_markers": ["设计记录", "設計記錄", "图号", "圖號", "标题栏", "標題欄", "工程图", "工程圖"],
        "exclude_markers": ["检具图", "檢具圖", "夹具图", "夾具圖"],
        "filename_patterns": ["设计记录", "設計記錄"],
    },
    2: {
        "aliases": ["工程变更", "工程變更", "工程更改", "变更通知", "變更通知"],
        "content_markers": ["工程变更通知", "工程變更通知", "工程变更单", "工程變更單", "生效日期", "变更原因", "變更原因", "变更等级", "變更等級"],
        "unique_markers": ["工程变更通知", "工程變更通知", "工程变更单", "工程變更單", "工程变更", "工程變更"],
        "filename_patterns": ["工程变更", "工程變更"],
    },
    3: {
        "aliases": ["客户工程批准", "客戶工程批准", "顾客工程批准", "顧客工程批准", "偏差许可", "偏差許可"],
        "content_markers": ["客户工程批准", "顧客工程批准", "偏差许可", "偏差許可", "客户签字", "客戶簽字", "批准日期"],
        "unique_markers": ["客户工程批准", "客戶工程批准", "顾客工程批准", "顧客工程批准", "偏差许可", "偏差許可"],
        "filename_patterns": ["客户工程批准", "顧客工程批准"],
    },
    4: {
        "aliases": ["设计失效模式", "設計失效模式", "设计FMEA", "設計FMEA"],
        "content_markers": ["设计失效", "設計失效", "设计功能", "設計功能", "严重度", "嚴重度", "频度", "頻度", "探测度", "探測度", "风险顺序数", "風險優先數"],
        "unique_markers": ["设计失效模式", "設計失效模式", "设计FMEA", "設計FMEA", "设计功能", "設計功能"],
        "exclude_markers": ["过程FMEA", "過程FMEA", "制程FMEA", "製程FMEA", "过程失效", "過程失效"],
        "filename_patterns": ["设计失效", "設計失效"],
    },
    5: {
        "aliases": ["过程流程图", "過程流程圖", "工艺流程图", "工藝流程圖", "制程流程图", "製程流程圖"],
        "content_markers": ["过程步骤", "過程步驟", "工序", "来料", "來料", "出货", "出貨", "返工", "作业说明", "作業說明"],
        "unique_markers": ["过程流程图", "過程流程圖", "工艺流程图", "工藝流程圖", "制程流程图", "製程流程圖"],
        "filename_patterns": ["过程流程", "過程流程", "工艺流程", "工藝流程"],
    },
    6: {
        "aliases": ["过程失效模式", "過程失效模式", "过程FMEA", "過程FMEA", "制程FMEA", "製程FMEA"],
        "content_markers": ["过程功能", "過程功能", "当前过程控制", "當前過程控制", "特殊特性", "严重度", "嚴重度", "频度", "頻度", "探测度", "探測度", "风险顺序数", "風險優先數", "失效模式"],
        "unique_markers": ["过程FMEA", "過程FMEA", "过程失效模式", "過程失效模式", "当前过程控制", "當前過程控制"],
        "exclude_markers": ["设计FMEA", "設計FMEA", "设计失效", "設計失效"],
        "continuation_markers": ["严重度", "嚴重度", "频度", "頻度", "探测度", "探測度", "失效模式", "过程步骤", "過程步驟"],
        "filename_patterns": ["过程失效", "過程失效", "过程FMEA", "過程FMEA"],
    },
    7: {
        "aliases": ["控制计划", "控制計劃"],
        "content_markers": ["反应计划", "反應計劃", "抽样频率", "抽樣頻率", "控制方法", "样本容量", "樣本容量", "特殊特性", "预投产", "預投產", "生产控制计划", "生產控制計劃"],
        "unique_markers": ["控制计划", "控制計劃", "反应计划", "反應計劃", "抽样频率", "抽樣頻率", "控制方法"],
        "filename_patterns": ["控制计划", "控制計劃"],
    },
    8: {
        "aliases": ["测量系统分析", "測量系統分析", "量具再现性", "量具R&R"],
        "content_markers": ["测量系统分析", "測量系統分析", "重复性", "重複性", "再现性", "再現性", "偏倚", "线性", "線性", "稳定性", "穩定性"],
        "unique_markers": ["测量系统分析", "測量系統分析", "量具R&R", "重复性", "重複性", "再现性", "再現性"],
        "filename_patterns": ["测量系统", "測量系統", "量具"],
    },
    9: {
        "aliases": ["尺寸结果", "尺寸結果", "尺寸报告", "尺寸報告", "全尺寸"],
        "content_markers": ["实测值", "實測值", "尺寸检验", "尺寸檢驗", "三坐标", "三座標", "气泡图", "氣泡圖", "合格", "超差", "名义值", "名義值"],
        "unique_markers": ["尺寸结果", "尺寸結果", "全尺寸检验", "全尺寸檢驗", "尺寸报告", "尺寸報告"],
        "filename_patterns": ["尺寸结果", "尺寸結果", "全尺寸"],
    },
    10: {
        "aliases": ["材料试验", "材料試驗", "性能试验", "性能試驗", "材质证明", "材質證明"],
        "content_markers": ["化学成分", "化學成分", "抗拉强度", "抗拉強度", "硬度", "炉号", "爐號", "材质报告", "材質報告", "合格证明", "合格證明"],
        "unique_markers": ["材质证明", "材質證明", "材料试验", "材料試驗", "性能试验", "性能試驗", "化学成分", "化學成分"],
        "filename_patterns": ["材料试验", "材料試驗", "材质证明", "材質證明"],
    },
    11: {
        "aliases": ["初始过程能力", "初始過程能力", "过程能力", "過程能力", "能力研究"],
        "content_markers": ["过程能力", "過程能力", "控制图", "控制圖", "子组", "子組", "规格上限", "規格上限", "规格下限", "規格下限"],
        "unique_markers": ["过程能力", "過程能力", "初始过程研究", "初始過程研究", "初始过程能力", "初始過程能力"],
        "filename_patterns": ["过程能力", "過程能力", "初始过程", "初始過程"],
    },
    12: {
        "aliases": ["合格实验室", "合格實驗室", "实验室认可", "實驗室認可", "实验室资质", "實驗室資質"],
        "content_markers": ["认可证书", "認可證書", "实验室范围", "實驗室範圍", "检测能力", "檢測能力"],
        "unique_markers": ["实验室认可", "實驗室認可", "合格实验室", "合格實驗室"],
        "filename_patterns": ["实验室认可", "實驗室認可", "合格实验室", "合格實驗室"],
    },
    13: {
        "aliases": ["外观批准", "外觀批准", "外观批准报告", "外觀批准報告"],
        "content_markers": ["色板", "光泽", "光澤", "纹理", "紋理", "外观", "外觀"],
        "unique_markers": ["外观批准报告", "外觀批准報告", "外观批准", "外觀批准"],
        "filename_patterns": ["外观批准", "外觀批准"],
    },
    14: {
        "aliases": ["生产件样品", "生產件樣品", "样件", "樣件", "样品标签", "樣品標籤"],
        "content_markers": ["样品数量", "樣品數量", "装箱单", "裝箱單", "样品提交", "樣品提交"],
        "unique_markers": ["生产件样品", "生產件樣品", "样品标签", "樣品標籤"],
        "exclude_markers": ["标准样品", "標準樣品", "主样品", "主樣品", "金样", "金樣"],
        "filename_patterns": ["生产件样品", "生產件樣品", "样件", "樣件"],
    },
    15: {
        "aliases": ["标准样品", "標準樣品", "主样品", "主樣品"],
        "content_markers": ["留样", "留樣", "标准样品协议", "標準樣品協議", "存放位置"],
        "unique_markers": ["标准样品", "標準樣品", "主样品", "主樣品"],
        "filename_patterns": ["标准样品", "標準樣品", "主样品", "主樣品"],
    },
    16: {
        "aliases": ["检验辅具", "檢驗輔具", "检具", "檢具", "通止规", "通止規"],
        "content_markers": ["检具编号", "檢具編號", "校准", "校準", "夹具", "夾具"],
        "unique_markers": ["检验辅具", "檢驗輔具", "检具", "檢具", "通止规", "通止規"],
        "filename_patterns": ["检验辅具", "檢驗輔具", "检具", "檢具"],
    },
    17: {
        "aliases": ["顾客特殊要求", "顧客特殊要求", "客户特殊要求", "客戶特殊要求"],
        "content_markers": ["顾客要求", "顧客要求", "主机厂", "主機廠", "附加要求"],
        "unique_markers": ["顾客特殊要求", "顧客特殊要求", "客户特殊要求", "客戶特殊要求"],
        "filename_patterns": ["顾客特殊要求", "顧客特殊要求", "客户特殊要求", "客戶特殊要求"],
    },
    18: {
        "aliases": ["零件提交保证书", "零件提交保證書", "提交保证书", "提交保證書", "保证书", "保證書"],
        "content_markers": ["声明", "聲明", "零件名称", "零件名稱", "零件号", "零件號", "采购订单", "採購訂單", "提交等级", "提交等級", "供应商授权签字", "供應商授權簽字"],
        "unique_markers": ["零件提交保证书", "零件提交保證書", "供应商授权签字", "供應商授權簽字", "提交等级", "提交等級"],
        "filename_patterns": ["零件提交保证书", "零件提交保證書", "保证书", "保證書"],
    },
}


def _extend(existing: list[object], extra: list[str]) -> list[object]:
    seen = {str(item) for item in existing}
    merged = list(existing)
    for item in extra:
        if item not in seen:
            merged.append(item)
            seen.add(item)
    return merged


def merge_file(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    binder = payload.setdefault("binder_rules", {})
    binder["index_phrases"] = _extend(list(binder.get("index_phrases") or []), BINDER_INDEX_PHRASES)
    binder["psw_form_markers"] = _extend(list(binder.get("psw_form_markers") or []), BINDER_PSW_MARKERS)
    binder["languages"] = ["en", "zh-Hans", "zh-Hant"]

    by_number = {int(item["number"]): item for item in payload["elements"]}
    for number, additions in CHINESE.items():
        record = by_number[number]
        for field, values in additions.items():
            record[field] = _extend(list(record.get(field) or []), values)

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for path in RULE_PATHS:
        if not path.is_file():
            raise SystemExit(f"Missing {path}")
        merge_file(path)
        print(f"updated {path}")


if __name__ == "__main__":
    main()
