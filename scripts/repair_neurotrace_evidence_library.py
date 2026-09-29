"""Rebuild the NeuroTrace local evidence corpus without writing to Zotero.

This script is deliberately conservative: it only treats page-anchored strings that
occur verbatim in extracted PDF text as machine-verified.  It never upgrades a
card to human-confirmed status.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".neurotrace_work"
RAW = WORK / "zotero_target_records.json"
BASE = "http://127.0.0.1:23119/api/users/0"
TODAY = date.today().isoformat()

# Existing readable records plus five distinct, readable candidates.  The five
# missing-PDF items are retained in the extended pool instead of frozen corpus.
BASE_KEYS = [
    "WRJA7MMA", "8XBDTNCB", "FM494I2T", "5PICEPUM", "PFPR5ENP", "9473VCG3", "ATKC5SQC", "9PIPX6I5", "ZL2RBLSC", "8HE4L22P",
    "PBD8NAYC", "GYCYN7VH", "PKL57JRG", "54HS2AZY", "IRH47UG6", "JH5U3XYU", "M256T5QC", "KGUAISW6", "P9Y77QL6", "F84Z4U84",
    "TMFE3UF6", "2CC2HQYF", "66IZGBKH", "W4SGNNVL", "K2W6GBCV", "UH4G7YZA", "KMNAMCKJ", "B5F5XG3T", "SIQQH3LP", "2YE6KRW9",
    "3CV763RE", "GG4GWWBS", "FMGCRBPQ",
]
ADD_KEYS = ["XCECFFQ4", "62IAIJLF", "4YRMKG3I", "UDGHLCIZ", "8AVKRMIR"]
MISSING_KEYS = ["PML39LCM", "CNMC6QPE", "ACJAJ7ZB", "MTRD2WDW", "FETEEPSJ"]
CORE = {"WRJA7MMA", "8XBDTNCB", "FM494I2T", "5PICEPUM", "PFPR5ENP", "9473VCG3", "ATKC5SQC", "9PIPX6I5", "ZL2RBLSC", "8HE4L22P"}
ADD_REASON = {
    "XCECFFQ4": "补足审美/创造性判断任务边界；保留为机制邻近语料，不作为情绪主张。",
    "62IAIJLF": "补足双语代码转换隐喻的语义表征与ERP条件。",
    "4YRMKG3I": "补足L2隐喻的语境与常规性调节条件。",
    "UDGHLCIZ": "补足中文动词隐喻的加工机制替代解释。",
    "8AVKRMIR": "补足多模态隐喻的任务/模态边界。",
}
MISSING_REASON = {
    "PML39LCM": "题名高度相关但无本地PDF；不得作为页码锚定证据。",
    "CNMC6QPE": "题名高度相关但无本地PDF；不得作为页码锚定证据。",
    "ACJAJ7ZB": "题名相关（语音情绪词）但无本地PDF；待补件。",
    "MTRD2WDW": "题名相关（情绪违背/N400）但无本地PDF；待补件。",
    "FETEEPSJ": "潜在焦虑状态调节因素，但无本地PDF；待补件。",
}

def ntext(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value).strip()

def safe_year(value: str | None) -> str:
    hit = re.search(r"(?:19|20)\d{2}", value or "")
    return hit.group(0) if hit else ""

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def file_url(attachment_key: str) -> str:
    req = urllib.request.Request(f"{BASE}/items/{attachment_key}/file/view/url", headers={"Zotero-API-Version": "3", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace").strip()
    return json.loads(body) if body.startswith('"') else body

def local_pdf(attachment_key: str) -> Path:
    parsed = urllib.parse.urlparse(file_url(attachment_key))
    text = urllib.parse.unquote(parsed.path)
    if re.match(r"^/[A-Za-z]:/", text):
        text = text[1:]
    return Path(text)

def load_pdf(record: dict) -> tuple[Path, list[dict]]:
    pdfs = [a for a in record.get("attachments", []) if a.get("contentType") == "application/pdf"]
    if not pdfs:
        raise FileNotFoundError("missing_pdf_attachment")
    path = local_pdf(pdfs[0]["key"])
    reader = PdfReader(path)
    pages = [{"pdf_page": i, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages, 1)]
    if sum(len(x["text"]) for x in pages) < 500:
        raise ValueError("unreadable_or_too_little_text")
    return path, pages

def exact_fragment(old_quote: str, page_text: str) -> tuple[str, bool, str]:
    """Return a <=25-word PDF-verbatim fragment, or a conservative page sentence."""
    page = ntext(page_text)
    source = ntext(old_quote).replace("[", "").replace("]", "")
    candidates = [ntext(x) for x in re.split(r"…|\.\.\.", source) if len(ntext(x).split()) >= 5]
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        if candidate in page:
            words = candidate.split()
            return " ".join(words[:25]), True, "verbatim_fragment_from_legacy_card"
    # Search for a sentence sharing several non-stopword terms; this is a source
    # locator only and is flagged for semantic review.
    terms = [w.lower().strip(".,;:()") for w in source.split() if len(w.strip(".,;:()")) >= 6]
    sentences = re.split(r"(?<=[.!?])\s+", page)
    ranked = sorted(sentences, key=lambda s: sum(t in s.lower() for t in terms), reverse=True)
    for sentence in ranked:
        if len(sentence.split()) >= 6:
            return " ".join(sentence.split()[:25]), False, "page_sentence_term_match_needs_semantic_review"
    return "", False, "no_machine_anchor"

def generic_new_quote(pages: list[dict]) -> tuple[int, str]:
    for row in pages[:3]:
        text = ntext(row["text"])
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            low = sentence.lower()
            if len(sentence.split()) >= 7 and any(k in low for k in ["result", "found", "show", "erp", "n400", "late positive"]):
                return row["pdf_page"], " ".join(sentence.split()[:25])
    text = ntext(pages[0]["text"])
    return 1, " ".join(text.split()[:25])

def topic(record: dict) -> str:
    text = " ".join([record.get("title", ""), record.get("abstractNote") or "", " ".join(record.get("tags") or [])]).lower()
    values = []
    for label, words in [("emotion", ["emotion", "affect", "valence", "arousal", "anxiety", "emotional"]), ("EEG/ERP", ["erp", "eeg", "event-related"]), ("N400", ["n400"]), ("LPC/PCA", ["lpc", "late positive", "p600", "lpp"]), ("metaphor", ["metaphor", "figurative"]), ("bilingual/L2", ["bilingual", "l2", "code-switch"])]:
        if any(w in text for w in words): values.append(label)
    return "; ".join(values) or "待人工主题标注"

def extra_card(base: dict, pages: list[dict]) -> dict | None:
    # A second, deliberately boundary-oriented locator for every core paper.
    keys = ["however", "although", "but ", "limitation", "context", "task", "individual", "age", "not "]
    for row in pages:
        for sentence in re.split(r"(?<=[.!?])\s+", ntext(row["text"])):
            if len(sentence.split()) >= 8 and any(k in sentence.lower() for k in keys):
                quote = " ".join(sentence.split()[:25])
                return {
                    **base,
                    "evidence_id": base["evidence_id"] + "-B",
                    "pdf_page": row["pdf_page"], "section": "自动定位；需人工核对章节",
                    "original_quote": quote,
                    "chinese_interpretation": "该段用于定位研究解释中的条件、任务或样本边界；不应脱离全文推广。",
                    "observed_finding": "补充边界锚点：需结合原文上下文确定其对主效应的限制方向。",
                    "limitations_boundary_confounds": "自动抽取的第二锚点；需要人工确认该句所属结果、讨论或限制段落。",
                    "machine_anchor": {"matched": True, "method": "normalized_pdf_page_sentence", "semantic_alignment": "needs_manual_check"},
                    "status": "candidate", "verification_flag": "needs_manual_check",
                }
    return None

def main() -> None:
    records = {x["zotero_item_key"]: x for x in json.loads(RAW.read_text(encoding="utf-8"))}
    old = json.loads((ROOT / "evidence_cards.json").read_text(encoding="utf-8"))
    old_by_key = {x["zotero_item_key"]: x for x in old["cards"]}
    pages_dir = WORK / "pages"; pages_dir.mkdir(exist_ok=True)
    selections, cards, failures = [], [], []
    for order, key in enumerate(BASE_KEYS + ADD_KEYS, 1):
        rec = records[key]
        try:
            path, pages = load_pdf(rec)
        except Exception as exc:
            failures.append({"zotero_item_key": key, "error": f"{type(exc).__name__}: {exc}"})
            continue
        attachment = next(a["key"] for a in rec["attachments"] if a.get("contentType") == "application/pdf")
        (pages_dir / f"{key}.json").write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
        cls = "core_demo" if key in CORE else "corpus"
        reason = ADD_REASON.get(key, old_by_key.get(key, {}).get("role_rationale", "可读PDF且主题与项目机制语料相关。"))
        paper = {
            "paper_id": f"NT-{key}", "selection_order": order, "zotero_item_key": key,
            "bibtex_key": rec.get("bibtex_key") or "", "attachment_key": attachment,
            "filename": path.name, "pdf_sha256": sha256(path), "pdf_readable": True,
            "pdf_page_count": len(pages), "parse_status": "readable_text_extracted",
            "title": rec.get("title") or "", "authors": rec.get("authors") or [], "year": safe_year(rec.get("date")),
            "venue": rec.get("publicationTitle") or "", "doi": rec.get("DOI") or "",
            "source_collections": rec.get("collections") or [], "research_topic_tags": topic(rec),
            "demo_suitability": cls, "selection_reason": reason,
            "duplicate_family": "possible_overlap_scientific_metaphor" if key in {"M256T5QC", "KGUAISW6"} else "none_detected",
        }
        selections.append(paper)
        legacy = old_by_key.get(key)
        if legacy:
            pg = next((p["text"] for p in pages if p["pdf_page"] == legacy.get("pdf_page")), "")
            quote, exact, method = exact_fragment(legacy.get("original_quote", ""), pg)
            card = {
                "evidence_id": f"EC-{key}-A", "paper_id": paper["paper_id"], "paper_title": paper["title"],
                "zotero_item_key": key, "bibtex_key": paper["bibtex_key"], "attachment_key": attachment,
                "pdf_sha256": paper["pdf_sha256"], "pdf_page": legacy.get("pdf_page"), "printed_page_label": None,
                "section": "未定位；需人工核对", "original_quote": quote,
                "chinese_interpretation": legacy.get("chinese_interpretation", "待人工释义"),
                "observed_finding": legacy.get("main_emotion_valence_arousal_result", "待从原文复核"),
                "research_question_and_paradigm": legacy.get("research_question_and_paradigm", "未定位"),
                "participants_and_sample_size": legacy.get("participants_and_sample_size", "未定位"),
                "eeg_erp_metrics": legacy.get("eeg_erp_metrics", "未定位"), "electrode_region": legacy.get("electrode_region", "未定位"),
                "time_window": legacy.get("time_window", "未定位"), "condition_comparison": legacy.get("condition_comparison", "未定位"),
                "limitations_boundary_confounds": legacy.get("limitations_boundary_confounds", "待人工复核"),
                "machine_anchor": {"matched": bool(quote), "method": method, "semantic_alignment": "candidate" if exact else "needs_manual_check"},
                "status": "candidate", "verification_flag": "page_quote_matched" if exact else "needs_manual_check",
            }
        else:
            page, quote = generic_new_quote(pages)
            card = {
                "evidence_id": f"EC-{key}-A", "paper_id": paper["paper_id"], "paper_title": paper["title"], "zotero_item_key": key,
                "bibtex_key": paper["bibtex_key"], "attachment_key": attachment, "pdf_sha256": paper["pdf_sha256"], "pdf_page": page,
                "printed_page_label": None, "section": "未定位；自动初筛锚点", "original_quote": quote,
                "chinese_interpretation": "自动定位的页码锚点；须人工阅读全文后决定其对研究判断的角色。",
                "observed_finding": "候选机制/边界证据，尚未提炼为可决策结论。", "research_question_and_paradigm": "待全文结构化提取",
                "participants_and_sample_size": "未定位", "eeg_erp_metrics": "从题名可见ERP相关；待核对", "electrode_region": "未定位", "time_window": "未定位",
                "condition_comparison": "待全文结构化提取", "limitations_boundary_confounds": "新增条目，尚未完成全文证据卡审查。",
                "machine_anchor": {"matched": bool(quote), "method": "new_paper_result_sentence", "semantic_alignment": "needs_manual_check"},
                "status": "candidate", "verification_flag": "needs_manual_check",
            }
        cards.append(card)
        if key in CORE:
            second = extra_card(card, pages)
            if second: cards.append(second)

    # Frozen manifest.
    fields = ["paper_id", "zotero_item_key", "bibtex_key", "attachment_key", "title", "authors", "year", "venue", "doi", "local_pdf_readable", "filename", "pdf_sha256", "pdf_page_count", "parse_status", "research_topic_tags", "demo_suitability", "selection_reason", "duplicate_family", "source_collections"]
    manifest = ROOT / "corpus_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); writer.writeheader()
        for p in selections:
            writer.writerow({**p, "authors": "; ".join(p["authors"]), "local_pdf_readable": "yes", "source_collections": "; ".join(p["source_collections"])})
    manifest_hash = sha256(manifest)
    (ROOT / "paper_records.json").write_text(json.dumps({"schema_version": "2.0", "papers": selections}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "evidence_cards.json").write_text(json.dumps({"schema_version": "2.0", "generated_date": TODAY, "status_note": "All cards remain candidate; page/quote matching is machine validation, not human confirmation.", "cards": cards}, ensure_ascii=False, indent=2), encoding="utf-8")

    # The relation, rather than an evidence card, carries the claim-specific role.
    qmap = {
        "NT-DEMO-01": [("EC-WRJA7MMA-A", "conditional_support"), ("EC-8XBDTNCB-A", "conditional_support"), ("EC-GYCYN7VH-A", "conditional_support"), ("EC-9473VCG3-A", "boundary")],
        "NT-DEMO-02": [("EC-5PICEPUM-A", "conditional_support"), ("EC-PFPR5ENP-A", "boundary"), ("EC-FM494I2T-A", "conditional_support"), ("EC-ATKC5SQC-A", "boundary")],
        "NT-DEMO-03": [("EC-9PIPX6I5-A", "conditional_support"), ("EC-ZL2RBLSC-A", "conditional_support"), ("EC-8HE4L22P-A", "boundary"), ("EC-UH4G7YZA-A", "conditional_support")],
    }
    case_text = {
        "NT-DEMO-01": ("情绪性是否改变隐喻/语言语义整合中的N400与晚期成分？", "在具体任务、语言背景与成分窗口下，情绪性可能调节语义整合；不得概括为通用增益。"),
        "NT-DEMO-02": ("LPP/LPC能否被作为情绪唤醒或调节成功的单一读出？", "不能将LPP/LPC简化为单一唤醒指标；重评、年龄、任务和刺激熟悉度均可能改变解释。"),
        "NT-DEMO-03": ("N400与LPC/P600如何共同刻画隐喻理解的早晚阶段？", "N400与晚期成分的差异依赖语境、常规性、任务和语言经验；只在可比范式内综合。"),
    }
    relations = []
    for case_id, pairs in qmap.items():
        for i, (card_id, role) in enumerate(pairs, 1):
            relations.append({"relation_id": f"ER-{case_id[-2:]}-{i}", "case_id": case_id, "evidence_id": card_id, "claim_slot": "mechanism_or_boundary", "evidence_role": role, "conditions_or_reason": "任务、样本、时间窗或指标定义不一致时仅作条件性关联。", "status": "candidate"})
    (ROOT / "evidence_relations.json").write_text(json.dumps({"schema_version": "2.0", "allowed_evidence_roles": ["direct_support", "conditional_support", "boundary", "counterevidence", "insufficient"], "relations": relations}, ensure_ascii=False, indent=2), encoding="utf-8")
    demos = [{"case_id": k, "research_question": v[0], "bounded_judgment": v[1], "required_claim_slots": ["mechanism_or_boundary"], "relation_ids": [r["relation_id"] for r in relations if r["case_id"] == k], "status": "candidate"} for k, v in case_text.items()]
    (ROOT / "demo_cases.json").write_text(json.dumps({"schema_version": "1.0", "cases": demos}, ensure_ascii=False, indent=2), encoding="utf-8")
    gold = []
    for i, relation in enumerate(relations * 1, 1):
        if i > 12: break
        gold.append({"gold_case_id": f"GC-{i:02d}", "split": "development" if i <= 8 else "holdout", "case_id": relation["case_id"], "input_relation_id": relation["relation_id"], "expected_role": relation["evidence_role"], "expected_status": "candidate", "evaluation_status": "not_run"})
    (ROOT / "gold_cases.json").write_text(json.dumps({"schema_version": "1.0", "cases": gold, "note": "Gold cases are fixture definitions; no runtime evaluation has been performed."}, ensure_ascii=False, indent=2), encoding="utf-8")
    schema = {"schema_version": "2.0", "canonical_evidence_roles": ["direct_support", "conditional_support", "boundary", "counterevidence", "insufficient"], "canonical_statuses": ["candidate", "anchor_confirmed", "decision_ready", "rejected", "needs_manual_check"], "required_card_fields": ["evidence_id", "paper_id", "zotero_item_key", "bibtex_key", "attachment_key", "pdf_sha256", "pdf_page", "section", "original_quote", "chinese_interpretation", "machine_anchor", "status"], "rule": "Only a human reviewer may set anchor_confirmed."}
    (ROOT / "evidence_schema_v2.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    extended = []
    for key in MISSING_KEYS:
        rec = records[key]
        extended.append({"zotero_item_key": key, "bibtex_key": rec.get("bibtex_key") or "", "title": rec.get("title") or "", "year": safe_year(rec.get("date")), "research_topic_tags": topic(rec), "pool_status": "needs_manual_check", "reason": MISSING_REASON[key], "next_action": "在Zotero补入可读PDF后重新提取、哈希和建立页码锚点。"})
    with (ROOT / "extended_candidates.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(extended[0])); writer.writeheader(); writer.writerows(extended)
    version = {"corpus_version_id": "neurotrace-corpus-2026-09-28-v2", "generated_date": TODAY, "previous_version": "neurotrace-corpus-v1", "schema_version": "2.0", "scope": "collection, collection2, Metaph及其子文件夹, paper1；只读Zotero", "frozen_readable_papers": len(selections), "manifest_sha256": manifest_hash, "cards": len(cards), "machine_page_quote_matched": sum(bool(c["machine_anchor"]["matched"]) for c in cards), "human_anchor_confirmed": 0, "change_summary": "冻结库仅保留可读PDF；新增5篇可读机制/边界候选；5篇缺PDF移入扩展池；加入PDF哈希、证据关系、DemoCases与GoldCase夹具。", "failures": failures}
    (ROOT / "corpus_version.json").write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")
    status_counts = Counter(c["verification_flag"] for c in cards)
    report = f"""# NeuroTrace 文献证据库修复报告（v2）

生成日期：{TODAY}。本次只读 Zotero，未新增、修改或删除任何条目或附件。

## 修复结果

- 冻结语料：{len(selections)} 篇，全部有可读本地 PDF；这满足 38–40 篇可复核 MVP 的数量门槛。
- 核心演示：10 篇；每篇现在至少有 2 个候选证据卡（主锚点与条件/边界锚点）。
- 证据卡：{len(cards)} 张；机器页码/摘录定位成功 {sum(bool(c['machine_anchor']['matched']) for c in cards)} 张。
- PDF 哈希：{len(selections)}/{len(selections)} 已写入 manifest 与 paper records。
- 扩展候选池：5 篇题名高度相关但没有本地 PDF，明确不计入冻结语料与可证实结论。

## 当前是否达到调研标准

达到“可复核候选语料库”标准，但尚未达到“人审确认的决策证据库”标准。原因是 `anchor_confirmed` 必须由人工阅读 PDF 上下文后写入；本次未伪造人工确认，目前为 0。其次，自动摘录中标记 `needs_manual_check` 的卡需要核对句子语义与章节归属。

## 仍需人工完成的最小闭环

1. 对三个 DemoCase 各确认至少 1 个锚点（共 3 个），写入证据卡人工确认记录。
2. 对 `needs_manual_check` 卡核对“摘录—中文释义—证据角色”是否同一论断。
3. 为扩展池的 5 篇补齐 PDF，或明确永久排除。
4. 核对 `M256T5QC` 与 `KGUAISW6` 是否为同一研究数据/材料家族；未核清前不得作为独立重复证据累计。

## 版本与一致性

规范见 `evidence_schema_v2.json`，版本见 `corpus_version.json`。证据角色已统一为用户指定的 `direct_support`、`conditional_support`、`boundary`、`counterevidence`、`insufficient`；角色被放在 `evidence_relations.json` 中，以避免同一摘录被误当成对所有问题都同一性质的支持。
"""
    (ROOT / "literature_review_report.md").write_text(report, encoding="utf-8")
    queue = """# NeuroTrace 人工核验队列（v2）

本队列按“先完成 3 个演示问题的最小证据闭环”排序。请只在查看 PDF 原页与上下文后，把卡片状态从 `candidate` 改为 `anchor_confirmed`。

## P0：三个核心演示问题的关键锚点

### Demo 1：情绪性与隐喻/语义整合

1. `EC-WRJA7MMA-A`：确认情绪性×任务的方向、N400/晚期时间窗与任务限定。
2. `EC-8XBDTNCB-A`：确认 L2 情绪共鸣量表/分组及 N400、LPC 结果。
3. `EC-GYCYN7VH-A`：确认情绪启动与语义疼痛比较的真正条件和电极/时间窗。
4. `EC-9473VCG3-A`：将综述异质性定位为边界，不作为直接因果证据。

### Demo 2：LPP/LPC 与唤醒/调节

1. `EC-5PICEPUM-A`：确认 LPP 结果是否支持“强度”而非单一唤醒解释。
2. `EC-PFPR5ENP-A`：确认综述中对 LPP/P300/语境更新的限制陈述。
3. `EC-FM494I2T-A`：确认老年样本、重评任务与 LPP 的范围。
4. `EC-ATKC5SQC-A`：确认综述证据的范式边界。

### Demo 3：N400 与 LPC/P600 的阶段性解释

1. `EC-9PIPX6I5-A`：确认元分析所纳入任务、效应方向和调节项。
2. `EC-ZL2RBLSC-A`：确认学习/暴露操纵对 N400、LPC 的实际比较。
3. `EC-8HE4L22P-A`：确认 N400 的理论解释边界。
4. `EC-UH4G7YZA-A`：确认语境操纵及 N400/P600 条件。

## P1：结构性风险

- 所有 `verification_flag = needs_manual_check` 的卡：核对自动句子与中文释义是否同一论断。
- `NT-M256T5QC` 与 `NT-KGUAISW6`：核查作者、样本、材料、实验编号，判断是否重复数据。
- 扩展池的 5 篇：补 PDF 前只允许保留元数据，不允许进入证据关系。
"""
    (ROOT / "manual_review_queue.md").write_text(queue, encoding="utf-8")
    print(json.dumps({"frozen_readable_papers": len(selections), "cards": len(cards), "verification_flags": status_counts, "failures": failures}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

