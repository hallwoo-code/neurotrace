"""Read-only structural validation for NeuroTrace retrieval ontology and runtime GoldCases."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("02_数据与证据"))
    args = parser.parse_args()
    root = args.data_root

    cards = load(root / "evidence_cards.json")["cards"]
    contract = load(root / "runtime_corpus_contract_v1.json")
    profile = load(root / "retrieval_profile_v1.json")
    gold = load(root / "gold_cases_runtime_v1.json")
    card_by_id = {card["evidence_id"]: card for card in cards}
    errors: list[str] = []

    cases = gold["cases"]
    if len(cases) != 12 or len({case["gold_case_id"] for case in cases}) != 12:
        errors.append("gold case count/uniqueness")
    splits = Counter(case["split"] for case in cases)
    if dict(splits) != {"development": 8, "holdout": 4}:
        errors.append(f"split counts:{dict(splits)}")
    if len(profile.get("claim_slots", [])) != 10:
        errors.append("claim slot count")
    if contract["source_corpus_version_id"] != gold["source_corpus_version_id"]:
        errors.append("corpus version mismatch")

    required_coverage = {"conditional_support", "counterevidence", "adjacent_concept", "insufficient_evidence", "format_exception", "authorization_boundary"}
    observed_coverage = {coverage for case in cases for coverage in case.get("coverage", [])}
    missing_coverage = sorted(required_coverage - observed_coverage)
    if missing_coverage:
        errors.append("coverage missing:" + ",".join(missing_coverage))

    selector = contract["default_card_selector"]
    for case in cases:
        if not case.get("input") or not case.get("expected_verdict") or not case.get("allowed_finding"):
            errors.append(f"{case['gold_case_id']}:required contract field")
        for evidence_id in case.get("must_retrieve_evidence_ids", []):
            card = card_by_id.get(evidence_id)
            if card is None:
                errors.append(f"{case['gold_case_id']}:unknown card:{evidence_id}")
                continue
            if card["status"] not in selector["status"] or card["source_verification_status"] not in selector["source_verification_status"]:
                errors.append(f"{case['gold_case_id']}:non-retrievable card:{evidence_id}")
            if evidence_id in selector.get("exclude_evidence_ids", []):
                errors.append(f"{case['gold_case_id']}:excluded card:{evidence_id}")
        if "counterevidence" in case.get("must_surface_roles", []) and not any(
            card_by_id[evidence_id]["evidence_role"] == "counterevidence"
            for evidence_id in case.get("must_retrieve_evidence_ids", [])
            if evidence_id in card_by_id
        ):
            errors.append(f"{case['gold_case_id']}:missing counterevidence card")

    result = {
        "structural_validation": "pass" if not errors else "fail",
        "cases": len(cases),
        "splits": dict(splits),
        "claim_slots": len(profile.get("claim_slots", [])),
        "coverage": sorted(observed_coverage),
        "direct_support_coverage": "blocked_by_current_corpus_zero_direct_support_cards",
        "model_evaluation": "not_run_requires_runtime_implementation",
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

