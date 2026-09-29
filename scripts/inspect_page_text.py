"""Print a source page or compact text around a search phrase."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[1]
key = sys.argv[1]
page_number = int(sys.argv[2])
query = " ".join(sys.argv[3:]).strip()
pages = json.loads((root / ".neurotrace_work" / "pages" / f"{key}.json").read_text(encoding="utf-8"))
text = next(page["text"] for page in pages if page["pdf_page"] == page_number)
if not query:
    print(text)
else:
    normalized = re.sub(r"\s+", " ", text)
    match = re.search(re.escape(query), normalized, flags=re.IGNORECASE)
    if not match:
        tokens = query.split()
        for width in range(min(6, len(tokens)), 1, -1):
            probe = " ".join(tokens[:width])
            match = re.search(re.escape(probe), normalized, flags=re.IGNORECASE)
            if match:
                break
    if match:
        print(normalized[max(0, match.start() - 900) : min(len(normalized), match.end() + 1400)])
    else:
        print(normalized[:2500])

