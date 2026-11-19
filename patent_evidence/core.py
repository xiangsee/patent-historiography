"""Standard-library patent dataset QA.  Never infer invention or ownership from a family ID."""
from __future__ import annotations
import collections
import datetime
import glob
import hashlib
import json
import pathlib
import re

class AuditError(ValueError):
    pass

def key(value):
    """Comparable identifier, preserving raw identifier in the original record."""
    if value is None or str(value).strip() in ("", "-1"):
        return None
    return re.sub(r"[^0-9a-z]", "", str(value).lower()).upper() or None

def family(value):
    if value is None:
        return None
    v=str(value).strip()
    return v if v.upper() not in ("", "-1", "NULL", "NONE", "N/A") else None

def date_or_none(value):
    try:
        return datetime.date.fromisoformat(value) if isinstance(value,str) else None
    except ValueError:
        return None

def load(paths):
    """Read local IPHouse batch JSON with pages[].items/records, JSON arrays or JSONL.

    Returns private rows and page manifest. Public export is derived only.
    """
    sources=[]
    for pattern in paths:
        matches=sorted(glob.glob(pattern))
        if not matches:
            raise AuditError("input path/glob did not match: "+pattern)
        sources.extend(matches)
    rows=[]
    pages=[]
    seen=set()
    for filename in sources:
        path=pathlib.Path(filename).resolve()
        if path in seen:
            continue
        seen.add(path)
        content=path.read_text(encoding="utf8")
        digest=hashlib.sha256(content.encode("utf8")).hexdigest()
        if path.suffix==".jsonl":
            query={"source_type":"jsonl","file":path.name}
            page_list=[{"page":1,"records":[json.loads(x) for x in content.splitlines() if x.strip()]}]
        else:
            obj=json.loads(content)
            if isinstance(obj,list):
                query={"source_type":"json_list","file":path.name}
                page_list=[{"page":1,"records":obj}]
            elif isinstance(obj,dict):
                query=obj.get("query") or {"source_type":"object","file":path.name}
                if isinstance(obj.get("pages"),list):
                    page_list=obj["pages"]
                else:
                    records=obj.get("records",obj.get("items",obj.get("data")))
                    if not isinstance(records,list):
                        raise AuditError("no recognized records in "+str(path))
                    page_list=[{"page":obj.get("page",1),"records":records,"total":obj.get("total")}]
            else:
                raise AuditError("unsupported JSON shape "+str(path))
        qid=hashlib.sha256(json.dumps(query,ensure_ascii=False,sort_keys=True).encode("utf8")).hexdigest()[:16]
        for page in page_list:
            payload=page.get("records")
            if payload is None:
                payload=page.get("items")
            if not isinstance(payload,list):
                raise AuditError("missing records/items in "+str(path))
            pno=page.get("page")
            if not isinstance(pno,int) or pno<1:
                raise AuditError("invalid page number in "+str(path))
            total=page.get("reported_total",page.get("total"))
            if total is not None and not isinstance(total,int):
                raise AuditError("invalid provider total")
            pages.append({"query_id":qid,"query":query,"page":pno,"returned":len(payload),
                          "provider_total":total,"error":page.get("error"),
                          "source_file":path.name,"source_sha256":digest})
            for patent in payload:
                if not isinstance(patent,dict):
                    raise AuditError("one patent row is not an object")
                copied=dict(patent)
                copied["_query_id"]=qid
                rows.append(copied)
    return rows,pages

def pagination(pages):
    out=[]
    groups=collections.defaultdict(list)
    for page in pages:
        groups[page["query_id"]].append(page)
    for qid, ps in sorted(groups.items()):
        ps.sort(key=lambda p:p["page"])
        totals={p["provider_total"] for p in ps if p["provider_total"] is not None}
        observed=sum(p["returned"] for p in ps)
        issues=[]
        if [p["page"] for p in ps]!=list(range(1,len(ps)+1)):
            issues.append("missing_or_duplicate_page_number")
        if len(totals)!=1:
            issues.append("unknown_or_inconsistent_provider_total")
        total=next(iter(totals)) if len(totals)==1 else None
        if total is not None and observed!=total:
            issues.append("incomplete_provider_result")
        if any(p["error"] for p in ps):
            issues.append("page_error")
        size=ps[0]["query"].get("page_size")
        if size and any(p["returned"]>size for p in ps):
            issues.append("page_exceeds_declared_page_size")
        out.append({"query_id":qid,"query":ps[0]["query"],"page_count":len(ps),
                    "provider_total":total,"returned":observed,"complete":not issues,
                    "issues":issues,
                    "file_sha256":dict(sorted({p["source_file"]:p["source_sha256"] for p in ps}.items()))})
    return out

def analyse(rows, *, focus_name=None, review_limit=10):
    pubs=collections.Counter()
    apps=set()
    families=collections.defaultdict(list)
    years=collections.Counter()
    countries=collections.Counter()
    kind=collections.Counter()
    missing_family=0
    malformed_dates=0
    earlier_priority=0
    later_priority=0
    other_assignee_rows=0
    for r in rows:
        pub=key(r.get("publication_number"))
        if pub:
            pubs[pub]+=1
        app=key(r.get("application_number"))
        if app:
            apps.add(app)
        fam=family(r.get("family_id"))
        if fam:
            families[fam].append(r)
        else:
            missing_family+=1
        dt=date_or_none(r.get("filing_date"))
        pr=date_or_none(r.get("priority_date"))
        if r.get("filing_date") and not dt:
            malformed_dates+=1
        if dt and pr:
            earlier_priority+=int(pr<dt)
            later_priority+=int(pr>dt)
        years[str(dt.year) if dt else "UNKNOWN"]+=1
        countries[str(r.get("country_code") or "UNKNOWN")]+=1
        kind[str(r.get("kind_code") or "UNKNOWN")]+=1
        if focus_name:
            names=r.get("assignee") or []
            if isinstance(names,str):
                names=[names]
            if any(focus_name.lower() not in str(n).lower() for n in names):
                other_assignee_rows+=1
    risk=collections.Counter()
    review=[]
    for fid,members in families.items():
        offices={r.get("country_code") for r in members}
        filing_years={str(r.get("filing_date") or "")[:4] for r in members}
        titles={str(r.get("title") or "").strip().casefold() for r in members if r.get("title")}
        priorities={str(r["priority_date"]) for r in members if r.get("priority_date")}
        queries={r.get("_query_id") for r in members}
        names={str(n) for r in members for n in
               ([r["assignee"]] if isinstance(r.get("assignee"),str) else (r.get("assignee") or []))}
        flags=[]
        for condition,flag in [
            (len(members)>1,"multiple_publications"),
            (len(offices)>1,"multiple_authorities"),
            (len(filing_years)>1,"multiple_filing_years"),
            (len(titles)>1,"multiple_titles_not_multiple_inventions"),
            (len(priorities)>1,"different_provider_priority_dates"),
            (len(names)>1,"assignee_strings_vary_not_owner_proof"),
            (len(queries)>1,"cross_query_window"),
        ]:
            if condition:
                risk[flag]+=1
                flags.append(flag)
        review.append({"provider_family_id":fid,"publication_count":len(members),
                       "application_count":len({key(r.get("application_number")) for r in members
                                                if r.get("application_number")}),
                       "authorities":sorted(str(x) for x in offices),
                       "title_variants":len(titles),"flags":flags,
                       "sample_publication":members[0].get("publication_number")})
    review.sort(key=lambda row:(-len(row["flags"]),-row["publication_count"],
                                row["provider_family_id"]))
    return {
      "source_rows":len(rows),"unique_publications":len(pubs),
      "duplicate_publication_rows":sum(n-1 for n in pubs.values()),
      "unique_applications":len(apps),"distinct_provider_family_ids":len(families),
      "missing_or_sentinel_family_rows":missing_family,
      "family_risk_counts":dict(risk),
      "bad_filing_date_rows":malformed_dates,
      "priority_before_filing_rows":earlier_priority,
      "priority_after_filing_rows":later_priority,
      "non_focus_assignee_tagged_rows":other_assignee_rows if focus_name else None,
      "by_filing_year_document_rows":dict(sorted(years.items())),
      "by_publication_authority_document_rows":dict(sorted(countries.items())),
      "by_kind_document_rows":dict(sorted(kind.items())),
      "sha256_sorted_publication_ids":hashlib.sha256(
          "\n".join(sorted(pubs)).encode("utf8")).hexdigest(),
      "family_review_queue":review[:max(0,review_limit)],
      "verified_family_type":"UNVERIFIED",
      "proven_original_owners":"NOT_DETERMINED",
      "notice":"All counts are provider matches or records, not independent inventions or historical original ownership."
    }

def family_interface_audit(samples):
    out=[]
    for item in samples:
        row=dict(item)
        flags=[]
        sr=row.get("search_patents_total")
        fs=row.get("family_detail_size")
        m=row.get("family_detail_members_listed")
        if None in (sr,fs,m):
            flags.append("MISSING_INTERFACE_MEASUREMENT")
        else:
            if sr!=fs:
                flags.append("PROVIDER_INTERFACE_SCOPE_OR_LIMIT_MISMATCH")
            if m==50 and sr>fs:
                flags.append("POSSIBLE_MEMBER_RETURN_CAP_50")
            if row.get("anchor_not_in_members") and m+1==fs:
                flags.append("ANCHOR_EXCLUDED_FROM_MEMBER_LIST")
        row["flags"]=flags
        row["epo_simple_or_extended_verified"]=False
        out.append(row)
    return {"sample_size":len(out),
            "mismatch_count":sum("PROVIDER_INTERFACE_SCOPE_OR_LIMIT_MISMATCH" in x["flags"] for x in out),
            "possible_50_cap_count":sum("POSSIBLE_MEMBER_RETURN_CAP_50" in x["flags"] for x in out),
            "items":out,
            "warning":"Never treat family_size or provider_family_id as independent inventions or verified EPO family type."}
