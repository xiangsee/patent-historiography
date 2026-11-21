"""Evidence-conservative patent procedural-history ledger.

A patent's dated events are not synonymous with adjudicated legal status.
Published claim versions, opposition filings, revocation *notices*, appeals,
maintained-as-amended records, and corporate registry names are DIFFERENT
evidence objects.

This module never fetches patent data, never infers patent validity,
and never concludes two similarly named companies are the same legal entity.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
import json

VERSION = "0.6.0"

SOURCE_CLASSES = frozenset({
    "official_publication_xml",
    "official_epo_decision_webpage",
    "secondary_legal_event_aggregation",
    "synthetic_test",
})
EVENT_KINDS = frozenset({
    "application_publication",
    "patent_grant_publication",
    "opposition_filed_record",
    "opponent_identity_record",
    "revocation_communication",
    "appeal_notice_record",
    "interlocutory_revision_record",
    "opposition_withdrawal_record",
    "maintained_as_amended_event",
    "amended_specification_publication",
    "party_as_published",
    "opposition_appeal_decision",
})
ROLE_TYPES = frozenset({
    "applicant", "proprietor", "opponent", "respondent",
    "representative", "appellant", "entity_as_published",
})
STATUS_EVENTS_THAT_ARE_NOT_FINAL = frozenset({
    "revocation_communication", "appeal_notice_record",
    "interlocutory_revision_record", "opposition_withdrawal_record",
    "opposition_filed_record", "opponent_identity_record",
})


class ProcedureLedgerError(ValueError):
    pass


def _date(s, label):
    if not isinstance(s, str) or not s:
        raise ProcedureLedgerError(label + " missing ISO date")
    try:
        return date.fromisoformat(s)
    except ValueError as err:
        raise ProcedureLedgerError(label + " malformed ISO date: " + s) from err


def verify_events(events):
    """Schema checks without guessing legal effect or corporate identity."""
    if not isinstance(events, list):
        raise ProcedureLedgerError("events must be a list")
    ids = set()
    for index, e in enumerate(events):
        if not isinstance(e, dict):
            raise ProcedureLedgerError("event must be a dictionary")
        identifier = e.get("event_id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            raise ProcedureLedgerError("event IDs must be unique non-empty strings")
        ids.add(identifier)
        subject = e.get("case_id")
        if not isinstance(subject, str) or not subject.strip():
            raise ProcedureLedgerError("case_id required")
        kind = e.get("event_kind")
        if kind not in EVENT_KINDS:
            raise ProcedureLedgerError("Unsupported procedural event kind: " + str(kind))
        _date(e.get("event_date"), "event_date")
        class_name = e.get("source_class")
        if class_name not in SOURCE_CLASSES:
            raise ProcedureLedgerError("Unknown source class: " + str(class_name))
        source = e.get("source_url")
        if (not isinstance(source, str) or not source.startswith("https://")
                or " " in source):
            raise ProcedureLedgerError("Unverified source URL for " + identifier)
        available = e.get("first_contemporaneously_available_on")
        if available is not None:
            available_date = _date(available, "first_contemporaneously_available_on")
            # A later publication of an earlier decision is expected; a
            # supposedly earlier public observation requires independent proof.
            if available_date < _date(e["event_date"], "event_date"):
                raise ProcedureLedgerError("Knowledge availability earlier than historical event")
            if class_name == "secondary_legal_event_aggregation":
                raise ProcedureLedgerError(
                    "Aggregator date cannot be asserted as contemporaneous public availability"
                )
        roles = e.get("participant_roles", [])
        if not isinstance(roles, list):
            raise ProcedureLedgerError("participant_roles must be list")
        for role in roles:
            if not isinstance(role, dict):
                raise ProcedureLedgerError("role must be a dictionary")
            if role.get("role") not in ROLE_TYPES:
                raise ProcedureLedgerError("unknown role")
            if not isinstance(role.get("entity_name"), str) or not role["entity_name"].strip():
                raise ProcedureLedgerError("role must identify a named entity")
        if kind == "revocation_communication" and e.get("final_revocation_confirmed") is True:
            raise ProcedureLedgerError(
                "A revocation communication is not proof of final revocation"
            )
        if kind == "opposition_withdrawal_record" and e.get("all_oppositions_withdrawn") is True:
            raise ProcedureLedgerError(
                "One indexed withdrawal does not establish all oppositions withdrawn"
            )
        if class_name == "secondary_legal_event_aggregation" and e.get("official_decision_text_verified") is True:
            raise ProcedureLedgerError(
                "Secondary legal-event index is not a verified original decision"
            )
    return True


def procedural_view(events, *, as_of, knowledge_as_of=None, case_id=None):
    """Two explicit clocks: when an event happened and when evidence could be known.

    retrospective: historical events dated <= as_of, interpreted with today's
    verified access. Secondary index records can appear but remain labeled.

    contemporaneously_observable: include only events with independently
    established first_contemporaneously_available_on <= knowledge_as_of.
    Secondary legal-event index records have UNKNOWN release dates and do
    not enter a contemporaneous public history just by assuming event date.
    """
    verify_events(events)
    when = _date(as_of, "as_of")
    knowledge = _date(knowledge_as_of or as_of, "knowledge_as_of")
    if knowledge < when:
        raise ProcedureLedgerError("knowledge_as_of earlier than as_of; choose a historical target")
    cohort = [e for e in events if
              (not case_id or e["case_id"] == case_id) and
              _date(e["event_date"], "event_date") <= when]
    cohort.sort(key=lambda e: (e["event_date"], e["event_id"]))
    seen = []
    unknown_availability = []
    for e in cohort:
        available = e.get("first_contemporaneously_available_on")
        if available is None:
            unknown_availability.append(e["event_id"])
        elif _date(available, "first_contemporaneously_available_on") <= knowledge:
            seen.append(e)
    def event_summary(e):
        return {
            "event_id": e["event_id"],
            "case_id": e["case_id"],
            "event_kind": e["event_kind"],
            "event_date": e["event_date"],
            "source_class": e["source_class"],
            "source_url": e["source_url"],
            "participant_roles": e.get("participant_roles", []),
            "first_contemporaneously_available_on": e.get("first_contemporaneously_available_on"),
            "summary_claim": e.get("summary_claim", ""),
            "original_decision_full_text_verified": e.get("official_decision_text_verified", False),
        }
    by_kind = Counter(e["event_kind"] for e in cohort)
    by_source = Counter(e["source_class"] for e in cohort)
    return {
        "as_of": as_of,
        "knowledge_as_of": knowledge_as_of or as_of,
        "case_id_filter": case_id,
        "historical_events_retrospectively_observed": [event_summary(e) for e in cohort],
        "events_known_from_contemporaneously_dated_evidence": [e["event_id"] for e in seen],
        "events_without_verified_contemporaneous_availability": unknown_availability,
        "counts_by_event_kind": dict(sorted(by_kind.items())),
        "counts_by_source_class": dict(sorted(by_source.items())),
        "status_note": (
            "Chronological observations only: revocation communications are not "
            "final revocation; amended B2 publication is not a reconstruction of the opposition decision."
        ),
        "legal_validity_or_title_as_of_independently_determined": False,
        # Completeness of an event ledger cannot be proven merely by
        # validating the few entries that were supplied. It requires a
        # separately audited full official file-wrapper/document register.
        "source_quality_ledger_complete": False,
        "full_official_case_file_inventory_audited": False,
    }


def compare_roles_across_cases(events, *, term_a, term_b):
    """Find cross-case role reversal candidates using explicit textual names.

    This is not entity resolution. Case-insensitive substring matches are
    flagged as exploratory. The exact legal persons remain unverified.
    """
    verify_events(events)
    if not term_a or not term_b or term_a.casefold() == term_b.casefold():
        raise ProcedureLedgerError("Two distinct nonblank research name substrings required")
    pairings = []
    for e in events:
        roles = e.get("participant_roles", [])
        matches_a = [r for r in roles if term_a.casefold() in r["entity_name"].casefold()]
        matches_b = [r for r in roles if term_b.casefold() in r["entity_name"].casefold()]
        if matches_a and matches_b:
            pairings.append({
                "case_id": e["case_id"],
                "event_id": e["event_id"],
                "event_date": e["event_date"],
                "source_class": e["source_class"],
                "party_a_names_and_roles": matches_a,
                "party_b_names_and_roles": matches_b,
                "source_url": e["source_url"],
            })
    directions = []
    for p in pairings:
        roles_a = {r["role"] for r in p["party_a_names_and_roles"]}
        roles_b = {r["role"] for r in p["party_b_names_and_roles"]}
        if "opponent" in roles_a and "applicant" in roles_b:
            directions.append({"case_id":p["case_id"],"direction":"A_opponent_B_applicant"})
        if "opponent" in roles_b and "proprietor" in roles_a:
            directions.append({"case_id":p["case_id"],"direction":"B_opponent_A_proprietor"})
    return {
        "search_name_substrings": [term_a, term_b],
        "cases_with_both_name_substrings": pairings,
        "observed_role_directions": directions,
        "opposite_party_roles_in_separate_cases_observed": len(set(d["direction"] for d in directions)) >= 2,
        "legal_entity_identity_verified": False,
        "corporate_group_membership_verified": False,
        "commercial_market_competition_strategy_proven": False,
        "caution": (
            "Name substring comparison is not identity resolution; documents concern "
            "distinct patents and proceedings and do not imply bilateral commercial intent."
        ),
    }

def review_claim_lifecycle(claims, events):
    """Validate explicit affected_claim/impact_type/verification_next metadata.

    Claim pointers must refer to actual event IDs in the researcher-supplied
    ledger, but resolving the pointers does NOT independently verify the
    underlying legal or scientific claims.
    """
    verify_events(events)
    if not isinstance(claims, list):
        raise ProcedureLedgerError("Claim Lifecycle must be a list")
    events_by_id = {e["event_id"]: e for e in events}
    ids = set()
    results = []
    for c in claims:
        if not isinstance(c, dict):
            raise ProcedureLedgerError("Claim entry must be a dict")
        cid = c.get("claim_id")
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ProcedureLedgerError("claim_id duplicate or missing")
        ids.add(cid)
        for field in ("affected_claim", "impact_type", "verification_next", "state"):
            if not isinstance(c.get(field), str) or not c[field].strip():
                raise ProcedureLedgerError("Claim Lifecycle must include " + field)
        evidence = c.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            raise ProcedureLedgerError("Each claim must name at least one evidence event")
        missing = [ref for ref in evidence if ref not in events_by_id]
        if missing:
            raise ProcedureLedgerError("Claim has missing event references: " + ", ".join(missing))
        source_mix = Counter(events_by_id[ref]["source_class"] for ref in evidence)
        results.append({
            "claim_id": cid,
            "affected_claim": c["affected_claim"],
            "impact_type": c["impact_type"],
            "verification_next": c["verification_next"],
            "state_from_researcher": c["state"],
            "evidence_event_ids": evidence,
            "evidence_sources_by_tier": dict(source_mix),
            "referenced_events_exist": True,
            "factual_claim_independently_proven_by_this_software": False,
        })
    return {
        "claim_count": len(results),
        "records": results,
        "event_references_resolve": True,
        "historical_claim_truth_not_automatically_verified": True,
    }
