#!/usr/bin/env python3
"""Validate publicly publishable derived Google 2000-05 patent slices.
No privately fetched vendor bulk responses are included here.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/"pilots/google-longitudinal/derived/google-inc-2000-2005-joint-audit.json").read_text(encoding="utf8"))
cases=json.loads((root/"pilots/google-longitudinal/derived/historical-family-origin-cases.json").read_text(encoding="utf8"))
slices=data["windows"]
assert len(slices)==2
assert [w["page_count"] for w in slices]==[22,17]
assert [w["counts"]["records"] for w in slices]==[1067,850]
assert [w["counts"]["unique_application_numbers"] for w in slices]==[843,622]
assert [w["counts"]["valid_family_id_distinct"] for w in slices]==[522,370]
assert data["combined"]["records"]==1917
assert data["combined"]["unique_publications"]==1917
assert data["combined"]["unique_application_numbers"]==1465
assert data["combined"]["valid_family_id_distinct"]==836
assert data["cross_window_family_overlap"]==56
assert data["naive_sum_family_ids_by_window"]==892
assert 892-56==836
assert slices[1]["counts"]["records_with_earlier_priority_year_than_filing_year"]==589
assert slices[1]["counts"]["records_with_non_google_cotagged_assignee"]==196
geo=data["classification_signal_comparison"]["G01C21"]
assert geo["2000_2004"]["publication_documents"]==16
assert geo["2005"]["publication_documents"]==53
assert geo["2005"]["different_provider_family_ids"]==12
assert {c["case_id"] for c in cases["cases"]}=={"FAM3814761","FAM24968825","MAPS2004"}
assert any(c["source_family_id"]=="3814761" and c.get("provider_matching_documents_no_time_filter")==358 for c in cases["cases"])
assert data["evidence_levels"]["complete_company_history"] is False
assert data["evidence_levels"]["historical_tech_turning_points_verified"] is False
assert data["evidence_levels"]["provider_family_semantics_independent_validation"] is False
print("PASS: 39 pages, 1,917 documents, 1,465 apps, 836 provider family IDs, 56 cross-window overlaps, ownership caveats")
