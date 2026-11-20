import unittest
from patent_evidence.text_quality import cn_number_year, document_audit, audit_documents

MISSING={
 "requested":True,"original_completeness":"not_verified",
 "fields":{
   "description":{"status":"missing_in_index","index_has_any_text":False,"source_chars":0,"returned_chars":0,"truncated":False},
   "claims":{"status":"missing_in_index","index_has_any_text":False,"source_chars":0,"returned_chars":0,"truncated":False}
 }
}
class PatentDocumentQualityTests(unittest.TestCase):
    def test_cn_number_year(self):
        self.assertEqual(cn_number_year("CN-200710165788-A"),2007)
        self.assertIsNone(cn_number_year("CN-02134679-A"))
        self.assertIsNone(cn_number_year("US-200710165788-A"))

    def test_divisional_is_review_not_bad_year(self):
        r=document_audit({"publication_number":"CN-101166059-B",
            "application_number":"CN-200710165788-A",
            "filing_date":"2002-06-11",
            "parent":[{"type":"division","application_number":"CN-02112025-A"}],
            "full_text_status":MISSING})
        self.assertEqual(r["filing_date_review_alert"],"number_year_later_with_documented_divisional_parent")
        self.assertEqual(r["cn_application_number_year_candidate"],2007)
        self.assertEqual(r["description"]["availability_class"],"missing_in_current_provider_index")
        self.assertFalse(r["description"]["original_text_nonexistence_proved"])

    def test_same_year_mismatch_without_parent_requires_review(self):
        r=document_audit({"publication_number":"CN-1-B","application_number":"CN-200710165788-A",
            "filing_date":"2002-06-11","full_text_status":MISSING})
        self.assertEqual(r["filing_date_review_alert"],"number_year_conflict_needs_original_file_wrapper")

    def test_missing_index_is_not_absent_original(self):
        rec={"publication_number":"CN-1315292-C","application_number":"CN-02134679-A",
             "title_length":91,"abstract_length":500,"full_text_status":MISSING}
        a=audit_documents([rec])
        self.assertEqual(a["coverage_by_section"]["claims"]["missing_in_current_provider_index"],1)
        self.assertEqual(a["documents"][0]["abstract_chars_observed"],500)
        self.assertFalse(a["documents"][0]["abstract_full_original_verified"])

    def test_truncation_distinct_from_index_missing(self):
        status={"requested":True,"fields":{"description":{"status":"present","truncated":True,
                 "source_chars":10000,"returned_chars":500}}}
        r=document_audit({"publication_number":"CN-3-A","full_text_status":status})
        self.assertEqual(r["description"]["availability_class"],"truncated_in_provider_response")
        self.assertEqual(r["claims"]["availability_class"],"not_observed_in_response")

    def test_duplicate_publication_rejected(self):
        rec={"publication_number":"CN-1-A"}
        with self.assertRaises(ValueError):audit_documents([rec,rec])

if __name__ == "__main__":
    unittest.main()
