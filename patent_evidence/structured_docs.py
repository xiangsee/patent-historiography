"""Bounded, evidence-preserving parser for Google Patents HTML.

This is a PROVIDER ADAPTER, not a WIPO ST.96/ST.97 or USPTO official parser.
No network calls. Raw source HTML stays with the researcher; public derived
output omits all full description/claim text by default.

Optional private_text=True retains the extracted text for authorized local
analysis. Never publish that private output without a separate rights review.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from urllib.parse import urlparse
import re


ADAPTER_VERSION = "0.4.0"


class DocumentParseError(ValueError):
    """A publication cannot be structurally parsed or verified."""


def _normalize_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _sha(text):
    return sha256(_normalize_text(text).encode("utf-8")).hexdigest()


def _meta(soup, name, *, scheme=None):
    tags = soup.find_all("meta", attrs={"name": name})
    for tag in tags:
        if scheme is not None and tag.get("scheme") != scheme:
            continue
        if scheme is None and tag.get("scheme"):
            continue
        value = tag.get("content")
        if value:
            return _normalize_text(value)
    return None


def _locate(source_url, element, fallback):
    anchor = element.get("id")
    return source_url + "#" + anchor if anchor else source_url + "#" + fallback


def _segment(number, element, text, source_url, locator_fallback, private_text):
    row = {
        "number_as_published": str(number),
        "html_anchor": element.get("id"),
        "source_locator": _locate(source_url, element, locator_fallback),
        "normalized_text_char_count": len(text),
        "sha256_utf8_normalized_text": _sha(text),
        "sha256_semantics": "UTF-8 of whitespace-normalized extracted DOM text",
        "original_source_pdf_text_match_verified": False,
    }
    if private_text:
        row["private_extracted_text"] = text
    return row


def parse_google_patents_html(
    source_html,
    *,
    source_url,
    expected_publication=None,
    private_text=False,
    source_retrieved_at=None,
    strict=True,
):
    """Parse ONE public Google Patents HTML page into evidence segment records.

    Outputs:
      - bibliographic title/application/publication as rendered by provider
      - numbered claim nodes and explicit claim-ref edges
      - numbered description paragraphs and per-segment source hashes
      - abstract hash and provider page citation count
      - uncertainty/quality flags; never decides validity or actual deployment

    A claim with no explicit refs is an INDEPENDENT CANDIDATE only, not a legal
    claim construction. A provider hyperlink can omit implied range semantics.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise DocumentParseError(
            "HTML adapter requires beautifulsoup4: pip install -r requirements-document-parser.txt"
        ) from exc

    u = urlparse(source_url)
    if u.scheme != "https" or u.hostname != "patents.google.com":
        raise DocumentParseError("source_url must be an unchanged Google Patents HTTPS URL")
    if not isinstance(source_html, (bytes, str)):
        raise DocumentParseError("source_html must be original HTML bytes or UTF-8 string")
    html_bytes = (source_html if isinstance(source_html, bytes)
                  else source_html.encode("utf-8"))
    soup = BeautifulSoup(source_html, "html.parser")
    ref = _meta(soup, "citation_patent_publication_number")
    if not ref or ":" not in ref:
        raise DocumentParseError("No unambiguous citation_patent_publication_number in source")
    publication = re.sub(r"[^A-Za-z0-9]", "", ref).upper()
    if expected_publication and re.sub(r"[^A-Za-z0-9]", "", expected_publication).upper() != publication:
        raise DocumentParseError("Expected publication does not match rendered HTML metadata")

    title = _meta(soup, "DC.title")
    if not title:
        raise DocumentParseError("Missing DC.title; refuse to parse an unidentified document")

    claims_section = soup.select_one('section[itemprop="claims"]')
    description_section = soup.select_one('section[itemprop="description"]')
    abstract_section = soup.select_one('section[itemprop="abstract"]')
    if not claims_section or not description_section:
        raise DocumentParseError("Missing claims/description section in provider HTML")
    count_tag = claims_section.select_one('[itemprop="count"]')
    if not count_tag or not count_tag.get_text(strip=True).isdigit():
        raise DocumentParseError("Provider did not declare a numeric claim count")
    declared_count = int(count_tag.get_text(strip=True))
    claim_nodes = claims_section.select('div.claim[num]')

    issues = []
    claim_map = {}
    numbers = []
    for n in claim_nodes:
        raw_num = n.get("num")
        try:
            num = int(raw_num)
        except (TypeError, ValueError):
            issues.append("invalid_claim_number")
            continue
        if n.get("id"):
            claim_map[n.get("id")] = num
        numbers.append(num)
    if len(claim_nodes) != declared_count:
        issues.append("claims_count_disagrees_with_html_header")
    if len(set(numbers)) != len(numbers):
        issues.append("duplicate_claim_number")
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        issues.append("gaps_or_nonsequential_claim_numbers")

    claims = []
    classification = Counter()
    edges = []
    for node in claim_nodes:
        try:
            number = int(node.get("num"))
        except (ValueError, TypeError):
            continue
        text = _normalize_text(node.get_text(" ", strip=True))
        ref_ids = [x.get("idref") for x in node.select("claim-ref[idref]")]
        mapped = [claim_map.get(x) for x in ref_ids]
        unknown = [x for x in ref_ids if x not in claim_map]
        refs = sorted(set(x for x in mapped if x is not None))
        # No XML/HTML claim-ref link, but the text mentions a claim number:
        # flag ambiguity rather than incorrectly declaring independence.
        has_unlinked_ref_text = (
            not ref_ids and bool(re.search(r"(?:权利要求\s*\d+|\bclaims?\s+\d+\b)", text, flags=re.I))
        )
        if unknown:
            claim_type = "unresolved_reference"
            issues.append("unresolved_claim_ref")
        elif refs:
            claim_type = "dependent_candidate_explicit_links"
        elif has_unlinked_ref_text:
            claim_type = "claim_type_unresolved_unlinked_reference_text"
            issues.append("possible_unlinked_claim_reference")
        else:
            claim_type = "independent_candidate_no_explicit_references"
        classification[claim_type] += 1
        if any(x >= number for x in refs):
            issues.append("self_or_forward_claim_reference")
        base = _segment(number, node, text, source_url, "claim-" + str(number), private_text)
        base.update({
            "number": number,
            "provider_claim_id": node.get("id"),
            "claim_type_candidate": claim_type,
            "explicit_reference_target_anchors": ref_ids,
            "explicit_reference_claim_numbers": refs,
            "unresolved_reference_anchors": unknown,
            "dependent_claim_reference_exhaustiveness_verified": False,
            "legal_claim_type_independently_verified": False,
        })
        claims.append(base)
        for destination in refs:
            edges.append({
                "from_claim_number": number,
                "referenced_claim_number": destination,
                "source_locator": base["source_locator"],
                "relation": "explicit_html_claim_ref_not_exhaustive_legal_dependency",
            })

    container = description_section.select_one('[itemprop="content"]')
    if not container:
        raise DocumentParseError("No description content container")
    paragraphs = container.select('div.description-paragraph[num], div.description-line[num]')
    descriptions = []
    para_ids = set()
    for n in paragraphs:
        text = _normalize_text(n.get_text(" ", strip=True))
        num = n.get("num")
        ident = n.get("id")
        if ident and ident in para_ids:
            issues.append("duplicate_description_anchor")
        para_ids.add(ident)
        descriptions.append(_segment(num, n, text, source_url, "description-" + str(num), private_text))
    if not descriptions:
        issues.append("no_numbered_description_paragraphs")

    abstract_content = (abstract_section.select_one('[itemprop="content"]')
                        if abstract_section else None)
    abstract_text = (_normalize_text(abstract_content.get_text(" ", strip=True))
                     if abstract_content else "")
    if not abstract_text:
        issues.append("abstract_missing_on_provider_page")

    source_lang = None
    c = claims_section.select_one('[lang]')
    if c:
        source_lang = c.get("lang")
    if not source_lang:
        c = description_section.select_one('[lang]')
        source_lang = c.get("lang") if c else None

    citations = []
    citation_rows = soup.select('tr[itemprop="backwardReferences"]')
    for row in citation_rows:
        element = row.select_one('[itemprop="publicationNumber"]')
        val = _normalize_text(element.get_text(" ", strip=True)) if element else None
        if val:
            citations.append(val)
    meta_cite = [_normalize_text(t.get("content")) for t in
                 soup.select('meta[name="DC.relation"][scheme="references"]')
                 if t.get("content")]

    publication_date = _meta(soup, "DC.date")
    date_submitted = _meta(soup, "DC.date", scheme="dateSubmitted")
    app = _meta(soup, "citation_patent_application_number")
    abstract = {
        "source_locator": source_url + "#abstract",
        "normalized_text_char_count": len(abstract_text),
        "sha256_utf8_normalized_text": _sha(abstract_text) if abstract_text else None,
        "original_source_pdf_text_match_verified": False,
    }
    if private_text:
        abstract["private_extracted_text"] = abstract_text

    result = {
        "adapter": "google_patents_html",
        "adapter_version": ADAPTER_VERSION,
        "source_url": source_url,
        "source_provider": "Google Patents public HTML viewer (NOT issuing patent office)",
        "html_retrieved_at": source_retrieved_at,
        "source_html_sha256": sha256(html_bytes).hexdigest(),
        "source_html_bytes": len(html_bytes),
        "publication_number": publication,
        "publication_number_as_provider_meta": ref,
        "application_number_as_provider_meta": app,
        "title_as_published": title,
        "source_language": source_lang,
        "kind_code_as_provider_meta": ref.split(":")[-1],
        "publication_date_as_provider_meta": publication_date,
        "dc_date_submitted_as_provider_meta": date_submitted,
        "do_not_infer_divisional_actual_filing_date_from_dc_date": True,
        "abstract": abstract,
        "claims": claims,
        "claim_dependency_edges": edges,
        "description_paragraphs": descriptions,
        "backward_citation_table": {
            "row_count": len(citation_rows),
            "publication_numbers_as_rendered": citations,
            "dc_relation_references_count": len(meta_cite),
            "not_guaranteed_official_complete": True,
        },
        "counts": {
            "claims_declared_in_html": declared_count,
            "claims_numbered_extracted": len(claims),
            "claim_classifications": dict(sorted(classification.items())),
            "description_numbered_paragraphs": len(descriptions),
            "explicit_claim_reference_edges": len(edges),
        },
        "quality": {
            "structural_issues": sorted(set(issues)),
            "count_and_numbering_check_passed": not any(x in issues for x in [
                "claims_count_disagrees_with_html_header",
                "duplicate_claim_number",
                "gaps_or_nonsequential_claim_numbers",
            ]),
            "official_issuing_office_original_verified": False,
            "publication_version_compared_to_grant": False,
            "all_legal_claim_dependencies_resolved": False,
            "independent_claims_are_only_candidates": True,
            "full_text_rights_republication_cleared": False,
            "private_text_included": bool(private_text),
        },
    }
    if strict and issues:
        raise DocumentParseError("Strict structural audit failed: " + ", ".join(sorted(set(issues))))
    return result

