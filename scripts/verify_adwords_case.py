#!/usr/bin/env python3
"""Validate a sampled historical evidence corpus, not the entire corporate patent dataset."""
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
src=load("data/examples/adwords-overture-source-index.json")["sources"]
evs=load("data/examples/adwords-overture-events.json")["events"]
cl=load("data/examples/adwords-overture-claims.json")["claims"]
source_ids={s["id"] for s in src}
assert len(source_ids)==len(src),"duplicate source IDs"
event_ids={e["event_id"] for e in evs}
assert len(event_ids)==len(evs),"duplicate event IDs"
claim_ids={c["claim_id"] for c in cl}
assert len(claim_ids)==len(cl),"duplicate claim IDs"
assert all(set(e["source_ids"]).issubset(source_ids) for e in evs),"dangling event source"
assert all({s["source_id"] for s in c["sources"]}.issubset(source_ids) for c in cl),"dangling claim source"

try:
    import jsonschema
    for x in evs:jsonschema.validate(x,load("schemas/history-event.schema.json"))
    for x in cl:jsonschema.validate(x,load("schemas/historical-claim.schema.json"))
    print("JSON-Schema validated",len(evs),"events and",len(cl),"claims")
except ModuleNotFoundError:
    print("WARNING jsonschema missing: integrity checks only")

byid={e["event_id"]:e for e in evs}
assert byid["E09-04"]["date_text"]=="2000-10-23"
assert byid["E09-07"]["date_text"]=="2002-02-20"
assert byid["E09-06"]["knowledge_as_of_date"]=="2003-03-06","do not back-date public knowledge to patent priority"
assert byid["E09-02"]["disclosure_time"]=="2001-07-31","GoTo application was not public at filing"
assert byid["E09-09"]["date_precision"]=="month","do not invent exact April filing date from SEC"

status=Counter(c["status"] for c in cl)
assert all(k in status for k in ("REJECTED","OBSERVED","HYPOTHESIS","INTERPRETED"))
assert next(c for c in cl if c["claim_id"]=="C09-04")["status"]=="REJECTED","combined settlement cannot be single patent price"
print("PASS historical case:",len(src),"sources,",len(evs),"events,",len(cl),"claims; statuses",dict(status))
