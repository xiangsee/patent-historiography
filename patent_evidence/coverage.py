"""Coverage and publication chronology of bounded provider queries."""

from collections import Counter, defaultdict
from hashlib import sha256

from .core import AuditError, date_or_none, family, key, pagination


def _identifiers(row):
    return {
        "application": key(row.get("application_number")),
        "family": family(row.get("family_id")),
        "office": row.get("country_code"),
        "filing": date_or_none(row.get("filing_date")),
        "publication": date_or_none(row.get("publication_date")),
        "priority": date_or_none(row.get("priority_date")),
    }


def _summary(documents):
    return {
        "publications": len(documents),
        "application_numbers": len({d["application"] for d in documents if d["application"]}),
        "provider_family_ids": len({d["family"] for d in documents if d["family"]}),
        "missing_application_rows": sum(d["application"] is None for d in documents),
        "missing_family_rows": sum(d["family"] is None for d in documents),
        "missing_priority_rows": sum(d["priority"] is None for d in documents),
        "earlier_priority_year_rows": sum(
            bool(d["priority"] and d["priority"].year < d["filing"].year) for d in documents
        ),
        "publication_offices": dict(Counter(d["office"] or "UNKNOWN" for d in documents)),
    }


def _digest(publication_ids):
    return sha256("\n".join(sorted(publication_ids)).encode("utf-8")).hexdigest()


def audit_longitudinal_coverage(rows, pages, *, as_of_dates, before=None):
    """Require complete windows, then de-duplicate publications and count source-date coverage.

    A publication date is evidence about the document's release date only. The
    matching name is a query filter applied to the provider snapshot today.
    """
    reports = pagination(pages)
    if not reports or any(not report["complete"] for report in reports):
        raise AuditError("At least one declared query window is missing or incomplete")
    if any(page["provider_total"] is None for page in pages):
        raise AuditError("Each page must report the provider total")
    page_lengths = defaultdict(dict)
    for page in pages:
        page_lengths[page["query_id"]][page["page"]] = page["returned"]
    cutoffs = {value: date_or_none(value) for value in as_of_dates}
    before_date = date_or_none(before)
    if not cutoffs or not all(cutoffs.values()) or (before is not None and not before_date):
        raise AuditError("Use YYYY-MM-DD for publication cutoffs and --before")

    windows = {}
    for report in reports:
        query = report["query"]
        name = query.get("assignee")
        start = date_or_none(query.get("filing_date_from"))
        end = date_or_none(query.get("filing_date_to"))
        if not isinstance(name, str) or not name.strip() or not start or not end or start > end:
            raise AuditError("Each query needs an assignee and an ordered filing-date window")
        windows[report["query_id"]] = (name, start, end)

    by_window = defaultdict(dict)
    source_ids = defaultdict(set)
    publications = {}
    names = defaultdict(set)
    for row in rows:
        qid = row.get("_query_id")
        if qid not in windows:
            raise AuditError("Row lacks a declared query window")
        name, start, end = windows[qid]
        pub_id = key(row.get("publication_number"))
        if not pub_id or pub_id in by_window[qid]:
            raise AuditError(f"Missing or duplicate publication identifier in {qid}: {pub_id}")
        document = _identifiers(row)
        if not document["filing"] or not start <= document["filing"] <= end:
            raise AuditError(f"Filing date outside declared window for {pub_id}")
        by_window[qid][pub_id] = document
        source_ids[qid].add(str(row["publication_number"]))
        merged = publications.setdefault(pub_id, document.copy())
        for field, value in document.items():
            if value is None:
                continue
            if merged[field] is not None and merged[field] != value:
                raise AuditError(f"Conflicting {field} for {pub_id} across query windows")
            merged[field] = value
        names[pub_id].add(name)

    query_audits = []
    for report in reports:
        qid = report["query_id"]
        results = by_window[qid]
        if len(results) != report["provider_total"]:
            raise AuditError(f"Unique publications do not match provider total for {qid}")
        query_audits.append({
            "query": report["query"],
            "page_count": report["page_count"],
            "returned_by_page": [page_lengths[qid][i] for i in range(1, report["page_count"] + 1)],
            "provider_total": report["provider_total"],
            "counts": _summary(list(results.values())),
            "input_sha256_by_batch": report["file_sha256"],
            "sorted_publication_ids_sha256": _digest(results),
            "sorted_source_publication_ids_sha256": _digest(source_ids[qid]),
        })

    by_year = defaultdict(list)
    for pub_id, document in publications.items():
        by_year[document["filing"].year].append(pub_id)

    def coverage(pub_ids):
        return {
            **_summary([publications[pub_id] for pub_id in pub_ids]),
            "matches_by_assignee_filter": dict(Counter(name for pub_id in pub_ids for name in names[pub_id])),
            "multiple_assignee_filter_matches": sum(len(names[pub_id]) > 1 for pub_id in pub_ids),
        }

    snapshots = {}
    for label, cutoff in sorted(cutoffs.items()):
        eligible = [d for d in publications.values() if d["filing"] <= cutoff]
        dated = [d["publication"] for d in eligible
                 if d.get("publication") and d["publication"] >= d["filing"]]
        snapshots[label] = {
            "matched_filing_dates_through_cutoff": len(eligible),
            "reported_published_by_cutoff": sum(day <= cutoff for day in dated),
            "reported_published_after_cutoff": sum(day > cutoff for day in dated),
            "unknown_or_inconsistent_publication_date": len(eligible) - len(dated),
        }

    return {
        "scope": "retrospective provider query matches; no historical ownership or invention attribution",
        "query_audits": sorted(query_audits, key=lambda a: (a["query"]["filing_date_from"], a["query"]["assignee"])),
        "union": coverage(list(publications)),
        "sorted_publication_ids_sha256": _digest(publications),
        "by_filing_year": {str(year): coverage(ids) for year, ids in sorted(by_year.items())},
        "publication_date_snapshots": snapshots,
        "filings_before": {"date": before, **coverage([
            pub_id for pub_id, d in publications.items() if d["filing"] < before_date
        ])} if before_date else None,
    }
