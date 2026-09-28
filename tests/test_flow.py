import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from neurotrace.engine import (
    analyze_with_ollama, exports, investigate, load_samples, parse_pdf, pdf_bytes,
    recompute, review, verify_anchor,
)


def test_pdf():
    content = b"BT /F1 12 Tf 72 720 Td (Emotional arousal affects LPC amplitude in this task and requires further evidence.) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    data = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    start = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    data += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    data += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(start).encode() + b"\n%%EOF\n"
    return data


class FlowTests(unittest.TestCase):
    def test_demo_review_and_all_exports(self):
        case = investigate("情绪唤醒度是否影响 LPC 振幅？", load_samples())
        self.assertTrue(case["cards"])
        for card in case["cards"]:
            review(case, card["card_id"], "confirmed")
        self.assertEqual(case["finding"]["status"], "demo_only")
        output = exports(case)
        self.assertEqual(json.loads(output["json"])["case_id"], case["case_id"])
        self.assertIn("非科研结论", output["md"])
        self.assertIn("demo_only", output["csv"])
        for card in case["cards"]:
            review(case, card["card_id"], "rejected")
        self.assertEqual(case["finding"]["verdict"], "insufficient_evidence")
        self.assertFalse(case["finding"]["active_card_ids"])

    def test_empty_retrieval_does_not_invent_evidence(self):
        case = investigate("zzzzunrelatedxxxxx", load_samples())
        self.assertEqual(case["cards"], [])
        self.assertEqual(case["finding"]["verdict"], "insufficient_evidence")

    def test_model_failure_is_not_replaced_by_demo(self):
        with patch("neurotrace.engine.analyze_with_ollama", side_effect=TimeoutError):
            case = investigate("LPC emotion", load_samples(), mode="ollama", model="test")
        self.assertTrue(case["error"])
        self.assertEqual(case["relations"], [])

    def test_invalid_model_ids_rejected(self):
        response = io.BytesIO(json.dumps({"message": {"content": json.dumps({"relations": [{"card_id": "invented", "role": "direct_support", "reason": "r", "conditions": "c"}]})}}).encode())
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(ValueError):
                analyze_with_ollama("q", [load_samples()[0]], "http://localhost:11434", "test")

    def test_real_pdf_anchor_and_tampered_quote(self):
        cards = parse_pdf(test_pdf(), "test-fixture.pdf")
        self.assertEqual(cards[0]["page"], 1)
        self.assertTrue(verify_anchor(cards[0]))
        self.assertEqual(pdf_bytes(cards[0]), test_pdf())
        card = dict(cards[0], quote="This sentence does not exist.")
        self.assertFalse(verify_anchor(card))

    def test_counterevidence_and_rejection_recompute(self):
        cards = parse_pdf(test_pdf(), "test-fixture.pdf")
        first = cards[0]
        second = dict(first, card_id="second-card")
        result = [{"card_id": first["card_id"], "role": "direct_support", "reason": "test", "conditions": "task"}, {"card_id": second["card_id"], "role": "counterevidence", "reason": "test", "conditions": "task"}]
        with patch("neurotrace.engine.analyze_with_ollama", return_value=(result, {})):
            case = investigate("LPC", [first, second], "ollama", model="mock")
        review(case, first["card_id"], "confirmed")
        review(case, second["card_id"], "confirmed")
        self.assertEqual(case["finding"]["verdict"], "contested")
        self.assertNotEqual(case["finding"]["status"], "citation_ready")
        review(case, first["card_id"], "rejected")
        review(case, second["card_id"], "rejected")
        self.assertEqual(case["finding"]["verdict"], "insufficient_evidence")

    def test_invalid_anchor_blocks_citation(self):
        cards = parse_pdf(test_pdf(), "test-fixture.pdf")
        relation = [{"card_id": cards[0]["card_id"], "role": "direct_support", "reason": "test", "conditions": "task"}]
        with patch("neurotrace.engine.analyze_with_ollama", return_value=(relation, {})):
            case = investigate("LPC", cards, "ollama", model="mock")
        review(case, cards[0]["card_id"], "confirmed")
        self.assertEqual(case["finding"]["status"], "citation_ready")
        case["cards"][0]["quote"] = "invented text"
        recompute(case)
        self.assertEqual(case["finding"]["status"], "review_required")

    def test_question_required(self):
        with self.assertRaises(ValueError):
            investigate("  ", load_samples())


class PageTests(unittest.TestCase):
    def test_page_submit_review_export(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        case = app.session_state["case"]
        self.assertTrue(case["cards"])
        reject = next(b for b in app.button if b.label == "驳回证据")
        reject.click().run()
        self.assertEqual(len(app.exception), 0)
        reason = next(field for field in app.text_area if field.label == "驳回原因")
        reason.set_value("测试：该证据不满足本案限定条件。")
        commit = next(b for b in app.button if b.label == "提交驳回并重算")
        commit.click().run()
        self.assertEqual(len(app.exception), 0)
        case = app.session_state["case"]
        self.assertTrue(any(r["decision"] == "rejected" for r in case["reviews"].values()))
        self.assertEqual(len(app.get("download_button")), 3)


if __name__ == "__main__":
    unittest.main()
