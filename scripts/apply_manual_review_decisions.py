"""Apply the user's manual-review decisions to the v2 NeuroTrace corpus."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()

# A = conditional support, B = boundary, D = replace anchor before judgement.
DECISIONS = {
    "EC-WRJA7MMA-A": ("A", "conditional_support"),
    "EC-8XBDTNCB-A": ("D", "insufficient"),
    "EC-GYCYN7VH-A": ("B", "boundary"),
    "EC-9473VCG3-A": ("B", "boundary"),
    "EC-5PICEPUM-A": ("B", "boundary"),
    "EC-PFPR5ENP-A": ("B", "boundary"),
    "EC-FM494I2T-A": ("A", "conditional_support"),
    "EC-ATKC5SQC-A": ("B", "boundary"),
    "EC-9PIPX6I5-A": ("D", "insufficient"),
    "EC-ZL2RBLSC-A": ("A", "conditional_support"),
    "EC-8HE4L22P-A": ("D", "insufficient"),
    "EC-UH4G7YZA-A": ("A", "conditional_support"),
}

def main() -> None:
    cards_path = ROOT / "evidence_cards.json"
    cards_doc = json.loads(cards_path.read_text(encoding="utf-8"))
    cards = {card["evidence_id"]: card for card in cards_doc["cards"]}
    for evidence_id, (decision, role) in DECISIONS.items():
        card = cards[evidence_id]
        if decision in {"A", "B"}:
            card["status"] = "anchor_confirmed"
            card["verification_flag"] = "human_confirmed"
            note = "用户人工复核：确认条件支持。" if decision == "A" else "用户人工复核：确认边界证据。"
        else:
            card["status"] = "needs_manual_check"
            card["verification_flag"] = "replace_anchor_required"
            note = "用户人工复核：当前摘录不适合定案；须替换完整、语义自足的原文锚点。"
        card["human_review"] = {"reviewed_on": TODAY, "reviewer": "user", "decision": decision, "assigned_evidence_role": role, "note": note}
    cards_doc["status_note"] = "Cards with human_review are user-reviewed. D decisions retain needs_manual_check until a replacement anchor is reviewed."
    cards_path.write_text(json.dumps(cards_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    rel_path = ROOT / "evidence_relations.json"
    rel_doc = json.loads(rel_path.read_text(encoding="utf-8"))
    for relation in rel_doc["relations"]:
        if relation["evidence_id"] in DECISIONS:
            decision, role = DECISIONS[relation["evidence_id"]]
            relation["evidence_role"] = role
            relation["status"] = "anchor_confirmed" if decision in {"A", "B"} else "needs_manual_check"
            relation["manual_review_decision"] = decision
    rel_path.write_text(json.dumps(rel_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    version_path = ROOT / "corpus_version.json"
    version = json.loads(version_path.read_text(encoding="utf-8"))
    version["human_anchor_confirmed"] = sum(card["status"] == "anchor_confirmed" for card in cards_doc["cards"])
    version["manual_review_update"] = {"date": TODAY, "reviewed_priority_anchors": len(DECISIONS), "confirmed": sum(d in {"A", "B"} for d, _ in DECISIONS.values()), "replacement_required": sum(d == "D" for d, _ in DECISIONS.values())}
    version_path.write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")

    queue = f"""# NeuroTrace 人工核验队列（v2，已处理首轮）

首轮用户人工判断日期：{TODAY}。12 个 P0 锚点中，9 个已确认（4 个 `conditional_support`、5 个 `boundary`），3 个必须换锚点后再判。

## P0：必须替换原文锚点

1. `EC-8XBDTNCB-A` — 当前摘录从统计量中段开始且结尾截断。请在 p.10 定位包含“高情绪共鸣 L2 参与者 + LPC 一致性效应 + 统计模型/条件”的完整句；同时确认 N400 是否只是无调节而非无效应。
2. `EC-9PIPX6I5-A` — 当前摘录只说明纳入 22 项研究（N=627），并不支持任何最终方向或调节判断。请从结果/讨论定位完整句：总效应方向、N400 与 LPC/P600 的差异，以及任务/常规性调节。
3. `EC-8HE4L22P-A` — 当前摘录混入作者信息和摘要开头。请从正文定位 N400 的理论边界句：N400 与意义加工相关，但不能被当作情绪或隐喻的特异指标。

## 已确认的 P0 判断

- `conditional_support`：`EC-WRJA7MMA-A`、`EC-FM494I2T-A`、`EC-ZL2RBLSC-A`、`EC-UH4G7YZA-A`
- `boundary`：`EC-GYCYN7VH-A`、`EC-9473VCG3-A`、`EC-5PICEPUM-A`、`EC-PFPR5ENP-A`、`EC-ATKC5SQC-A`

## P1：下一轮

- 核对 10 篇核心文献的 B 卡，确认其章节归属以及是否真正构成限制条件。
- 核对 `NT-M256T5QC` 与 `NT-KGUAISW6` 是否共享样本或材料；未排除重叠前，不得把它们作为独立重复证据累计。
- 扩展池的 5 篇缺 PDF 条目只保留元数据，补件前不进入证据关系。
"""
    (ROOT / "manual_review_queue.md").write_text(queue, encoding="utf-8")
    report_path = ROOT / "literature_review_report.md"
    report = report_path.read_text(encoding="utf-8")
    report += f"\n\n## 首轮人工核验更新（{TODAY}）\n\n用户已判断 12 个 P0 锚点：9 个升级为 `anchor_confirmed`，其中 4 个为 `conditional_support`、5 个为 `boundary`；3 个（`8XBDTNCB`、`9PIPX6I5`、`8HE4L22P`）因摘录不完整或不适合作为主张锚点，保留为 `needs_manual_check` 并进入换锚点队列。\n"
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(version["manual_review_update"], ensure_ascii=False))

if __name__ == "__main__":
    main()

