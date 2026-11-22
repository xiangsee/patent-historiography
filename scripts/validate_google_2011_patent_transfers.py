#!/usr/bin/env python3
"""Verify the round 24 name census, IBM asset rows and Motorola title controls."""

import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame, record_path


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def batch_rows(record):
    event = record['assignment']
    for asset in record['properties']:
        issue = iso(asset['issueDate'])
        recorded = iso(event['recordationDate'])
        yield {
            'reel_frame': reel_frame(event),
            'property_sequence': str(asset['propertySequenceNumber']),
            'execution_date_as_recorded': iso(event['assignorExecutionDate']),
            'recordation_date': recorded,
            'conveyance_as_recorded': event['conveyance'],
            'application_serial': asset['applicationNumber'] or '',
            'filing_date': iso(asset['fillingDate']),
            'patent_number': asset['patentNumber'] or '',
            'issue_date': issue,
            'patent_issued_by_recordation': 'yes' if issue and issue <= recorded else 'no_evidence',
            'publication_number': asset['publicationNumber'] or '',
            'title_in_register': (asset['inventionTitle'] or '').rstrip(),
        }


def ibm_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['execution_date_as_recorded']].append(row)
    return [
        {'execution_date_as_recorded': day, 'reel_count': len({p['reel_frame'] for p in group}),
         'property_rows': len(group), 'distinct_us_serials': len({p['application_serial'] for p in group}),
         'recordation_years': dict(sorted(Counter(p['recordation_date'][:4] for p in group).items()))}
        for day, group in sorted(groups.items())
    ]


def observed_chain(events, refs):
    return [
        {'reel_frame': reel_frame(e), 'execution_date_as_recorded': iso(e['assignorExecutionDate']),
         'recordation_date': iso(e['recordationDate']), 'conveyance_as_recorded': e['conveyance'],
         'from_entities': [x['assignorName'] for x in e['assignors']],
         'to_entities': [x['assigneeName'] for x in e['assignees']], 'original_record_url': e['imageURL']}
        for e in events if reel_frame(e) in refs
    ]


def read_record_pages(folder, item):
    ref = item['reel_frame']
    total = item['total_property_rows']
    if item['property_pages'] == 1:
        request, response = official(record_path(folder, ref))
        assert request['searchBy'] == 'reelFrame' and response['totalRows'] == total
        assert not response['backendPagination']
        assert len(response['data']['properties']) == total
        return response['data']
    assets = []
    assignment = None
    for n in range(1, item['property_pages'] + 1):
        leaf = ref.replace('/', '-')
        req, result = official(folder / 'registry' / f'reel-{leaf}-pagesize1000-page{n}.json')
        data = result['data']
        assert result['backendPagination'] and result['totalRows'] == total
        assert req['dataFilter']['currentPage'] == n and req['dataFilter']['rowsPerPage'] == 1000
        assert len(data['properties']) == min(1000, total - (n - 1) * 1000)
        if assignment is None:
            assignment = data['assignment']
        assert data['assignment'] == assignment
        assets.extend(data['properties'])
    assert len(assets) == len({p['propertySequenceNumber'] for p in assets}) == total
    return {'assignment': assignment, 'properties': assets}


def validate_public(window, combined, rights, ledger):
    queries = window['query_audits']
    assert [q['page_count'] for q in queries] == [89, 10]
    assert [q['provider_total'] for q in queries] == [4432, 480]
    assert all(sum(q['returned_by_page']) == q['provider_total'] for q in queries)
    assert [window['union'][k] for k in ('publications', 'application_numbers', 'provider_family_ids',
                                        'multiple_assignee_filter_matches', 'earlier_priority_year_rows')] == [4792, 3636, 2509, 120, 2679]
    assert [combined['union'][k] for k in ('publications', 'application_numbers', 'provider_family_ids')] == [14409, 10556, 5438]
    assert (combined['pages'], combined['query_windows']) == (313, 17)
    assert combined['cross_window_overlap'] == {'publications': 0, 'application_numbers': 0, 'provider_family_ids': 605}
    for report, expected in ((window, [39, 81, 112, 344, 915]), (combined, [4252, 4945, 5091, 5222, 5844, 6928])):
        assert [p['reported_published_by_cutoff'] for p in report['publication_date_snapshots'].values()] == expected

    assert len(ledger) == len({(p['reel_frame'], p['property_sequence']) for p in ledger}) == 2394
    assert len({p['application_serial'] for p in ledger}) == 2393
    assert len({p['reel_frame'] for p in ledger}) == 21
    assert len({p['reel_frame'] for p in ledger if p['recordation_date'][:4] == '2011'}) == 8
    assert [p['application_serial'] for p in ledger if p['reel_frame'] == '026933/0001'] == ['08929730']
    corrected = [p for p in ledger if p['application_serial'] == '08929730']
    assert {p['reel_frame'] for p in corrected} == {'026894/0001', '026933/0001'}
    assert {p['patent_number'] for p in corrected} == {'5956597'}
    assert '0595697' in corrected[-1]['conveyance_as_recorded']
    assert rights['ibm']['by_execution_date'] == ibm_summary(ledger)
    for refs, rows, grants in [({'026569/0275', '026664/0866'}, 1031, 1030), ({'026894/0001'}, 1023, 1023),
                                ({'027463/0594'}, 223, 187)]:
        group = [p for p in ledger if p['reel_frame'] in refs]
        assert len(group) == rows
        assert sum(p['patent_issued_by_recordation'] == 'yes' for p in group) == grants
    assert {p['application_serial'] for p in ledger if p['filing_date'].startswith('2011')} == {'13185404', '13326489'}

    moto = rights['motorola']
    corporate = moto['corporate_chronology']
    assert [corporate[k]['date'] for k in ('motorola_separation', 'signing', 'closing', 'operating_entity_conversion',
                                          'lenovo_closing')] == ['2011-01-04','2011-08-15','2012-05-22','2012-06-22','2014-10-30']
    direct = [r for r in moto['reels'] if 'motorola-inc-to-google' in r['routes']]
    assert len(direct) == 6 and {r['execution_date_as_recorded'] for r in direct} == {'2011-03-30'}
    assert sum(r['recordation_date'] < corporate['signing']['date'] for r in direct) == 4
    conversion = [r for r in moto['reels'] if 'motorola-2012-conversion-recorded' in r['routes']]
    assert len(conversion) == 5 and {r['execution_date_as_recorded'] for r in conversion} == {'2012-06-22'}
    assert sum(r['total_property_rows'] for r in conversion) == moto['2012_conversion_records']['property_rows'] == 6861
    assert moto['2012_conversion_records']['distinct_us_serials'] == 6858
    assert {r['reel_frame']: r['total_property_rows'] for r in moto['reels'] if r['property_pages'] > 1} == {
        '025673/0558': 6919, '029216/0282': 5581,
    }
    expected = {'10652131': ['025673/0558','029216/0282','034449/0001'],
                '13316895': ['028561/0557','034286/0001','034538/0001'],
                '07909262': ['025673/0558','026453/0324']}
    assert {c['application_serial']: [e['reel_frame'] for e in c['events']] for c in moto['application_chains']} == expected
    scanned = {e['reel_frame'] for e in rights['original_record_scans']}
    assert len(scanned) == len(rights['original_record_scans']) == 38
    assert {r['reel_frame'] for r in rights['ibm']['reels']} <= scanned
    assert all(len(bytes.fromhex(e['sha256'])) == 32 for e in rights['original_record_scans'] + rights['us_publications'])


def replay_private(folder, window, combined, rights, ledger):
    paths = [str(folder / '*.batch.json'), *(str(folder.parent / r / '*.batch.json') for r in ('round23','round22')),
             str(folder.parent / '*.batch.json')]
    rows, pages = load(paths[:1])
    annual = audit_longitudinal_coverage(rows, pages, as_of_dates=window['publication_date_snapshots'])
    assert annual == {k: v for k, v in window.items() if k not in ('tool', 'tool_version')}
    roster = read_csv(folder / 'google-2011-publication-list.csv')
    names = {p['query_id']: p['query']['assignee'] for p in pages}
    publication_names = defaultdict(set)
    for row in rows:
        publication_names[key(row['publication_number'])].add(names[row['_query_id']])
    assert [r['publication_key'] for r in roster] == sorted(publication_names)
    assert all(set(r['matching_query_names'].split(' | ')) == publication_names[r['publication_key']] for r in roster)
    for c in rights['name_union_controls']:
        assert (c['publication'] in publication_names) == c['in_2011_union']
    all_rows, all_pages = load(paths)
    replay = audit_longitudinal_coverage(all_rows, all_pages, as_of_dates=combined['publication_date_snapshots'])
    for field in ('union', 'sorted_publication_ids_sha256', 'publication_date_snapshots'):
        assert replay[field] == combined[field]
    older = [r for r in all_rows if r['_query_id'] not in names]
    for label, field, match in [('publications','publication_number',key),('application_numbers','application_number',key),
                                 ('provider_family_ids','family_id',family)]:
        assert len({match(r[field]) for r in older} & {match(r[field]) for r in rows}) == combined['cross_window_overlap'][label]

    scope = rights['registry_queries']
    by_query = {}
    for label, q in scope.items():
        req, res = official(folder / q['file'])
        assert req == q['request'] and len(res['data']) == res['totalRows'] == q['returned_reels']
        by_query[label] = {reel_frame(a) for a in res['data']}
    assert by_query['ibm-google'] == by_query['ibm-google-contains'] == by_query['ibm-google-reversed-test']
    assert by_query['ibm-google-2011'] == {p['reel_frame'] for p in ledger}
    assert by_query['ibm-google'] - by_query['ibm-google-2011'] == {'025077/0868'}
    expected = []
    motorola_assets = []
    for area, result in (('ibm', expected), ('motorola', motorola_assets)):
        for item in rights[area]['reels']:
            data = read_record_pages(folder, item)
            event = data['assignment']
            assert reel_frame(event) == item['reel_frame']
            assert iso(event['recordationDate']) == item['recordation_date']
            assert iso(event['assignorExecutionDate']) == item['execution_date_as_recorded']
            assert event['conveyance'] == item['conveyance_as_recorded']
            if area == 'motorola' or item['execution_date_as_recorded'].startswith('2011'):
                result.extend(batch_rows(data))
    assert expected == ledger
    assert motorola_assets == read_csv(folder / 'motorola-selected-register-properties.csv')
    conversion_reels = {r['reel_frame'] for r in rights['motorola']['reels']
                        if 'motorola-2012-conversion-recorded' in r['routes']}
    conversion_serials = {r['application_serial'] for r in motorola_assets
                          if r['reel_frame'] in conversion_reels and r['application_serial']}
    assert len(conversion_serials) == rights['motorola']['2012_conversion_records']['distinct_us_serials']
    for chain in rights['motorola']['application_chains']:
        serial = chain['application_serial']
        req, res = official(folder / 'registry' / f'application-{serial}.json')
        assert req['property'] == serial and len(res['data']['assignment']) == res['totalRows']
        refs = {e['reel_frame'] for e in chain['events']}
        assert observed_chain(res['data']['assignment'], refs) == chain['events']
        assert refs <= {p['reel_frame'] for p in motorola_assets if p['application_serial'] == serial}
    for description in rights['original_record_scans'] + rights['us_publications']:
        file = folder / description['file']
        with file.open('rb') as handle:
            assert handle.read(4) == b'%PDF'
            handle.seek(0)
            digest = sha256()
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        assert digest.hexdigest() == description['sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-source-dir', type=Path)
    args = parser.parse_args()
    window = read_json(DERIVED / 'google-2011-name-coverage-2026-11-22.json')
    combined = read_json(DERIVED / 'google-1996-2011-combined-audit-2026-11-22.json')
    rights = read_json(DERIVED / 'google-2011-ibm-motorola-rights-2026-11-22.json')
    ledger = read_csv(DERIVED / rights['ibm']['asset_ledger'])
    validate_public(window, combined, rights, ledger)
    if args.private_source_dir:
        replay_private(args.private_source_dir.resolve(), window, combined, rights, ledger)
        print('PASS: 313 pages replayed, IBM and Motorola agency rows, original file hashes')
    print('PASS: 4,792 publications, 2,393 IBM serials, three traced Motorola title chains')


if __name__ == '__main__':
    main()
