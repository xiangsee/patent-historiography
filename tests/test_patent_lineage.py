import json
from pathlib import Path
import unittest

from patent_evidence.lineage import (
    canonical_application, priority_link_audit, registry_snapshot,
)

CASE=Path(__file__).resolve().parents[1] / "data/examples/maps-priority-rights-v0-2.json"

class HistoryEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(CASE.read_text(encoding="utf8"))

    def test_application_normalization_not_just_dates(self):
        self.assertEqual(canonical_application("US-52540003-P"),"US52540003P")
        self.assertNotEqual(canonical_application("US-52540003-P"),
                            canonical_application("US-52542003-P"))

    def test_shared_priorities_across_separate_provider_families(self):
        result=priority_link_audit(self.data["documents"])
        edges={(x["left"],x["right"]):x for x in result["comparisons"]}
        e=edges[("US20050270311A1","US7599790B2")]
        self.assertEqual(e["relation"],"overlapping_reported_priority_identifiers")
        self.assertEqual(len(e["shared_application_ids"]),2)
        self.assertFalse(e["same_provider_family_id"])
        self.assertFalse(e["is_official_epo_docdb_family_match"])

    def test_same_day_but_different_priority_applications(self):
        result=priority_link_audit(self.data["documents"])
        edges={(x["left"],x["right"]):x for x in result["comparisons"]}
        e=edges[("US20050182770A1","US7730389B2")]
        self.assertEqual(e["relation"],"same_priority_date_but_no_shared_identifier_observed")
        self.assertEqual(e["shared_application_ids"],[])
        self.assertFalse(e["is_official_epo_inpadoc_family_match"])

    def test_missing_priority_claims_is_unknown(self):
        data=[
            {"document_id":"A","application_number":"US-1-A","related_priority_application_ids":[]},
            {"document_id":"B","application_number":"US-2-A","related_priority_application_ids":["US-1-P"]},
        ]
        z=priority_link_audit(data)
        self.assertEqual(z["comparisons"][0]["relation"],"priority_identifiers_insufficient")

    def test_no_lookahead_into_assignment_on_product_launch(self):
        z=registry_snapshot(self.data["rights_events"],"US20050270311A1","2005-02-08")
        self.assertIsNone(z["last_recorded_interest_entity"])
        self.assertFalse(z["historical_legal_title_independently_confirmed"])

    def test_later_google_assignment_cannot_prove_earlier_origin(self):
        z=registry_snapshot(self.data["rights_events"],"US20050270311A1","2005-12-31")
        self.assertEqual(z["last_recorded_interest_entity"],"Google Inc.")
        self.assertFalse(z["inventor_or_technology_origin_confirmed"])
        self.assertIn("R-MAPS-2005-08-12",z["applied_registry_event_ids"])

    def test_bitemporal_recordation_after_effective_day(self):
        unknown=registry_snapshot(self.data["rights_events"],"US20050182770A1",
                                  "2005-04-26","2005-04-26")
        self.assertIsNone(unknown["last_recorded_interest_entity"])
        later_known=registry_snapshot(self.data["rights_events"],"US20050182770A1",
                                      "2005-04-26","2005-04-27")
        self.assertEqual(later_known["last_recorded_interest_entity"],"Google Inc.")

    def test_name_change_is_not_a_new_original_invention(self):
        before=registry_snapshot(self.data["rights_events"],"US20050182770A1",
                                 "2017-09-30","2017-09-30")
        after=registry_snapshot(self.data["rights_events"],"US20050182770A1",
                                "2017-10-06")
        self.assertEqual(before["current_label_for_that_recorded_interest"],"Google Inc.")
        self.assertEqual(after["current_label_for_that_recorded_interest"],"Google LLC")
        self.assertEqual(after["last_recorded_interest_entity"],"Google Inc.")
        self.assertFalse(after["inventor_or_technology_origin_confirmed"])

    def test_license_is_not_assignment(self):
        a=registry_snapshot(self.data["rights_events"],"SYNTHETIC-EXAMPLE-ONLY",
                            "2011-01-01")
        self.assertIsNone(a["last_recorded_interest_entity"])
        self.assertEqual(a["other_legal_events"][0]["reason"],"license_does_not_transfer_title")

    def test_duplicate_document_ids_fail(self):
        d=[dict(self.data["documents"][0])]*2
        with self.assertRaises(ValueError):
            priority_link_audit(d)

if __name__=="__main__":
    unittest.main()
