"""Synthetic, locally authored XML. Never commit official full patent texts."""
import re
import unittest
from patent_evidence.official_xml import (
    PatentXMLParseError, parse_ep_patent_document, parse_wipo_st96_patent_publication,
)
EPO_URL="https://data.epo.org/publication-server/rest/v1.2/patents/EP0123456NWB1/document.xml"
WIPO_URL="https://www.wipo.int/standards/en/st96/v10-0/annex-vii/PatentPublication_Example.xml"
EPO=b'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ep-patent-document PUBLIC "-//EPO//EP PATENT DOCUMENT 1.4//EN" "ep-patent-document-v1-4.dtd">
<ep-patent-document id="EP98765432B1" country="EP" doc-number="0123456" kind="B1" lang="en" date-publ="20251120" dtd-version="ep-patent-document-v1-4">
<SDOBI><B540><B541>en</B541><B542>Synthetic sensor for seeds</B542></B540></SDOBI>
<description id="desc" lang="en"><p id="p0001" num="0001">This is a test.</p><p id="p0002" num="0002">A seed is inspected.</p></description>
<claims lang="en"><claim id="c-en-01-0001" num="0001"><claim-text>1. A sensor.</claim-text></claim><claim id="c-en-01-0002" num="0002"><claim-text>2. The sensor of claim 1.</claim-text></claim></claims>
<claims lang="de"><claim id="c-de-01-0001" num="0001"><claim-text>1. Sensor.</claim-text></claim><claim id="c-de-01-0002" num="0002"><claim-text>2. Sensor nach Anspruch 1.</claim-text></claim></claims>
<claims lang="fr"><claim id="c-fr-01-0001" num="0001"><claim-text>1. Capteur.</claim-text></claim><claim id="c-fr-01-0002" num="0002"><claim-text>2. Capteur selon la revendication 1.</claim-text></claim></claims>
<ep-reference-list><patcit id="pat1" dnum="US1000000A1"/></ep-reference-list>
</ep-patent-document>'''
WIPO=b'''<pat:PatentPublication xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent"
 xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common"
 com:st96Version="V8_0" com:languageCode="en" com:documentStatusText="TEST">
<pat:BibliographicData>
<pat:PatentPublicationIdentification><com:IPOfficeCode>ZX</com:IPOfficeCode><com:PublicationNumber>7654321</com:PublicationNumber><pat:PatentDocumentKindCode>B2</pat:PatentDocumentKindCode><com:PublicationDate>2025-11-20</com:PublicationDate></pat:PatentPublicationIdentification>
<pat:InventionTitleBag><pat:InventionTitle>Synthetic seed process</pat:InventionTitle></pat:InventionTitleBag>
<pat:ClaimTotalQuantity>2</pat:ClaimTotalQuantity>
<pat:ReferenceCitationBag><pat:ReferenceCitation><pat:PatentCitation>Sample only</pat:PatentCitation></pat:ReferenceCitation></pat:ReferenceCitationBag>
</pat:BibliographicData>
<pat:Description><com:P com:id="p-0001" com:pNumber="0001">This is a test description.</com:P></pat:Description>
<pat:Claims>
<pat:Claim com:id="CLM-00001"><pat:ClaimNumber>1</pat:ClaimNumber><pat:ClaimTypeCategory>Independent</pat:ClaimTypeCategory><pat:ClaimText>1. A tiny sensor.</pat:ClaimText></pat:Claim>
<pat:Claim com:id="CLM-00002"><pat:ClaimNumber>2</pat:ClaimNumber><pat:ClaimTypeCategory>Dependent</pat:ClaimTypeCategory><pat:ClaimText>2. The sensor of <pat:ClaimReference com:idrefs="CLM-00001">claim 1</pat:ClaimReference>.</pat:ClaimText></pat:Claim>
</pat:Claims>
<pat:Abstract><com:P>Example only.</com:P></pat:Abstract>
</pat:PatentPublication>'''

class OfficialXMLTests(unittest.TestCase):
    def test_ep_claim_translations_do_not_become_new_claims(self):
        d=parse_ep_patent_document(EPO,source_url=EPO_URL,expected_publication="EP0123456B1")
        self.assertEqual(d["claim_counts_per_language"],{"en":2,"de":2,"fr":2})
        self.assertEqual(d["claims_primary_language_count"],2)
        self.assertEqual(d["claim_nodes_all_languages"],6)
        self.assertEqual(len(d["description_paragraphs"]),2)
        self.assertEqual(d["patent_citation_nodes_observed"],1)
        self.assertEqual(d["document_publication"],"EP0123456B1")
        self.assertEqual(d["document_root_id_as_issued"],"EP98765432B1")
        self.assertFalse(d["quality"]["dtd_or_xsd_schema_validation_completed"])

    def test_ep_mismatched_translation_counts_are_not_silent(self):
        x=EPO.replace(b'<claim id="c-fr-01-0002" num="0002"><claim-text>2. Capteur selon la revendication 1.</claim-text></claim>',b'')
        a=parse_ep_patent_document(x,source_url=EPO_URL)
        self.assertIn("claim_counts_differ_across_languages_review",a["quality"]["issues"])

    def test_wipo_claim_numbers_refs_and_test_status(self):
        a=parse_wipo_st96_patent_publication(WIPO,source_url=WIPO_URL)
        self.assertEqual(a["document_publication"],"ZX7654321B2")
        self.assertEqual(a["claims_numbered_count"],2)
        self.assertEqual(a["claim_types_from_sample"],{"Independent":1,"Dependent":1})
        self.assertEqual(a["claim_group"][1]["structured_claim_refs"],[1])
        self.assertEqual(a["description_paragraphs"][0]["xml_id"],"p-0001")
        self.assertEqual(a["reference_citation_nodes_observed"],1)
        self.assertEqual(a["schema_or_dtd_version_as_declared"],"V8_0")
        self.assertEqual(a["document_status_as_declared"],"TEST")
        self.assertFalse(a["quality"]["this_is_real_patent"])

    def test_wipo_bibl_count_mismatch_flagged(self):
        xml=WIPO.replace(b"<pat:ClaimTotalQuantity>2</pat:ClaimTotalQuantity>",
                         b"<pat:ClaimTotalQuantity>3</pat:ClaimTotalQuantity>")
        a=parse_wipo_st96_patent_publication(xml,source_url=WIPO_URL)
        self.assertIn("st96_bibliographic_claim_total_differs_from_body",a["quality"]["issues"])

    def test_untrusted_url_or_wrong_pub_rejected(self):
        with self.assertRaises(PatentXMLParseError):
            parse_ep_patent_document(EPO,source_url=EPO_URL,expected_publication="EP9999999B1")
        with self.assertRaises(PatentXMLParseError):
            parse_wipo_st96_patent_publication(WIPO,source_url="https://invalid.example/example.xml")

    def test_custom_entity_blocked_before_parsing(self):
        xml=EPO.replace(b'<!DOCTYPE ep-patent-document PUBLIC "-//EPO//EP PATENT DOCUMENT 1.4//EN" "ep-patent-document-v1-4.dtd">',
                        b'<!DOCTYPE ep-patent-document [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>')
        with self.assertRaises(PatentXMLParseError):
            parse_ep_patent_document(xml,source_url=EPO_URL)

    def test_missing_all_claim_groups_rejected(self):
        xml=re.sub(rb'<claims[^>]*>.*?</claims>',b'',EPO,flags=re.S)
        with self.assertRaises(PatentXMLParseError):
            parse_ep_patent_document(xml,source_url=EPO_URL)

    def test_bibliographic_only_ep_xml_explicitly_allowed(self):
        xml=re.sub(rb'<claims[^>]*>.*?</claims>',b'',EPO,flags=re.S)
        xml=re.sub(rb'<description[^>]*>.*?</description>',b'',xml,flags=re.S)
        xml=xml.replace(b'kind="B1"',b'kind="A1"')
        with self.assertRaises(PatentXMLParseError):
            parse_ep_patent_document(xml,source_url=EPO_URL)
        a=parse_ep_patent_document(xml,source_url=EPO_URL,
                                   expected_publication="EP0123456A1",
                                   allow_no_claims=True)
        self.assertFalse(a["claims_present_in_this_XML"])
        self.assertIsNone(a["claims_primary_language_count"])
        self.assertEqual(a["description_paragraphs"],[])
        self.assertTrue(a["absence_from_XML_is_not_proof_original_published_patent_had_no_claims"])

    def test_official_ep_version_diff_is_not_claim_scope_legal_opinion(self):
        from patent_evidence.official_version_diff import compare_ep_publication_versions
        a=parse_ep_patent_document(EPO,source_url=EPO_URL)
        xml=EPO.replace(b'kind="B1"',b'kind="B2"').replace(b'date-publ="20251120"',b'date-publ="20261120"')
        xml=re.sub(rb'<claim[^>]*num="0002".*?</claim>',b'',xml,flags=re.S)
        b=parse_ep_patent_document(xml,source_url=EPO_URL)
        d=compare_ep_publication_versions(a,b)
        self.assertEqual((d["first_primary_claims"],d["second_primary_claims"]),(2,1))
        self.assertEqual(d["first_all_language_claim_nodes"],6)
        self.assertEqual(d["second_all_language_claim_nodes"],3)
        self.assertEqual(d["first_unmatched_claim_positions"],[2])
        self.assertEqual(d["second_kind_semantics_from_EPO"],
                         "New European patent specification after opposition procedure")
        self.assertFalse(d["legal_scope_change_magnitude_inferred"])

    def test_nonmatching_namespaces_rejected(self):
        xml=WIPO.replace(b"http://www.wipo.int/standards/XMLSchema/ST96/Patent",
                         b"http://invalid.example/Patent")
        with self.assertRaises(PatentXMLParseError):
            parse_wipo_st96_patent_publication(xml,source_url=WIPO_URL)

if __name__=="__main__":
    unittest.main()
