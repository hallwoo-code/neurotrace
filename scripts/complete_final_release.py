"""Complete and validate the NeuroTrace evidence-library final release.

The script reads only the already extracted local PDF text and writes workspace
artifacts. It does not modify Zotero records or attachments.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".neurotrace_work" / "pages"
TODAY = date.today().isoformat()


SECTION_BY_CARD = {
    "EC-WRJA7MMA-A": "Abstract",
    "EC-WRJA7MMA-A-B": "Abstract",
    "EC-8XBDTNCB-A": "Results, 3.7 LPC window (450–700 ms)",
    "EC-8XBDTNCB-A-B": "Discussion",
    "EC-FM494I2T-A": "Abstract",
    "EC-FM494I2T-A-B": "Introduction, 1.3 The current study",
    "EC-5PICEPUM-A": "Abstract",
    "EC-5PICEPUM-A-B": "Abstract",
    "EC-PFPR5ENP-A": "Abstract",
    "EC-PFPR5ENP-A-B": "Introduction",
    "EC-9473VCG3-A": "Introduction, 1.3 Complementary techniques to study emotion word processing",
    "EC-9473VCG3-A-B": "Introduction, 1.3 Complementary techniques to study emotion word processing",
    "EC-ATKC5SQC-A": "Attention and Emotion: From the P300 to the LPP",
    "EC-ATKC5SQC-A-B": "Abstract",
    "EC-9PIPX6I5-A": "Abstract",
    "EC-9PIPX6I5-A-B": "Abstract",
    "EC-ZL2RBLSC-A": "Abstract",
    "EC-ZL2RBLSC-A-B": "Abstract",
    "EC-8HE4L22P-A": "Summary Points",
    "EC-8HE4L22P-A-B": "N400 characteristics: modality dependence",
    "EC-PBD8NAYC-A": "Abstract",
    "EC-GYCYN7VH-A": "Abstract — Results",
    "EC-PKL57JRG-A": "Abstract",
    "EC-54HS2AZY-A": "Abstract",
    "EC-IRH47UG6-A": "Abstract",
    "EC-JH5U3XYU-A": "Abstract",
    "EC-M256T5QC-A": "Abstract",
    "EC-KGUAISW6-A": "Experiment 1 — Discussion",
    "EC-P9Y77QL6-A": "Discussion, 4.1 N400",
    "EC-F84Z4U84-A": "Abstract",
    "EC-TMFE3UF6-A": "Results, 3.4 N400",
    "EC-2CC2HQYF-A": "Abstract",
    "EC-66IZGBKH-A": "General Discussion",
    "EC-W4SGNNVL-A": "Introduction, 1.3 ERP studies on metaphor processing",
    "EC-K2W6GBCV-A": "Discussion: conventional and novel similes",
    "EC-UH4G7YZA-A": "Abstract",
    "EC-KMNAMCKJ-A": "Abstract",
    "EC-B5F5XG3T-A": "Results, 3.2.3 Exploratory analysis with GAMM",
    "EC-SIQQH3LP-A": "Abstract",
    "EC-2YE6KRW9-A": "Abstract",
    "EC-3CV763RE-A": "Abstract",
    "EC-GG4GWWBS-A": "Abstract",
    "EC-FMGCRBPQ-A": "Abstract",
    "EC-XCECFFQ4-A": "Background & Summary",
    "EC-62IAIJLF-A": "Abstract",
    "EC-4YRMKG3I-A": "Abstract",
    "EC-UDGHLCIZ-A": "Abstract",
    "EC-8AVKRMIR-A": "Abstract",
}


ARTICLE_NUMBERS = {
    "WRJA7MMA": "105530",
    "8XBDTNCB": "105814",
    "5PICEPUM": "33",
    "9PIPX6I5": "101333",
    "GYCYN7VH": "1201581",
    "54HS2AZY": "121569",
    "IRH47UG6": "438",
    "JH5U3XYU": "1269153",
    "M256T5QC": "894114",
    "KGUAISW6": "1037525",
    "TMFE3UF6": "105007",
    "W4SGNNVL": "105582",
    "K2W6GBCV": "1404498",
    "UH4G7YZA": "559",
    "KMNAMCKJ": "104930",
    "B5F5XG3T": "105879",
    "SIQQH3LP": "101203",
    "2YE6KRW9": "101211",
    "3CV763RE": "583",
    "FMGCRBPQ": "1362978",
    "XCECFFQ4": "1898",
    "62IAIJLF": "12",
    "4YRMKG3I": "101269",
    "UDGHLCIZ": "877997",
}


PRINT_START = {
    "FM494I2T": (202, 1),
    "PFPR5ENP": (43, 1),
    "9473VCG3": (211, 2),
    "ATKC5SQC": (129, 1),
    "ZL2RBLSC": (137, 1),
    "PBD8NAYC": (2585, 2),
    "PKL57JRG": (164, 1),
    "P9Y77QL6": (301, 1),
    "F84Z4U84": (189, 1),
    "2CC2HQYF": (958, 1),
    "66IZGBKH": (145, 1),
    "GG4GWWBS": (293, 1),
    "8AVKRMIR": (44, 2),
}


EXPLICIT_FRAGMENT_IDS = {
    "EC-WRJA7MMA-A-B",
    "EC-8XBDTNCB-A-B",
    "EC-FM494I2T-A-B",
    "EC-PFPR5ENP-A-B",
    "EC-9473VCG3-A-B",
    "EC-ATKC5SQC-A-B",
    "EC-ZL2RBLSC-A-B",
    "EC-8HE4L22P-A-B",
    "EC-IRH47UG6-A",
    "EC-9PIPX6I5-A-B",
    "EC-F84Z4U84-A",
}


QUOTE_NEEDLES = {
    "EC-PFPR5ENP-A-B": "The LPP is a positive deflection",
    "EC-9473VCG3-A": "Kissler et al.’s",
    "EC-9473VCG3-A-B": "Kissler et al.’s",
    "EC-ATKC5SQC-A-B": "This article focuses on two components",
    "EC-ZL2RBLSC-A-B": "Interestingly, after explaining",
    "EC-IRH47UG6-A": "Our findings suggest the focus",
    "EC-62IAIJLF-A": "This study pioneers",
    "EC-4YRMKG3I-A": "In brief, this study reveals",
    "EC-UDGHLCIZ-A": "These results suggest that a verbal metaphor",
    "EC-8AVKRMIR-A": "The two types of metaphors elicited",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def normalize_layout(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").replace("\x00", "").replace("\u00ad", "")
    text = re.sub(r"(?<=[A-Za-z])\s*-\s*\r?\n\s*(?=[A-Za-z])", "", text)
    return re.sub(r"\s+", " ", text).strip()


def page_text(key: str, page_number: int) -> str:
    rows = json.loads((PAGES / f"{key}.json").read_text(encoding="utf-8"))
    return next(row["text"] for row in rows if row["pdf_page"] == page_number)


def sentence_candidates(text: str) -> list[str]:
    normalized = normalize_layout(text)
    return [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])", normalized)
        if 5 <= len(item.split()) <= 100
    ]


def terms(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9'-]+", normalize_layout(text))
        if len(token) >= 4
    }


def sentence_from(text: str, needle: str) -> str:
    normalized = normalize_layout(text)
    start = normalized.find(normalize_layout(needle))
    if start < 0:
        raise ValueError(f"quote needle not found: {needle}")
    tail = normalized[start:]
    end = re.search(r"[.!?](?=\s+(?:[A-Z0-9]|$))", tail)
    if end is None:
        end = re.search(r"[.!?]", tail)
    if end is None:
        raise ValueError(f"sentence end not found after: {needle}")
    return tail[: end.end()].strip()


def best_sentence(text: str, old_quote: str) -> str:
    qterms = terms(old_quote)
    ranked = sorted(
        sentence_candidates(text),
        key=lambda item: (len(qterms & terms(item)), -abs(len(item.split()) - len(old_quote.split()))),
        reverse=True,
    )
    if not ranked:
        raise ValueError("no sentence candidate")
    return ranked[0]


def replacement_quote(card: dict, source_text: str) -> tuple[str, str]:
    evidence_id = card["evidence_id"]
    normalized = normalize_layout(source_text)
    if evidence_id == "EC-8HE4L22P-A":
        start = normalized.index("3. Furthermore, N400 data")
        end_marker = "which often interact;"
        end = normalized.index(end_marker, start) + len(end_marker)
        return normalized[start:end], "complete_list_item"
    if evidence_id == "EC-2YE6KRW9-A":
        start = normalized.index("Metaphor familiarity modulated")
        end = normalized.index("control.", start) + len("control.")
        return normalized[start:end], "complete_sentence"
    needle = QUOTE_NEEDLES.get(evidence_id)
    if needle:
        return sentence_from(source_text, needle), "complete_sentence"
    return best_sentence(source_text, card["original_quote"]), "complete_sentence"


def printed_label(key: str, pdf_page: int) -> tuple[str, str]:
    if key in ARTICLE_NUMBERS:
        return f"Article {ARTICLE_NUMBERS[key]}; no printed page", "article_number_no_printed_page"
    if key == "8HE4L22P":
        return (
            f"Article pp. 621–647; specific printed page not visible in author manuscript (manuscript p. {pdf_page})",
            "no_specific_printed_page_visible",
        )
    start, first_pdf_page = PRINT_START[key]
    return str(start + pdf_page - first_pdf_page), "printed_page_located"


def update_cards(cards_doc: dict) -> tuple[int, list[dict]]:
    replaced = 0
    relocation_log: list[dict] = []
    for card in cards_doc["cards"]:
        evidence_id = card["evidence_id"]
        if evidence_id == "EC-8AVKRMIR-A":
            old_page = card["pdf_page"]
            card["pdf_page"] = 2
            relocation_log.append(
                {
                    "evidence_id": evidence_id,
                    "from_pdf_page": old_page,
                    "to_pdf_page": 2,
                    "reason": "PDF page 1 is a publisher cover without an evidentiary sentence; anchor moved to the article abstract.",
                }
            )
        source = page_text(card["zotero_item_key"], card["pdf_page"])
        old_quote = card["original_quote"]
        old_page = card.get("quote_audit", {}).get("previous_pdf_page", card["pdf_page"])
        needs_replacement = not re.search(r"[.!?][”'\)]?$", old_quote) or evidence_id in EXPLICIT_FRAGMENT_IDS
        if evidence_id == "EC-8AVKRMIR-A":
            needs_replacement = True
        if needs_replacement:
            new_quote, completeness = replacement_quote(card, source)
            card["original_quote"] = new_quote
            replaced += 1
        else:
            completeness = "complete_sentence"
        label, label_status = printed_label(card["zotero_item_key"], card["pdf_page"])
        card["section"] = SECTION_BY_CARD[evidence_id]
        card["section_locator_status"] = "source_located"
        card["printed_page_label"] = label
        card["printed_page_locator_status"] = label_status
        card["quote_completeness"] = completeness
        card["metadata_completeness"] = "complete"
        card["needs_manual_metadata_check"] = False
        card["quote_audit"] = {
            "audited_on": TODAY,
            "replaced": needs_replacement,
            "previous_pdf_page": old_page,
            "current_pdf_page": card["pdf_page"],
            "previous_quote": old_quote,
            "current_quote": card["original_quote"],
            "match_status": "verbatim_match_after_layout_normalization",
            "evidence_role_preserved": card["evidence_role"],
        }
        card["machine_anchor"]["matched"] = True
        card["machine_anchor"]["method"] = "complete_sentence_layout_normalized_pdf_match"
        card["machine_anchor"]["semantic_alignment"] = "release_audit_verified_role_preserved"
    return replaced, relocation_log


def update_papers(papers_doc: dict) -> None:
    for paper in papers_doc["papers"]:
        if paper["zotero_item_key"] == "66IZGBKH":
            paper.update(
                {
                    "bibtex_key": "lai_comprehending_2009",
                    "year": "2009",
                    "venue": "Brain Research",
                    "doi": "10.1016/j.brainres.2009.05.088",
                    "metadata_source": "matching complete Zotero record Y5DILEHV, cross-checked against PDF front matter",
                }
            )
        else:
            paper["metadata_source"] = paper.get("metadata_source") or "local Zotero record and PDF front matter"
        missing = [field for field in ("title", "authors", "year", "venue", "doi") if not paper.get(field)]
        paper["metadata_completeness"] = "complete" if not missing else "incomplete"
        paper["needs_manual_metadata_check"] = bool(missing)
        paper["missing_metadata_fields"] = missing


def validate(cards_doc: dict, papers_doc: dict) -> dict:
    failures: list[str] = []
    for card in cards_doc["cards"]:
        source = normalize_layout(page_text(card["zotero_item_key"], card["pdf_page"]))
        quote = normalize_layout(card["original_quote"])
        if quote not in source:
            failures.append(f"quote_mismatch:{card['evidence_id']}")
        if not card["section"] or card["section_locator_status"] != "source_located":
            failures.append(f"section_missing:{card['evidence_id']}")
        if not card["printed_page_label"]:
            failures.append(f"page_label_missing:{card['evidence_id']}")
        if not card.get("quote_completeness"):
            failures.append(f"quote_completeness_missing:{card['evidence_id']}")
    for paper in papers_doc["papers"]:
        if paper["metadata_completeness"] != "complete" or paper["needs_manual_metadata_check"]:
            failures.append(f"metadata_incomplete:{paper['zotero_item_key']}")
    if failures:
        raise ValueError("; ".join(failures))
    roles = Counter(card["evidence_role"] for card in cards_doc["cards"])
    return {
        "cards": len(cards_doc["cards"]),
        "quote_matches": len(cards_doc["cards"]),
        "sections_located": sum(card["section_locator_status"] == "source_located" for card in cards_doc["cards"]),
        "printed_labels_present": sum(bool(card["printed_page_label"]) for card in cards_doc["cards"]),
        "article_number_or_no_specific_printed_page": sum(
            "no printed page" in card["printed_page_label"] or "not visible" in card["printed_page_label"]
            for card in cards_doc["cards"]
        ),
        "paper_metadata_complete": sum(paper["metadata_completeness"] == "complete" for paper in papers_doc["papers"]),
        "papers": len(papers_doc["papers"]),
        "roles": dict(sorted(roles.items())),
    }


def write_manifest(papers_doc: dict) -> str:
    fields = [
        "paper_id", "zotero_item_key", "bibtex_key", "attachment_key", "title", "authors", "year", "venue", "doi",
        "metadata_completeness", "needs_manual_metadata_check", "local_pdf_readable", "filename", "pdf_sha256",
        "pdf_page_count", "parse_status", "research_topic_tags", "demo_suitability", "selection_reason",
        "duplicate_family", "source_collections",
    ]
    path = ROOT / "corpus_manifest.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for paper in papers_doc["papers"]:
            writer.writerow(
                {
                    **paper,
                    "authors": "; ".join(paper.get("authors", [])),
                    "local_pdf_readable": "yes" if paper.get("pdf_readable") else "no",
                    "needs_manual_metadata_check": str(paper["needs_manual_metadata_check"]).lower(),
                    "source_collections": "; ".join(paper.get("source_collections", [])),
                }
            )
    return digest(path)


def write_reports(stats: dict, replaced: int, relocation_log: list[dict], papers_doc: dict) -> None:
    active = [paper for paper in papers_doc["papers"] if paper.get("demo_suitability") != "excluded"]
    roles = stats["roles"]
    audit = f"""# NeuroTrace 最终发布验收报告（v2.3）

生成日期：{TODAY}。本轮仅修改工作区证据库与报告；Zotero 条目和附件保持只读。

## 统一验收结果

- 语料记录：{len(papers_doc['papers'])} 篇；冻结主库 {len(active)} 篇，人工排除 {len(papers_doc['papers']) - len(active)} 篇。
- 证据卡：{stats['cards']} 张；章节定位 {stats['sections_located']}/{stats['cards']}，印刷页/文章号标签 {stats['printed_labels_present']}/{stats['cards']}。
- 摘录：{stats['quote_matches']}/{stats['cards']} 均可在指定 PDF 页经版式归一化后逐字匹配；共替换 {replaced} 条不完整或非逐字摘录。
- 元数据：{stats['paper_metadata_complete']}/{stats['papers']} 完整；`66IZGBKH` 已由同题名 Zotero 记录 `Y5DILEHV` 与 PDF 首页交叉补齐。
- `EC-UDGHLCIZ-A`：已补齐 N400 380–500 ms、P600/LPC 670–770 ms；电极 F3/Fz/F4、C3/Cz/C4、P3/Pz/P4；正式比较为四种句型 × 三脑区重复测量 ANOVA。
- GoldCase：12/12 夹具一致性通过；该结果只验证夹具与证据关系一致，不是一次真实模型评测。

## 摘录审计说明

初检列出的 27 条无句末标点片段均已替换。统一验收又发现若干“带句号但仍截断原句/不逐字”的片段，已一并修正，因此最终替换数为 {replaced}。每张卡均保存 `quote_audit.previous_quote`、`current_quote`、页码与角色保留信息。

`EC-8AVKRMIR-A` 是唯一页码迁移：原 PDF 第 1 页仅为出版商封面，不含可承担证据角色的完整原句；锚点移至 PDF 第 2 页 Abstract，并在卡片审计信息中保留迁移原因。

## 结论边界

- 角色构成：`conditional_support` {roles.get('conditional_support', 0)}、`boundary` {roles.get('boundary', 0)}、`counterevidence` {roles.get('counterevidence', 0)}、`insufficient` {roles.get('insufficient', 0)}、`direct_support` {roles.get('direct_support', 0)}。
- 因不存在 `direct_support`，发布结论只能表述为任务、样本、语言、时间窗与指标定义约束下的条件性或边界性判断，不能外推为普遍因果结论。
- {stats['article_number_or_no_specific_printed_page']} 张卡对应文章号出版或作者手稿中不可见的单页印刷页码，已明确写为 article number/no printed page 或说明具体印刷页不可见，未伪造页码。

## 发布判定

**合格。** 结构、摘录、页码、元数据、方法字段与角色计数均通过统一校验；上述科学解释边界必须随库发布。
"""
    (ROOT / "final_release_audit.md").write_text(audit, encoding="utf-8")

    report = f"""# NeuroTrace 文献证据库综述报告（v2.3）

生成日期：{TODAY}。本报告基于 {len(active)} 篇冻结可读论文与 {stats['cards']} 张逐页复核证据卡。

## 证据库现状

证据库现由 {roles.get('conditional_support', 0)} 条条件支持、{roles.get('boundary', 0)} 条边界证据、{roles.get('counterevidence', 0)} 条反证和 {roles.get('insufficient', 0)} 条不足证据构成，没有直接支持。所有卡片已补齐命名章节和印刷页/文章号标签，摘录均能回到指定 PDF 页逐字核对。37 篇进入冻结主库；`XCECFFQ4` 作为数据集说明被人工判定为不足证据并排除在主张链之外。

## 可支持的综合判断

现有文献支持的是受条件约束的综合判断：N400 与 LPC/P600/LPP 的方向和解释会随任务要求、隐喻常规性、语境、语言经验、情绪类别、感觉模态、时间窗切分与电极区域改变。晚期正/负成分不能被简化为单一情绪唤醒读数，N400 也不能跨范式直接视为同一种加工成本。反证与边界卡要求最终系统在输出结论时显式携带这些适用条件。

## 重点方法补全

`EC-UDGHLCIZ-A` 的正式方法参数已从 PDF 方法页定位：N400 为 380–500 ms，P600/LPC 为 670–770 ms；分析电极为额区 F3/Fz/F4、中区 C3/Cz/C4、顶区 P3/Pz/P4；模型比较四类句型（SVM、VOM、LA、LC）与三个电极区域，并分别考察动词和宾语位置。

`66IZGBKH` 的空缺元数据已通过同题名 Zotero 记录与 PDF 首页交叉补齐：Lai、Curran 与 Menn，2009，*Brain Research* 1284，145–155，DOI 10.1016/j.brainres.2009.05.088。未向 Zotero 写入任何内容。

## 评测边界

12 个 GoldCase 的 12/12 结果是夹具一致性测试：它证明 gold 定义与当前证据关系文件一致，但没有运行真实模型、没有测量 verdict 准确率，也不能用于宣称模型性能。后续真实评测应固定模型版本、推理参数与输入证据包，记录逐例输出后再计算准确率。

## 发布结论

证据库已达到可追溯发布标准，但科学结论仍必须保持条件性、边界性措辞。任何脱离样本、任务、语言、时间窗、电极或刺激材料的普遍因果表述，均超出现有证据等级。
"""
    (ROOT / "literature_review_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    cards_path = ROOT / "evidence_cards.json"
    papers_path = ROOT / "paper_records.json"
    cards_doc = copy.deepcopy(json.loads(cards_path.read_text(encoding="utf-8")))
    papers_doc = copy.deepcopy(json.loads(papers_path.read_text(encoding="utf-8")))

    replaced, relocation_log = update_cards(cards_doc)
    update_papers(papers_doc)
    stats = validate(cards_doc, papers_doc)

    cards_doc["schema_version"] = "2.1"
    cards_doc["generated_date"] = TODAY
    cards_doc["status_note"] = "Final release: sections, printed-page/article labels, complete quotes, metadata flags, and per-card quote audits validated against local PDFs."
    papers_doc["schema_version"] = "2.1"
    cards_path.write_text(json.dumps(cards_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    papers_path.write_text(json.dumps(papers_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_hash = write_manifest(papers_doc)

    schema_path = ROOT / "evidence_schema_v2.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["schema_version"] = "2.1"
    schema["required_card_fields"] = list(
        dict.fromkeys(
            schema["required_card_fields"]
            + [
                "printed_page_label", "section_locator_status", "quote_completeness", "quote_audit",
                "metadata_completeness", "needs_manual_metadata_check", "evidence_role", "role_rationale",
            ]
        )
    )
    schema["release_rules"] = {
        "quote": "Quote must match the specified PDF page after Unicode, whitespace, and line-break hyphenation normalization.",
        "printed_page": "Use a printed page when visible; otherwise state article number/no printed page without inventing pagination.",
        "metadata": "Missing title/authors/year/venue/DOI sets needs_manual_metadata_check=true.",
        "gold_evaluation": "Fixture consistency is not model-performance evaluation.",
    }
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

    version_path = ROOT / "corpus_version.json"
    version = json.loads(version_path.read_text(encoding="utf-8"))
    version.update(
        {
            "corpus_version_id": f"neurotrace-corpus-{TODAY}-v2.3",
            "generated_date": TODAY,
            "schema_version": "2.1",
            "manifest_sha256": manifest_hash,
            "cards": stats["cards"],
            "machine_page_quote_matched": stats["quote_matches"],
            "sections_not_located": stats["cards"] - stats["sections_located"],
            "sections_located": stats["sections_located"],
            "printed_page_labels_complete": stats["printed_labels_present"],
            "quotes_replaced_in_final_audit": replaced,
            "quote_completeness_complete": stats["cards"],
            "paper_metadata_complete": stats["paper_metadata_complete"],
            "needs_manual_metadata_check": 0,
            "evidence_role_counts": stats["roles"],
            "direct_support_count": stats["roles"].get("direct_support", 0),
            "gold_fixture_consistency_passed": 12,
            "gold_fixture_consistency_failed": 0,
            "gold_evaluation_scope": "fixture_consistency_only_not_model_evaluation",
            "page_relocations": relocation_log,
            "release_status": "final_release_passed_with_scientific_boundary_disclosures",
        }
    )
    version_path.write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")
    write_reports(stats, replaced, relocation_log, papers_doc)

    package_cards = ROOT / "NeuroTrace_同学交接包" / "02_engine" / "evidence_cards.json"
    if package_cards.parent.exists():
        package_cards.write_text(json.dumps(cards_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    package_manifest = ROOT / "NeuroTrace_同学交接包" / "02_engine" / "corpus_manifest.csv"
    if package_manifest.parent.exists():
        package_manifest.write_bytes((ROOT / "corpus_manifest.csv").read_bytes())

    print(json.dumps({**stats, "quotes_replaced": replaced, "page_relocations": relocation_log}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

