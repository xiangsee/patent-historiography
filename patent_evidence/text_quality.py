"""Audit provider document availability and CN divisional-date ambiguities.

This code DOES NOT infer that missing indexed text is absent from the
original patent, or that an application-number year is its legal filing year.
Only derived coverage status is exported, not copyrighted patent text.
"""
from __future__ import annotations
from collections import Counter
from datetime import date
import re


def cn_number_year(number):
    if not isinstance(number, str):
        return None
    norm = re.sub(r"[^A-Za-z0-9]", "", number).upper()
    match = re.match(r"^CN((?:19|20)\d{2})\d{5,}", norm)
    return int(match.group(1)) if match else None


def _year(value):
    try:
        return date.fromisoformat(value).year if isinstance(value, str) else None
    except ValueError:
        return None


def _section(record, field):
    status = record.get("full_text_status") or {}
    fields = status.get("fields") or {}
    source = fields.get(field) or {}
    provider_status = source.get("status", "not_observed_in_response")
    count = record.get(field + "_length")
    if count is None:
        raw = record.get(field)
        count = len(raw) if isinstance(raw, str) else 0
    returned = source.get("returned_chars")
    if not isinstance(returned, int):
        returned = count
    if source.get("truncated"):
        classification = "truncated_in_provider_response"
    elif provider_status == "missing_in_index":
        classification = "missing_in_current_provider_index"
    elif returned > 0:
        classification = "text_returned_completeness_unverified"
    elif provider_status in ("not_requested", "not_observed_in_response"):
        classification = provider_status
    elif source.get("source_chars", 0) and returned == 0:
        classification = "indexed_but_not_returned"
    else:
        classification = "unavailable_or_empty_unclassified"
    return {
        "availability_class": classification,
        "provider_status": provider_status,
        "returned_chars": returned,
        "provider_source_chars": source.get("source_chars"),
        "provider_truncated": bool(source.get("truncated")),
        "original_text_nonexistence_proved": False,
        "full_original_verified": False,
    }


def document_audit(record):
    pub = record.get("publication_number")
    if not isinstance(pub, str) or not pub:
        raise ValueError("document must have a publication_number")
    app = record.get("application_number")
    parents = record.get("parent") or []
    if not isinstance(parents, list):
        raise ValueError("parent must be a list")
    parent_types = sorted({str(p.get("type") or "unknown") for p in parents if isinstance(p, dict)})
    is_division = any(p.lower().startswith("divis") for p in parent_types)
    app_year = cn_number_year(app)
    filing_year = _year(record.get("filing_date"))
    if app_year and filing_year and app_year != filing_year:
        alert = ("number_year_later_with_documented_divisional_parent"
                 if is_division and app_year > filing_year else
                 "number_year_conflict_needs_original_file_wrapper")
    else:
        alert = "no_detected_mismatch_or_number_year_unknown"
    title_count = record.get("title_length")
    if title_count is None:
        title_count = len(record.get("title") or "")
    abstract_count = record.get("abstract_length")
    if abstract_count is None:
        abstract_count = len(record.get("abstract") or "")
    citations = record.get("citations_count")
    if citations is None and isinstance(record.get("citation"), list):
        citations = len(record["citation"])
    info = record.get("full_text_status") or {}
    return {
        "publication_number": pub,
        "application_number": app,
        "filing_date_as_reported": record.get("filing_date"),
        "priority_date_as_reported": record.get("priority_date"),
        "cn_application_number_year_candidate": app_year,
        "parent_relationship_types": parent_types,
        "filing_date_review_alert": alert,
        "title_chars_observed": title_count,
        "abstract_chars_observed": abstract_count,
        "abstract_full_original_verified": False,
        "full_text_requested": bool(info.get("requested")),
        "original_completeness_status": info.get("original_completeness", "not_verified"),
        "description": _section(record, "description"),
        "claims": _section(record, "claims"),
        "citations_count_observed": citations,
        "verified_against_official_full_document": False,
    }


def audit_documents(records):
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    rows = [document_audit(r) for r in records]
    if len({r["publication_number"] for r in rows}) != len(rows):
        raise ValueError("duplicate publication number in text audit input")
    statuses = {}
    for section in ("description", "claims"):
        statuses[section] = dict(Counter(r[section]["availability_class"] for r in rows))
    return {
        "records_audited": len(rows),
        "coverage_by_section": statuses,
        "number_year_divisional_review_count": sum(
            r["filing_date_review_alert"] == "number_year_later_with_documented_divisional_parent"
            for r in rows),
        "number_year_unexplained_review_count": sum(
            r["filing_date_review_alert"] == "number_year_conflict_needs_original_file_wrapper"
            for r in rows),
        "documents": rows,
        "limits": [
            "missing_in_current_provider_index does not mean the patent lacks original claims or description",
            "CN application number year is a heuristic, not proof of actual filing date",
            "a divisional may share an effective filing date with its parent while having a later application number",
            "abstract and text completeness require an original document, not an index-length heuristic",
            "this report contains availability metadata only, not original patent full text",
        ]
    }
