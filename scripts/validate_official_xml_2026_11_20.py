#!/usr/bin/env python3
"""Regression over derived official XML facts, with full source files kept private."""
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]/"data/examples"
m=json.loads((R/"official-xml-four-source-derived-2026-11-20.json").read_text("utf8"))
h=json.loads((R/"alkermes-ep0729353-1996-2012-derived.json").read_text("utf8"))

assert m["tool_version"]=="0.5.0"
assert m["total_european_real_patents"]==2
assert m["total_wipo_test_xml_examples"]==2
assert m["epo_number_of_distinct_claim_positions_across_two_real_patents"]==11
assert m["epo_total_xml_claim_nodes_across_language_versions"]==33
assert m["wipo_v10_directory_actual_st96_schema_version"]=="V8_0"
assert not m["full_claim_text_republished_in_public_repo"]
for item in m["source_records"]:
    assert len(item["sha256_source_xml"])==64
    assert item["source_url"].startswith("https://")
    assert not item["issue_flags"]
    if item["source_type"]=="EPO_official_real_patent_XML":
        assert set(item["claim_counts_per_language"])=={"en","de","fr"}
        assert all(v==item["primary_language_claim_count"]
                   for v in item["claim_counts_per_language"].values())
        assert item["claim_count_inflation_if_wrongly_summed"]==3.0
        assert item["xml_schema_or_dtd_validated"] is False
    else:
        assert item["document_status"]=="TEST"
        assert item["is_real_published_patent"] is False
        assert item["claims_in_example"]==10
        assert item["reported_claim_types_in_example"]=={"Independent":3,"Dependent":7}
assert len(h["historical_published_versions"])==3
versions=h["historical_published_versions"]
assert [v["publication_number"] for v in versions]==[
    "EP0729353A1","EP0729353B1","EP0729353B2"]
assert [v["publication_date"] for v in versions]==[
    "1996-09-04","2002-02-06","2012-09-12"]
assert [v["primary_claims"] for v in versions]==[None,6,4]
assert [v["claims_all_languages"] for v in versions]==[0,18,12]
assert versions[0]["not_original_patent_absence"] is True
assert versions[0]["has_claims_in_this_XML"] is False
assert versions[0]["as_published_parties"]["A_document_applicant_B711"]==[
    "Alkermes Controlled Therapeutics, Inc."]
assert versions[1]["as_published_parties"]["B_document_proprietor_B731"]==[
    "Alkermes Controlled Therapeutics, Inc."]
assert versions[2]["as_published_parties"]["B_document_proprietor_B731"]==[
    "Alkermes, Inc."]
diff=h["b1_to_b2_textual_structural_comparison"]
assert (diff["first_primary_claims"],diff["second_primary_claims"])==(6,4)
assert diff["same_number_claim_positions_examined"]==4
assert diff["same_number_change_count"]==4
assert diff["first_DTD_as_declared"]=="ep-patent-document-v1-1"
assert diff["second_DTD_as_declared"]=="ep-patent-document-v1-4"
assert "after opposition" in diff["second_kind_semantics_from_EPO"]
assert not diff["legal_scope_change_magnitude_inferred"]
assert not diff["opposition_file_and_reasoning_independently_reviewed"]
assert h["rights_transfer_continuity_confirmed"] is False
assert h["public_original_full_xml_uploaded"] is False
print("PASS: EPO 2 real/WIPO 2 TEST; 11 distinct/33 translated claims; EP0729353 A1→B1→B2")
