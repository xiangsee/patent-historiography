# Patent Evidence Workbench (v0.7)

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


## v0.5｜Official EPO XML and WIPO ST.96 TEST files

The official XML adapter uses only Python standard library and **local files**; it never downloads external resources or resolves remote DTD entities.

    python3 -m patent_evidence.cli official-xml --format epo \
      --input /private/EP0729353NWB1.xml \
      --source-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB1/document.xml \
      --expected-publication EP0729353B1 \
      --output /private/ep-b1-structure.json

    python3 -m patent_evidence.cli official-xml --format epo \
      --input /private/EP0729353NWA1.xml \
      --source-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWA1/document.xml \
      --expected-publication EP0729353A1 \
      --allow-no-claims \
      --output /private/ep-a1-bibliographic-only.json

    python3 -m patent_evidence.cli compare-epo \
      --first-input /private/EP0729353NWB1.xml --second-input /private/EP0729353NWB2.xml \
      --first-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB1/document.xml \
      --second-url https://data.epo.org/publication-server/rest/v1.2/patents/EP0729353NWB2/document.xml \
      --first-publication EP0729353B1 --second-publication EP0729353B2 \
      --output /private/ep-opposition-delta.json

The EPO adapter parses each claim language separately; primary-language claim count is NOT the total across translations. WIPO Annex VII XML is a TEST example, not a real patent; the document-declared ST.96 version controls parsing. Only source-linked hashes and quality metadata may be shared by default.

[Official XML v0.5 method contract](../docs/PATENT_EVIDENCE_TOOLKIT_V0_5.md) · [Real EP timeline research](../research/19-alkermes-ep-postgrant-and-official-xml.md).


## v0.6｜Procedural event ledger, source tiers, role network

    python3 -m patent_evidence.cli procedure-check \
      --input data/examples/epo-cross-case-procedural-events-2026-11-21.json \
      --case-id EP0729353 --as-of 2005-07-20 \
      --output /tmp/procedure_as_of_2005.json

    python3 -m patent_evidence.cli procedure-check \
      --input data/examples/epo-cross-case-procedural-events-2026-11-21.json \
      --as-of 2012-09-12 --party-a Alkermes --party-b "Southern Research" \
      --output /tmp/role_candidates_2012.json

    python3 scripts/validate_ep_procedural_ledger_v06.py

A revocation notice is not a final revocation. A secondary event index's recorded event_date is not assumed to be its historical publication date. The cross-case name substring match is exploratory and never constitutes legal entity resolution or proof of commercial strategy.

See [v0.6 methods](../docs/PATENT_EVIDENCE_TOOLKIT_V0_6.md) and [historical report](../research/20-alkermes-sri-opposition-network.md).

## v0.7 Longitudinal query coverage and publication dates

```sh
python3 -m patent_evidence.cli coverage-check \
  --inputs '/private/google/*.batch.json' \
  --as-of 1999-12-31 2004-12-31 2005-12-31 2006-12-31 \
  --before 1998-09-01 --output /tmp/google-coverage.json
python3 scripts/validate_google_1996_2006_coverage.py
```

Use the existing batch input format. Every batch `query` must carry `assignee`, `filing_date_from`, and `filing_date_to`, plus the actual provider restrictions. Each page must include its number, returned records and provider total. The auditor rejects incomplete pages, duplicate publication identifiers within one query, out-of-window filing dates and conflicting bibliographic values for the same publication across queries.

The result retains counts, query parameters, per-batch hashes, and hashes of sorted publication IDs joined with newlines. The source ID digest preserves the original identifier strings for comparison with the earlier Google fixtures. The union uses normalized publication IDs. Application and provider family counts use their own identifiers. Date snapshots first restrict by filing date, then tally publication on or before the cutoff, publication after it and unresolved publication dates. Each name represents a filter in the retrospective snapshot. Historical rights require evidence from the relevant dates.

The public regression verifies the aggregates and the four source-linked EPO document records. Pass `--private-source-dir /private/google` to replay the seven saved batches, the legacy publication-set hashes, the independent PageRank lookup and the locally retained EPO files. The live results come from one provider snapshot. [Round 21 report](../research/21-google-1996-2006-patent-coverage.md)
