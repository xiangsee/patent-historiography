"""Research-grade temporal rights and patent priority links (stdlib-only).

IMPORTANT: An observed registry/aggregator entry is not an adjudication of
title, inventor contribution, patent validity, or actual product deployment.
Shared priorities identify *candidate* links, not certified EPO families.
"""
from __future__ import annotations

from datetime import date
from itertools import combinations
import re


def _parse_date(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field}: expected ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field}: invalid ISO date: {value}") from exc


def canonical_application(value):
    """Only syntax normalization. Does not resolve legal application equivalents."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Blank application identifier")
    return re.sub(r"[^A-Za-z0-9]", "", value).upper()


def priority_link_audit(documents):
    """Compare explicitly enumerated priority/parent claim sets, conservatively.

    Do NOT treat a shared *date* as shared priority. Do NOT treat identical
    provider-listed sets as EPO DOCDB simple families without official validation.
    """
    if not isinstance(documents, list):
        raise ValueError("documents must be a list")
    normalized = []
    seen = set()
    for d in documents:
        ident = d.get("document_id")
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise ValueError("Document IDs must be nonblank and unique")
        seen.add(ident)
        ids = d.get("related_priority_application_ids") or []
        if not isinstance(ids, list):
            raise ValueError("related_priority_application_ids must be a list")
        rawset = {canonical_application(v) for v in ids}
        own = d.get("application_number")
        if own:
            rawset.discard(canonical_application(own))
        normalized.append({
            "document_id": ident,
            "provider_family_id": d.get("provider_family_id"),
            "first_priority_date": d.get("first_priority_date"),
            "priority_applications": sorted(rawset),
            "source_scope": d.get("source_scope", "unverified_provider_preview"),
        })
    edges = []
    for left, right in combinations(normalized, 2):
        x = set(left["priority_applications"])
        y = set(right["priority_applications"])
        shared = sorted(x & y)
        if not x or not y:
            relation = "priority_identifiers_insufficient"
        elif x == y:
            relation = "same_reported_priority_set"
        elif shared:
            relation = "overlapping_reported_priority_identifiers"
        elif left["first_priority_date"] and left["first_priority_date"] == right["first_priority_date"]:
            relation = "same_priority_date_but_no_shared_identifier_observed"
        else:
            relation = "no_direct_shared_priority_observed"
        if left["first_priority_date"]:
            _parse_date(left["first_priority_date"], "first_priority_date")
        if right["first_priority_date"]:
            _parse_date(right["first_priority_date"], "first_priority_date")
        edges.append({
            "left": left["document_id"], "right": right["document_id"],
            "relation": relation, "shared_application_ids": shared,
            "same_provider_family_id": bool(left["provider_family_id"]
                                            and left["provider_family_id"] == right["provider_family_id"]),
            "is_official_epo_docdb_family_match": False,
            "is_official_epo_inpadoc_family_match": False,
            "source_scope": "provider_reported_not_official_epo_mapping",
        })
    return {
        "documents": normalized,
        "comparisons": edges,
        "epistemic_limitations": [
            "Same priority dates are not the same legal priority application identifiers.",
            "Shared provider-reported claims may include parent/continuation links; official EPO rules differ.",
            "No direct shared claim in the observed data does NOT establish that two applications are unrelated.",
            "This algorithm does not declare a DOCDB simple or INPADOC extended family.",
        ],
    }


def registry_snapshot(events, patent_id, as_of, knowledge_as_of=None):
    """An *evidence* snapshot, not a legal title determination.

    - as_of: historical date that the study asks about.
    - knowledge_as_of: latest registry/publication knowledge allowed.
      If omitted, uses as_of to avoid look-ahead bias.
    - date_effective missing means the recorded event is observable after
      its recording date, but cannot establish its true earlier effective day.
    """
    when = _parse_date(as_of, "as_of")
    known = _parse_date(knowledge_as_of or as_of, "knowledge_as_of")
    if known < when:
        # Earlier knowledge about a later target date is a valid question, but
        # no later event is considered when it has not been recorded.
        pass
    seen_ids = set()
    eligible = []
    not_yet_known = []
    uncertain_dates = []
    for e in events:
        if e.get("patent_id") != patent_id:
            continue
        eid = e.get("event_id")
        if not eid or eid in seen_ids:
            raise ValueError("Duplicate or missing rights event ID")
        seen_ids.add(eid)
        recorded = _parse_date(e.get("date_recorded"), "date_recorded")
        effective = _parse_date(e["date_effective"], "date_effective") if e.get("date_effective") else None
        event_kind = e.get("event_kind")
        if event_kind not in ("assignment", "name_change", "license", "merger", "correction"):
            raise ValueError("Unsupported legal-event kind " + str(event_kind))
        if recorded > known:
            not_yet_known.append(eid)
            continue
        if effective and effective > when:
            continue
        if not effective and recorded > when:
            uncertain_dates.append(eid)
            continue
        eligible.append((effective or recorded, recorded, e))
    eligible.sort(key=lambda item: (item[0], item[1], item[2]["event_id"]))
    holder = None
    label = None
    applied = []
    non_ownership = []
    for _, _, e in eligible:
        eid = e["event_id"]
        kind = e["event_kind"]
        if kind in ("assignment", "merger"):
            holder = e.get("to_entity")
            label = holder
            applied.append(eid)
        elif kind == "name_change":
            # A name change is NOT a newly acquired invention.
            if holder and (not e.get("from_entity") or e["from_entity"] == label):
                label = e.get("to_entity") or label
                applied.append(eid)
            else:
                non_ownership.append({"event_id": eid, "reason": "name_change_without_prior_rights_event"})
        elif kind == "license":
            non_ownership.append({"event_id": eid, "reason": "license_does_not_transfer_title"})
        else:
            non_ownership.append({"event_id": eid, "reason": "correction_does_not_establish_title"})
    return {
        "patent_id": patent_id,
        "historical_date": as_of,
        "knowledge_cutoff_date": knowledge_as_of or as_of,
        "last_recorded_interest_entity": holder,
        "current_label_for_that_recorded_interest": label,
        "applied_registry_event_ids": applied,
        "not_yet_recorded_by_knowledge_cutoff": not_yet_known,
        "event_date_unknown_for_target": uncertain_dates,
        "other_legal_events": non_ownership,
        "historical_legal_title_independently_confirmed": False,
        "inventor_or_technology_origin_confirmed": False,
        "interpretation": (
            "This is a chronology of observed registry/aggregator interests, not an "
            "adjudicated owner, and absence of earlier record is not proof of no rights."
        ),
    }
