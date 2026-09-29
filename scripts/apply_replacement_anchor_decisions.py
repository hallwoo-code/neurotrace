"""Record the user's review of replacement anchors for three priority cards."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
UPDATES = {
    "EC-8XBDTNCB-A": {
        "pdf_page": 10, "section": "Results, 3.7 LPC window (450–700 ms)",
        "original_quote": "L2 participants with higher emotional resonance capabilities showed a larger LPC congruency effect overall.",
        "chinese_interpretation": "在该新学 L2 伪词的一致性任务中，情绪共鸣能力较高的 L2 参与者呈现更大的 LPC 一致性效应。",
        "observed_finding": "LPC 一致性效应与 L2 情绪共鸣相关；原文进一步限定该增强主要由厌恶伪词条件驱动。",
        "role": "conditional_support", "decision": "A", "note": "用户确认：仅作为特定 L2 学习任务、情绪类别与 LPC 时间窗下的条件支持。",
    },
    "EC-9PIPX6I5-A": {
        "pdf_page": 1, "section": "Abstract",
        "original_quote": "more negative N400 and less positive LPC responses to metaphors compared to literal expressions",
        "chinese_interpretation": "该元分析的总体结果显示：相对字面表达，隐喻引发更负的 N400 与较不正的 LPC。",
        "observed_finding": "22 项研究（N=627）的合成结果支持上述总体模式；具体解释仍受 LPC/P600 窗口与范式异质性限制。",
        "role": "conditional_support", "decision": "A", "note": "用户确认：作为元分析层面的条件支持，不外推为所有隐喻范式的固定模式。",
    },
    "EC-8HE4L22P-A": {
        "pdf_page": 32, "section": "Summary Points",
        "original_quote": "a distributed, multimodal, bi-hemispheric comprehension system that is simultaneously open to linguistic and non-linguistic influences",
        "chinese_interpretation": "N400 所涉理解系统是分布式、多模态且双半球的，并同时开放于语言与非语言影响。",
        "observed_finding": "N400 不能被作为情绪或隐喻的专属指标；其解释需考虑刺激、任务、语境和跨模态信息。",
        "role": "boundary", "decision": "B", "note": "用户确认：作为 N400 非特异性与语境依赖的边界证据。",
    },
}

def main() -> None:
    cards_file = ROOT / "evidence_cards.json"
    cards_doc = json.loads(cards_file.read_text(encoding="utf-8"))
    cards = {x["evidence_id"]: x for x in cards_doc["cards"]}
    for evidence_id, update in UPDATES.items():
        card = cards[evidence_id]
        for field in ["pdf_page", "section", "original_quote", "chinese_interpretation", "observed_finding"]:
            card[field] = update[field]
        card["status"] = "anchor_confirmed"
        card["verification_flag"] = "human_confirmed"
        card["machine_anchor"] = {"matched": True, "method": "user_selected_replacement_anchor", "semantic_alignment": "human_confirmed"}
        card["human_review"] = {"reviewed_on": TODAY, "reviewer": "user", "decision": update["decision"], "assigned_evidence_role": update["role"], "note": update["note"]}
    cards_file.write_text(json.dumps(cards_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    relations_file = ROOT / "evidence_relations.json"
    relations_doc = json.loads(relations_file.read_text(encoding="utf-8"))
    for relation in relations_doc["relations"]:
        if relation["evidence_id"] in UPDATES:
            update = UPDATES[relation["evidence_id"]]
            relation["evidence_role"] = update["role"]
            relation["status"] = "anchor_confirmed"
            relation["manual_review_decision"] = update["decision"]
            relation["conditions_or_reason"] = update["note"]
    relations_file.write_text(json.dumps(relations_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    version_file = ROOT / "corpus_version.json"
    version = json.loads(version_file.read_text(encoding="utf-8"))
    version["human_anchor_confirmed"] = sum(x["status"] == "anchor_confirmed" for x in cards_doc["cards"])
    version["replacement_anchor_update"] = {"date": TODAY, "updated_cards": list(UPDATES), "confirmed": 3}
    version_file.write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")

    report_file = ROOT / "literature_review_report.md"
    report_file.write_text(report_file.read_text(encoding="utf-8") + f"\n\n## 替换锚点人工核验更新（{TODAY}）\n\n三个替换锚点已完成：`8XBDTNCB` 与 `9PIPX6I5` 归为 `conditional_support`，`8HE4L22P` 归为 `boundary`。三个 DemoCase 的现有关系均已完成首轮人工锚点确认。\n", encoding="utf-8")
    print(json.dumps({"updated": len(UPDATES), "human_anchor_confirmed": version["human_anchor_confirmed"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()

