import json
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[1]
payload = json.loads((root / "evidence_cards.json").read_text(encoding="utf-8"))
cards = payload["cards"]
for card in cards:
    print(
        "\t".join(
            [
                card.get("evidence_id", ""),
                card.get("zotero_item_key", ""),
                f"p{card.get('pdf_page', '')}",
                f"sec={card.get('section', '')}",
                f"loc={card.get('section_locator_status', '')}",
                f"print={card.get('printed_page_label', '')}",
                f"role={card.get('evidence_role', '')}",
                f"quote={card.get('original_quote', '')}",
            ]
        )
    )

