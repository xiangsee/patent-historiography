#!/usr/bin/env python3
"""Validate public derived Tencent/Huawei patent QA; no private bulk dataset needed."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]/"data/examples"
a=json.loads((R/"cross-company-document-qa-2026-11-20.json").read_text(encoding="utf8"))
t=a["samples"]["tencent_cn_2002"]
h=a["samples"]["huawei_cn_2002"]
assert t["complete"] and t["provider_total"]==t["returned_rows"]==4
assert t["distinct_publications"]==4 and t["distinct_applications"]==2
assert t["distinct_provider_family_ids"]==2
assert not h["complete"] and h["provider_total"]==2039 and h["returned_rows"]==8
assert "incomplete_provider_result" in h["issues"]
b=a["full_text_field_audit"]
assert b["records"]==3 and b["documented_divisional_year_alerts"]==1
assert b["claims_status"]["missing_in_current_provider_index"]==3
assert b["description_status"]["missing_in_current_provider_index"]==3
assert all(not x.get("case_specific_family_verified",False)
           and not x.get("original_assignment_deed_retrieved",False)
           for x in a["external_official_case_attempts"])
c=json.loads((R/"cn2002-text-quality-result-v0-3.json").read_text(encoding="utf8"))
assert c["records_audited"]==3 and c["version"]=="0.3.0"
assert c["number_year_divisional_review_count"]==1
assert all(not q["claims"]["original_text_nonexistence_proved"]
           and not q["description"]["original_text_nonexistence_proved"]
           for q in c["documents"])
print("PASS Tencent 4/4; Huawei properly incomplete 8/2039; three missing text indexes, one divisional-date warning")
