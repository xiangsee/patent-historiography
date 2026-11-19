# Patent Evidence Workbench (v0.2)

Run from the repository root using Python 3.10+ with only the standard library.

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
