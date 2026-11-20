"""Synthetic structural tests for the Google Patents HTML provider adapter.

The HTML is original, tiny synthetic input authored here; no copyrighted
patent text or third-party bulk content is committed to the repository.
"""
import hashlib
import unittest

from patent_evidence.structured_docs import DocumentParseError, parse_google_patents_html


def synthetic_html(number="ZX:987:A1", declared=2, include_link=True, pub_date="2022-04-10"):
    reference = '<claim-ref idref="cl1">claim 1</claim-ref>' if include_link else "claim 1"
    return f"""<!doctype html><html><head>
<meta name="citation_patent_publication_number" content="{number}">
<meta name="citation_patent_application_number" content="ZX:21/005">
<meta name="DC.title" content="Synthetic interface for garden irrigation">
<meta name="DC.date" scheme="dateSubmitted" content="2020-02-01">
<meta name="DC.date" content="{pub_date}">
<meta name="DC.relation" scheme="references" content="US:1234567">
</head><body>
<section itemprop="abstract"><div itemprop="content">A private original test case.</div></section>
<section itemprop="description"><div itemprop="content">
<div class="description" lang="EN">
<div class="description-line" num="0001" id="p1">A sensor emits a status.</div>
<div class="description-line" num="0002" id="p2">A controller records the status.</div>
</div></div></section>
<section itemprop="claims"><span itemprop="count">{declared}</span>
<div itemprop="content"><div class="claims" lang="EN">
<div class="claim" id="cl1" num="0001"><div class="claim-text">1. An irrigation sensor comprising a power cell.</div></div>
<div class="claim" id="cl2" num="0002"><div class="claim-text">2. The apparatus of {reference} using a timer.</div></div>
</div></div></section>
<table><tr itemprop="backwardReferences"><td><span itemprop="publicationNumber">US1234567B1</span></td></tr></table>
</body></html>"""


class StructuredPatentDocumentTest(unittest.TestCase):
    def setUp(self):
        self.url = "https://patents.google.com/patent/ZX987A1/en"

    def test_structural_claims_and_description(self):
        html = synthetic_html()
        d = parse_google_patents_html(html, source_url=self.url, expected_publication="ZX987A1")
        self.assertEqual(d["publication_number"], "ZX987A1")
        self.assertEqual(d["counts"]["claims_declared_in_html"], 2)
        self.assertEqual(d["counts"]["claims_numbered_extracted"], 2)
        self.assertEqual(d["counts"]["description_numbered_paragraphs"], 2)
        self.assertEqual(d["counts"]["explicit_claim_reference_edges"], 1)
        self.assertEqual(d["claims"][0]["claim_type_candidate"],
                         "independent_candidate_no_explicit_references")
        self.assertEqual(d["claims"][1]["explicit_reference_claim_numbers"], [1])
        self.assertEqual(d["claims"][1]["evidence_id"], "ZX987A1:CLAIM:2")
        self.assertEqual(d["description_paragraphs"][0]["evidence_id"], "ZX987A1:DESC:0001")
        self.assertEqual(d["publication_date_as_provider_meta"], "2022-04-10")
        self.assertEqual(d["backward_citation_table"]["row_count"], 1)
        self.assertEqual(d["source_html_sha256"], hashlib.sha256(html.encode()).hexdigest())

    def test_private_text_opt_in_and_default_hash_only(self):
        a = parse_google_patents_html(synthetic_html(), source_url=self.url)
        self.assertFalse(a["quality"]["private_text_included"])
        self.assertNotIn("private_extracted_text", a["claims"][0])
        self.assertEqual(len(a["claims"][0]["sha256_utf8_normalized_text"]), 64)
        b = parse_google_patents_html(synthetic_html(), source_url=self.url, private_text=True)
        self.assertIn("irrigation sensor", b["claims"][0]["private_extracted_text"])
        self.assertTrue(b["quality"]["private_text_included"])

    def test_version_separate_publication_numbers(self):
        d = parse_google_patents_html(
            synthetic_html(number="ZX:987:B1", pub_date="2024-02-02"),
            source_url="https://patents.google.com/patent/ZX987B1/en",
            expected_publication="ZX987B1")
        self.assertEqual(d["kind_code_as_provider_meta"], "B1")
        self.assertEqual(d["publication_number"], "ZX987B1")
        self.assertNotEqual(d["claims"][0]["evidence_id"], "ZX987A1:CLAIM:1")

    def test_declared_claim_count_mismatch_fails_closed(self):
        html = synthetic_html(declared=3)
        with self.assertRaises(DocumentParseError):
            parse_google_patents_html(html, source_url=self.url)
        d = parse_google_patents_html(html, source_url=self.url, strict=False)
        self.assertIn("claims_count_disagrees_with_html_header", d["quality"]["structural_issues"])
        self.assertFalse(d["quality"]["count_and_numbering_check_passed"])

    def test_unknown_claim_reference_is_not_valid_dependency(self):
        html = synthetic_html().replace('idref="cl1"', 'idref="missing"')
        with self.assertRaises(DocumentParseError):
            parse_google_patents_html(html, source_url=self.url)
        d = parse_google_patents_html(html, source_url=self.url, strict=False)
        self.assertEqual(d["claims"][1]["claim_type_candidate"], "unresolved_reference")
        self.assertEqual(d["claims"][1]["unresolved_reference_anchors"], ["missing"])

    def test_unlinked_prose_reference_is_not_independent(self):
        d = parse_google_patents_html(synthetic_html(include_link=False),
                                      source_url=self.url, strict=False)
        self.assertEqual(d["claims"][1]["claim_type_candidate"],
                         "claim_type_unresolved_unlinked_reference_text")
        self.assertIn("possible_unlinked_claim_reference", d["quality"]["structural_issues"])

    def test_wrong_publication_fails_not_silent_misassociation(self):
        with self.assertRaises(DocumentParseError):
            parse_google_patents_html(synthetic_html(), source_url=self.url,
                                      expected_publication="ZX111A1")

    def test_untrusted_source_uri_rejected(self):
        with self.assertRaises(DocumentParseError):
            parse_google_patents_html(synthetic_html(), source_url="http://patents.google.com/ZX")
        with self.assertRaises(DocumentParseError):
            parse_google_patents_html(synthetic_html(), source_url="https://another.site/ZX")


if __name__ == "__main__":
    unittest.main()

