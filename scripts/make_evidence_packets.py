from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".neurotrace_work"


def sentences(text: str):
    cleaned = re.sub(r"\s+", " ", text.replace("\u00ad", ""))
    for part in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", cleaned):
        part = part.strip()
        if 35 <= len(part) <= 900:
            yield part


PATTERNS = {
    "sample": re.compile(r"\b(participants?|subjects?|sample|\bn\s*=|right-handed|native speakers?|aged?)\b", re.I),
    "task": re.compile(r"\b(task|paradigm|presented|viewed|read|judg|decision|priming|reapprais|congru|experiment)\w*\b", re.I),
    "erp": re.compile(r"\b(N400|LPC|LPP|P300|P3|P600|late positiv|late negativ|EEG|ERP|electrode|centro|pariet|frontal|\d{3}\s*[-–]\s*\d{3}\s*ms)\b", re.I),
    "result": re.compile(r"\b(result|show|reveal|found|elicited|significant|effect|modulat|larger|smaller|greater|more negative|more positive|amplitude)\w*\b", re.I),
    "limit": re.compile(r"\b(limit|however|caution|cannot|unclear|future|inconsistent|heterogen|only|not significant|did not|failed to)\w*\b", re.I),
}


def score(sentence: str, category: str) -> int:
    value = 3 * bool(PATTERNS[category].search(sentence))
    value += 2 * bool(PATTERNS["erp"].search(sentence))
    value += 2 * bool(PATTERNS["result"].search(sentence))
    value += bool(re.search(r"\b(emotion|emotional|arousal|valence|metaphor|semantic|context)\w*\b", sentence, re.I))
    value += bool(re.search(r"\b\d{2,3}\s*[-–]\s*\d{2,4}\s*ms\b", sentence, re.I))
    return value


def select(rows, category: str, limit: int):
    candidates = []
    seen = set()
    for row in rows:
        for sentence in sentences(row["text"]):
            if not PATTERNS[category].search(sentence):
                continue
            normalized = re.sub(r"\W+", " ", sentence.lower())[:180]
            if normalized in seen:
                continue
            seen.add(normalized)
            candidates.append((score(sentence, category), row["pdf_page"], sentence))
    candidates.sort(key=lambda item: (-item[0], item[1], len(item[2])))
    return candidates[:limit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True, choices=(1, 2, 3, 4))
    args = parser.parse_args()
    state = json.loads((WORK / "selection_state.json").read_text(encoding="utf-8"))
    readable = [r for r in state if r["demo_suitability"] != "excluded" and r["pdf_readable"]]
    batches = [readable[:9], readable[9:17], readable[17:25], readable[25:33]]
    batch = batches[args.batch - 1]
    lines = [f"# Batch {args.batch} evidence packet", ""]
    for record in batch:
        key = record["zotero_item_key"]
        rows = json.loads((WORK / "pages" / f"{key}.json").read_text(encoding="utf-8"))
        lines.extend([
            f"## {key} — {record['title']}",
            "",
            f"Authors: {', '.join(record.get('authors') or [])}",
            f"Date/Venue: {record.get('date') or ''}; {record.get('publicationTitle') or ''}",
            f"Topics: {record['research_topic_tags']}",
            "",
        ])
        for category, limit in (("sample", 3), ("task", 3), ("erp", 5), ("result", 7), ("limit", 3)):
            lines.append(f"### {category}")
            for points, page, sentence in select(rows, category, limit):
                lines.append(f"- PDF p.{page} [score {points}]: {sentence}")
            lines.append("")
    out = WORK / f"batch_{args.batch}_packet.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"batch": args.batch, "papers": len(batch), "path": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

