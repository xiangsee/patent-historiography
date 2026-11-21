#!/usr/bin/env python3
"""Validate EP post-grant proceedings as evidence, not as a legal ruling."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from patent_evidence.procedural_ledger import (
    verify_events, procedural_view, compare_roles_across_cases, review_claim_lifecycle,
)
R=Path(__file__).resolve().parents[1]/"data/examples"
fixture=json.loads((R/"epo-cross-case-procedural-events-2026-11-21.json").read_text(encoding="utf8"))
derived=json.loads((R/"epo-procedure-evidence-audit-v0-6.json").read_text(encoding="utf8"))
events=fixture["events"]
assert verify_events(events)
assert derived["tool_version"]=="0.6.0"
assert derived["event_totals"]=={
    "all":12,"EP0729353":10,"official_epo_xml":3,
    "official_epo_decision_page":2,"secondary_legal_event_index":7
}
early=procedural_view(events,as_of="2005-07-20",case_id="EP0729353")
assert len(early["historical_events_retrospectively_observed"])==5
assert early["events_known_from_contemporaneously_dated_evidence"]==[
    "EP-A1-19960904","EP-B1-20020206"
]
assert "EP-REVOCATION-NOTICE-20050713" in early["events_without_verified_contemporaneous_availability"]
assert not early["legal_validity_or_title_as_of_independently_determined"]
assert not early["source_quality_ledger_complete"]
late=procedural_view(events,as_of="2012-09-12",case_id="EP0729353")
assert late["counts_by_event_kind"]["amended_specification_publication"]==1
assert late["counts_by_event_kind"]["opposition_withdrawal_record"]==1
assert "EP-B2-20120912" in late["events_known_from_contemporaneously_dated_evidence"]
other=procedural_view(events,as_of="2002-06-26",case_id="T0507/98")
assert not other["events_known_from_contemporaneously_dated_evidence"]
other_online=procedural_view(events,as_of="2002-09-17",case_id="T0507/98")
assert other_online["events_known_from_contemporaneously_dated_evidence"]==["T0507-DECISION-20020626"]
net=compare_roles_across_cases(events,term_a="Alkermes",term_b="Southern Research")
assert net["opposite_party_roles_in_separate_cases_observed"]
assert len(net["cases_with_both_name_substrings"])==3
assert not net["legal_entity_identity_verified"]
assert not net["commercial_market_competition_strategy_proven"]
claims=review_claim_lifecycle(fixture["claim_lifecycle"],events)
assert claims["claim_count"]==4 and claims["event_references_resolve"]
assert not derived["baseline_2005_07_20"]["final_revocation_independently_verified"]
assert derived["cross_case_parties"]["bilateral_market_competition_strategy_not_proven"] is True
assert len(derived["claim_lifecycle"])==4
assert derived["access_barriers"]["real_USPTO_bulk_XML_under_current_auth_not_retrieved"]
print("PASS: 12 source-graded procedural events, 3 cases, 4 Claim Lifecycle links, no final revocation or premature public-knowledge inference")
