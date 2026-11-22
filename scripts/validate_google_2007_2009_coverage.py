#!/usr/bin/env python3
"""Verify the round 22 coverage and the link from deals to patent records."""

import argparse
import csv
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from patent_evidence.lineage import registry_snapshot
from patent_evidence.official_xml import parse_ep_patent_document

DERIVED = ROOT / "pilots/google-longitudinal/derived"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_public(new, joined, deals, rights):
    audits = new["query_audits"]
    assert [a["page_count"] for a in audits] == [23, 3, 25, 3, 31, 6]
    assert [a["provider_total"] for a in audits] == [1104, 112, 1203, 131, 1533, 252]
    assert all(sum(a["returned_by_page"]) == a["provider_total"] for a in audits)
    union = new["union"]
    assert union["matches_by_assignee_filter"] == {"Google Inc.": 3840, "Google LLC": 495}
    assert union["publications"] == 4152 and union["application_numbers"] == 2966
    assert union["provider_family_ids"] == 1745 and union["multiple_assignee_filter_matches"] == 183
    assert [r["publications"] for r in new["by_filing_year"].values()] == [1171, 1289, 1692]
    assert [r["reported_published_by_cutoff"] for r in new["publication_date_snapshots"].values()] == [112, 589, 1149]
    assert joined["pages"] == 168 and joined["query_windows"] == 13
    assert [joined["union"][k] for k in ("publications", "application_numbers", "provider_family_ids")] == [7449, 5343, 2774]
    assert joined["cross_window_overlap"] == {"publications": 0, "application_numbers": 0, "provider_family_ids": 201}
    assert joined["publication_date_snapshots"]["2009-12-31"]["reported_published_by_cutoff"] == 3084

    assert len(deals) == len({d["deal_id"] for d in deals}) == 26
    assert Counter(d["candidate_year"] for d in deals) == {"2007": 16, "2008": 3, "2009": 7}
    indexed = {d["deal_id"]: d for d in deals}
    assert {d["deal_id"] for d in deals if d["date_basis"] == "closed_after_scope"} == {"on2", "admob"}
    assert indexed["begun"]["date_basis"] == "regulator_rejected"
    assert indexed["marratech"]["date_basis"] == "software_acquisition_announced"
    assert all(d["date_source_url"].startswith("https://") and d["iphouse_reported_documents"].isdigit() for d in deals)
    scans = rights["uspto_original_record_scans"]
    assert len(scans) == len({s["reel_frame"] for s in scans}) == 11
    assert len({s["case_id"] for s in scans}) == 9
    for scan in scans:
        assert scan["case_id"] in indexed and scan["us_application_numbers"]
        assert date.fromisoformat(scan["date_executed"]) <= date.fromisoformat(scan["date_recorded"])
        assert len(bytes.fromhex(scan["source_sha256"])) == 32
    assert len(rights["epo_native_publications"]) == 2
    assert {c["case_id"] for c in rights["verified_external_publication_controls"]} == {"postini", "admob", "jaiku", "teracent"}

    doubleclick = next(s for s in scans if s["case_id"] == "doubleclick")
    assert indexed["doubleclick"]["observed_deal_date_or_period"] == "2008-03-11"
    event = {
        "event_id": doubleclick["reel_frame"], "patent_id": "US11/250575", "event_kind": "merger",
        "date_effective": doubleclick["date_effective"], "date_recorded": doubleclick["date_recorded"],
        "to_entity": doubleclick["to_entity"],
    }
    assert registry_snapshot([event], "US11/250575", "2008-03-11", "2026-11-22")["last_recorded_interest_entity"] is None
    assert registry_snapshot([event], "US11/250575", "2008-05-01")["not_yet_recorded_by_knowledge_cutoff"]
    assert registry_snapshot([event], "US11/250575", "2008-05-01", "2008-09-24")["last_recorded_interest_entity"] == "Google Inc."


def replay_private(folder, new, joined, deals, rights):
    path = str(folder / "*.batch.json")
    rows, pages = load([path])
    report = audit_longitudinal_coverage(rows, pages, as_of_dates=new["publication_date_snapshots"])
    assert report == {k: v for k, v in new.items() if k not in ("tool", "tool_version")}
    pub_ids = {key(doc["publication_number"]) for doc in rows}
    assert all(c["publication_number"] not in pub_ids for c in rights["verified_external_publication_controls"])

    all_rows, all_pages = load([path, str(folder.parent / "*.batch.json")])
    report = audit_longitudinal_coverage(all_rows, all_pages, as_of_dates=joined["publication_date_snapshots"])
    for field in ("union", "sorted_publication_ids_sha256", "publication_date_snapshots"):
        assert report[field] == joined[field]

    probes = {p["name"]: p["response"]["total"] for p in read_json(folder / "target-assignee-probes.json")}
    assert len(probes) == 35
    assert all(probes[d["iphouse_assignee_probe"]] == int(d["iphouse_reported_documents"]) for d in deals)
    for scan in rights["uspto_original_record_scans"]:
        contents = (folder / scan["file"]).read_bytes()
        assert contents.startswith(b"%PDF") and sha256(contents).hexdigest() == scan["source_sha256"]
    for e in rights["epo_native_publications"]:
        xml = (folder / e["file"]).read_bytes()
        parsed = parse_ep_patent_document(
            xml, source_url=e["source_url"], expected_publication=e["publication"], allow_no_claims=True,
        )
        party_field = {"applicant": "A_document_applicant_B711", "proprietor": "B_document_proprietor_B731"}[e["role"]]
        assert e["entity"] in parsed["parties_as_published"][party_field]
        assert parsed["publication_date"] == e["publication_date"]
        assert parsed["source_xml_sha256"] == e["source_sha256"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-source-dir", type=Path)
    args = parser.parse_args()
    new = read_json(DERIVED / "google-2007-2009-name-coverage-2026-11-22.json")
    joined = read_json(DERIVED / "google-1996-2009-combined-audit-2026-11-22.json")
    rights = read_json(DERIVED / "google-2007-2009-patent-rights-2026-11-22.json")
    with (DERIVED / rights["roster"]).open(encoding="utf-8", newline="") as handle:
        deals = list(csv.DictReader(handle))
    validate_public(new, joined, deals, rights)
    if args.private_source_dir:
        replay_private(args.private_source_dir.resolve(), new, joined, deals, rights)
        print("PASS: private 2007–2009 and joint coverage replay, 35 target probes, 11 scans and 2 EPO files")
    print("PASS: 91 pages, 4,152 publications, 26 named cases, 4 external publication controls")


if __name__ == "__main__":
    main()
