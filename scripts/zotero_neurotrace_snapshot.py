from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


BASE = "http://127.0.0.1:23119/api/users/0"
ROOT_COLLECTIONS = {
    "collection": "TIGIF3TV",
    "collection2": "M2D9DVST",
    "Metaph": "F5CNA6N5",
    "paper1": "UZ4QRTAA",
}
OUT = Path(__file__).resolve().parents[1] / ".neurotrace_work"


def request(path: str, *, accept: str = "application/json"):
    req = urllib.request.Request(
        BASE + path,
        headers={"Zotero-API-Version": "3", "Accept": accept},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response, body


def get_json(path: str):
    response, body = request(path)
    if "json" not in (response.headers.get("Content-Type") or ""):
        raise RuntimeError(f"Expected JSON from {path}")
    return json.loads(body)


def paged(path: str):
    separator = "&" if "?" in path else "?"
    start = 0
    rows = []
    while True:
        response, body = request(f"{path}{separator}limit=100&start={start}")
        chunk = json.loads(body)
        rows.extend(chunk)
        total_raw = response.headers.get("Total-Results")
        total = int(total_raw) if total_raw and total_raw.isdigit() else None
        if not chunk or len(chunk) < 100 or (total is not None and len(rows) >= total):
            return rows
        start += len(chunk)


def creators(data: dict) -> list[str]:
    values = []
    for creator in data.get("creators", []):
        name = creator.get("name") or " ".join(
            x for x in (creator.get("firstName"), creator.get("lastName")) if x
        )
        if name:
            values.append(name)
    return values


def bibtex_key(item_key: str) -> str | None:
    query = urllib.parse.urlencode(
        {"itemKey": item_key, "format": "bibtex", "limit": 100}
    )
    _, body = request(f"/items?{query}", accept="application/x-bibtex")
    match = re.search(r"@\w+\s*\{\s*([^,\s]+)", body)
    return match.group(1) if match else None


def main() -> int:
    OUT.mkdir(exist_ok=True)
    collections = paged("/collections")
    by_key = {row["key"]: row for row in collections}
    children = defaultdict(list)
    for row in collections:
        parent = row.get("data", {}).get("parentCollection")
        if parent:
            children[parent].append(row["key"])

    target_keys = set(ROOT_COLLECTIONS.values())
    queue = [ROOT_COLLECTIONS["Metaph"]]
    while queue:
        parent = queue.pop()
        for child in children.get(parent, []):
            if child not in target_keys:
                target_keys.add(child)
                queue.append(child)

    collection_items = {}
    item_sources = defaultdict(list)
    items_by_key = {}
    for collection_key in sorted(target_keys):
        rows = paged(f"/collections/{collection_key}/items/top?sort=title&direction=asc")
        collection_items[collection_key] = [row["key"] for row in rows]
        label = by_key[collection_key]["data"]["name"]
        for row in rows:
            items_by_key[row["key"]] = row
            item_sources[row["key"]].append(label)

    attachment_type_counts = Counter()
    records = []
    for index, item_key in enumerate(sorted(items_by_key)):
        item = items_by_key[item_key]
        data = item.get("data", {})
        child_rows = paged(f"/items/{item_key}/children?sort=title&direction=asc")
        attachments = []
        for child in child_rows:
            cdata = child.get("data", {})
            if cdata.get("itemType") != "attachment":
                continue
            content_type = cdata.get("contentType") or ""
            attachment_type_counts[content_type] += 1
            attachments.append(
                {
                    "key": child.get("key"),
                    "title": cdata.get("title"),
                    "contentType": content_type,
                    "linkMode": cdata.get("linkMode"),
                    "path": cdata.get("path"),
                    "url": cdata.get("url"),
                    "filename": cdata.get("filename"),
                }
            )
        records.append(
            {
                "zotero_item_key": item_key,
                "bibtex_key": bibtex_key(item_key),
                "itemType": data.get("itemType"),
                "title": data.get("title"),
                "authors": creators(data),
                "date": data.get("date"),
                "publicationTitle": data.get("publicationTitle")
                or data.get("conferenceName")
                or data.get("proceedingsTitle"),
                "DOI": data.get("DOI"),
                "abstractNote": data.get("abstractNote"),
                "tags": [t.get("tag") for t in data.get("tags", []) if t.get("tag")],
                "collections": item_sources[item_key],
                "extra": data.get("extra"),
                "url": data.get("url"),
                "attachments": attachments,
            }
        )
        if (index + 1) % 50 == 0:
            print(f"Fetched {index + 1}/{len(items_by_key)} records", file=sys.stderr)

    summary = {
        "root_collections": ROOT_COLLECTIONS,
        "target_collection_keys": sorted(target_keys),
        "target_collections": [
            {
                "key": key,
                "name": by_key[key]["data"]["name"],
                "parentCollection": by_key[key]["data"].get("parentCollection"),
                "top_item_count": len(collection_items[key]),
            }
            for key in sorted(target_keys)
        ],
        "unique_top_items": len(records),
        "item_type_counts": dict(Counter(r["itemType"] for r in records)),
        "attachment_type_counts": dict(attachment_type_counts),
        "items_with_pdf_attachment": sum(
            any(a["contentType"] == "application/pdf" for a in r["attachments"])
            for r in records
        ),
    }
    (OUT / "zotero_target_records.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "zotero_target_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

