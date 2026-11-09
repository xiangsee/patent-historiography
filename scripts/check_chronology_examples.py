#!/usr/bin/env python3
"""Executable smoke test: nested chronology scopes are distinct, preserving uncertainty.
No external dependencies; not a substitute for JSON Schema Draft 2020-12 validation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
file = ROOT / "data/examples/shiji-chronology-scopes.json"
obj = json.loads(file.read_text(encoding="utf-8"))
scopes = obj["scopes"]
assert len(scopes) == 2
ids = {s["scope_id"] for s in scopes}
assert len(ids) == len(scopes), "Duplicate scope_id"
for s in scopes:
    for key in ("source_id","research_question","start_event","end_event",
                "scope_rationale","interpretation_status"):
        assert s.get(key), f"{s['scope_id']}: missing {key}"
    assert s["calendar_system"].startswith("BCE"), "Do not silently pretend ISO dates"
    assert s["bce_start_year"] >= s["bce_end_year"]
    assert s["bce_start_year"] - s["bce_end_year"] + 1 == s["inclusive_named_years"]
    assert s["interpretation_status"] != "attested", (
        "Calendar window explanation is scholarly interpretation, not primary fact"
    )
    assert set(s["counter_readings"]).issubset(ids)
assert {s["inclusive_named_years"] for s in scopes} == {5,8}
print("PASS: two competing time scopes preserved; 5/8 named-year counts and counter-readings validated")
