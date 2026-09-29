import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[1]
papers = json.loads((root / "paper_records.json").read_text(encoding="utf-8"))["papers"]
requested = set(sys.argv[1:])
for paper in papers:
    if not requested or paper["zotero_item_key"] in requested:
        print(json.dumps(paper, ensure_ascii=False))

