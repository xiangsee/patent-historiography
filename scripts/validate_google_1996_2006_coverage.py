#!/usr/bin/env python3
"""Validate the public Google coverage audit and optionally replay private sources."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from patent_evidence.official_xml import parse_ep_patent_document

DERIVED = ROOT / "pilots/google-longitudinal/derived"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_public(report, sources):
    archive = read_json(DERIVED / "google-inc-2000-2004-global-audit.json")
    audits = report["query_audits"]
    assert [a["page_count"] for a in audits] == [2, 1, 22, 10, 17, 21, 4]
    assert [a["provider_total"] for a in audits] == [62, 20, 1067, 469, 850, 1003, 171]
    assert all(sum(a["returned_by_page"]) == a["provider_total"] for a in audits)
    assert audits[2]["sorted_source_publication_ids_sha256"] == archive["sha256_sorted_publication_ids"]
    union = report["union"]
    assert [union[k] for k in ("publications", "application_numbers", "provider_family_ids")] == [3297, 2377, 1230]
    assert union["matches_by_assignee_filter"] == {"Google Inc.": 2982, "Google LLC": 660}
    assert sum(a["provider_total"] for a in audits) - union["publications"] == union["multiple_assignee_filter_matches"] == 345
    assert len(union["publication_offices"]) == 24
    years = report["by_filing_year"]
    assert list(years) == [str(year) for year in range(1996, 2007)]
    assert sum(y["publications"] for y in years.values()) == union["publications"]
    assert sum(y["multiple_assignee_filter_matches"] for y in years.values()) == 345
    assert years["2006"]["publications"] == 1078 and years["2006"]["earlier_priority_year_rows"] == 777
    before = report["filings_before"]
    assert before["date"] == "1998-09-01" and before["publications"] == 32
    snapshots = report["publication_date_snapshots"]
    assert [s["reported_published_by_cutoff"] for s in snapshots.values()] == [22, 223, 528, 963]
    for label, snapshot in snapshots.items():
        assert snapshot["matched_filing_dates_through_cutoff"] == sum(
            year["publications"] for y, year in years.items() if y <= label[:4]
        )
        assert sum(v for k, v in snapshot.items() if k != "matched_filing_dates_through_cutoff") == snapshot["matched_filing_dates_through_cutoff"]

    assert {c["epo_application_number"] for c in sources["cases"]} == {"99107559.9", "98954045.5"}
    for case in sources["cases"]:
        published_application, grant = case["versions"]
        assert published_application["publication_date"] < grant["publication_date"]
        assert published_application["filing_date"] == grant["filing_date"]
        assert published_application["parties_as_published"]["A_document_applicant_B711"] in [
            ["XEROX CORPORATION"], ["The Microoptical Corporation"]
        ]
        assert grant["parties_as_published"]["B_document_proprietor_B731"] == ["Google Inc."]


def replay_private(folder, report, sources):
    folder = folder.resolve()
    rows, pages = load([str(folder / "*.batch.json")])
    replay = audit_longitudinal_coverage(
        rows, pages, as_of_dates=report["publication_date_snapshots"], before=report["filings_before"]["date"]
    )
    assert replay == {k: v for k, v in report.items() if k not in ("tool", "tool_version")}

    old_rows, _ = load([str(folder / filename) for filename in ("baseline.batch.json", "2005-inc.batch.json")])
    old_id_set = {r["publication_number"] for r in old_rows}
    old_digest = sha256("\n".join(sorted(old_id_set)).encode("utf-8")).hexdigest()
    archive = read_json(DERIVED / "google-inc-2000-2005-joint-audit.json")
    assert old_digest == archive["combined"]["sha256_sorted_publication_numbers"]

    assert all(key(row["publication_number"]) != "US6285999B1" for row in rows)
    known = read_json(folder / "pagerank.lookup.json")["response"]
    assert known["total"] == 1 and key(known["data"][0]["publication_number"]) == "US6285999B1"
    assert known["data"][0]["assignee"] == ["The Board Of Trustees Of The Leland Stanford Junior University"]

    inc_2006, _ = load([str(folder / "2006-inc.batch.json")])
    dmarc = {key(row["publication_number"]) for row in inc_2006
             if any("dmarc broadcasting" in name.casefold() for name in row["assignee"])}
    assert len(dmarc) == 11 and {"CA2601390A1", "CA2601390C"} <= dmarc
    for case in sources["cases"]:
        for version in case["versions"]:
            stem = version["source_url"].split("/")[-2]
            parsed = parse_ep_patent_document(
                (folder / f"{stem}.xml").read_bytes(), source_url=version["source_url"],
                expected_publication=version["publication"], allow_no_claims=True,
            )
            for field in ("publication_date", "parties_as_published", "source_xml_sha256"):
                assert parsed[field] == version[field]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-source-dir", type=Path)
    args = parser.parse_args()
    report = read_json(DERIVED / "google-1996-2006-name-coverage-2026-11-22.json")
    sources = read_json(DERIVED / "google-early-epo-party-evidence-2026-11-22.json")
    validate_public(report, sources)
    if args.private_source_dir:
        replay_private(args.private_source_dir, report, sources)
        print("PASS: private data replay, archived IDs, PageRank lookup and four EPO XML files")
    print("PASS: 77 pages, 3,297 publications, 345 alias overlaps and four publication-date snapshots")


if __name__ == "__main__":
    main()
