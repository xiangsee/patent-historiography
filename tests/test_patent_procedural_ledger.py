"""Synthetic and actual fact-pointer regressions for procedural patent history."""
import copy
import json
from pathlib import Path
import unittest

from patent_evidence.procedural_ledger import (
    ProcedureLedgerError, verify_events, procedural_view,
    compare_roles_across_cases, review_claim_lifecycle,
)

FIXTURE=Path(__file__).resolve().parents[1]/"data/examples/epo-cross-case-procedural-events-2026-11-21.json"


class ProceduralLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.events=cls.data["events"]

    def test_actual_evidence_fixture_validates(self):
        self.assertTrue(verify_events(self.events))
        self.assertEqual(len(self.events),12)
        self.assertEqual(len({e["case_id"] for e in self.events}),3)

    def test_revocation_notice_does_not_prove_final_reversal(self):
        x=procedural_view(self.events,as_of="2005-07-20",case_id="EP0729353")
        kinds=x["counts_by_event_kind"]
        self.assertEqual(kinds["revocation_communication"],1)
        self.assertFalse(x["legal_validity_or_title_as_of_independently_determined"])
        self.assertTrue(any("EP-REVOCATION-NOTICE" in e["event_id"]
            for e in x["historical_events_retrospectively_observed"]))
        self.assertIn("EP-REVOCATION-NOTICE-20050713",
                      x["events_without_verified_contemporaneous_availability"])

    def test_publication_proven_and_indexed_event_not_automatically_known(self):
        x=procedural_view(self.events,as_of="2005-07-20",case_id="EP0729353")
        self.assertEqual(x["events_known_from_contemporaneously_dated_evidence"],
                         ["EP-A1-19960904","EP-B1-20020206"])
        self.assertNotIn("EP-REVOCATION-NOTICE-20050713",
                         x["events_known_from_contemporaneously_dated_evidence"])

    def test_official_appeal_online_date_not_decision_date(self):
        prior=procedural_view(self.events,as_of="2002-06-26",case_id="T0507/98")
        self.assertEqual(len(prior["historical_events_retrospectively_observed"]),1)
        self.assertEqual(len(prior["events_known_from_contemporaneously_dated_evidence"]),0)
        after=procedural_view(self.events,as_of="2002-09-17",case_id="T0507/98")
        self.assertEqual(after["events_known_from_contemporaneously_dated_evidence"],
                         ["T0507-DECISION-20020626"])

    def test_EP2012_B2_amended_not_scope_proven(self):
        view=procedural_view(self.events,as_of="2012-09-12",case_id="EP0729353")
        kinds=view["counts_by_event_kind"]
        self.assertEqual(kinds["patent_grant_publication"],1)
        self.assertEqual(kinds["amended_specification_publication"],1)
        self.assertEqual(kinds["opposition_withdrawal_record"],1)
        self.assertFalse(view["legal_validity_or_title_as_of_independently_determined"])

    def test_opposing_roles_across_different_cases_are_only_candidates(self):
        x=compare_roles_across_cases(self.events,term_a="Alkermes",term_b="Southern Research")
        directions={e["direction"] for e in x["observed_role_directions"]}
        self.assertIn("A_opponent_B_applicant",directions)
        self.assertIn("B_opponent_A_proprietor",directions)
        self.assertTrue(x["opposite_party_roles_in_separate_cases_observed"])
        self.assertFalse(x["legal_entity_identity_verified"])
        self.assertFalse(x["commercial_market_competition_strategy_proven"])
        self.assertEqual(len({x["case_id"] for x in x["cases_with_both_name_substrings"]}),3)

    def test_final_revocation_from_notice_is_illegal_input(self):
        e=copy.deepcopy(self.events)
        for entry in e:
            if entry["event_kind"]=="revocation_communication":
                entry["final_revocation_confirmed"]=True
        with self.assertRaises(ProcedureLedgerError):
            verify_events(e)

    def test_aggregator_cannot_claim_historical_publication_date(self):
        e=copy.deepcopy(self.events)
        for entry in e:
            if entry["source_class"]=="secondary_legal_event_aggregation":
                entry["first_contemporaneously_available_on"]=entry["event_date"]
                break
        with self.assertRaises(ProcedureLedgerError):
            verify_events(e)

    def test_withdrawal_of_one_opposition_does_not_mean_every_opposition(self):
        e=copy.deepcopy(self.events)
        for entry in e:
            if entry["event_kind"]=="opposition_withdrawal_record":
                entry["all_oppositions_withdrawn"]=True
        with self.assertRaises(ProcedureLedgerError):
            verify_events(e)

    def test_claim_lifecycle_pointers_resolve(self):
        x=review_claim_lifecycle(self.data["claim_lifecycle"],self.events)
        self.assertEqual(x["claim_count"],4)
        self.assertTrue(x["event_references_resolve"])
        self.assertTrue(all(not c["factual_claim_independently_proven_by_this_software"]
                            for c in x["records"]))
        item=next(c for c in x["records"] if c["claim_id"]=="HIST-EP-002")
        self.assertIn("secondary_legal_event_aggregation",item["evidence_sources_by_tier"])

    def test_unknown_claim_evidence_not_silently_accepted(self):
        fake=copy.deepcopy(self.data["claim_lifecycle"])
        fake[0]["evidence"].append("FAKE-NONEXISTENT-EVENT")
        with self.assertRaises(ProcedureLedgerError):
            review_claim_lifecycle(fake,self.events)

    def test_duplicate_ids_rejected(self):
        e=copy.deepcopy(self.events)
        e.append(copy.deepcopy(e[0]))
        with self.assertRaises(ProcedureLedgerError):
            verify_events(e)

    def test_invalid_publication_future_knowledge(self):
        e=copy.deepcopy(self.events)
        e[0]["first_contemporaneously_available_on"]="1990-01-01"
        with self.assertRaises(ProcedureLedgerError):
            verify_events(e)

if __name__ == "__main__":
    unittest.main()

