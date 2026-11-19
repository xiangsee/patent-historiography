#!/usr/bin/env python3
"""Validate derived Google 2000-04 world-scope patent query, not copyrighted bulk data."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a=json.loads((root/'pilots/google-longitudinal/derived/google-inc-2000-2004-global-audit.json').read_text(encoding='utf8'))
m=json.loads((root/'pilots/google-longitudinal/derived/alias-region-count-probes-2026-11-19.json').read_text(encoding='utf8'))
assert a['records_retrieved']==1067
assert a['unique_publication_numbers']==1067
assert a['duplicate_publication_entries']==0
assert a['unique_application_numbers']==843
assert a['valid_family_ids_distinct']==522
assert a['pages_requested']==22 and a['pages_received']==22
pages=a['page_metadata']
assert [p['page'] for p in pages]==list(range(1,23))
assert [p['returned'] for p in pages]==[50]*21+[17]
assert all(p['reported_total']==1067 and p['error'] is None for p in pages)
assert sum(a['filing_year_document_counts'].values())==1067
assert sum(a['publication_country_document_counts'].values())==1067
assert a['publication_country_document_counts']['US']==452
assert a['family_id_type_not_independently_verified'] is True
assert a['not_an_invention_count'] and a['not_global_corporate_corpus']
assert a['raw_records_disclosed_in_public_repo'] is False
assert len(a['sha256_sorted_publication_ids'])==64
assert len(m['rows'])==21
assert all(p.get('code')==200 and p.get('total') is not None for p in m['rows'])
print('PASS: 22 complete pages, 1,067 publications, year/country totals, 21 alias-region count probes')
