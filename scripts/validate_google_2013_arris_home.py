#!/usr/bin/env python3
"""Replay the 2013 name corpus and the Motorola Home title evidence."""

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame
from validate_google_2011_patent_transfers import read_csv
from validate_google_2012_motorola_assets import comparable_publication, pdf_or_archive_hash, reel_data

CLOSING = '2013-04-17'
SAME_NAME_GIC = {'GENERALINSTRUMENTCORPORATION', 'GENERALINSTRUMENTCORP'}
TITLE_EVENTS = {"ASSIGNMENT OF ASSIGNOR'S INTEREST", "ASSIGNMENT OF ASSIGNORS INTEREST",
                'MERGER', 'MERGER AND CHANGE OF NAME', 'CHANGE OF NAME'}
SECURITY = '030498/0023'


def ledger_row(scope, event, p):
    return {
        'scope': scope, 'reel_frame': reel_frame(event), 'property_sequence': str(p['propertySequenceNumber']),
        'application_serial': p['applicationNumber'] or '', 'filing_date': iso(p['fillingDate']),
        'publication_number': p['publicationNumber'] or '', 'patent_number': p['patentNumber'] or '',
        'execution_date_as_recorded': iso(event['assignorExecutionDate']), 'recordation_date': iso(event['recordationDate']),
        'from_entities': ' | '.join(a['assignorName'] for a in event['assignors']),
        'to_entities': ' | '.join(a['assigneeName'] for a in event['assignees']),
        'conveyance_as_recorded': event['conveyance'], 'title_in_register': (p['inventionTitle'] or '').rstrip(),
    }


def nonempty_ids(rows):
    return {r['application_serial'] for r in rows if r['application_serial']}


def published_in_google(rows, google_ids):
    ids = set()
    for row in rows:
        if row['publication_number']:
            ids.add(comparable_publication(row['publication_number']))
        if row['patent_number']:
            ids.update('US' + row['patent_number'] + kind for kind in ('B1','B2','S','S1','A','E','E1'))
    return ' | '.join(sorted(google_ids & ids))


def history(folder, serial):
    request, result = official(folder/'registry'/f'application-{serial}.json')
    assert request['searchBy']=='applicationNumber' and request['property']==serial
    events = result['data']['assignment']
    assert len(events)==result['totalRows'] and not result['backendPagination']
    return events


def gic_title_before_close(events):
    def party(event, collection, field):
        return any(key(p[field]) in SAME_NAME_GIC for p in event[collection])

    def event_date(event):
        return iso(event['assignorExecutionDate']), iso(event['recordationDate'])

    dated = [e for e in events if e['conveyance'].upper() in TITLE_EVENTS
             and '' < iso(e['assignorExecutionDate']) <= CLOSING]
    receipts = [e for e in dated if party(e,'assignees','assigneeName')]
    if not receipts:
        return None
    last = max(receipts, key=event_date)
    if any(event_date(e)[0] >= event_date(last)[0] and party(e,'assignors','assignorName')
           and not party(e,'assignees','assigneeName') for e in dated):
        return None
    return last


def title_rows(assets, reviewed, google_ids):
    by_app = defaultdict(list)
    for p in assets:
        if p['application_serial']:
            by_app[p['application_serial']].append(p)
    prefixes = ('home-carve-out-april15', 'home-retained-may28', 'holdings-to-home-at-close',
                'other-home-period-mobile-to-holdings', 'home-to-arris-successors')
    for serial, props in sorted(by_app.items()):
        scope = defaultdict(list)
        for p in props:
            scope[p['scope']].append(p['reel_frame'])
        carve, retained, home, mobile, successor = [scope[s] for s in prefixes]
        if not (carve or retained or home or mobile or successor or scope['retention-reconciled']):
            continue
        combo = {p['reel_frame'] for p in props if p['scope']=='retention-reconciled'}
        carve = [*carve, *sorted(combo & {'038858/0532','063229/0506'})]
        retained = [*retained, *sorted(combo & {'034582/0099'})]
        ctrl = reviewed.get(serial, {})
        gic = ctrl.get('preclose_title_event') or {}
        representative = max(props, key=lambda p:(bool(p['title_in_register']), p['recordation_date']))
        if carve and retained:
            category = 'retained_both_hops'
        elif home and mobile:
            category = 'home_contribution_both_hops'
        elif successor and gic:
            category = 'gic_preclose_receipt_and_arris_succession'
        elif carve or retained:
            category = 'retained_chain_one_hop'
        else:
            category = 'arris_successor_record_only'
        yield {
            'application_serial':serial, 'filing_date_in_register':representative['filing_date'],
            'title_in_register':representative['title_in_register'],
            'publication_numbers':' | '.join(sorted({p['publication_number'] for p in props if p['publication_number']})),
            'patent_numbers':' | '.join(sorted({p['patent_number'] for p in props if p['patent_number']})),
            'title_evidence':category,
            'gic_to_holdings':' | '.join(sorted(set(carve))), 'holdings_to_mobility':' | '.join(sorted(set(retained))),
            'mobility_to_holdings_for_home':' | '.join(sorted(set(mobile))), 'holdings_to_gic_for_home':' | '.join(sorted(set(home))),
            'gic_to_arris_successor':' | '.join(sorted(set(successor))),
            'preclose_gic_receipt':gic.get('reel_frame', ''),
            'preclose_gic_receipt_recorded':gic.get('recordation_date', ''),
            'closing_security_record':SECURITY if ctrl.get('closing_security_record') else '',
            'matched_google_2013_publications':published_in_google(props, google_ids),
        }


def validate_public(window, combined, assets, titles, rights):
    q = window['query_audits']
    assert [a['page_count'] for a in q] == [142,19]
    assert [a['provider_total'] for a in q] == [7088,913]
    assert all(sum(a['returned_by_page'])==a['provider_total'] for a in q)
    assert [window['union'][k] for k in ('publications','application_numbers','provider_family_ids',
                                        'multiple_assignee_filter_matches','earlier_priority_year_rows')] == [7873,5641,4306,128,4680]
    assert (combined['query_windows'],combined['pages']) == (21,617)
    assert [combined['union'][k] for k in ('publications','application_numbers','provider_family_ids')] == [29208,21485,11565]
    assert combined['cross_window_overlap'] == {'publications':0,'application_numbers':0,'provider_family_ids':1307}
    assert [s['reported_published_by_cutoff'] for s in window['publication_date_snapshots'].values()] == [10,25,47,724]
    assert [s['reported_published_by_cutoff'] for s in combined['publication_date_snapshots'].values()] == [9097,10283,10848,11309,13581]

    announced = rights['transaction']['disclosed_patent_assets']
    assert (announced['home_at_signing'],announced['home_acquired'],announced['home_retained_and_licensed'])==(3164,991,2173)
    assert announced['home_at_signing']==announced['home_acquired']+announced['home_retained_and_licensed']
    assert rights['transaction']['contract_date']=='2012-12-19' and rights['transaction']['actual_closing']==CLOSING
    assert rights['transaction']['individual_license_schedule_obtained'] is False
    scopes = defaultdict(list)
    for row in assets:
        scopes[row['scope']].append(row)
    for k, rows, unique in [('home-carve-out-april15',1075,1035),('home-retained-may28',1078,1038),
                             ('holdings-to-home-at-close',20,18),('other-home-period-mobile-to-holdings',20,18),
                             ('home-to-arris-successors',704,615)]:
        assert len(scopes[k])==rows and len(nonempty_ids(scopes[k]))==unique
    assert len(nonempty_ids(scopes['home-carve-out-april15']) & nonempty_ids(scopes['home-retained-may28']))==1033
    assert nonempty_ids(scopes['holdings-to-home-at-close']) == nonempty_ids(scopes['other-home-period-mobile-to-holdings'])
    assert len(assets)==len({(r['reel_frame'],r['property_sequence']) for r in assets})==2988
    assert len(rights['reels'])==105 and len(scopes['retention-reconciled'])==3
    assert {r['reel_frame'] for r in scopes['retention-reconciled']} == {'034582/0099','038858/0532','063229/0506'}
    by_code = Counter(t['title_evidence'] for t in titles)
    assert by_code['retained_both_hops']==1036 and by_code['retained_chain_one_hop']==4
    assert by_code['home_contribution_both_hops']==18
    assert sum(bool(r['gic_to_arris_successor'] and r['preclose_gic_receipt']) for r in titles)==479
    assert sum(bool(r['gic_to_arris_successor'] and r['closing_security_record'] and r['filing_date_in_register']<=CLOSING)
               for r in titles)==480
    assert len(titles)==len({t['application_serial'] for t in titles})==1657
    continuity = rights['closing_continuity']
    assert [continuity[k] for k in ('candidate_preclose_filers_in_successor_reels','recorded_by_closing',
                                     'continuity_and_security_pledge','also_named_in_closing_transfer_chain')]==[542,458,433,16]


def replay(folder, window, combined, assets, titles, rights):
    paths=[str(folder/'*.batch.json'),*(str(folder.parent/r/'*.batch.json') for r in ('round25','round24','round23','round22')),
           str(folder.parent/'*.batch.json')]
    rows,pages=load(paths[:1]); report=audit_longitudinal_coverage(rows,pages,as_of_dates=window['publication_date_snapshots'])
    assert report=={k:v for k,v in window.items() if k not in ('tool','tool_version')}
    fields={'publications':('publication_number',key), 'application_numbers':('application_number',key), 'provider_family_ids':('family_id',family)}
    all_rows,all_pages=load(paths)
    longer=audit_longitudinal_coverage(all_rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert longer[field]==combined[field]
    qids={p['query_id'] for p in pages}
    prior=[r for r in all_rows if r['_query_id'] not in qids]
    for label,(field,normalize) in fields.items():
        assert len({normalize(r[field]) for r in rows}&{normalize(r[field]) for r in prior})==combined['cross_window_overlap'][label]
    pubs={comparable_publication(r['publication_number']) for r in rows}
    names={p['query_id']:p['query']['assignee'] for p in pages}; hits=defaultdict(set)
    for row in rows: hits[key(row['publication_number'])].add(names[row['_query_id']])
    roster=read_csv(folder/'google-2013-publication-list.csv')
    assert [r['publication_key'] for r in roster]==sorted(hits)
    assert all(set(r['matching_query_names'].split(' | '))==hits[r['publication_key']] for r in roster)

    expected=[]
    for reel in rights['reels']:
        total=reel['property_rows']; inspected=[]
        for n,data in enumerate(reel_data(folder,reel['reel_frame'],reel['pages']),1):
            event=data['data']['assignment']; items=data['data']['properties']
            assert reel_frame(event)==reel['reel_frame'] and data['totalRows']==total
            if reel['pages']>1: assert data['backendPagination'] and len(items)==min(1000,total-(n-1)*1000)
            inspected.extend(ledger_row(reel['scope'],event,p) for p in items)
        assert len(inspected)==len({r['property_sequence'] for r in inspected})==total
        if reel['scope']!='collateral_context': expected.extend(inspected)
    assert expected==assets
    reviewed=read_json(folder/'registry/continuity-review.json')
    assert titles==list(title_rows(assets,reviewed,pubs))
    for serial,value in reviewed.items():
        records=history(folder,serial); event=gic_title_before_close(records)
        assert (reel_frame(event) if event else None)==(value['preclose_title_event'] or {}).get('reel_frame')
        assert any(reel_frame(e)==SECURITY for e in records)==value['closing_security_record']
    lookups={}
    for name,item in rights['registry_queries'].items():
        request,response=official(folder/item['file'])
        assert request==item['request'] and response['totalRows']==len(response['data'])==item['returned_records']
        lookups[name]=response['data']
    scope_checks = {
        'home-carve-out-april15': ('gic-to-gih',{'2013-04-15'}),
        'home-retained-may28': ('gih-to-mm',{'2013-05-28'}),
        'holdings-to-home-at-close': ('gih-to-gic',{'2013-04-16','2013-04-17'}),
        'home-to-arris-successors': ('gi-to-arris',None),
    }
    for scope,(query,days) in scope_checks.items():
        from_query={reel_frame(e) for e in lookups[query] if days is None or iso(e['assignorExecutionDate']) in days}
        assert from_query=={r['reel_frame'] for r in rights['reels'] if r['scope']==scope}
    for target in rights['target_queries'].values():
        data=read_json(folder/target['file']);assert sum(len(p['records']) for p in data['pages'])==target['provider_total']
    for source in rights['archived_sources']:
        assert pdf_or_archive_hash(folder/source['file'])==source['sha256']
        if source['kind']=='epo_native_xml':
            xml=ElementTree.parse(folder/source['file']).getroot()
            assert xml.attrib['country']+xml.attrib['doc-number']+xml.attrib['kind']==source['publication']
            assert xml.findtext('.//B210')==source['application_number']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-source-dir',type=Path)
    args=parser.parse_args()
    window=read_json(DERIVED/'google-2013-name-coverage-2026-11-22.json')
    combined=read_json(DERIVED/'google-1996-2013-combined-audit-2026-11-22.json')
    rights=read_json(DERIVED/'google-2013-arris-home-rights-2026-11-22.json')
    assets=read_csv(DERIVED/rights['asset_ledger']);titles=read_csv(DERIVED/rights['title_ledger'])
    validate_public(window,combined,assets,titles,rights)
    if args.private_source_dir:
        replay(args.private_source_dir.resolve(),window,combined,assets,titles,rights)
        print('PASS: 617-page replay, ARRIS and Home recorded assets, serial histories and source hashes')
    print('PASS: 7,873 publications, 1,036 retained title paths, 18 closing contributions')


if __name__=='__main__':
    main()
