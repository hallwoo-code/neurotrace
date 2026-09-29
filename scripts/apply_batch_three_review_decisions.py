"""Apply user decisions for the third manual-review batch."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
DECISIONS = {
    "EC-5PICEPUM-A-B": ("B", "boundary"), "EC-PBD8NAYC-A": ("B", "boundary"),
    "EC-PKL57JRG-A": ("E", "counterevidence"), "EC-54HS2AZY-A": ("A", "conditional_support"),
    "EC-M256T5QC-A": ("A", "conditional_support"), "EC-P9Y77QL6-A": ("B", "boundary"),
    "EC-F84Z4U84-A": ("A", "conditional_support"), "EC-TMFE3UF6-A": ("E", "counterevidence"),
    "EC-2CC2HQYF-A": ("A", "conditional_support"),
}

def main() -> None:
    path = ROOT / "evidence_cards.json"; doc = json.loads(path.read_text(encoding="utf-8")); cards = {x["evidence_id"]: x for x in doc["cards"]}
    for evidence_id, (decision, role) in DECISIONS.items():
        card = cards[evidence_id]
        card["status"] = "anchor_confirmed"; card["verification_flag"] = "human_confirmed"
        card["human_review"] = {"reviewed_on": TODAY, "reviewer": "user", "decision": decision, "assigned_evidence_role": role, "note": "用户人工复核确认；角色仅适用于所述任务、样本、比较和时间窗。"}
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    version_path = ROOT / "corpus_version.json"; version = json.loads(version_path.read_text(encoding="utf-8")); version["human_anchor_confirmed"] = sum(x["status"] == "anchor_confirmed" for x in doc["cards"]); version["batch_three_manual_review"] = {"date": TODAY, "confirmed": len(DECISIONS), "roles": {"conditional_support": 3, "boundary": 3, "counterevidence": 2, "duplicate_pending": ["EC-M256T5QC-A"]}}; version_path.write_text(json.dumps(version, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"updated":len(DECISIONS),"confirmed":version["human_anchor_confirmed"]},ensure_ascii=False))

if __name__ == "__main__": main()

