import json
from pathlib import Path
import tempfile
import unittest

from patent_evidence.core import analyse, load, pagination, family_interface_audit, key, family


def rec(pub, app, fam, filing, country="US", title="Method", assignee=None, priority=None):
    return {
        "publication_number": pub,
        "application_number": app,
        "family_id": fam,
        "country_code": country,
        "filing_date": filing,
        "priority_date": priority or filing,
        "title": title,
        "assignee": assignee or ["Alpha Research"],
        "kind_code": pub.split("-")[-1],
    }


class PatentEvidenceTest(unittest.TestCase):
    def test_identifier_and_missing_family(self):
        self.assertEqual(key("US-00001234-A1"), "US00001234A1")
        self.assertEqual(key("us00001234a1"), "US00001234A1")
        self.assertIsNone(family("-1"))
        self.assertIsNone(family(None))

    def test_document_application_family_are_distinct_units(self):
        rows = [
            rec("US-001-A1", "US-APP001", "100", "2001-02-01"),
            rec("US-001-B2", "US-APP001", "100", "2001-02-01"),
            rec("CN-001-A", "CN-APP001", "100", "2002-01-10", "CN",
                "Method with adaptation", ["Different Corp"], "2001-02-01"),
            rec("US-002-A1", "US-APP002", "-1", "2002-05-01"),
            rec("US-003-A1", "US-APP003", "200", "2003-06-01"),
        ]
        a = analyse(rows,focus_name="Alpha",review_limit=2)
        self.assertEqual(a["source_rows"], 5)
        self.assertEqual(a["unique_publications"], 5)
        self.assertEqual(a["unique_applications"], 4)
        self.assertEqual(a["distinct_provider_family_ids"], 2)
        self.assertEqual(a["missing_or_sentinel_family_rows"], 1)
        self.assertEqual(a["family_risk_counts"]["multiple_authorities"], 1)
        self.assertEqual(a["family_risk_counts"]["multiple_filing_years"], 1)
        self.assertEqual(a["non_focus_assignee_tagged_rows"], 1)
        self.assertEqual(a["priority_before_filing_rows"], 1)
        self.assertEqual(len(a["family_review_queue"]),2)
        self.assertEqual(a["verified_family_type"],"UNVERIFIED")

    def test_duplicate_document_is_flagged(self):
        r = rec("US-001-A1","US-APP001","111","2001-01-01")
        a = analyse([r,r])
        self.assertEqual(a["source_rows"],2)
        self.assertEqual(a["unique_publications"],1)
        self.assertEqual(a["duplicate_publication_rows"],1)

    def test_complete_multi_file_pagination(self):
        with tempfile.TemporaryDirectory() as tmp:
            query={"assignee":"Google Inc.","page_size":2}
            for page, count in [(1,2),(2,1)]:
                d={"query":query,"pages":[
                    {"page":page,"total":3,"items":[rec(f"US-{page}{i}-A1",f"APP{page}{i}",
                                                      "100", "2001-01-01") for i in range(count)]}
                ]}
                Path(tmp,f"part{page}.json").write_text(json.dumps(d),encoding="utf8")
            rows,pages=load([str(Path(tmp,"part*.json"))])
            self.assertEqual(len(rows),3)
            self.assertTrue(pagination(pages)[0]["complete"])
            subset_rows,subset_pages=load([str(Path(tmp,"part1.json"))])
            self.assertEqual(len(subset_rows),2)
            self.assertFalse(pagination(subset_pages)[0]["complete"])
            self.assertEqual(pagination(subset_pages)[0]["issues"],["incomplete_provider_result"])

    def test_jsonl_local_export_is_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp,"export.jsonl")
            f.write_text(json.dumps(rec("US-01-A1","APP1","10","2001-01-01"))+"\n",encoding="utf8")
            records,pages=load([str(f)])
            self.assertEqual(len(records),1)
            self.assertTrue(pagination(pages)[0]["complete"])

    def test_missing_page_number(self):
        page={"query_id":"a","query":{"page_size":1},"page":2,"returned":1,
              "provider_total":1,"error":None,"source_file":"mock","source_sha256":"abc"}
        self.assertIn("missing_or_duplicate_page_number",pagination([page])[0]["issues"])

    def test_cross_query_family_is_not_additive(self):
        x=rec("US-001-A1","APP1","10","2001-01-01")
        y=rec("US-002-A1","APP2","10","2002-01-01")
        x["_query_id"]="query_2001"
        y["_query_id"]="query_2002"
        a=analyse([x,y])
        self.assertEqual(a["distinct_provider_family_ids"],1)
        self.assertEqual(a["family_risk_counts"]["cross_query_window"],1)

    def test_family_interface_count_mismatch_and_list_anchor(self):
        res=family_interface_audit([
            {"search_patents_total":358,"family_detail_size":51,
             "family_detail_members_listed":50,"anchor_not_in_members":True},
            {"search_patents_total":10,"family_detail_size":10,
             "family_detail_members_listed":9,"anchor_not_in_members":True},
        ])
        self.assertEqual(res["mismatch_count"],1)
        self.assertEqual(res["possible_50_cap_count"],1)
        self.assertIn("ANCHOR_EXCLUDED_FROM_MEMBER_LIST",res["items"][0]["flags"])


if __name__ == "__main__":
    unittest.main()
