# Patent Evidence Workbench (v0.4)

Run from the repository root using Python 3.10+. Existing data, lineage and text-availability tools use only the standard library. HTML parsing has an optional BeautifulSoup dependency.

~~~sh
python3 -m unittest discover -s tests -p 'test_patent_evidence.py' -v
python3 -m patent_evidence.cli audit --inputs '/private/batch*.json' --output /private/audit.json --require-complete
python3 -m patent_evidence.cli family-check --input data/examples/iphouse-family-api-10-sample-2026-11-19.json --output /private/family-check.json
~~~

Inputs: IPHouse batches containing query plus pages[].records or pages[].items, or self-contained local JSON arrays/JSONL. No network access, credentials or dependencies. The script produces a **derived quality report** and a small manual review queue, not raw redistribution or legal findings.

All family counts are unverified provider identifiers. Current assignee is not historical invention origin. Read the full method contract: [Patent Evidence Toolkit v0.1](../docs/PATENT_EVIDENCE_TOOLKIT_V0_1.md).

Development stages: ingest and QA (implemented) → official family and historical ownership verification → structured patent text, claim and citation analysis → five-form historiographical evidence links. Changes require synthetic tests and one real-data regression.

## v0.2｜优先权与历史权益的双时间研究（实际案例）

~~~sh
python3 -m unittest discover -s tests -p 'test_patent_*.py' -v
python3 -m patent_evidence.cli history-check --input data/examples/maps-priority-rights-v0-2.json --patent-id US20050270311A1 --as-of 2005-02-08 --output /tmp/maps-on-launch.json
python3 -m patent_evidence.cli history-check --input data/examples/maps-priority-rights-v0-2.json --patent-id US20050182770A1 --as-of 2005-04-26 --knowledge-as-of 2005-04-27 --output /tmp/geo-patent-backdated-interest.json
~~~

The rights output reports observed recorded interests, NOT adjudicated title. Related-priority comparisons are provider-based candidates, NOT official EPO DOCDB or INPADOC family memberships. Full documentation: [v0.2 method](../docs/PATENT_EVIDENCE_TOOLKIT_V0_2.md) and [Google Maps research](../research/16-google-maps-ownership-timeline-and-family-audit.md).

## v0.3｜Patent text coverage and divisional date review

~~~sh
python3 -m patent_evidence.cli text-check --input data/examples/cn2002-text-availability-v0-3.json --output /tmp/cn-text-coverage.json
python3 scripts/validate_cross_company_2026_11_20.py
~~~

3 connected Tencent/Huawei patent detail replies showed claims and description missing in this provider index, NOT a lack of claims in original patents. A Huawei 2007-numbered divisional retains 2002 original filing/priority metadata and has a parent link; it is flagged for legal chronology review, not blindly repaired. More: [tool v0.3](../docs/PATENT_EVIDENCE_TOOLKIT_V0_3.md).

## v0.4｜Source-located patent claims and multi-version texts

Install the optional HTML adapter requirements:

    python3 -m pip install -r requirements-document-parser.txt

Run from the repository root:

    python3 -m patent_evidence.cli parse-html \
      --input /private/CN101166059A_zh.html \
      --source-url https://patents.google.com/patent/CN101166059A/zh \
      --expected-publication CN101166059A \
      --output /private/cn101166059a_evidence_metadata.json

    python3 -m patent_evidence.cli compare-html \
      --first-input /private/CN101166059A_zh.html \
      --second-input /private/CN101166059B_zh.html \
      --first-url https://patents.google.com/patent/CN101166059A/zh \
      --second-url https://patents.google.com/patent/CN101166059B/zh \
      --first-publication CN101166059A \
      --second-publication CN101166059B \
      --output /private/cn_application_to_grant_diff.json

By default, NO full claim or description text is emitted—only source locators, IDs, counts, and normalized-content SHA-256 hashes. The explicit --private-text opt-in cannot write inside the public repository. Claims labelled independent/dependent are structural candidates, not official legal construction. Hash differences across versions are not evidence of changed protection scope without human review.

See [v0.4 method contract](../docs/PATENT_EVIDENCE_TOOLKIT_V0_4.md) and [six-page real derived public fixture](../data/examples/six-patent-publication-version-structures-2026-11-20.json).
