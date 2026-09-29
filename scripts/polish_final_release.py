"""Polish known PDF extraction artifacts and rerun the final release checks."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".neurotrace_work" / "pages"
sys.stdout.reconfigure(encoding="utf-8")


CLEAN_QUOTES = {
    "EC-WRJA7MMA-A-B": "Findings indicate that stimulus emotionality and task demand co-determine the extent to which emotion- and semantic-related neural resources are recruited during metaphor comprehension.",
    "EC-FM494I2T-A-B": "The current study leveraged the LPP to index emotional reactivity and regulation among an older adult sample who reported high or low emotional well-being (high WB group and low WB group, respectively).",
    "EC-8HE4L22P-A-B": "N400s thus are modality-dependent but not modality-specific (perhaps marking a unimodal to amodal interface; see section on theory) – an electrophysiological marker of processing in a distributed semantic memory system.",
    "EC-JH5U3XYU-A": "In N400, results revealed that UT and LT elicited significantly more negative waveforms than MT in both primes.",
    "EC-F84Z4U84-A": "Explorative analyses in a later time window (500–900 ms) revealed that ERP activity in this phase indexes appropriateness (nonsense > creative = common).",
    "EC-2CC2HQYF-A": "ERPs measured from 300 to 500 msec after the onset of the sentence-final words differed as a function of metaphoricity: Literal endings elicited the smallest N400, metaphors the largest N400, whereas literal mappings elicited an N400 of intermediate amplitude.",
}


def source_text(key: str, page_number: int) -> str:
    pages = json.loads((PAGES / f"{key}.json").read_text(encoding="utf-8"))
    return next(page["text"] for page in pages if page["pdf_page"] == page_number)


def comparison_form(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").replace("\x00", "").replace("\u00ad", "")
    replacements = {
        "/four.tnum/zero.tnum/zero.tnum": "400",
        "4creative 1⁄4common": "> creative = common",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # PDF line wrapping and font extraction can add/drop spaces or discretionary hyphens.
    return re.sub(r"[\s\-‐‑‒–—]+", "", text)


cards_path = ROOT / "evidence_cards.json"
doc = json.loads(cards_path.read_text(encoding="utf-8"))
for card in doc["cards"]:
    evidence_id = card["evidence_id"]
    if evidence_id in CLEAN_QUOTES:
        card["original_quote"] = CLEAN_QUOTES[evidence_id]
        card["quote_audit"]["current_quote"] = CLEAN_QUOTES[evidence_id]
        card["quote_audit"]["normalization_note"] = "Corrected PDF extraction-only spacing, discretionary hyphenation, or encoded mathematical glyphs; lexical content and evidence role are unchanged."
    if evidence_id == "EC-UDGHLCIZ-A":
        card["time_window"] = "N400 380–500 ms; P600/LPC 670–770 ms; epoch −200 to 800 ms with a 200-ms prestimulus baseline."
        card["electrode_region"] = "Frontal F3/Fz/F4; central C3/Cz/C4; parietal P3/Pz/P4."
        card["condition_comparison"] = "4 sentence types (SVM, VOM, LA, LC) × 3 electrode areas (frontal, central, parietal) repeated-measures ANOVA, evaluated for verb and object targets."
        card["structured_extraction_status"] = "complete"
        card["limitations_boundary_confounds"] = "Mandarin student sample; syntactic position is confounded with the location of literal–metaphorical conflict; component windows and effects are specific to the four sentence types and verb/object target positions."
    source = comparison_form(source_text(card["zotero_item_key"], card["pdf_page"]))
    quote = comparison_form(card["original_quote"])
    if quote not in source:
        raise ValueError(f"quote mismatch after PDF-layout normalization: {evidence_id}")
    if not re.search(r"[.!?;][”'\)]?$", card["original_quote"]):
        raise ValueError(f"incomplete quote: {evidence_id}")
    card["quote_audit"]["match_status"] = "verbatim_match_after_layout_and_known_pdf_symbol_normalization"

cards_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "NeuroTrace_同学交接包" / "02_engine" / "evidence_cards.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
)

udg = next(card for card in doc["cards"] if card["evidence_id"] == "EC-UDGHLCIZ-A")
print(
    json.dumps(
        {
            "cards_validated": len(doc["cards"]),
            "cleaned_pdf_extraction_artifacts": len(CLEAN_QUOTES),
            "udghlciz": {
                "time_window": udg["time_window"],
                "electrode_region": udg["electrode_region"],
                "condition_comparison": udg["condition_comparison"],
            },
        },
        ensure_ascii=False,
        indent=2,
    )
)

