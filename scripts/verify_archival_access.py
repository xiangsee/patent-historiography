#!/usr/bin/env python3
"""Evidence gate: verifying a patent's reference to a CD is NOT retrieval of code."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/"schemas/external-archive-artifact.schema.json"
P=ROOT/"data/examples/us7110993-cd-access.json"
schema=json.loads(S.read_text(encoding="utf8"))
a=json.loads(P.read_text(encoding="utf8"))
try:
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(a,schema)
except ImportError:
    print("WARNING: jsonschema not installed; structural gates still checked")
assert a["asserted_count"]==22808 and a["asserted_bytes"]==101776919
assert a["catalog_name"]=="dir_s"
assert a["attestation_source"].endswith("/US7110993B2/en")
assert len(a["access_probes"])>=3
assert any(p["outcome"]=="http_403" for p in a["access_probes"])
assert not any(a["verification_flags"].values()),"Do not claim disc obtained or custody confirmed"
assert a["verified_sha256"] is None and a["actual_files"] is None
assert a["actual_bytes"] is None and a["reuse_status"]=="unknown"
print("PASS: documentary claim verified; media, custody, hashes, code, and permission remain unknown")
