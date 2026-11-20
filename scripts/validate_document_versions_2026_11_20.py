#!/usr/bin/env python3
"""Reproducible public derived QA for six Google Patents publication pages.

Raw HTML and complete patent claims/descriptions are NOT stored in this repo.
The validation checks an audited single snapshot, not legal claim scope.
"""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=root/"data/examples/six-patent-publication-version-structures-2026-11-20.json"
data=json.loads(p.read_text(encoding="utf-8"))

expected={
 "CN101166059A":(10,111,3),
 "CN101166059B":(7,111,3),
 "CN1482771A":(4,46,1),
 "CN1315292C":(4,47,1),
 "US20050270311A1":(74,136,8),
 "US7158878B2":(74,137,8),
}
assert data["tool_version"]=="0.4.0"
assert len(data["documents"])==len(expected)==6
assert data["official_source_verified"] is False
assert data["copyright_and_source_reuse"]
seen=set()
for doc in data["documents"]:
    key=doc["publication_number"]
    assert key not in seen and key in expected
    seen.add(key)
    counts=doc["count"]
    claim_count,para_count,indep=expected[key]
    assert counts["claims_numbered_extracted"]==counts["claims_declared_in_html"]==claim_count
    assert counts["description_numbered_paragraphs"]==para_count
    assert counts["claim_classifications"].get("independent_candidate_no_explicit_references")==indep
    assert not doc["claim_structural_issues"]
    assert not doc["private_text_included"]
    assert doc["original_official_text_verified"] is False
    assert doc["source_url"].startswith("https://patents.google.com/patent/"+key+"/")
    assert len(doc["html_sha256"])==64
    assert len(doc["abstract_text_hash"])==64
    for group in ("first_three_claim_evidence","first_three_description_evidence"):
        assert 0 < len(doc[group]) <=3
        for item in doc[group]:
            assert item["locator"].startswith(doc["source_url"]+"#")
            assert len(item["hash"])==64
            assert not any(field in item for field in ("text","private_extracted_text","claims_text","description_text"))
assert sum(x["count"]["claims_numbered_extracted"] for x in data["documents"])==173
assert sum(x["count"]["description_numbered_paragraphs"] for x in data["documents"])==588
pairs={(x["first_publication"],x["second_publication"]):x
       for x in data["version_comparisons"]}
assert len(pairs)==3
assert pairs["CN101166059A","CN101166059B"]["claim_counts"]=={
 "first":10,"second":7,"difference_second_minus_first":-3}
assert pairs["CN1482771A","CN1315292C"]["claim_counts"]["difference_second_minus_first"]==0
assert pairs["US20050270311A1","US7158878B2"]["claim_counts"]["difference_second_minus_first"]==0
assert [pairs[k]["changed_count_same_number"] for k in [
 ("CN101166059A","CN101166059B"),
 ("CN1482771A","CN1315292C"),
 ("US20050270311A1","US7158878B2")]]==[6,4,74]
assert all(not pair["legal_protection_scope_narrowed_or_expanded_verified"] for pair in pairs.values())
assert all(pair["review_required_for_claim_merger_and_renumbering"] for pair in pairs.values())
print("PASS: 6 publications, 173 numbered claims, 588 description paragraphs, 3 version pairs; hashes only")
