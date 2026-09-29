from __future__ import annotations

import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".neurotrace_work"
RAW = WORK / "zotero_target_records.json"
BASE = "http://127.0.0.1:23119/api/users/0"

# Selection is intentionally frozen and ordered for batching. Duplicate Zotero records
# were collapsed before this list was made, preferring complete metadata + readable PDF.
SELECTION = [
    ("WRJA7MMA", "core_demo", "emotion;metaphor;N400;late positivity;task demand", "Directly tests whether stimulus emotionality and task demands change metaphor ERP effects."),
    ("8XBDTNCB", "core_demo", "emotional resonance;L2;N400;LPC;congruency", "Direct N400/LPC evidence with an individual-difference measure of emotional resonance."),
    ("FM494I2T", "core_demo", "emotion regulation;LPP;older adults;reappraisal", "Direct LPP evidence and a strong population boundary for age and well-being."),
    ("5PICEPUM", "core_demo", "emotional intensity;LPP;visual attention", "Mechanistic test of what emotion-related LPP amplitude does and does not imply."),
    ("PFPR5ENP", "core_demo", "P300;LPP;context updating;memory", "Critical synthesis distinguishing LPP from a simple arousal readout."),
    ("9473VCG3", "core_demo", "emotion words;valence;arousal;ERP;review", "Maps valence/arousal interactions and heterogeneity across emotion-word ERP studies."),
    ("ATKC5SQC", "core_demo", "emotion;emotion regulation;ERP;review", "Integrative review for component and paradigm boundaries."),
    ("9PIPX6I5", "core_demo", "metaphor;N400;LPC;P600;meta-analysis", "Cross-study estimate and moderator analysis for N400 and LPC/P600 metaphor effects."),
    ("ZL2RBLSC", "core_demo", "metaphor conventionalization;N400;LPC;learning", "Within-study evidence that exposure/meaning explanation changes N400 and LPC."),
    ("8HE4L22P", "core_demo", "N400;semantic processing;review", "Foundational source for interpreting N400 without reducing it to emotion."),
    ("PBD8NAYC", "corpus", "metaphor;emotional engagement;fMRI;arousal", "Useful conceptual boundary: emotional engagement evidence is hemodynamic, not ERP."),
    ("GYCYN7VH", "corpus", "affective priming;semantic pain;ERP;N400", "Tests affective context and semantic pain with ERP."),
    ("PKL57JRG", "corpus", "reappraisal;LPP;generalization;negative pictures", "Tests whether LPP regulation effects generalize to novel stimuli."),
    ("54HS2AZY", "corpus", "olfaction;emotion regulation;LPP;positive stimuli", "Adds a sensory-modality boundary to LPP emotion-regulation evidence."),
    ("IRH47UG6", "corpus", "bilingualism;emotion;systematic review;neurolinguistics", "Summarizes population/language heterogeneity relevant to emotional resonance."),
    ("JH5U3XYU", "corpus", "Chinese metaphor;N400;late stage;priming", "Separates early semantic access from later metaphor processing."),
    ("M256T5QC", "corpus", "scientific metaphor;bilingual;N400;LPC", "Directly reports N400 and LPC windows across L1/L2 scientific metaphors."),
    ("KGUAISW6", "corpus", "scientific metaphor;bilingual;N400;LPC", "Related bilingual scientific-metaphor ERP evidence for replication/consistency checking."),
    ("P9Y77QL6", "corpus", "novel metaphor;creativity;N400;late component", "Links graded semantic novelty to N400 and later integration."),
    ("F84Z4U84", "corpus", "creative uses;N400;late component;judgment task", "Task variant for testing whether late components generalize beyond metaphor."),
    ("TMFE3UF6", "corpus", "novel metaphor;creativity;N400;late component;replication", "Replication/extension evidence with individual differences."),
    ("2CC2HQYF", "corpus", "metaphor;conceptual integration;N400;posterior positivity", "Classic graded N400 plus posterior positivity result."),
    ("66IZGBKH", "corpus", "conventional metaphor;novel metaphor;N400;P600", "Classic comparison of conventional and novel metaphor processing."),
    ("W4SGNNVL", "corpus", "scientific metaphor;context;N400;late positivity", "Directly tests contextual modulation of ERP effects."),
    ("K2W6GBCV", "corpus", "Chinese metaphor;simile;conventionality;N400;P600", "Shows form and conventionality can change the ERP pattern."),
    ("UH4G7YZA", "corpus", "metaphor;context;N400;P600", "Explicit context manipulation provides a key boundary condition."),
    ("KMNAMCKJ", "corpus", "metaphor;irony;N400;late negativity;eLORETA", "Separates N400, late N400, and slow-wave effects across figurative forms."),
    ("B5F5XG3T", "corpus", "physical metaphor;mental metaphor;N400;theory of mind", "Tests subtype and individual-difference heterogeneity within metaphor ERP."),
    ("SIQQH3LP", "corpus", "metaphor evaluation;N400;attention", "Connects N400 effects to attentional networks and explicit evaluation task."),
    ("2YE6KRW9", "corpus", "L2 metaphor;executive control;ERP;sLORETA", "Adds executive-control and L2 boundaries to metaphor ERP interpretation."),
    ("3CV763RE", "corpus", "figurative language;masked priming;ERP;literal meaning", "Tests automatic literal activation with masked priming."),
    ("GG4GWWBS", "corpus", "metaphor;time course;ERP;N400", "Early time-course anchor for metaphor ERP findings."),
    ("FMGCRBPQ", "corpus", "action metaphor;embodiment;ERP;N400", "Embodiment-focused ERP evidence broadens mechanism alternatives."),
    ("PML39LCM", "corpus", "emotional context;emotion words;ERP", "Directly relevant context-by-emotion study; no local PDF, so metadata-only pending manual access."),
    ("CNMC6QPE", "corpus", "contextual prediction;emotion words;ERP", "Direct prediction/valence study; no local PDF, so claims remain unverified."),
    ("ACJAJ7ZB", "corpus", "accentuation;spoken emotion words;ERP", "Auditory/prosodic boundary candidate; no local PDF."),
    ("MTRD2WDW", "corpus", "emotional violation;faces;emoji;words;N400", "Cross-modal emotional violation candidate; no local PDF."),
    ("FETEEPSJ", "corpus", "anxiety;unexpected semantics;N400", "Potential state-anxiety moderator; no local PDF."),
    ("AX5MZNYI", "excluded", "idiom;emotion;fMRI", "Excluded from active ERP corpus: emotional response study uses fMRI and does not provide ERP timing/components."),
    ("C5QYA7JW", "excluded", "figurative language;emotional depth;behavioral", "Excluded from active ERP corpus: adjacent construct and no EEG/ERP outcome central to the paper."),
]


def file_url(attachment_key: str) -> str:
    req = urllib.request.Request(
        f"{BASE}/items/{attachment_key}/file/view/url",
        headers={"Zotero-API-Version": "3", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace").strip()
        if body.startswith('"'):
            return json.loads(body)
        return body


def year(value: str | None) -> str:
    match = re.search(r"(?:19|20)\d{2}", value or "")
    return match.group(0) if match else ""


def main() -> None:
    records = {r["zotero_item_key"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))}
    state = []
    pages_dir = WORK / "pages"
    pages_dir.mkdir(exist_ok=True)
    for position, (key, status, topics, reason) in enumerate(SELECTION, start=1):
        record = records[key]
        pdfs = [a for a in record["attachments"] if a.get("contentType") == "application/pdf"]
        attachment_key = pdfs[0]["key"] if pdfs else ""
        pdf_path = ""
        readable = False
        page_count = 0
        extracted_chars = 0
        error = ""
        page_rows = []
        if attachment_key:
            try:
                url = file_url(attachment_key)
                path_text = urllib.parse.unquote(urllib.parse.urlparse(url).path)
                if re.match(r"^/[A-Za-z]:/", path_text):
                    path_text = path_text[1:]
                pdf_path = str(Path(path_text))
                reader = PdfReader(pdf_path)
                page_count = len(reader.pages)
                for page_number, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    extracted_chars += len(text)
                    page_rows.append({"pdf_page": page_number, "text": text})
                readable = page_count > 0 and extracted_chars >= 500
                (pages_dir / f"{key}.json").write_text(
                    json.dumps(page_rows, ensure_ascii=False), encoding="utf-8"
                )
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        state.append(
            {
                **record,
                "selection_order": position,
                "demo_suitability": status,
                "research_topic_tags": topics,
                "selection_reason": reason,
                "attachment_key": attachment_key,
                "pdf_path": pdf_path,
                "pdf_readable": readable,
                "pdf_page_count": page_count,
                "pdf_extracted_chars": extracted_chars,
                "pdf_error": error,
            }
        )
        print(f"{position:02d}/40 {key} readable={readable} pages={page_count} chars={extracted_chars}")

    (WORK / "selection_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fields = [
        "zotero_item_key", "bibtex_key", "attachment_key", "title", "authors",
        "year", "venue", "doi", "local_pdf_readable", "research_topic_tags",
        "demo_suitability", "selection_reason", "source_collections", "pdf_page_count",
        "pdf_issue",
    ]
    with (ROOT / "corpus_manifest.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in state:
            writer.writerow(
                {
                    "zotero_item_key": row["zotero_item_key"],
                    "bibtex_key": row.get("bibtex_key") or "",
                    "attachment_key": row["attachment_key"],
                    "title": row.get("title") or "",
                    "authors": "; ".join(row.get("authors") or []),
                    "year": year(row.get("date")),
                    "venue": row.get("publicationTitle") or "",
                    "doi": row.get("DOI") or "",
                    "local_pdf_readable": "yes" if row["pdf_readable"] else "no",
                    "research_topic_tags": row["research_topic_tags"],
                    "demo_suitability": row["demo_suitability"],
                    "selection_reason": row["selection_reason"],
                    "source_collections": "; ".join(row.get("collections") or []),
                    "pdf_page_count": row["pdf_page_count"] or "",
                    "pdf_issue": row["pdf_error"] or ("missing_pdf_attachment" if not row["attachment_key"] else ""),
                }
            )

    selected = [r for r in state if r["demo_suitability"] != "excluded"]
    print(json.dumps({
        "manifest_rows": len(state),
        "active_selected": len(selected),
        "core_demo": sum(r["demo_suitability"] == "core_demo" for r in state),
        "corpus": sum(r["demo_suitability"] == "corpus" for r in state),
        "excluded": sum(r["demo_suitability"] == "excluded" for r in state),
        "active_readable_pdf": sum(r["pdf_readable"] for r in selected),
        "active_missing_or_unreadable_pdf": sum(not r["pdf_readable"] for r in selected),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

