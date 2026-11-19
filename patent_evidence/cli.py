"""Python -m patent_evidence.cli audit / family-check."""
import argparse
import json
from pathlib import Path
import sys
from .core import AuditError, load, pagination, analyse, family_interface_audit

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
    args=p.parse_args(argv)
    try:
        if args.cmd=="audit":
            rows,pages=load(args.inputs)
            page_reports=pagination(pages)
            if args.require_complete and any(not x["complete"] for x in page_reports):
                raise AuditError("At least one query window incomplete")
            result={"tool":"patent_evidence","version":"0.1.0",
                    "data_scope":"provider_observations_not_full_corporate_corpus",
                    "provider_family_type":"UNVERIFIED","historical_ownership":"NOT_DETERMINED",
                    "query_audits":page_reports,"aggregate":analyse(
                        rows,focus_name=args.focus_name,review_limit=args.review_limit)}
        else:
            obj=json.loads(Path(args.input).read_text(encoding="utf8"))
            result=family_interface_audit(obj["samples"])
            result["tool"]="patent_evidence"
            result["version"]="0.1.0"
        target=Path(args.output)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                          encoding="utf8")
        print(json.dumps({"output":str(target),"tool_version":"0.1.0",
                          "rows":result.get("aggregate",{}).get("source_rows"),
                          "family_api_mismatches":result.get("mismatch_count")},ensure_ascii=False))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print("PATENT_EVIDENCE_ERROR "+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
