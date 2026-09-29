"""Record review decisions for the five added readable-corpus candidates."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
DECISIONS = {
    "EC-XCECFFQ4-A": ("C", "insufficient", "rejected", "人审确认：数据集说明未提供可进入主张链的直接 ERP 结果；移出冻结主证据库。"),
    "EC-62IAIJLF-A": ("A", "conditional_support", "anchor_confirmed", "人审确认：仅作为越南语—汉语双语代码转换隐喻范式下的条件支持。"),
    "EC-4YRMKG3I-A": ("A", "conditional_support", "anchor_confirmed", "人审确认：仅作为 L2 新颖隐喻、支持性语境与特定时间窗下的条件支持。"),
    "EC-UDGHLCIZ-A": ("B", "boundary", "anchor_confirmed", "人审确认：作为不同隐喻句法类型对应不同加工机制的边界证据。"),
    "EC-8AVKRMIR-A": ("B", "boundary", "anchor_confirmed", "人审确认：作为言语与图文隐喻晚期加工差异的模态边界证据。"),
}

def main() -> None:
    cards_file = ROOT / "evidence_cards.json"
    cards_doc = json.loads(cards_file.read_text(encoding="utf-8"))
    cards = {x["evidence_id"]: x for x in cards_doc["cards"]}
    for evidence_id, (decision, role, status, note) in DECISIONS.items():
        card = cards[evidence_id]
        card["status"] = status
        card["verification_flag"] = "human_confirmed" if status == "anchor_confirmed" else "human_rejected"
        card["human_review"] = {"reviewed_on": TODAY, "reviewer": "user", "decision": decision, "assigned_evidence_role": role, "note": note}
    cards_file.write_text(json.dumps(cards_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    papers_file = ROOT / "paper_records.json"
    papers_doc = json.loads(papers_file.read_text(encoding="utf-8"))
    for paper in papers_doc["papers"]:
        if paper["zotero_item_key"] == "XCECFFQ4":
            paper["demo_suitability"] = "excluded"
            paper["selection_reason"] = "人审排除：EEG 数据集说明，不作为本项目的论文级主证据。"
    papers_file.write_text(json.dumps(papers_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    version_file = ROOT / "corpus_version.json"
    version = json.loads(version_file.read_text(encoding="utf-8"))
    version["human_anchor_confirmed"] = sum(x["status"] == "anchor_confirmed" for x in cards_doc["cards"])
    version["new_candidate_review_update"] = {"date": TODAY, "reviewed": len(DECISIONS), "confirmed": 4, "rejected": 1, "replacement_required_for_frozen_count": 1}
    version_file.write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(version["new_candidate_review_update"], ensure_ascii=False))

if __name__ == "__main__":
    main()

