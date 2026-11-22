#!/usr/bin/env python3
"""Verify the round 23 longitudinal census and agency-record asset ledger."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from patent_evidence.official_xml import parse_ep_patent_document

DERIVED = ROOT / 'pilots/google-longitudinal/derived'
LOOKUP = 'https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/search/patent'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def official(path):
    payload = read_json(path)
    assert payload['response']['statusCode'] == 200
    return payload['request'], payload['response']['successResponse']


def iso(value):
    return datetime.strptime(value, '%m/%d/%Y').date().isoformat() if value else ''


def reel_frame(event):
    return f"{event['reelNumber']:06d}/{event['frameNumber']:04d}"


def record_path(folder, ref):
    return folder / 'registry' / f"reel-{ref.replace('/', '-')}.json"


def project_assets(route, record, source):
    event = record['assignment']
    ref = reel_frame(event)
    for asset in record['properties']:
        yield {
            'route': route,
            'reel_frame': ref,
            'property_sequence': str(asset['propertySequenceNumber']),
            'application_serial': asset['applicationNumber'] or '',
            'filing_date': iso(asset['fillingDate']),
            'publication_number': asset['publicationNumber'] or '',
            'grant_number': asset['patentNumber'] or '',
            'title_in_register': asset['inventionTitle'] or '',
            'from_entity': ' | '.join(p['assignorName'] for p in event['assignors']),
            'to_entity': ' | '.join(p['assigneeName'] for p in event['assignees']),
            'conveyance_as_recorded': event['conveyance'],
            'execution_date_as_recorded': iso(event['assignorExecutionDate']),
            'recordation_date': iso(event['recordationDate']),
            'discovery': source,
            'original_record_url': event['imageURL'] or '',
        }


def select_routes(rows, definitions):
    routes = defaultdict(set)
    for event in rows:
        if not '2010' <= event['recordationDate'][-4:] <= '2012':
            continue
        fr = {key(p['assignorName']) for p in event['assignors']}
        to = {key(p['assigneeName']) for p in event['assignees']}
        for route, info in definitions.items():
            if key(info['from_query']) in fr and key(info['to_filter']) in to:
                routes[route].add(reel_frame(event))
    return routes


def row_set(ledger, route, year=None):
    return {a['application_serial'] for a in ledger if a['route'] == route
            and (year is None or a['recordation_date'].startswith(year))}


def sample_controls(apps, definitions, folder):
    controls = {}
    for serial, receiver in apps.items():
        request, result = official(folder / 'registry' / f'application-{serial}.json')
        assert request['searchBy'] == 'applicationNumber' and request['property'] == serial
        rows = result['data']['assignment']
        assert len(rows) == result['totalRows']
        controls[serial] = [
            {
                'reel_frame': reel_frame(a),
                'execution_date_as_recorded': iso(a['assignorExecutionDate']),
                'recordation_date': iso(a['recordationDate']),
                'to_entity': receiver,
                'original_record_url': a['imageURL'],
            }
            for a in rows if '2012' >= a['recordationDate'][-4:]
            and key(receiver) in {key(p['assigneeName']) for p in a['assignees']}
            and not select_routes([a], definitions)
        ]
    return controls


def validate_public(window, combined, rights, ledger):
    counts = window['union']
    assert [a['page_count'] for a in window['query_audits']] == [39, 7]
    assert [a['provider_total'] for a in window['query_audits']] == [1936, 321]
    assert all(sum(a['returned_by_page']) == a['provider_total'] for a in window['query_audits'])
    assert [counts[k] for k in ('publications', 'application_numbers', 'provider_family_ids',
                               'multiple_assignee_filter_matches', 'earlier_priority_year_rows')] == [2168, 1577, 1052, 89, 1495]
    assert len(counts['publication_offices']) == 19
    assert [combined['union'][k] for k in ('publications', 'application_numbers', 'provider_family_ids')] == [9617, 6920, 3534]
    assert (combined['query_windows'], combined['pages']) == (15, 214)
    assert combined['cross_window_overlap'] == {'publications': 0, 'application_numbers': 0, 'provider_family_ids': 292}
    for stats, filed, visible in [(window, [232, 800, 2168], [0, 8, 228]),
                                  (combined, [7449, 7681, 8249, 9617], [3084, 3248, 3565, 4252])]:
        assert [v['matched_filing_dates_through_cutoff'] for v in stats['publication_date_snapshots'].values()] == filed
        assert [v['reported_published_by_cutoff'] for v in stats['publication_date_snapshots'].values()] == visible

    assert len(ledger) == len({(a['reel_frame'], a['property_sequence']) for a in ledger}) == 115
    assert len({a['reel_frame'] for a in ledger}) == 96
    assert len({a['application_serial'] for a in ledger}) == 64
    assert Counter(a['route'] for a in ledger) == {
        'on2-inc': 38, 'on2-llc': 42, 'on2-finland': 6, 'hantro': 5,
        'duck': 7, 'admob-inc': 8, 'admob-google': 9,
    }
    assert all(a['execution_date_as_recorded'] <= a['recordation_date'] for a in ledger)
    assert {a['reel_frame'] for a in ledger if a['discovery'] == 'application_number'} == {'025389/0176'}
    assert row_set(ledger, 'on2-inc', '2010') == row_set(ledger, 'on2-llc', '2010')
    assert len(row_set(ledger, 'on2-inc', '2010')) == 26
    on2_inc, on2_llc = row_set(ledger, 'on2-inc'), row_set(ledger, 'on2-llc')
    assert len(on2_inc) == 37 and len(on2_llc) == 42 and on2_inc <= on2_llc
    assert row_set(ledger, 'hantro') < row_set(ledger, 'on2-finland')
    assert row_set(ledger, 'on2-finland') - row_set(ledger, 'hantro') == {'12724497'}
    assert not row_set(ledger, 'duck') & (on2_llc | row_set(ledger, 'on2-finland'))
    assert row_set(ledger, 'admob-google') - row_set(ledger, 'admob-inc') == {'61340726'}
    assert row_set(ledger, 'admob-inc') < row_set(ledger, 'admob-google')
    assert all(any(c['recordation_date'] < '2010-05-27' for c in rights['application_controls'][serial])
               for serial in row_set(ledger, 'admob-inc'))
    assert [c['reel_frame'] for c in rights['application_controls']['61340726']] == ['025189/0501']
    assert [c['reel_frame'] for c in rights['application_controls']['13069325']] == ['027157/0541']
    correction = {a['reel_frame']: a for a in ledger if a['application_serial'] == '61059367'}
    assert correction['025374/0472']['execution_date_as_recorded'] == '2010-10-28'
    assert correction['025608/0310']['execution_date_as_recorded'] == '2010-02-19'
    assert '025374 FRAME 0472' in correction['025608/0310']['conveyance_as_recorded']
    assert {e['child_serial'] for e in rights['us_lineage'] if e['parent_serial'] == '10713807'
            and e['relation'] == 'continuation'} == on2_llc - on2_inc
    assert {e['child_serial'] for e in rights['us_lineage'] if e['parent_serial'] == '61340726'
            and e['relation'] == 'claims_provisional_benefit'} == {'13069325'}
    assert sum(e['relation'] == 'continuation' for e in rights['us_lineage']) == 6
    assert {item['role'] for item in rights['epo_publications']} == {'applicant', 'proprietor'}
    transfer = rights['epo_register_transfer']
    assert tuple(transfer[k] for k in ('transfer_request_received', 'applicant_change_event_date',
                                        'registration_notification_dated', 'applicant_change_bulletin_date')) == (
        '2011-10-28', '2011-12-02', '2011-12-06', '2012-01-04',
    )
    assert {'EP' + p['application_number'] for p in rights['epo_publications']} == {transfer['application_number']}
    assert transfer['underlying_agreement_execution_date'] is None
    assert all(len(bytes.fromhex(item['sha256'])) == 32 for section in (
        'original_record_scans', 'us_publications', 'epo_publications') for item in rights[section])


def replay_private(folder, window, combined, rights, ledger):
    paths = [str(folder / '*.batch.json'), str(folder.parent / 'round22' / '*.batch.json'),
             str(folder.parent / '*.batch.json')]
    rows, pages = load(paths[:1])
    report = audit_longitudinal_coverage(rows, pages, as_of_dates=window['publication_date_snapshots'])
    assert report == {k: v for k, v in window.items() if k not in ('tool', 'tool_version')}
    pubs = {key(doc['publication_number']) for doc in rows}
    query_names = {p['query_id']: p['query']['assignee'] for p in pages}
    publication_names = defaultdict(set)
    for row in rows:
        publication_names[key(row['publication_number'])].add(query_names[row['_query_id']])
    with (folder / 'google-2010-publication-list.csv').open(encoding='utf-8', newline='') as handle:
        roster = list(csv.DictReader(handle))
    assert [r['publication_key'] for r in roster] == sorted(pubs)
    assert all(set(r['matching_query_names'].split(' | ')) == publication_names[r['publication_key']] for r in roster)
    for control in rights['name_union_controls']:
        assert (control['id'] in pubs) == control['in_2010_publication_union']
    all_rows, all_pages = load(paths)
    report = audit_longitudinal_coverage(all_rows, all_pages, as_of_dates=combined['publication_date_snapshots'])
    for field in ('union', 'sorted_publication_ids_sha256', 'publication_date_snapshots'):
        assert report[field] == combined[field]
    names_2010 = {p['query_id'] for p in pages}
    before = [r for r in all_rows if r['_query_id'] not in names_2010]
    for label, field, normalize in [('publications', 'publication_number', key),
                                    ('application_numbers', 'application_number', key),
                                    ('provider_family_ids', 'family_id', family)]:
        assert len({normalize(r[field]) for r in before} & {normalize(r[field]) for r in rows}) == combined['cross_window_overlap'][label]

    definitions = rights['registry_scope']['routes']
    name_routes = {}
    for route, definition in definitions.items():
        req, res = official(folder / f'official-search-{route}.json')
        assert req['searchBy'] == 'exactAssignorName' and req['property'] == definition['from_query']
        assert res['totalRows'] == len(res['data']) == definition['name_response_rows']
        name_routes[route] = select_routes((r['assignment'] for r in res['data']), definitions)[route]
        assert len(name_routes[route]) == definition['reels_from_name']
    all_routes = {route: refs.copy() for route, refs in name_routes.items()}
    for serial in {a['application_serial'] for a in ledger}:
        req, res = official(folder / 'registry' / f'application-{serial}.json')
        assert req['searchBy'] == 'applicationNumber' and req['property'] == serial
        assert len(res['data']['assignment']) == res['totalRows']
        for route, found in select_routes(res['data']['assignment'], definitions).items():
            all_routes[route].update(found)
    expected_ledger = []
    for route, refs in sorted(all_routes.items()):
        assert len(refs) == definitions[route]['reels_after_application_reconciliation']
        for ref in sorted(refs):
            _, res = official(record_path(folder, ref))
            record = res['data']
            assert record['noOfProperties'] == len(record['properties']) == res['totalRows']
            assert reel_frame(record['assignment']) == ref
            source = 'assignor_name' if ref in name_routes[route] else 'application_number'
            expected_ledger.extend(project_assets(route, record, source))
    assert ledger == expected_ledger
    assert sample_controls(rights['application_control_receivers'], definitions, folder) == rights['application_controls']

    probes = read_json(folder / 'target-assignee-probes.json')
    actual = {p['source_metadata']['arguments']['assignee']: len(p['response']['data']) for p in probes}
    assert actual == rights['target_name_probes']
    assert all(len(p['response']['data']) == p['response']['total'] for p in probes)
    for section in ('original_record_scans', 'us_publications', 'epo_publications'):
        for item in rights[section]:
            contents = (folder / item['file']).read_bytes()
            assert sha256(contents).hexdigest() == item['sha256']
            if section == 'epo_publications':
                parsed = parse_ep_patent_document(contents, source_url=item['url'],
                                                  expected_publication=item['id'], allow_no_claims=True)
                role = {'applicant': 'A_document_applicant_B711', 'proprietor': 'B_document_proprietor_B731'}[item['role']]
                assert parsed['parties_as_published'][role] == [item['entity']]
                xml = ElementTree.fromstring(contents)
                assert xml.findtext('.//B210') == item['application_number']
                assert xml.findtext('.//B310') == item['priority_number']
                assert parsed['publication_date'] == item['publication_date']
            else:
                assert contents.startswith(b'%PDF')
    sources = {s['kind']: s for s in rights['epo_register_transfer']['sources']}
    for item in sources.values():
        assert sha256((folder / item['file']).read_bytes()).hexdigest() == item['sha256']
    events = (folder / sources['register_event_html']['file']).read_text(encoding='utf-8')
    doclist = (folder / sources['register_file_index_html']['file']).read_text(encoding='utf-8')
    assert re.search(r'02\.12\.2011</td>\s*<td[^>]*>Change - applicant</td>\s*<td[^>]*>published on&nbsp;&nbsp;04\.01\.2012', events)
    assert re.search(r'28\.10\.2011</td>[^\n]*\n[^\n]*ESD9FB2S9300FI4[^\n]*Request for assignment', doclist)
    assert re.search(r'06\.12\.2011</td>[^\n]*\n[^\n]*ESI4R9EW6196FI4[^\n]*Communication of the registration', doclist)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-source-dir', type=Path)
    args = parser.parse_args()
    window = read_json(DERIVED / 'google-2010-name-coverage-2026-11-22.json')
    combined = read_json(DERIVED / 'google-1996-2010-combined-audit-2026-11-22.json')
    rights = read_json(DERIVED / 'google-2010-on2-admob-rights-2026-11-22.json')
    with (DERIVED / rights['asset_ledger']).open(encoding='utf-8', newline='') as handle:
        ledger = list(csv.DictReader(handle))
    validate_public(window, combined, rights, ledger)
    if args.private_source_dir:
        replay_private(args.private_source_dir.resolve(), window, combined, rights, ledger)
        print('PASS: private 214-page replay, 64 application lookups, USPTO and EPO source fingerprints')
    print('PASS: 2,168 publications, 96 scoped reels, 115 property rows, six verified U.S. continuations')


if __name__ == '__main__':
    main()
