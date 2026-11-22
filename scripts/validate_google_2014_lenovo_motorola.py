#!/usr/bin/env python3
"""Validate the 2014 Google corpus and the Motorola Mobility ownership evidence."""

import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame
from validate_google_2011_patent_transfers import read_csv
from validate_google_2012_motorola_assets import pdf_or_archive_hash, reel_data
from validate_google_2013_arris_home import history, published_in_google

CLOSE = '2014-10-30'
CARVE_DATES = {'2014-10-28', '2014-10-29'}
GTH = 'GOOGLETECHNOLOGYHOLDINGSLLC'
MOBILITY = {'MOTOROLAMOBILITYLLC', 'MOTOROLOAMOBILITYLLC'}
TITLE_EVENT_CODES = {23, 33, 34, 36}
EXCLUDED_SERIAL = '13466482'
MANUAL_CONTROLS = {'10652131', '13093211', '13316895', EXCLUDED_SERIAL, '13478811'}
PREFIX = 'google-2014-lenovo-motorola-'


def corporate_names(event, side):
    return [p[f'{side}Name'] for p in event[f'{side}s']]


def event_scope(event, ref):
    source = {key(name) for name in corporate_names(event, 'assignor')}
    target = {key(name) for name in corporate_names(event, 'assignee')}
    date = iso(event['assignorExecutionDate'])
    code = event['conveyanceCode']
    if code == 40:
        return 'corrective_record'
    if code == 33:
        return 'name_change_as_indexed'
    if code == 23 and date in CARVE_DATES and source & MOBILITY:
        if GTH in target:
            return 'closing_period_mobility_to_gth'
        if 'GOOGLEINC' in target:
            return 'closing_period_mobility_to_google_inc'
    if ref == '036398/0001':
        return '2015_gth_to_mobility'
    if code == 23 and source & MOBILITY and any(n.startswith('LENOVO') for n in target):
        return 'later_mobility_to_lenovo_entity'
    return 'other_2014_mobility_to_google'


def replay_assets(folder, reels):
    rows = []
    for ref, details in sorted(reels.items()):
        results = list(reel_data(folder, ref, details['pages']))
        event = results[0]['data']['assignment']
        properties = [p for result in results for p in result['data']['properties']]
        assert reel_frame(event) == ref
        assert all(result['totalRows'] == len(properties) for result in results)
        assert len(properties) == len({p['propertySequenceNumber'] for p in properties})
        assert len(properties) == details['property_count'], ref
        assert details['scope'] == event_scope(event, ref), ref
        assert details['recordation_date'] == iso(event['recordationDate']), ref
        for p in sorted(properties, key=lambda item: item['propertySequenceNumber']):
            rows.append({
                'scope': details['scope'], 'reel_frame': ref,
                'property_sequence': str(p['propertySequenceNumber']),
                'application_serial': (p['applicationNumber'] or '').strip(),
                'filing_date_in_register': iso(p['fillingDate']),
                'publication_number_in_register': (p['publicationNumber'] or '').strip(),
                'patent_number_in_register': (p['patentNumber'] or '').strip(),
                'pct_number_in_register': (p['pctNumber17'] or p['pctNumber'] or '').strip(),
                'document_execution_date': iso(event['assignorExecutionDate']),
                'uspto_recordation_date': iso(event['recordationDate']),
                'from_entities': ' | '.join(corporate_names(event, 'assignor')),
                'to_entities': ' | '.join(corporate_names(event, 'assignee')),
                'conveyance_code': str(event['conveyanceCode']),
                'conveyance_as_indexed': event['conveyance'].rstrip(),
                'title_in_register': (p['inventionTitle'] or '').rstrip(),
            })
    return rows


def title_evidence(events):
    def dated(e):
        return iso(e['assignorExecutionDate']), iso(e['recordationDate']), reel_frame(e)

    events = sorted(events, key=dated)
    receipts = []
    exits = []
    for event in events:
        executed, _, _ = dated(event)
        if not executed or event['conveyanceCode'] not in TITLE_EVENT_CODES:
            continue
        sources = {key(p) for p in corporate_names(event, 'assignor')}
        targets = {key(p) for p in corporate_names(event, 'assignee')}
        if targets & MOBILITY and executed <= CLOSE:
            receipts.append(event)
        if sources & MOBILITY and targets - MOBILITY and executed <= CLOSE:
            exits.append(event)
    last = max(receipts, key=dated) if receipts else None
    exit_after = last and any(dated(e)[0] >= dated(last)[0] for e in exits)
    return last if last and not exit_after else None, exits


def distinct_refs(rows, *scopes):
    return ' | '.join(sorted({p['reel_frame'] for p in rows if p['scope'] in scopes}))


def replay_titles(assets, grants, selected_histories, google_ids):
    by_app = defaultdict(list)
    grants = {g['application_id']: g for g in grants}
    for p in assets:
        if p['application_serial']:
            by_app[p['application_serial']].append(p)
    rows = []
    for serial in sorted(set(by_app) | set(grants) | MANUAL_CONTROLS):
        props = by_app[serial]
        grant = grants.get(serial, {})
        events = selected_histories.get(serial, [])
        receipt, exits = title_evidence(events)
        gth = distinct_refs(props, 'closing_period_mobility_to_gth')
        inc = distinct_refs(props, 'closing_period_mobility_to_google_inc')
        returned = distinct_refs(props, '2015_gth_to_mobility')
        correction = distinct_refs(props, 'corrective_record')
        filed = next((p['filing_date_in_register'] for p in props if p['filing_date_in_register']), grant.get('filing_date', ''))
        if serial == EXCLUDED_SERIAL:
            category = 'identifier_removed_by_correction'
            correction = '035053/0059'
        elif gth and filed > CLOSE:
            category = 'gth_later_filing_under_carve_out_document'
        elif gth and not filed:
            category = 'gth_under_carve_out_document_filing_date_missing'
        elif gth:
            category = 'gth_at_carve_out_then_returned' if returned else 'gth_at_carve_out'
        elif inc:
            category = 'google_inc_at_carve_out'
        elif returned:
            category = 'later_gth_to_motorola_only'
        elif receipt and grant and not exits:
            category = 'motorola_continuity_through_closing'
        elif grant:
            category = 'motorola_grant_requires_title_qualification'
        else:
            category = 'other_registry_evidence'
        title = next((p['title_in_register'] for p in props if p['title_in_register']), grant.get('patent_title', ''))
        indexed = [{
            'publication_number': p['publication_number_in_register'], 'patent_number': p['patent_number_in_register'],
        } for p in props]
        rows.append({
            'application_serial': serial,
            'filing_date': filed, 'title': title, 'title_evidence': category,
            'us_publication_numbers_in_register': ' | '.join(sorted({p['publication_number'] for p in indexed if p['publication_number']})),
            'us_patent_numbers_in_register': ' | '.join(sorted({p['patent_number'] for p in indexed if p['patent_number']})),
            'gth_carve_out_reels': gth, 'google_inc_carve_out_reels': inc,
            'correction_reels': correction,
            'other_mobility_to_google_reels': distinct_refs(props,'other_2014_mobility_to_google','name_change_as_indexed'),
            'later_gth_to_mobility_reels': returned,
            'later_mobility_to_lenovo_reels': distinct_refs(props,'later_mobility_to_lenovo_entity'),
            'verified_motorola_preclose_receipt': reel_frame(receipt) if receipt else '',
            'verified_motorola_preclose_execution': iso(receipt['assignorExecutionDate']) if receipt else '',
            'verified_motorola_preclose_recordation': iso(receipt['recordationDate']) if receipt else '',
            'reviewed_preclose_outbound_reels': ' | '.join(reel_frame(e) for e in exits),
            'sampled_motorola_grant': f"US{grant['patent_id']}{grant['wipo_kind']}" if grant else '',
            'sampled_motorola_grant_date': grant.get('patent_date',''),
            'matched_google_2014_publications': published_in_google(indexed, google_ids),
        })
    return rows


def corpus_summary(window, combined):
    q = window['query_audits']
    assert [a['page_count'] for a in q] == [110,25]
    assert [a['provider_total'] for a in q] == [5495,1204]
    assert all(sum(a['returned_by_page']) == a['provider_total'] for a in q)
    counts = ('publications','application_numbers','provider_family_ids')
    assert tuple(window['union'][k] for k in counts) == (6556,4622,3471)
    assert window['union']['multiple_assignee_filter_matches'] == 143
    assert window['union']['earlier_priority_year_rows'] == 4230
    assert (combined['query_windows'],combined['pages']) == (23,752)
    assert tuple(combined['union'][k] for k in counts) == (35764,26107,13481)
    assert combined['cross_window_overlap'] == {'publications':0,'application_numbers':0,'provider_family_ids':1555}
    assert [window['publication_date_snapshots'][d]['reported_published_by_cutoff'] for d in
            ('2014-01-29','2014-06-26','2014-10-28','2014-10-30','2014-12-31')] == [1,116,597,624,928]
    assert [combined['publication_date_snapshots'][d]['reported_published_by_cutoff'] for d in
            ('2013-12-31','2014-01-29','2014-06-26','2014-10-28','2014-10-30','2014-12-31')] == [13581,13987,16555,18882,18934,19973]


def registry_summary(rows, titles):
    scope_totals = {}
    by_scope = defaultdict(list)
    for row in rows:
        by_scope[row['scope']].append(row)
    for scope, subset in sorted(by_scope.items()):
        scope_totals[scope] = {
            'reels': len({p['reel_frame'] for p in subset}),
            'property_rows': len(subset),
            'application_serials': len({p['application_serial'] for p in subset if p['application_serial']}),
        }
    return {
        'by_scope': scope_totals, 'all_property_rows': len(rows), 'all_title_rows': len(titles),
        'by_title_evidence': dict(Counter(t['title_evidence'] for t in titles)),
        'reels_recorded_by_year': {year:len(refs) for year,refs in _reels_by_year(rows).items()},
        'title_rows_matching_google_2014': sum(bool(t['matched_google_2014_publications']) for t in titles),
    }


def _reels_by_year(rows):
    years = defaultdict(set)
    for row in rows:
        years[row['uspto_recordation_date'][:4]].add(row['reel_frame'])
    return years


def validate_registry(assets, titles, rights):
    assert len(assets) == len({(r['reel_frame'], r['property_sequence']) for r in assets})
    assert len(titles) == len({r['application_serial'] for r in titles})
    assert all(p['application_serial'] or p['patent_number_in_register'] or p['pct_number_in_register'] for p in assets)
    assert set(rights['reels']) == {p['reel_frame'] for p in assets}
    assert registry_summary(assets,titles) == rights['uspto_totals']
    assert len(rights['reels']) == 603 and len(assets) == 8966 and len(titles) == 8651
    totals = rights['uspto_totals']
    assert totals['by_scope']['closing_period_mobility_to_gth'] == {
        'reels': 573, 'property_rows': 8799, 'application_serials': 8576,
    }
    gth = [p for p in assets if p['scope'] == 'closing_period_mobility_to_gth']
    assert len({p['pct_number_in_register'] for p in gth if not p['application_serial']}) == 186
    assert Counter(p['document_execution_date'] for p in {q['reel_frame']:q for q in gth}.values()) == {
        '2014-10-28':568, '2014-10-29':5,
    }
    assert min(p['uspto_recordation_date'] for p in gth) == CLOSE
    assert len({p['reel_frame'] for p in gth if p['uspto_recordation_date'] <= '2014-12-31'}) == 207
    assert totals['by_title_evidence']['gth_at_carve_out'] == 8293
    assert totals['by_title_evidence']['gth_later_filing_under_carve_out_document'] == 264
    assert totals['by_title_evidence']['gth_under_carve_out_document_filing_date_missing'] == 3
    assert totals['by_title_evidence']['motorola_continuity_through_closing'] == 16
    assert totals['by_title_evidence']['gth_at_carve_out_then_returned'] == 16
    assert totals['by_title_evidence']['later_gth_to_motorola_only'] == 2
    tx = rights['transaction']
    assert (tx['contract_date'],tx['actual_closing'],tx['equity_percent']) == ('2014-01-29',CLOSE,100)
    assert tx['closing_date_as_disclosed_by_google_sec'] == '2014-10-29'
    assert tx['asset_bands_in_eu_decision'] == {'design_patents':[2000,3000], 'utility_patents':[100,200],
                                                'pending_applications_less_than':100}
    assert tx['license']['terms'] == ['nonexclusive','royalty-free','worldwide','perpetual']
    assert tx['license']['effective_as_of_as_recited'] == '2014-10-27T11:20:00-07:00'
    assert tx['license']['signed_agreement_obtained'] is False
    assert tx['individual_sale_schedule_obtained'] is False
    t = {row['application_serial']:row for row in titles}
    assert t[EXCLUDED_SERIAL]['title_evidence'] == 'identifier_removed_by_correction'
    assert t['29469942']['title_evidence'] == 'motorola_continuity_through_closing'
    assert t['29485246']['title_evidence'] == 'gth_at_carve_out_then_returned'
    assert t['13732515']['title_evidence'] == 'gth_at_carve_out'
    assert t['29485246']['later_gth_to_mobility_reels'] == '036398/0001'
    assert t['10652131']['gth_carve_out_reels'] == '034449/0001'


def replay(folder, window, combined, assets, titles, rights):
    paths = [str(folder/'*.batch.json'),*(str(folder.parent/r/'*.batch.json') for r in
             ('round26','round25','round24','round23','round22')),str(folder.parent/'*.batch.json')]
    annual, pages = load(paths[:1])
    report = audit_longitudinal_coverage(annual,pages,as_of_dates=window['publication_date_snapshots'])
    assert report == {k:v for k,v in window.items() if k not in ('tool','tool_version')}
    rows, all_pages = load(paths)
    report = audit_longitudinal_coverage(rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert report[field] == combined[field], field
    assert len(report['query_audits']) == combined['query_windows'] and len(all_pages) == combined['pages']
    annual_ids = {p['query_id'] for p in pages}
    older = [r for r in rows if r['_query_id'] not in annual_ids]
    for label, field, normalize in [('publications','publication_number',key),('application_numbers','application_number',key),
                                    ('provider_family_ids','family_id',family)]:
        assert len({normalize(r[field]) for r in older}&{normalize(r[field]) for r in annual}) == combined['cross_window_overlap'][label]
    google_ids = {key(r['publication_number']) for r in annual}
    annual_csv = read_csv(folder/'google-2014-publication-list.csv')
    assert len(annual_csv) == len(google_ids) == window['union']['publications']
    assert {r['publication_key'] for r in annual_csv} == google_ids

    for name, expected in rights['provider_name_probes'].items():
        probe_rows, probe_pages = load([str(folder/f'target-{name}.json')])
        assert len(probe_pages) == expected['pages']
        assert len(probe_rows) == expected['total']
        assert len(google_ids & {key(r['publication_number']) for r in probe_rows}) == expected['google_2014_overlap']

    comparison = read_json(folder/'registry'/'comparison-reel-index.json')
    full = read_json(folder/'registry'/'reel-index.json')
    pairs = read_json(folder/'registry'/'pair-index.json')
    assert set(full) == {f"{int(e['reelNumber']):06d}/{int(e['frameNumber']):04d}"
                         for group in pairs.values() for e in group if iso(e['assignorExecutionDate']).startswith('2014')}
    assert set(full)|set(comparison) == set(rights['reels'])
    for name, expected in rights['uspto_pair_queries'].items():
        request, result = official(folder/'registry'/f'pair-{name}-page1.json')
        assert request['searchCriteria'] == expected['criteria']
        actual = result.get('data') or []
        assert result['totalRows'] == len(pairs[name]) == len(actual) == expected['returned_reels']
        assert actual == pairs[name]
    assert assets == replay_assets(folder,rights['reels'])
    grants = read_json(folder/'sources'/'mobility-assigned-postclose-grants.json')
    grant_source = folder.parent/'round25'/'sources'/'patentsview'/'extract'
    by_patent = {g['patent_id']:g for g in read_json(grant_source/'g_patent.json')}
    filings = {p['patent_id']:p for p in read_json(grant_source/'g_application.json')}
    raw_assignees = read_json(grant_source/'g_assignee_not_disambiguated.json')
    expected_grants = {r['identifier'] for r in raw_assignees if r['entity'] == 'Motorola Mobility LLC'
                       and filings[r['identifier']]['filing_date'] <= CLOSE < by_patent[r['identifier']]['patent_date']}
    assert {r['patent_id'] for r in grants} == expected_grants and len(grants) == 93
    for grant in grants:
        pid = grant['patent_id']
        assert grant['application_id'] == filings[pid]['application_id']
        assert grant['patent_date'] == by_patent[pid]['patent_date']
    checked = read_json(folder/'registry'/'continuity-serials.json')
    histories = {s:history(folder,s) for s in checked}
    assert titles == replay_titles(assets,grants,histories,google_ids)
    for case in rights['schedule_A_evidence']['document_only_controls']:
        serial = case['application_serial']
        assert all(p['application_serial'] != serial for p in assets)
        assert not any(iso(e['assignorExecutionDate']).startswith('2014') for e in history(folder,serial))
    for source in rights['archived_sources'].values():
        assert pdf_or_archive_hash(folder/source['file']) == source['sha256'], source['file']


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path)
    args = parser.parse_args()
    stamp = '-2026-11-22.json'
    window = read_json(DERIVED/('google-2014-name-coverage'+stamp))
    combined = read_json(DERIVED/('google-1996-2014-combined-audit'+stamp))
    rights = read_json(DERIVED/(PREFIX+'rights'+stamp))
    assets = read_csv(DERIVED/(PREFIX+'us-asset-register.csv'))
    titles = read_csv(DERIVED/(PREFIX+'title-evidence.csv'))
    corpus_summary(window,combined)
    validate_registry(assets,titles,rights)
    if args.source_dir:
        replay(args.source_dir,window,combined,assets,titles,rights)
    print('Google 2014 / Lenovo–Motorola Mobility:',window['union']['publications'],'publications,',
          combined['pages'],'longitudinal pages,',len(rights['reels']),'USPTO reels,',len(titles),'application rows',
          '(private replay)' if args.source_dir else '(public summaries and ledgers)')


if __name__ == '__main__':
    main()
