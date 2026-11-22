import unittest

from patent_evidence.core import AuditError
from patent_evidence.coverage import audit_longitudinal_coverage


def page(query_id, assignee, returned, total):
    return {
        "query_id": query_id,
        "query": {"assignee": assignee, "filing_date_from": "1996-01-01", "filing_date_to": "1999-12-31"},
        "page": 1,
        "returned": returned,
        "provider_total": total,
        "error": None,
        "source_file": f"{query_id}.json",
        "source_sha256": "0" * 64,
    }


def document(query_id, pub_id, **overrides):
    return {
        "_query_id": query_id,
        "publication_number": pub_id,
        "application_number": "US-1-A",
        "country_code": "US",
        "family_id": "987",
        "filing_date": "1998-01-09",
        "priority_date": "1997-01-10",
        "publication_date": "2001-09-04",
        **overrides,
    }


class CoverageTests(unittest.TestCase):
    def test_alias_overlap_keeps_unit_counts_and_time_boundaries(self):
        rows = [
            document("inc", "US-1-B1"),
            document("inc", "US-2-A1", publication_date="1999-12-31"),
            document("llc", "US1B1"),
        ]
        pages = [page("inc", "Example Inc.", 2, 2), page("llc", "Example LLC", 1, 1)]
        report = audit_longitudinal_coverage(rows, pages, as_of_dates=["1999-12-31"], before="1998-01-09")
        self.assertEqual(report["union"]["publications"], 2)
        self.assertEqual(report["union"]["application_numbers"], 1)
        self.assertEqual(report["union"]["provider_family_ids"], 1)
        self.assertEqual(report["union"]["matches_by_assignee_filter"], {"Example Inc.": 2, "Example LLC": 1})
        self.assertEqual(report["by_filing_year"]["1998"]["multiple_assignee_filter_matches"], 1)
        self.assertEqual(report["filings_before"]["publications"], 0)
        self.assertEqual(report["publication_date_snapshots"]["1999-12-31"], {
            "matched_filing_dates_through_cutoff": 2,
            "reported_published_by_cutoff": 1,
            "reported_published_after_cutoff": 1,
            "unknown_or_inconsistent_publication_date": 0,
        })

    def test_partial_pages_cannot_produce_a_union(self):
        with self.assertRaisesRegex(AuditError, "incomplete"):
            audit_longitudinal_coverage(
                [document("inc", "US1B1")], [page("inc", "Example Inc.", 1, 2)], as_of_dates=["1999-12-31"]
            )

    def test_duplicate_within_a_query_cannot_satisfy_provider_total(self):
        with self.assertRaisesRegex(AuditError, "duplicate publication"):
            audit_longitudinal_coverage(
                [document("inc", "US1B1"), document("inc", "US-1-B1")],
                [page("inc", "Example Inc.", 2, 2)], as_of_dates=["1999-12-31"],
            )

    def test_conflicting_facts_across_names_are_rejected(self):
        with self.assertRaisesRegex(AuditError, "Conflicting family"):
            audit_longitudinal_coverage(
                [document("inc", "US1B1"), document("llc", "US1B1", family_id="975")],
                [page("inc", "Example Inc.", 1, 1), page("llc", "Example LLC", 1, 1)],
                as_of_dates=["1999-12-31"],
            )

    def test_missing_and_inconsistent_publication_dates_are_visible(self):
        rows = [
            document("inc", "US1B1", publication_date=None, family_id="-1"),
            document("inc", "US2A1", publication_date="1997-12-31"),
        ]
        report = audit_longitudinal_coverage(
            rows, [page("inc", "Example Inc.", 2, 2)], as_of_dates=["1999-12-31"]
        )
        self.assertEqual(report["union"]["missing_family_rows"], 1)
        self.assertEqual(report["publication_date_snapshots"]["1999-12-31"]["unknown_or_inconsistent_publication_date"], 2)

    def test_out_of_scope_dates_are_rejected(self):
        with self.assertRaisesRegex(AuditError, "Filing date outside"):
            audit_longitudinal_coverage(
                [document("inc", "US1B1", filing_date="2000-01-01")],
                [page("inc", "Example Inc.", 1, 1)], as_of_dates=["1999-12-31"],
            )

    def test_finished_empty_query_is_retained(self):
        report = audit_longitudinal_coverage(
            [], [page("inc", "Example Inc.", 0, 0)], as_of_dates=["1999-12-31"]
        )
        self.assertEqual(report["query_audits"][0]["provider_total"], 0)
        self.assertEqual(report["union"]["publications"], 0)
