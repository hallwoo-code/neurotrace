"""Show header/footer lines likely to contain printed or article page labels."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[1]
cards = json.loads((root / "evidence_cards.json").read_text(encoding="utf-8"))["cards"]
seen: set[tuple[str, int]] = set()
for card in cards:
    pair = (card["zotero_item_key"], card["pdf_page"])
    if pair in seen:
        continue
    seen.add(pair)
    pages = json.loads((root / ".neurotrace_work" / "pages" / f"{pair[0]}.json").read_text(encoding="utf-8"))
    text = next(page["text"] for page in pages if page["pdf_page"] == pair[1])
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    edge = lines[:12] + lines[-14:]
    likely = [
        line
        for line in edge
        if re.search(r"\b(page|article|volume|vol\.|frontiers|doi|\d{3}\s*[–-]\s*\d{3}|\b\d{1,3}\b)", line, re.I)
    ]
    print(f"{pair[0]}\tp{pair[1]}\t" + " || ".join(likely[-8:]))

