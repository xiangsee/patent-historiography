#!/usr/bin/env python3
import json
from pathlib import Path
from math import isclose
R=Path(__file__).resolve().parents[1]
load=lambda n:json.loads((R/"data/examples"/n).read_text(encoding="utf-8"))
f=load("search-ads-company-financials.json")
p=load("search-ads-patent-lineage.json")
t=load("search-ads-tech-forks-and-people.json")
assert [x["year"] for x in f["rows"]]==[2000,2001,2002]
assert all(x["overture_m"]>x["google_m"] for x in f["rows"])
assert isclose(f["rows"][1]["overture_tac_m"]/f["rows"][1]["overture_m"],.56,abs_tol=.01)
assert isclose(f["rows"][2]["overture_tac_m"]/f["rows"][2]["overture_m"],.58,abs_tol=.01)
assert "not_equal_market_share" in f["status"]
ids={x["id"] for x in p["patents"]}
assert len(ids)==len(p["patents"])
for e in p["rights_events"]:
 assert e["patent_id"] in ids
 if e["effective"]:assert e["recorded"]>=e["effective"]
for x in p["document_relationships"]:assert x["source_id"] in ids and x["target_id"] in ids
assert p["status"].startswith("google_patents_aggregator")
sids={s["id"] for s in t["sources"]}
for b in t["branches"]:assert set(b["sources"]).issubset(sids)
assert {b["result"] for b in t["branches"]}=={"adopted_2002_Feb","shelved","revisited_contextual_ads"}
for person in t["contributions"]:
 assert set(person["patent_ids"]).issubset(ids)
 assert set(person["source_ids"]).issubset(sids)
assert t["status"].startswith("researcher_retrospective")
print("PASS: revenue comparison, TAC ratios, patent legal events, citation lineage, technical forks, inventor attribution evidence boundaries")
