"""Command-line interface: patent data, family API, and historical evidence QA."""
import argparse
import json
from pathlib import Path
import sys
from .core import AuditError, load, pagination, analyse, family_interface_audit
from .lineage import priority_link_audit, registry_snapshot

VERSION="0.2.0"

def main(argv=None):
    p=argparse.ArgumentParser(description="Patent data quality workbench: local data, no network")
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("audit")
    a.add_argument("--inputs",nargs="+",required=True)
    a.add_argument("--output",required=True)
    a.add_argument("--focus-name")
    a.add_argument("--review-limit",type=int,default=10)
    a.add_argument("--require-complete",action="store_true")
    f=sub.add_parser("family-check")
    f.add_argument("--input",required=True)
    f.add_argument("--output",required=True)
    h=sub.add_parser("history-check",help="Compare priority claims and registered interests as-of date")
    h.add_argument("--input",required=True,help="JSON fixture with documents and rights_events")
    h.add_argument("--output",required=True)
    h.add_argument("--patent-id",required=True,help="One patent/document identifier from fixture")
    h.add_argument("--as-of",required=True,help="Historical ISO date YYYY-MM-DD")
    h.add_argument("--knowledge-as-of",help="Only filings/recordings known by this ISO date")
    args=p.parse_args(argv)
    try:
        if args.cmd=="audit":
            rows,pages=load(args.inputs)
            page_reports=pagination(pages)
            if args.require_complete and any(not x["complete"] for x in page_reports):
                raise AuditError("At least one query window incomplete")
            result={"tool":"patent_evidence","version":VERSION,
                    "data_scope":"provider_observations_not_full_corporate_corpus",
                    "provider_family_type":"UNVERIFIED","historical_ownership":"NOT_DETERMINED",
                    "query_audits":page_reports,"aggregate":analyse(
                        rows,focus_name=args.focus_name,review_limit=args.review_limit)}
        elif args.cmd=="family-check":
            obj=json.loads(Path(args.input).read_text(encoding="utf8"))
            result=family_interface_audit(obj["samples"])
            result["tool"]="patent_evidence"
            result["version"]=VERSION
        else:
            obj=json.loads(Path(args.input).read_text(encoding="utf8"))
            ids={x.get("document_id") for x in obj["documents"]}
            if args.patent_id not in ids:
                raise AuditError("Patent not in reference case: "+args.patent_id)
            result={
                "tool":"patent_evidence",
                "version":VERSION,
                "case_id":obj.get("case_id"),
                "priority_evidence":priority_link_audit(obj["documents"]),
                "registered_interests":registry_snapshot(
                    obj["rights_events"],args.patent_id,args.as_of,args.knowledge_as_of
                ),
                "scope":"provider/aggregator evidence only; not an official EPO family or adjudicated patent title",
            }
        target=Path(args.output)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                          encoding="utf8")
        print(json.dumps({"output":str(target),"tool_version":VERSION,
                          "rows":result.get("aggregate",{}).get("source_rows"),
                          "family_api_mismatches":result.get("mismatch_count"),
                          "historical_date":result.get("registered_interests",{}).get("historical_date")},
                         ensure_ascii=False))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print("PATENT_EVIDENCE_ERROR "+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
