#!/usr/bin/env python3
"""Replay Google's 2012 census, Motorola's U.S. register roster and publication names."""

import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
from pathlib import Path
import re
import sys
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame
from validate_google_2011_patent_transfers import read_csv

ENTITIES = {
    'MOTOROLAMOBILITYINC': 'Motorola Mobility, Inc.',
    'MOTOROLAMOBILITYLLC': 'Motorola Mobility LLC',
    'MOTOROLAMOBILITYHOLDINGSINC': 'Motorola Mobility Holdings, Inc.',
    'MOTOROLAMOBILITYHOLDINGSLLC': 'Motorola Mobility Holdings LLC',
    'GOOGLETECHNOLOGYHOLDINGSLLC': 'Google Technology Holdings LLC',
}
MOTOROLA = {v for k, v in ENTITIES.items() if k.startswith('MOTOROLAMOBILITY')}


def pdf_or_archive_hash(path):
    digest = sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def comparable_publication(value):
    normalized = key(value)
    us_pg = re.fullmatch(r'US(20[0-9]{2})([0-9]{1,7})(A[129])', normalized or '')
    if us_pg:
        year, number, kind = us_pg.groups()
        return f'US{year}{number.zfill(7)}{kind}'
    return normalized


def asset_rows(route, event, properties):
    for asset in properties:
        yield {
            'route': route,
            'reel_frame': reel_frame(event),
            'property_sequence': str(asset['propertySequenceNumber']),
            'application_serial': asset['applicationNumber'],
            'filing_date': iso(asset['fillingDate']),
            'publication_number': asset['publicationNumber'] or '',
            'patent_number': asset['patentNumber'] or '',
            'execution_date_as_recorded': iso(event['assignorExecutionDate']),
            'recordation_date': iso(event['recordationDate']),
            'conveyance_as_recorded': event['conveyance'],
            'recipient': ' | '.join(p['assigneeName'] for p in event['assignees']),
            'title_in_register': (asset['inventionTitle'] or '').rstrip(),
        }


def reel_data(folder, reference, pages):
    for page in range(1, pages + 1):
        leaf = reference.replace('/', '-')
        request, result = official(folder / 'registry' / f'reel-{leaf}-page{page}.json')
        assert request['searchBy'] == 'reelFrame' and request['dataFilter']['currentPage'] == page
        yield result


def transcribed_epo_roles(root):
    return {
        'applicant': sorted({n.text.strip() for n in root.findall('.//B710/B711/snm') if n.text}),
        'proprietor': sorted({n.text.strip() for n in root.findall('.//B730/B731/snm') if n.text}),
    }


def role_summary(rows, condition):
    docs = [r for r in rows if condition(r)]
    by_entity = defaultdict(set)
    for row in docs:
        by_entity[row['entity']].add(row['publication'])
    return {
        'publications': len({r['publication'] for r in docs}),
        'application_serials': len({r['application_serial'] for r in docs if r['application_serial']}),
        'motorola_named_publications': len({r['publication'] for r in docs if r['entity'] in MOTOROLA}),
        'motorola_named_outside_google_2012_union': len({r['publication'] for r in docs
              if r['entity'] in MOTOROLA and r['in_google_2012_union'] == 'no'}),
        'by_named_entity': {n: len(v) for n, v in sorted(by_entity.items())},
    }


def validate_public(window, combined, assets, roles, rights):
    audits = window['query_audits']
    assert [a['page_count'] for a in audits] == [128, 15]
    assert [a['provider_total'] for a in audits] == [6369, 723]
    assert all(sum(a['returned_by_page']) == a['provider_total'] for a in audits)
    assert [window['union'][k] for k in ('publications','application_numbers','provider_family_ids',
                                        'multiple_assignee_filter_matches','earlier_priority_year_rows')] == [6926,5289,4095,166,3791]
    assert [combined['union'][k] for k in ('publications','application_numbers','provider_family_ids')] == [21335,15844,8566]
    assert (combined['query_windows'], combined['pages']) == (19,456)
    assert combined['cross_window_overlap'] == {'publications':0, 'application_numbers':1, 'provider_family_ids':967}
    assert [s['reported_published_by_cutoff'] for s in window['publication_date_snapshots'].values()] == [27,60,223,545]
    assert [s['reported_published_by_cutoff'] for s in combined['publication_date_snapshots'].values()] == [5844,6955,7297,8143,9097]

    by_route = defaultdict(list)
    for row in assets:
        by_route[row['route']].append(row)
    first = by_route['june22_inc_to_llc']
    second = by_route['postclosing_inbound_2012_exclusive_of_conversion']
    assert len(assets) == len({(a['reel_frame'],a['property_sequence']) for a in assets}) == 7247
    assert len({r['reel_frame'] for r in first}) == 135 and len(first) == 7093
    assert {r['execution_date_as_recorded'] for r in first} == {'2012-06-22'}
    assert len({r['reel_frame'] for r in first if r['recordation_date'][:4]=='2012'}) == 5
    assert {r['conveyance_as_recorded'] for r in second} == {"ASSIGNMENT OF ASSIGNOR'S INTEREST"}
    assert len(second) == len({r['reel_frame'] for r in second}) == 154
    a = {r['application_serial'] for r in first}
    b = {r['application_serial'] for r in second}
    assert (len(a),len(b),len(a & b),len(a | b)) == (7074,154,17,7211)
    assert all('2012-05-22' <= r['execution_date_as_recorded'] <= r['recordation_date'] <= '2012-12-31' for r in second)

    scope = rights['publication_roles']
    for label,region,qualifier in [('us_2012_filings','US','in_2012_filing_cohort'),
                                   ('us_2012_published_after_close','US','published_2012_at_or_after_close'),
                                   ('epo_2012_filings','EP','in_2012_filing_cohort')]:
        assert role_summary(roles, lambda r: r['jurisdiction']==region and r[qualifier]=='yes') == scope[label]
    assert scope['epo_2012_filings']['motorola_named_publications'] == 140
    assert Counter(r['status'] for r in rights['epo_native_lookup']) == {'verified_xml':200,'unavailable':6}
    assert sum(e['publication']=='EP2803221B1' and e['entity']=='Motorola Mobility LLC' for e in roles) == 1
    assert rights['dates']['closing'] == '2012-05-22' and rights['dates']['conversion'] == '2012-06-22'
    assert [e['registration_event'] for e in rights['epo_register_cases']] == ['2012-07-27','2016-10-14','2016-06-17']


def replay(folder, window, combined, assets, roles, rights):
    older_dirs = ['round24','round23','round22']
    paths = [str(folder/'*.batch.json'), *(str(folder.parent/r/'*.batch.json') for r in older_dirs),
             str(folder.parent/'*.batch.json')]
    rows, pages = load(paths[:1])
    audit = audit_longitudinal_coverage(rows,pages,as_of_dates=window['publication_date_snapshots'])
    assert audit == {k:v for k,v in window.items() if k not in ('tool','tool_version')}
    publication_names = defaultdict(set)
    query_names = {p['query_id']:p['query']['assignee'] for p in pages}
    for p in rows:
        publication_names[key(p['publication_number'])].add(query_names[p['_query_id']])
    roster = read_csv(folder/'google-2012-publication-list.csv')
    assert [p['publication_key'] for p in roster] == sorted(publication_names)
    assert all(set(p['matching_query_names'].split(' | ')) == publication_names[p['publication_key']] for p in roster)
    normalized = {comparable_publication(p) for p in publication_names}
    assert all((comparable_publication(r['publication']) in normalized) == (r['in_google_2012_union']=='yes') for r in roles)
    all_rows, all_pages = load(paths)
    report = audit_longitudinal_coverage(all_rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert report[field] == combined[field]
    older = [r for r in all_rows if r['_query_id'] not in query_names]
    for label, field, match in [('publications','publication_number',key),('application_numbers','application_number',key),
                                 ('provider_family_ids','family_id',family)]:
        overlap = {match(r[field]) for r in older} & {match(r[field]) for r in rows}
        assert len(overlap) == combined['cross_window_overlap'][label]
        if label == 'application_numbers': assert overlap == {'US201214130729A'}

    source_groups = defaultdict(set)
    for group, records in rights['registry_queries'].items():
        req,res = official(folder/records['file'])
        assert req == records['request'] and res['totalRows']==len(res['data'])==records['source_matches']
        for r in res['data']:
            ref = reel_frame(r)
            if group == 'conversion_pair' and iso(r['assignorExecutionDate']) == '2012-06-22':
                source_groups['june22_inc_to_llc'].add(ref)
            elif group in {'inbound_inc','inbound_llc'} and (
                '2012-05-22' <= iso(r['assignorExecutionDate']) <= iso(r['recorded']) <= '2012-12-31'):
                source_groups['postclosing_inbound_2012_exclusive_of_conversion'].add(ref)
    source_groups['postclosing_inbound_2012_exclusive_of_conversion'] -= source_groups['june22_inc_to_llc']
    assert all(refs == {i['reel_frame'] for i in rights['registry_reels'] if i['route']==route}
               for route,refs in source_groups.items())
    expected = []
    for reel in rights['registry_reels']:
        matter = []
        for number, result in enumerate(reel_data(folder,reel['reel_frame'],reel['pages']),1):
            item = result['data']
            assert reel_frame(item['assignment']) == reel['reel_frame']
            assert result['totalRows'] == reel['property_rows']
            if reel['pages'] > 1:
                assert result['backendPagination'] and len(item['properties'])==min(1000,result['totalRows']-(number-1)*1000)
            matter.extend(asset_rows(reel['route'],item['assignment'],item['properties']))
        assert len(matter) == len({a['property_sequence'] for a in matter}) == reel['property_rows']
        if reel['route'] != 'context': expected.extend(matter)
    assert assets == expected

    for name, info in rights['target_queries'].items():
        target = read_json(folder/info['file'])
        assert target['query']['assignee'] == name
        assert all(p['reported_total']==info['provider_total'] for p in target['pages'])
        assert sum(len(p['records']) for p in target['pages']) == info['provider_total']
    for data in rights['epo_native_lookup']:
        if data['status'] != 'verified_xml': continue
        raw = (folder/data['file']).read_bytes()
        assert sha256(raw).hexdigest() == data['sha256']
        assert transcribed_epo_roles(ElementTree.fromstring(raw)) == data['roles_as_published']
    for desc in rights['source_files']:
        assert pdf_or_archive_hash(folder/desc['file']) == desc['sha256']
    us_rows = read_json(folder/'sources/patentsview/extract/selected-roles.json')
    assert {(r['publication'],r['application_serial'],r['entity_as_transcribed'],r['publication_role']) for r in us_rows} == {
             (r['publication'],r['application_serial'],r['name_as_published'],r['role']) for r in roles if r['source_level']=='patentsview_raw_xml_extract'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-source-dir', type=Path)
    args = parser.parse_args()
    window = read_json(DERIVED/'google-2012-name-coverage-2026-11-22.json')
    combined = read_json(DERIVED/'google-1996-2012-combined-audit-2026-11-22.json')
    rights = read_json(DERIVED/'google-2012-motorola-rights-2026-11-22.json')
    assets = read_csv(DERIVED/rights['asset_ledger'])
    roles = read_csv(DERIVED/rights['published_party_ledger'])
    validate_public(window,combined,assets,roles,rights)
    if args.private_source_dir:
        replay(args.private_source_dir.resolve(),window,combined,assets,roles,rights)
        print('PASS: 456-page private replay, agency property rows, native EPO parties and archive hashes')
    print('PASS: 6,926 publications, 7,211 U.S. asset serials and published-party evidence')


if __name__=='__main__':
    main()
