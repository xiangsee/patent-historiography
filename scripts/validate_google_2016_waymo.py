#!/usr/bin/env python3
"""Audit the Google 2016 corpus and replay the Waymo/X assignment inventory."""

import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path
import re
import sys
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame
from validate_google_2011_patent_transfers import read_csv
from validate_google_2012_motorola_assets import pdf_or_archive_hash, reel_data
from validate_google_2013_arris_home import history
from validate_google_2015_alphabet import party_names, serial, title_kind

YEAR = '2016'
LAUNCH = '2016-12-13'
LAST_CORE_TRANSFER = '2017-03-22'
DATES = {'before_launch':'2016-12-12', 'launch_day':LAUNCH, 'year_end':'2016-12-31',
         'after_core_transfers':'2017-03-23', 'after_core_recordation':'2017-03-28'}
PREFIX = 'google-2016-waymo-'
STAMP = '-2026-11-22.json'
GOOGLE = {'GOOGLEINC','GOOGLELLC'}
X = {'XDEVELOPMENTLLC'}
HOLDING = {'WAYMOHOLDINGINC','WAYMOHOLDINGSINC','WAYMOHOLDIINGINC','INCWAYMOHOLDING'}
WAYMO = {'WAYMOLLC','LLCWAYMO'}
DRIVING_TITLE = re.compile(r'\b(?:autonomous (?:vehicle|driving|car)|self[- ]driving|driverless|road user|remote (?:vehicle|assistance)|vehicle (?:trajectory|perception))', re.I)
ASSIGNEE_CORRECTION = re.compile(
    r'CORRECT THE (?:ASSIGNEE NAME|INCORRECT RECEIVING PARTY DATA)\s+PREVIOUSLY RECORDED '
    r'(?:AT|ON) REEL:?\s*(\d+)\s+FRAME:?\s*(\d+)',re.I,
)
MATCHED_ROUTES = {
    'google-waymo-wide':{'2016','2017'}, 'waymo-wide-waymo':{'2016','2017'},
    'google-x':{'2016'}, 'x-assignor':{'2016','2017'},
}


def selected_reels(groups, controls):
    return set(controls) | {
        reel_frame(e) for route,years in MATCHED_ROUTES.items()
        for e in groups[route] if iso(e['assignorExecutionDate'])[:4] in years
    } | {reel_frame(e) for e in groups['google-waymo']}


def classify(event):
    source = {key(p) for p in party_names(event,'assignor')}
    target = {key(p) for p in party_names(event,'assignee')}
    executed = iso(event['assignorExecutionDate'])
    kind = title_kind(event)
    if kind == 'correction':
        return 'correction'
    if kind == 'name_or_form':
        return 'name_or_form_as_indexed'
    if kind != 'assignment':
        return 'other_instrument'
    if source & GOOGLE and target & X and executed.startswith('2016'):
        return 'google_to_x'
    if source & GOOGLE and target & HOLDING and executed.startswith('2017'):
        return 'google_to_holding'
    if source & HOLDING and target & WAYMO and executed.startswith('2017'):
        return 'holding_to_waymo'
    if source & GOOGLE and target & WAYMO:
        return 'google_to_waymo_direct'
    if source & X and target - X:
        return 'x_outbound'
    return 'comparison'


def build_assets(folder, reels):
    for ref, meta in sorted(reels.items()):
        replies = list(reel_data(folder,ref,meta['pages']))
        event = replies[0]['data']['assignment']
        assert reel_frame(event)==ref
        properties = [p for r in replies for p in r['data']['properties']]
        assert len(properties)==meta['properties']==len({p['propertySequenceNumber'] for p in properties})
        assert all(r['totalRows']==len(properties) for r in replies)
        for p in sorted(properties,key=lambda p:p['propertySequenceNumber']):
            yield {
                'reel_frame':ref, 'property_sequence':str(p['propertySequenceNumber']),
                'application_serial':(p['applicationNumber'] or '').strip(),
                'patent_number':(p['patentNumber'] or '').strip(),
                'publication_number':(p['publicationNumber'] or '').strip(),
                'pct_number':(p['pctNumber17'] or p['pctNumber'] or '').strip(),
                'filing_date':iso(p['fillingDate']),'title':(p['inventionTitle'] or '').strip(),
                'execution_date':iso(event['assignorExecutionDate']), 'recordation_date':iso(event['recordationDate']),
                'instrument_as_of_date':meta.get('instrument_as_of_date',''),
                'record_type':title_kind(event),'scope':classify(event),
                'conveyance':event['conveyance'].strip(),
                'from_names':' | '.join(party_names(event,'assignor')),
                'to_names':' | '.join(party_names(event,'assignee')),
            }


def choose_case_cohort(rows):
    found = defaultdict(dict)
    for name, records in rows.items():
        for p in records:
            if p['country_code']!='US':
                continue
            if name in ('inc','llc') and not DRIVING_TITLE.search(p['title'] or ''):
                continue
            if name not in {'inc','llc','waymo','x'}:
                continue
            app = serial(p['application_number'])
            assert app, p['application_number']
            found[app][key(p['publication_number'])] = p
    return found


def owner_group(event):
    labels = {key(n) for n in party_names(event,'assignee')}
    if labels and labels <= GOOGLE:
        return 'google_inc_or_llc'
    if labels and labels <= X:
        return 'x_development'
    if labels and labels <= HOLDING:
        return 'waymo_holding'
    if labels and labels <= WAYMO:
        return 'waymo_llc'
    return 'other_or_joint'


def snapshot(events, filed, day, record_cutoff=False):
    if filed and filed>day:
        return 'not_yet_filed',None
    if events is None:
        return 'history_unavailable',None
    eligible = [e for e in events if ''<iso(e['assignorExecutionDate'])<=day
                and (not record_cutoff or ''<iso(e['recordationDate'])<=day)]
    title = {reel_frame(e):e for e in eligible if title_kind(e) in {'assignment','name_or_form','merger'}}
    for e in eligible:
        fix = ASSIGNEE_CORRECTION.search(e['conveyance'])
        if not fix:
            continue
        corrected_ref = f'{int(fix[1]):06d}/{int(fix[2]):04d}'
        original = title.get(corrected_ref)
        if original and original['assignorExecutionDate']==e['assignorExecutionDate']:
            title[corrected_ref] = e
    if not title:
        return 'no_title_event',None
    order = lambda e:(iso(e['assignorExecutionDate']),iso(e['recordationDate']),reel_frame(e))
    event = max(title.values(),key=order)
    participants = {owner_group(e) for e in title.values() if order(e)[0]==order(event)[0]}
    return ('same_day_multiple_recipient_groups' if len(participants)>1 else owner_group(event)), event


def build_titles(assets, cases, histories):
    by_app = defaultdict(list)
    for p in assets:
        if p['application_serial']:
            by_app[p['application_serial']].append(p)
    for number in sorted(set(by_app)|set(cases)|set(histories)):
        props = by_app[number]
        observed = cases.get(number,{})
        pg = min(observed.values(),key=lambda p:p['publication_date']) if observed else {}
        events = histories.get(number)
        refs = defaultdict(set)
        for p in props:
            refs[p['scope']].add(p['reel_frame'])
        first, second = refs['google_to_holding'], refs['holding_to_waymo']
        earliest = min((p['filing_date'] for p in props if p['filing_date']),default='')
        filed = earliest or pg.get('filing_date','')
        title = next((p['title'] for p in props if p['title']),pg.get('title','') or '')
        if first and second:
            pattern = 'two_hop_waymo'
        elif first or second:
            pattern = 'one_waymo_hop'
        elif refs['google_to_waymo_direct']:
            pattern = 'direct_waymo'
        elif refs['google_to_x']:
            pattern = 'x_transfer'
        else:
            pattern = 'other_or_comparator'
        entry = {
            'application_serial':number,'filing_date':filed,'title':title,'title_pattern':pattern,
            'targeted_2016_provider_publications':' | '.join(sorted(observed)),
            'us_patent_numbers_in_register':' | '.join(sorted({p['patent_number'] for p in props if p['patent_number']})),
            'google_to_holding_reels':' | '.join(sorted(first)), 'holding_to_waymo_reels':' | '.join(sorted(second)),
            'google_to_waymo_direct_reels':' | '.join(sorted(refs['google_to_waymo_direct'])),
            'google_to_x_reels':' | '.join(sorted(refs['google_to_x'])),
            'x_outbound_reels':' | '.join(sorted(refs['x_outbound'])),
            'correction_or_name_record_reels':' | '.join(sorted(refs['correction']|refs['name_or_form_as_indexed'])),
            'first_waymo_llc_recordation_in_inventory':min((p['recordation_date'] for p in props
                    if p['scope'] in ('holding_to_waymo','google_to_waymo_direct')),default=''),
            'original_as_of_reels':' | '.join(sorted({p['reel_frame'] for p in props if p['instrument_as_of_date']})),
            'history_event_count':str(len(events)) if events is not None else '',
        }
        for marker,day in DATES.items():
            state, e = snapshot(events,filed,day)
            contemporary, r = snapshot(events,filed,day,True)
            entry[marker+'_evidence'] = state
            entry[marker+'_reel'] = reel_frame(e) if e else ''
            entry[marker+'_holder'] = ' | '.join(party_names(e,'assignee')) if e else ''
            entry[marker+'_as_recorded'] = contemporary
            entry[marker+'_as_recorded_reel'] = reel_frame(r) if r else ''
        yield entry


def summary(assets, titles, target_cases):
    subsets = defaultdict(list)
    for p in assets:
        subsets[p['scope']].append(p)
    by_scope = {}
    for k,rows in subsets.items():
        by_scope[k] = {
            'reels':len({p['reel_frame'] for p in rows}), 'asset_rows':len(rows),
            'application_serials':len({p['application_serial'] for p in rows if p['application_serial']}),
            'pct_only_numbers':len({p['pct_number'] for p in rows if p['pct_number'] and not p['application_serial']}),
            'recordation_reels_by_year':dict(Counter({p['reel_frame']:p['recordation_date'][:4] for p in rows}.values())),
        }
    two_hop = [t for t in titles if t['title_pattern']=='two_hop_waymo']
    candidates = [t for t in titles if t['application_serial'] in target_cases]
    return {
        'by_scope':by_scope, 'asset_rows':len(assets),'title_rows':len(titles),
        'title_patterns':dict(Counter(t['title_pattern'] for t in titles)),
        'two_hop_filing_dates':dict(Counter(('missing' if not t['filing_date'] else
            'by_launch' if t['filing_date']<=LAUNCH else 'by_march_transfer'
            if t['filing_date']<=LAST_CORE_TRANSFER else 'after_march_transfer') for t in two_hop)),
        'earliest_observed_waymo_recordation_by_year':dict(Counter(t['first_waymo_llc_recordation_in_inventory'][:4]
            for t in two_hop if t['first_waymo_llc_recordation_in_inventory'])),
        'x_waymo_title_overlap':sum(t['google_to_x_reels'] and bool(t['google_to_holding_reels'] or
                 t['holding_to_waymo_reels'] or t['google_to_waymo_direct_reels']) for t in titles if t['google_to_x_reels']),
        'case_count':len(candidates), 'histories_in_case_cohort':sum(bool(t['history_event_count']) for t in candidates),
        'case_snapshot_counts':{d:dict(Counter(t[d+'_evidence'] for t in candidates)) for d in DATES},
        'case_public_registry_counts':{d:dict(Counter(t[d+'_as_recorded'] for t in candidates)) for d in DATES},
        'all_available_individual_histories':sum(bool(t['history_event_count']) for t in titles),
    }


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def continuation_index(archive, assets, cases):
    patents = {r['patent_number'] for r in assets if r['scope'] in {'google_to_holding','holding_to_waymo'}}
    patents.update(p[2:-2] for r in cases.values() for p in r if p.endswith(('B1','B2')))
    identifiers = {s.encode() for s in patents if s}
    relations = {(b'continuation',b'parent-doc'),(b'continuation',b'child-doc'),
                 (b'continuation-in-part',b'parent-doc'),(b'continuation-in-part',b'child-doc'),
                 (b'division',b'parent-doc'),(b'division',b'child-doc')}
    evidence = set()
    with ZipFile(archive) as source:
        member = next(n for n in source.namelist() if n.endswith('.tsv'))
        with source.open(member) as rows:
            columns = next(csv.reader([next(rows).decode()],delimiter='\t'))
            assert columns[:8] == ['patent_id','related_doc_number','published_country','related_doc_type',
                                   'related_doc_kind','related_doc_published_date','related_doc_status',
                                   'related_doc_sequence']
            for line in rows:
                parts = line.split(b'\t',8)
                if parts[0].strip(b'"') not in identifiers or len(parts)<9:
                    continue
                number, country, kind, role = (p.strip(b'"') for p in parts[1:5])
                if country != b'US' or (kind,role) not in relations or len(number)!=8 or not number.isdigit():
                    continue
                rec = next(csv.reader([line.decode()],delimiter='\t'))
                evidence.add((rec[0],rec[1],rec[3],rec[4],rec[5],rec[7]))
    fields = ('us_grant_number','related_us_application_serial','relation_as_indexed','relative_role_as_indexed',
              'related_date_as_indexed','sequence_in_grant_index')
    return [dict(zip(fields,row)) for row in sorted(evidence)]


def check_corpus(window, combined):
    q = window['query_audits']
    assert [r['page_count'] for r in q]==[81,87]
    assert [r['provider_total'] for r in q]==[4028,4306]
    assert all(sum(r['returned_by_page'])==r['provider_total'] for r in q)
    assert (combined['query_windows'],combined['pages'])==(27,1043)
    fields=('publications','application_numbers','provider_family_ids')
    assert [window['union'][k] for k in fields]==[8320,5605,3060]
    assert [combined['union'][k] for k in fields]==[50156,35800,16412]
    assert combined['cross_window_overlap']=={'publications':0,'application_numbers':0,'provider_family_ids':1590}


def replay(folder, window, combined, assets, titles, related, roles, rights):
    folders=('round28','round27','round26','round25','round24','round23','round22')
    paths=[str(folder/'*.batch.json'),*(str(folder.parent/r/'*.batch.json') for r in folders),str(folder.parent/'*.batch.json')]
    annual,pages=load(paths[:1])
    report=audit_longitudinal_coverage(annual,pages,as_of_dates=window['publication_date_snapshots'])
    assert report=={k:v for k,v in window.items() if k not in ('tool','tool_version')}
    rows,all_pages=load(paths)
    report=audit_longitudinal_coverage(rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert report[field]==combined[field]
    assert len(all_pages)==combined['pages']
    new_ids={p['query_id'] for p in pages}
    for field,label,normalize in [('publication_number','publications',key),('application_number','application_numbers',key),
                                 ('family_id','provider_family_ids',family)]:
        previous={normalize(r[field]) for r in rows if r['_query_id'] not in new_ids}
        assert len(previous&{normalize(r[field]) for r in annual})==combined['cross_window_overlap'][label]
    annual_ids={key(r['publication_number']) for r in annual}
    assert {r['publication_key'] for r in read_csv(folder/'google-2016-publication-list.csv')}==annual_ids

    named=defaultdict(list)
    buckets={r['query_id']:('inc' if r['query']['assignee']=='Google Inc.' else 'llc') for r in pages}
    for r in annual:
        named[buckets[r['_query_id']]].append(r)
    for name,meta in rights['provider_probes'].items():
        probe,probe_pages=load([str(folder/f'target-{name}.json')])
        named[name]=probe
        assert len(probe)==meta['rows'] and len(probe_pages)==meta['pages']
        assert len(annual_ids&{key(p['publication_number']) for p in probe})==meta['mother_publication_overlap']
    cases=choose_case_cohort(named)
    assert sorted(cases)==rights['case_serials']

    registry=folder/'registry'
    index=read_json(registry/'route-index.json')
    for name,route in rights['registry_queries'].items():
        gathered=[]
        for page in range(1,route['pages']+1):
            request,response=official(registry/f'route-{name}-page{page}.json')
            assert request['searchCriteria']==route['criteria']
            assert response['totalRows']==route['total_reels']
            gathered.extend(response['data'] or [])
        assert gathered==index[name]
    assert selected_reels(index,rights['control_reels'])==set(rights['reels'])|set(rights['reels_unavailable'])
    assert list(build_assets(folder,rights['reels']))==assets
    histories={p:history(folder,p) for p in rights['checked_individual_histories']}
    assert list(build_titles(assets,cases,histories))==titles
    assert read_json(folder/'sources'/'native-roles.json')==roles
    if related:
        assert continuation_index(folder/'sources'/'g_us_rel_doc.tsv.zip',assets,cases)==related
    for source in rights['archived_sources'].values():
        assert pdf_or_archive_hash(folder/source['file'])==source['sha256']
    for publication in rights['epo_publication_controls']:
        doc=ElementTree.parse(folder/publication['file']).getroot()
        assert doc.attrib['doc-number']+doc.attrib['kind']==publication['identifier'][2:]
        assert doc.attrib['date-publ']==publication['date'].replace('-','')
        role='B730/B731' if doc.attrib['kind']=='B1' else 'B710/B711'
        assert [n.text for n in doc.findall(f'.//{role}/snm')]==[publication['party']]


def validate_public(assets, titles, related, roles, rights):
    assert len(assets)==len({(r['reel_frame'],r['property_sequence']) for r in assets})
    assert len(titles)==len({r['application_serial'] for r in titles})
    assert rights['business']['launch_date']==LAUNCH
    assert rights['business']['main_contribution_as_of_date']=='2017-02-22'
    assert rights['business']['main_assignment_execution_dates']==['2017-03-21','2017-03-22']
    assert summary(assets,titles,set(rights['case_serials']))==rights['registry_totals']
    assert len(rights['reels'])==1129 and not rights['reels_unavailable']
    assert len(assets)==3607 and rights['registry_totals']['title_patterns']['two_hop_waymo']==1117
    assert rights['registry_totals']['histories_in_case_cohort']==406
    x=rights['registry_totals']['by_scope']['google_to_x']
    assert (x['reels'],x['application_serials'],rights['registry_totals']['x_waymo_title_overlap'])==(209,1059,0)
    assert len(roles)==rights['publication_roles']['rows']
    assert len(related)==rights['continuation_index']['rows']
    if related:
        assert any(r['us_grant_number']=='10718622' and r['related_us_application_serial']=='15645297'
                   and r['relation_as_indexed']=='continuation' and r['relative_role_as_indexed']=='parent-doc'
                   for r in related)
    by_serial={r['application_serial']:r for r in titles}
    assert by_serial['15347389']['before_launch_reel']=='042397/0260'
    assert by_serial['15347389']['before_launch_holder']=='GOOGLE INC.'
    assert by_serial['15075878']['title_pattern']=='two_hop_waymo'
    assert by_serial['15332619']['after_core_recordation_holder']=='GOOGLE INC.'
    for route in ('x-waymo','x-waymo-wide','x-holding-name'):
        assert rights['registry_queries'][route]['total_reels']==0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path)
    args=parser.parse_args()
    window=read_json(DERIVED/('google-2016-name-coverage'+STAMP))
    combined=read_json(DERIVED/('google-1996-2016-combined-audit'+STAMP))
    rights=read_json(DERIVED/(PREFIX+'rights'+STAMP))
    assets=read_csv(DERIVED/(PREFIX+'us-asset-register.csv'))
    titles=read_csv(DERIVED/(PREFIX+'us-title-evidence.csv'))
    roles=read_csv(DERIVED/(PREFIX+'published-parties.csv'))
    related=read_csv(DERIVED/(PREFIX+'us-continuation-index.csv')) if rights['continuation_index']['rows'] else []
    check_corpus(window,combined)
    validate_public(assets,titles,related,roles,rights)
    if args.source_dir:
        replay(args.source_dir,window,combined,assets,titles,related,roles,rights)
    print('Google 2016 / Waymo:',window['union']['publications'],'publications,',combined['pages'],
          'longitudinal pages,',len(rights['reels']),'USPTO reels,',len(titles),'application evidence rows',
          '(private replay)' if args.source_dir else '(public summaries and ledgers)')


if __name__=='__main__':
    main()
