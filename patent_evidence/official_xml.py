"""Read-only XML source adapter for *actual* EPO EP Patent Document and
official WIPO ST.96 PatentPublication examples.

This is an evidence extraction adapter, NOT validation against a DTD/XSD.
Original XML stays in a private/copyright-reviewed research environment.
Outputs only source identifiers, section counts, XML element locators and
SHA-256 of whitespace-normalized segment text. No network or DTD retrieval.

EPO documents may contain claim translations in several languages.
Claim node count across translations is not the number of legal claims.

WIPO Annex VII is an official schema example marked TEST, NOT a real patent.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ADAPTER_VERSION = "0.5.0"
COM = "http://www.wipo.int/standards/XMLSchema/ST96/Common"
PAT = "http://www.wipo.int/standards/XMLSchema/ST96/Patent"
MAX_XML_BYTES = 10_000_000


class PatentXMLParseError(ValueError):
    pass


def _ln(tag):
    return tag.rsplit("}", 1)[-1]


def _children(node, name):
    return [e for e in node if _ln(e.tag) == name]


def _desc(node, name):
    return [e for e in node.iter() if _ln(e.tag) == name]


def _first(node, name):
    if node is None:
        return None
    for e in node.iter():
        if _ln(e.tag) == name:
            return e
    return None


def _normalize(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _node_text(node):
    return _normalize("".join(node.itertext())) if node is not None else ""


def _hash(text):
    return sha256(_normalize(text).encode("utf-8")).hexdigest()


def _meta_segment(source_url, pub, field, index, node, text, *, language=None):
    xml_id = node.get("id") or node.get("{" + COM + "}id")
    number = str(index)
    if xml_id:
        locator = "#" + xml_id
        how = "xml_id_on_original_source_document_not_web_link_guarantee"
    else:
        locator = "/#/" + field + "/" + (language + "/" if language else "") + number
        how = "derived_structural_locator_not_xpath"
    return {
        "evidence_id": pub + ":" + field.upper() + ":" + (
            (language + ":") if language else "") + number,
        "number": number,
        "xml_id": xml_id,
        "xml_locator": locator,
        "xml_locator_type": how,
        "source_document_uri": source_url,
        "language": language,
        "normalized_text_chars": len(_normalize(text)),
        "sha256_normalized_utf8_text": _hash(text),
        "full_segment_text_in_public_output": False,
        "original_legal_text_against_independent_official_facsimile_verified": False,
    }


def _parse_input(raw, expected_tag):
    if not isinstance(raw, (bytes, str)):
        raise PatentXMLParseError("Expected XML bytes or string")
    data = raw if isinstance(raw, bytes) else raw.encode("utf-8")
    if len(data) > MAX_XML_BYTES:
        raise PatentXMLParseError("XML exceeds bounded sample size; chunking not supported")
    upper = data.upper()
    # Use ElementTree's internal parser only; fail closed on custom entity
    # declarations, and do not expand or fetch external DTD entities.
    if b"<!ENTITY" in upper or b"<![CDATA[" in upper and b"<!ENTITY" in upper:
        raise PatentXMLParseError("Custom ENTITY declaration not allowed")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise PatentXMLParseError("Malformed or unsupported XML/DTD entity") from exc
    if _ln(root.tag) != expected_tag:
        raise PatentXMLParseError("Unexpected XML root: " + _ln(root.tag))
    return root, sha256(data).hexdigest(), len(data)


def _source_uri_check(source_url, allowed_hosts):
    parsed = urlparse(source_url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise PatentXMLParseError("Source URL must be unchanged HTTPS on official allowed host")
    return source_url


def _iso_yyyymmdd(value):
    if not value:
        return None
    if re.fullmatch(r"\d{8}", value):
        return value[:4] + "-" + value[4:6] + "-" + value[6:]
    return value


def _validate_claim_numbers(numbers, issues, scope):
    if not numbers:
        issues.append(scope + "_no_claims")
        return
    if len(set(numbers)) != len(numbers):
        issues.append(scope + "_duplicate_claim_number")
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        issues.append(scope + "_claim_number_gaps")


def parse_ep_patent_document(raw, *, source_url, expected_publication=None, allow_no_claims=False):
    """Parse an EPO authoritative EP XML publication, retaining claim languages.

    EPO EP Patent Document variants share important structural elements;
    validated real samples include v1.1 B1/A1 and v1.4 B1/B2. This is not
    comprehensive validation of all historical EP DTD versions.
    """
    _source_uri_check(source_url, {"data.epo.org"})
    root, digest, nbytes = _parse_input(raw, "ep-patent-document")
    if root.tag != "ep-patent-document":
        raise PatentXMLParseError("Unexpected namespace for EPO EP document")
    office = root.get("country", "")
    docnum = root.get("doc-number", "")
    kind = root.get("kind", "")
    if not (office == "EP" and docnum and kind):
        raise PatentXMLParseError("Missing EP publication identity attributes")
    pub = "EP" + docnum + kind
    if expected_publication and pub != expected_publication:
        raise PatentXMLParseError("Mismatched expected EPO publication: " + pub)

    title_by_language = {}
    for group in _desc(root, "B540"):
        for child in _children(group, "B541"):
            siblings = list(group)
            idx = siblings.index(child)
            lang = _node_text(child).lower()
            if idx + 1 < len(siblings) and _ln(siblings[idx + 1].tag) == "B542":
                title_by_language[lang] = _node_text(siblings[idx + 1])
    # INID-style bibliographic party tags have different meanings:
    # B711 applicant in A publications; B731 proprietor in B specifications.
    # These labels are published assertions, not a reconstructed transfer chain.
    parties = {
        "A_document_applicant_B711": sorted(set(
            _node_text(_first(e, "snm")) for e in _desc(root, "B711")
            if _first(e, "snm") is not None
        )),
        "B_document_proprietor_B731": sorted(set(
            _node_text(_first(e, "snm")) for e in _desc(root, "B731")
            if _first(e, "snm") is not None
        )),
    }
    issues = []
    claim_by_lang = {}
    claim_nodes_total = 0
    for section in _children(root, "claims"):
        lang = (section.get("lang") or "unknown").lower()
        if lang in claim_by_lang:
            issues.append("duplicate_claim_language_group_" + lang)
            continue
        claims = []
        numbers = []
        for i, c in enumerate(_children(section, "claim"), start=1):
            n = c.get("num")
            if not n or not n.isdigit():
                issues.append("invalid_claim_number_" + lang)
                continue
            claim_no = int(n)
            numbers.append(claim_no)
            txt = _node_text(c)
            seg = _meta_segment(source_url, pub, "CLAIM", claim_no, c, txt, language=lang)
            seg["claim_number"] = claim_no
            seg["claim_type_status"] = "NOT_INFERRED_FROM_XML: no generic EPO claim-reference element asserted"
            seg["explicit_structured_claim_reference_ids"] = []
            claims.append(seg)
        _validate_claim_numbers(numbers, issues, lang)
        claim_by_lang[lang] = claims
        claim_nodes_total += len(claims)
    if not claim_by_lang and not allow_no_claims:
        raise PatentXMLParseError("EPO XML has no claim language groups")
    if not claim_by_lang:
        primary = None
        primary_count = None
        counts = {}
        issues.append("no_claim_language_groups_in_this_XML_not_proof_original_patent_lacks_claims")
    else:
        primary = (root.get("lang") or "en").lower()
        if primary not in claim_by_lang:
            primary = next(iter(claim_by_lang))
            issues.append("primary_claim_language_fallback")
        primary_count = len(claim_by_lang[primary])
        counts = {k: len(v) for k, v in claim_by_lang.items()}
        if any(k != primary_count for k in counts.values()):
            issues.append("claim_counts_differ_across_languages_review")
    desc = _first(root, "description")
    desc_segments = []
    if desc is not None:
        for i, n in enumerate(_desc(desc, "p"), start=1):
            number = n.get("num") or str(i)
            seg = _meta_segment(source_url, pub, "DESC", number, n, _node_text(n),
                                language=(desc.get("lang") or primary).lower())
            desc_segments.append(seg)
    if not desc_segments:
        issues.append("missing_numbered_description")
    cits = _desc(root, "patcit")
    return {
        "source_format": "EPO_EP_PATENT_DOCUMENT_ST36_FAMILY",
        "parser_version": ADAPTER_VERSION,
        "source_status": "official_EPO_publication_XML_real_patent",
        "source_url": source_url,
        "source_xml_sha256": digest,
        "source_xml_bytes": nbytes,
        "document_publication": pub,
        "document_root_id_as_issued": root.get("id"),
        "publication_date": _iso_yyyymmdd(root.get("date-publ")),
        "document_kind": kind,
        "schema_or_dtd_version_as_declared": root.get("dtd-version"),
        "publication_number_identity_route": "root.country+root.doc-number+root.kind_not_root_id",
        "title_by_language": title_by_language,
        "parties_as_published": parties,
        "proprietor_or_applicant_not_independently_audited_to_assignment_documents": True,
        "primary_claim_language": primary,
        "claim_groups": claim_by_lang,
        "claim_counts_per_language": counts,
        "claims_primary_language_count": primary_count,
        "claim_nodes_all_languages": claim_nodes_total,
        "claims_present_in_this_XML": bool(claim_by_lang),
        "absence_from_XML_is_not_proof_original_published_patent_had_no_claims": True,
        "description_paragraphs": desc_segments,
        "description_primary_language": (desc.get("lang") if desc is not None else None),
        "patent_citation_nodes_observed": len(cits),
        "quality": {
            "issues": sorted(set(issues)),
            "translation_groups_must_not_be_summed_as_inventions": True,
            "EPO_claims_language_equivalence_legally_verified": False,
            "dtd_or_xsd_schema_validation_completed": False,
            "official_issued_legal_claim_construction_verified": False,
            "full_original_xml_redistribution_authorized": False,
        },
    }


def parse_wipo_st96_patent_publication(raw, *, source_url):
    """Parse official WIPO Annex VII schema example (synthetic patent data)."""
    _source_uri_check(source_url, {"www.wipo.int"})
    root, digest, nbytes = _parse_input(raw, "PatentPublication")
    if root.tag != "{" + PAT + "}PatentPublication":
        raise PatentXMLParseError("Unexpected namespace for WIPO ST.96")
    version = root.get("{" + COM + "}st96Version")
    doc_status = root.get("{" + COM + "}documentStatusText")
    language = root.get("{" + COM + "}languageCode") or "unknown"
    bibl = _first(root, "BibliographicData")
    ident = _first(bibl, "PatentPublicationIdentification") if bibl is not None else None
    if ident is None:
        raise PatentXMLParseError("Missing patent publication identification")
    get_id=lambda key: _node_text(_first(ident, key))
    office, docnum, kind = get_id("IPOfficeCode"), get_id("PublicationNumber"), get_id("PatentDocumentKindCode")
    pub = office + docnum + kind
    if not (office and docnum and kind):
        raise PatentXMLParseError("Incomplete publication identity")
    title_element = _first(bibl, "InventionTitle") if bibl is not None else None
    title = _node_text(title_element)
    claims_parent = _first(root, "Claims")
    if claims_parent is None:
        raise PatentXMLParseError("Missing ST96 Claims element")
    claim_elems = _children(claims_parent, "Claim")
    claim_ids = {}
    for claim in claim_elems:
        n = _node_text(_first(claim, "ClaimNumber"))
        ident = claim.get("{" + COM + "}id")
        if ident and n.isdigit():
            claim_ids[ident] = int(n)
    numbers = []
    claims = []
    issues = []
    class_counter = Counter()
    for claim in claim_elems:
        n_raw = _node_text(_first(claim, "ClaimNumber"))
        if not n_raw.isdigit():
            issues.append("unparseable_claim_number")
            continue
        n = int(n_raw)
        numbers.append(n)
        # ClaimText can contain XHTML/MathML content. Keep native order.
        text = " ".join(_node_text(t) for t in _children(claim, "ClaimText"))
        seg = _meta_segment(source_url, pub, "CLAIM", n, claim, text, language=language)
        seg["claim_number"] = n
        kind_text = _node_text(_first(claim, "ClaimTypeCategory")) or "unknown"
        seg["claim_type_as_reported_by_sample"] = kind_text
        class_counter[kind_text] += 1
        refs = []
        unresolved = []
        for t in _desc(claim, "ClaimReference"):
            for ident in t.get("{" + COM + "}idrefs", "").split():
                if ident in claim_ids:
                    refs.append(claim_ids[ident])
                else:
                    unresolved.append(ident)
        seg["structured_claim_refs"] = sorted(set(refs))
        seg["unresolved_xml_ids"] = sorted(set(unresolved))
        seg["official_sample_legal_effect_confirmed"] = False
        if unresolved:
            issues.append("unresolved_st96_claim_reference")
        claims.append(seg)
    _validate_claim_numbers(numbers, issues, "st96")
    claim_total = _first(bibl, "ClaimTotalQuantity") if bibl is not None else None
    if claim_total is not None:
        tot = _node_text(claim_total)
        if tot.isdigit() and int(tot) != len(claims):
            issues.append("st96_bibliographic_claim_total_differs_from_body")
    description = _first(root, "Description")
    segments = []
    if description is not None:
        for i, para in enumerate(_desc(description, "P"), start=1):
            number = para.get("{" + COM + "}pNumber") or str(i)
            seg = _meta_segment(source_url, pub, "DESC", number, para,
                                _node_text(para), language=language)
            segments.append(seg)
    if not segments:
        issues.append("no_description_paragraphs")
    abstract = _first(root, "Abstract")
    abstract_txt = _node_text(abstract)
    citations = _desc(bibl, "ReferenceCitation") if bibl is not None else []
    return {
        "source_format": "WIPO_ST96_PATENT_PUBLICATION_XML",
        "parser_version": ADAPTER_VERSION,
        "source_status": (
            "WIPO_official_Annex_VII_TEST_example_not_real_patent"
            if doc_status == "TEST" and "/annex-vii/" in source_url
            else "WIPO_site_ST96_document_reality_and_source_status_unverified"
        ),
        "source_url": source_url,
        "source_xml_sha256": digest,
        "source_xml_bytes": nbytes,
        "schema_or_dtd_version_as_declared": version,
        "wipo_example_directory_version_is_not_schema_version": True,
        "document_status_as_declared": doc_status,
        "document_publication": pub,
        "publication_date": _node_text(_first(_first(bibl, "PatentPublicationIdentification"), "PublicationDate")),
        "title_as_example": title,
        "source_language": language,
        "claim_group": claims,
        "claims_numbered_count": len(claims),
        "claim_types_from_sample": dict(class_counter),
        "description_paragraphs": segments,
        "abstract_metadata": {
            "normalized_text_chars": len(abstract_txt),
            "sha256_normalized_utf8_text": _hash(abstract_txt),
        },
        "reference_citation_nodes_observed": len(citations),
        "quality": {
            "issues": sorted(set(issues)),
            "this_is_real_patent": False if doc_status == "TEST" else None,
            "WIPO_schema_validation_completed": False,
            "underlying_sample_claim_legal_effect_validated": False,
            "full_XML_redistribution_rights_reviewed": False,
        },
    }
