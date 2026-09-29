"""Show the best complete-sentence candidates for truncated evidence quotes."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"(?<=\w)-\s+(?=\w)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def sentences(text: str) -> list[str]:
    normalized = normalize(text)
    return [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])", normalized)
        if 5 <= len(item.split()) <= 90
    ]


def terms(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9'-]+", normalize(text))
        if len(token) >= 4
    }


cards = json.loads((ROOT / "evidence_cards.json").read_text(encoding="utf-8"))["cards"]
requested = set(sys.argv[1:])
for card in cards:
    quote = card["original_quote"]
    if re.search(r"[.!?][”'\)]?$", quote):
        continue
    if requested and card["evidence_id"] not in requested and card["zotero_item_key"] not in requested:
        continue
    pages = json.loads((ROOT / ".neurotrace_work" / "pages" / f"{card['zotero_item_key']}.json").read_text(encoding="utf-8"))
    page = next(row["text"] for row in pages if row["pdf_page"] == card["pdf_page"])
    qterms = terms(quote)
    ranked = sorted(
        sentences(page),
        key=lambda item: (len(qterms & terms(item)), -abs(len(item.split()) - len(quote.split()))),
        reverse=True,
    )
    print(json.dumps({"id": card["evidence_id"], "candidates": ranked[:3]}, ensure_ascii=False))

