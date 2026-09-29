"""Read publication pagination metadata from the Zotero local API."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:23119/api/users/0/items"
sys.stdout.reconfigure(encoding="utf-8")


papers = json.loads((ROOT / "paper_records.json").read_text(encoding="utf-8"))["papers"]
keys = [paper["zotero_item_key"] for paper in papers]
keys.append("Y5DILEHV")
for key in keys:
    request = urllib.request.Request(
        f"{BASE}/{key}", headers={"Zotero-API-Version": "3", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)["data"]
    print(
        json.dumps(
            {
                "key": key,
                "date": data.get("date"),
                "publicationTitle": data.get("publicationTitle"),
                "volume": data.get("volume"),
                "issue": data.get("issue"),
                "pages": data.get("pages"),
                "articleNumber": data.get("articleNumber"),
                "DOI": data.get("DOI"),
            },
            ensure_ascii=False,
        )
    )

