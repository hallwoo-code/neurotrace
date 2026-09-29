"""Read-only acceptance checks for the NeuroTrace v2.3 release artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".neurotrace_work" / "pages"


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_text(key: str, page_number: int) -> str:
    pages = json.loads((PAGES / f"{key}.json").read_text(encoding="utf-8"))
    return next(page["text"] for page in pages if page["pdf_page"] == page_number)


def comparison_form(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").replace("\x00", "").replace("\u00ad", "")
    text = text.replace("/four.tnum/zero.tnum/zero.tnum", "400")
    text = text.replace("4creative 1⁄4common", "> creative = common")
    return re.sub(r"[\s\-‐‑‒–—]+", "", text)


cards_doc = load("evidence_cards.json")
papers_doc = load("paper_records.json")
schema = load("evidence_schema_v2.json")
version = load("corpus_version.json")
gold = load("gold_case_evaluation.json")
cards = cards_doc["cards"]
papers = papers_doc["papers"]
errors: list[str] = []

if len(cards) != 48 or len({card["evidence_id"] for card in cards}) != 48:
    errors.append("evidence card count/uniqueness")
if len(papers) != 38 or len({paper["zotero_item_key"] for paper in papers}) != 38:
    errors.append("paper count/uniqueness")

for card in cards:
    missing = [field for field in schema["required_card_fields"] if field not in card]
    if missing:
        errors.append(f"{card['evidence_id']}:missing:{','.join(missing)}")
    if card.get("section_locator_status") != "source_located" or not card.get("section"):
        errors.append(f"{card['evidence_id']}:section")
    if not card.get("printed_page_label"):
        errors.append(f"{card['evidence_id']}:printed_page")
    if card.get("quote_completeness") not in {"complete_sentence", "complete_list_item"}:
        errors.append(f"{card['evidence_id']}:quote_completeness")
    if card.get("needs_manual_metadata_check"):
        errors.append(f"{card['evidence_id']}:metadata_flag")
    source = comparison_form(source_text(card["zotero_item_key"], card["pdf_page"]))
    if comparison_form(card["original_quote"]) not in source:
        errors.append(f"{card['evidence_id']}:quote_mismatch")
    if card["quote_audit"]["evidence_role_preserved"] != card["evidence_role"]:
        errors.append(f"{card['evidence_id']}:role_changed")

for paper in papers:
    if paper.get("metadata_completeness") != "complete" or paper.get("needs_manual_metadata_check"):
        errors.append(f"{paper['zotero_item_key']}:metadata")
    for field in ("title", "authors", "year", "venue", "doi"):
        if not paper.get(field):
            errors.append(f"{paper['zotero_item_key']}:missing_{field}")

with (ROOT / "corpus_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
    manifest = list(csv.DictReader(handle))
if len(manifest) != 38:
    errors.append("manifest count")
if sha256(ROOT / "corpus_manifest.csv") != version.get("manifest_sha256"):
    errors.append("manifest hash")

roles = Counter(card["evidence_role"] for card in cards)
expected_roles = {"conditional_support": 22, "boundary": 22, "counterevidence": 3, "insufficient": 1}
if dict(roles) != expected_roles:
    errors.append(f"role counts:{dict(roles)}")
if version.get("direct_support_count") != 0:
    errors.append("direct support disclosure")
if gold.get("passed") != 12 or gold.get("failed") != 0 or gold.get("evaluation_type") != "fixture_consistency_validation":
    errors.append("gold fixture scope")

paper_66 = next(paper for paper in papers if paper["zotero_item_key"] == "66IZGBKH")
if (paper_66["year"], paper_66["venue"], paper_66["doi"]) != (
    "2009", "Brain Research", "10.1016/j.brainres.2009.05.088"
):
    errors.append("66IZGBKH metadata")

udg = next(card for card in cards if card["evidence_id"] == "EC-UDGHLCIZ-A")
for value in ("380–500", "670–770", "F3/Fz/F4", "C3/Cz/C4", "P3/Pz/P4", "SVM", "VOM", "LA", "LC"):
    if value not in " ".join([udg["time_window"], udg["electrode_region"], udg["condition_comparison"]]):
        errors.append(f"UDGHLCIZ missing:{value}")

for report_name in ("final_release_audit.md", "literature_review_report.md"):
    report = (ROOT / report_name).read_text(encoding="utf-8")
    for disclosure in ("direct_support", "夹具一致性", "不是一次真实模型评测"):
        if disclosure not in report:
            errors.append(f"{report_name}:disclosure:{disclosure}")

package_cards = ROOT / "NeuroTrace_同学交接包" / "02_engine" / "evidence_cards.json"
package_manifest = ROOT / "NeuroTrace_同学交接包" / "02_engine" / "corpus_manifest.csv"
if sha256(package_cards) != sha256(ROOT / "evidence_cards.json"):
    errors.append("handoff evidence_cards sync")
if sha256(package_manifest) != sha256(ROOT / "corpus_manifest.csv"):
    errors.append("handoff manifest sync")

result = {
    "release": "pass" if not errors else "fail",
    "cards": len(cards),
    "sections_located": sum(card["section_locator_status"] == "source_located" for card in cards),
    "printed_labels": sum(bool(card["printed_page_label"]) for card in cards),
    "quote_matches": len(cards) - sum(error.endswith(":quote_mismatch") for error in errors),
    "complete_paper_metadata": sum(paper["metadata_completeness"] == "complete" for paper in papers),
    "role_counts": dict(roles),
    "gold_fixture_passed": gold.get("passed"),
    "gold_scope": gold.get("evaluation_type"),
    "errors": errors,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)

