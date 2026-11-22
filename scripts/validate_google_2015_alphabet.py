#!/usr/bin/env python3
"""Replay the 2015 Google name corpus and the U.S. title evidence around Alphabet."""

import argparse
from collections import Counter, defaultdict
import csv
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
from validate_google_2012_motorola_assets import pdf_or_archive_hash, reel_data
from validate_google_2013_arris_home import history

YEAR = '2015'
DATES = {'before':'2015-10-01', 'close_day':'2015-10-02', 'year_end':'2015-12-31'}
PREFIX = 'google-2015-alphabet-'
STAMP = '-2026-11-22.json'
US_SERIAL = re.compile(r'US(?:19|20)[0-9]{2}([0-9]{8})[A-Z][0-9]*')
NAMES = {
    'GOOGLEINC':'Google Inc.', 'GOOGLELLC':'Google LLC',
    'ALPHABETINC':'Alphabet Inc.',
    'GOOGLETECHNOLOGYHOLDINGSLLC':'Google Technology Holdings LLC',
    'GOOGLELIFESCIENCESLLC':'Google Life Sciences LLC',
    'VERILYLIFESCIENCESLLC':'Verily Life Sciences LLC',
    'NESTLABSINC':'Nest Labs, Inc.', 'DROPCAMINC':'Dropcam, Inc.',
    'CALICOLIFESCIENCESLLC':'Calico Life Sciences LLC',
    'XDEVELOPMENTLLC':'X Development LLC', 'GOOGLEFIBERINC':'Google Fiber Inc.',
    'DEEPMINDTECHNOLOGIESLIMITED':'DeepMind Technologies Limited',
    'WAYMOLLC':'Waymo LLC',
    'MOTOROLAMOBILITYLLC':'Motorola Mobility LLC',
    'MOTOROLOAMOBILITYLLC':'Motorola Mobility LLC',
}
GOOGLE_PARENT = {'GOOGLEINC','GOOGLELLC'}
TRACKED_UNITS = set(NAMES) - GOOGLE_PARENT - {'ALPHABETINC','MOTOROLAMOBILITYLLC','MOTOROLOAMOBILITYLLC'}


def serial(application_number):
    match = US_SERIAL.fullmatch(key(application_number))
    return match[1] if match else ''


def party_names(event, side):
    field = f'{side}Name'
    return [row[field].strip() for row in event[f'{side}s'] if row.get(field)]


def title_kind(event):
    text = event['conveyance'].upper()
    if 'CORRECT' in text or 'NULLIF' in text:
        return 'correction'
    if 'SECURITY' in text or 'LIEN' in text or 'COLLATERAL' in text:
        return 'security_or_release'
    if 'LICENSE' in text:
        return 'license'
    if text.startswith(('CHANGE OF NAME','CERTIFICATE OF CONVERSION','CONVERSION','CHANGE OF ENTITY')):
        return 'name_or_form'
    if text.startswith(('MERGER','CERTIFICATE OF MERGER')):
        return 'merger'
    if text.startswith(('ASSIGNMENT','ASSIGNORS','NUNC PRO TUNC ASSIGNMENT',
                        'PATENT ASSIGNMENT','CONTRIBUTION','TRANSFER')):
        return 'assignment'
    return 'other'


def party_class(event):
    if not event:
        return 'no_title_event'
    names = party_names(event,'assignee')
    ids = {key(s) for s in names}
    if ids == {'GOOGLEINC'}:
        return 'google_inc'
    if ids == {'GOOGLELLC'}:
        return 'google_llc'
    if ids and ids <= TRACKED_UNITS:
        return 'tracked_group_entity'
    if ids & (GOOGLE_PARENT | TRACKED_UNITS):
        return 'mixed_assignees'
    if ids == {'ALPHABETINC'}:
        cities = {key(p.get('city') or '') for p in event['assignees']}
        return 'alphabet_inc' if 'MOUNTAINVIEW' in cities else 'alphabet_name_requires_entity_check'
    return 'other_assignee'


def snapshot(events, filed, day, recorded_by_day):
    if filed > day:
        return 'not_filed_by_date',None
    eligible = []
    for event in events:
        executed=iso(event['assignorExecutionDate'])
        recorded=iso(event['recordationDate'])
        if not executed or executed>day or (recorded_by_day and (not recorded or recorded>day)):
            continue
        if title_kind(event) in {'assignment','merger','name_or_form'}:
            eligible.append(event)
    if not eligible:
        return 'no_title_event',None
    event = max(eligible,key=lambda e:(iso(e['assignorExecutionDate']),iso(e['recordationDate']),reel_frame(e)))
    same_day = {tuple(sorted(key(n) for n in party_names(e,'assignee')))
                for e in eligible if iso(e['assignorExecutionDate']) == iso(event['assignorExecutionDate'])}
    return ('multiple_same_day_recipients' if len(same_day)>1 else party_class(event)),event


def beneficiary_label(event):
    return ' | '.join(sorted({NAMES.get(key(n),n) for n in party_names(event,'assignee')})) if event else ''


def select_applications(rows_by_name):
    applications = defaultdict(list)
    skipped = set()
    for name, rows in rows_by_name.items():
        for row in rows:
            if row['country_code'] != 'US':
                continue
            sid=serial(row['application_number'])
            if not sid:
                skipped.add(row['application_number'])
                continue
            applications[sid].append((name,row))
    return applications,skipped


def cohort_rows(applications, histories):
    for sid, entries in sorted(applications.items()):
        labels = sorted({name for name,_ in entries})
        representative = min((r for _,r in entries),key=lambda r:(r['publication_date'],r['publication_number']))
        filed = representative['filing_date']
        events = histories.get(sid)
        row = {
            'application_serial':sid,'filing_date':filed,'title':(representative['title'] or '').strip(),
            'provider_publications':' | '.join(sorted({key(r['publication_number']) for _,r in entries})),
            'provider_query_names':' | '.join(labels),'history_event_count':str(len(events)) if events is not None else '',
        }
        for label,day in DATES.items():
            if events is None:
                status, event = ('not_filed_by_date' if filed > day else 'history_unavailable'), None
                contemporary, c_event = status, None
            else:
                status,event=snapshot(events,filed,day,False)
                contemporary,c_event=snapshot(events,filed,day,True)
            row.update({
                f'{label}_evidence':status,
                f'{label}_assignees':beneficiary_label(event),
                f'{label}_reel':reel_frame(event) if event else '',
                f'{label}_execution_date':iso(event['assignorExecutionDate']) if event else '',
                f'{label}_recordation_date':iso(event['recordationDate']) if event else '',
                f'{label}_as_recorded':contemporary,
                f'{label}_as_recorded_reel':reel_frame(c_event) if c_event else '',
            })
        row['all_2015_organizational_or_outbound_reels']=' | '.join(sorted({
            reel_frame(e) for e in (events or []) if iso(e['assignorExecutionDate']).startswith(YEAR)
            and (title_kind(e) in {'name_or_form','merger'} or
                 (title_kind(e)=='assignment' and {key(n) for n in party_names(e,'assignor')}
                  & (GOOGLE_PARENT | TRACKED_UNITS | {'ALPHABETINC'})))
        }))
        yield row


def compact_ref(row):
    return f"{int(row['reelNumber']):06d}/{int(row['frameNumber']):04d}"


def route_provenance(groups, selected):
    links = defaultdict(set)
    for name, rows in groups.items():
        for row in rows:
            ref = compact_ref(row)
            if ref in selected:
                links[ref].add(name)
    return links


def asset_row(event, prop, routes, basis):
    return {
        'reel_frame':reel_frame(event),'property_sequence':str(prop['propertySequenceNumber']) if basis=='reel_inventory' else '',
        'application_serial':(prop['applicationNumber'] or '').strip(),
        'patent_number':(prop['patentNumber'] or '').strip(),
        'publication_number':(prop['publicationNumber'] or '').strip(),
        'pct_number':(prop['pctNumber17'] or prop['pctNumber'] or '').strip(),
        'filing_date':iso(prop['fillingDate']),'title':(prop['inventionTitle'] or '').strip(),
        'execution_date':iso(event['assignorExecutionDate']),'recordation_date':iso(event['recordationDate']),
        'conveyance':event['conveyance'].strip(),'kind':title_kind(event),
        'from_names':' | '.join(party_names(event,'assignor')),
        'to_names':' | '.join(party_names(event,'assignee')),
        'search_routes':' | '.join(sorted(routes)),'property_basis':basis,
    }


def ledger_rows(folder, indexes, route_links, paths):
    for ref, info in sorted(indexes.items()):
        pages = list(reel_data(folder,ref,info['pages']))
        event = pages[0]['data']['assignment']
        properties = sorted((p for page in pages for p in page['data']['properties']),
                            key=lambda p:p['propertySequenceNumber'])
        assert reel_frame(event)==ref and len(properties)==len({p['propertySequenceNumber'] for p in properties})==info['properties']
        for p in properties:
            yield asset_row(event,p,route_links[ref],'reel_inventory')
    for path in sorted(paths):
        _,result=official(path)
        data=result['data']
        if not data['properties']:
            continue
        for event in data['assignment']:
            ref=reel_frame(event)
            if ref in route_links and ref not in indexes:
                yield asset_row(event,data['properties'],route_links[ref],'application_history_match')


def event_rows(groups):
    targets=selected_reels(groups)
    routes=route_provenance(groups,targets)
    indexed={compact_ref(r):r for v in groups.values() for r in v if compact_ref(r) in targets}
    for ref,event in sorted(indexed.items()):
        yield {
            'reel_frame':ref, 'execution_date':iso(event['assignorExecutionDate']),
            'recordation_date':iso(event['recorded']), 'kind':title_kind(event),
            'conveyance':event['conveyance'].strip(),
            'from_names':' | '.join(x['assignorName'].strip() for x in event['assignors']),
            'to_names':' | '.join(n.strip() for n in event['assignees']),
            'search_routes':' | '.join(sorted(routes[ref])),
        }


def selected_reels(groups):
    return {compact_ref(q) for name,rows in groups.items() for q in rows
            if (name.startswith('alphabet') and '-wide' not in name)
            or iso(q.get('assignorExecutionDate')).startswith(YEAR)
            or iso(q.get('recorded')).startswith(YEAR)}


def cohort_totals(rows):
    mother = [p for p in rows if any(n in p['provider_query_names'].split(' | ') for n in ('inc','llc'))]
    result = {}
    for label,column in [('all_named_cohorts',rows),('google_two_name_corpus',mother)]:
        result[label] = {'application_serials':len(column), 'no_events':sum(p['history_event_count']=='0' for p in column),
                         'unavailable_histories':sum(not p['history_event_count'] for p in column)}
        for day in DATES:
            result[label][day] = dict(Counter(p[day+'_evidence'] for p in column))
            result[label][day+'_as_recorded'] = dict(Counter(p[day+'_as_recorded'] for p in column))
        result[label]['same_google_inc_before_and_year_end'] = sum(
            p['before_evidence']==p['year_end_evidence']=='google_inc' for p in column)
        result[label]['same_google_inc_on_all_three_dates'] = sum(
            all(p[day+'_evidence']=='google_inc' for day in DATES) for p in column)
        result[label]['same_google_inc_on_all_three_dates_as_recorded'] = sum(
            all(p[day+'_as_recorded']=='google_inc' for day in DATES) for p in column)
    return result


def ledger_totals(rows):
    result={}
    field=lambda row:'executed_2015' if row['execution_date'].startswith(YEAR) else (
        'other_execution_recorded_2015' if row['recordation_date'].startswith(YEAR) else 'outside_2015_alphabet_control')
    subsets=defaultdict(list)
    for row in rows:
        subsets[field(row)].append(row)
    for label,subset in subsets.items():
        result[label]={
            'reels':len({r['reel_frame'] for r in subset}),'property_rows':len(subset),
            'unique_us_application_serials':len({r['application_serial'] for r in subset if r['application_serial']}),
            'reels_by_kind':dict(Counter({r['reel_frame']:r['kind'] for r in subset}.values())),
        }
    return result


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def check_corpus(window, combined):
    q=window['query_audits']
    assert [r['page_count'] for r in q]==[87,36]
    assert [r['provider_total'] for r in q]==[4347,1783]
    assert all(sum(r['returned_by_page'])==r['provider_total'] for r in q)
    assert combined['pages']==875 and combined['query_windows']==25
    assert [window['union'][k] for k in ('publications','application_numbers','provider_family_ids')] == [6072,4089,2815]
    assert [combined['union'][k] for k in ('publications','application_numbers','provider_family_ids')] == [41836,30195,14942]
    assert combined['cross_window_overlap']=={'publications':0,'application_numbers':1,'provider_family_ids':1354}
    assert window['publication_date_snapshots']['2015-10-02']['reported_published_by_cutoff']==417


def replay(folder, window, combined, ledger, cohort, events, rights):
    folders=('round27','round26','round25','round24','round23','round22')
    paths=[str(folder/'*.batch.json'),*(str(folder.parent/r/'*.batch.json') for r in folders),str(folder.parent/'*.batch.json')]
    annual,pages=load(paths[:1])
    report=audit_longitudinal_coverage(annual,pages,as_of_dates=window['publication_date_snapshots'])
    assert report=={k:v for k,v in window.items() if k not in ('tool','tool_version')}
    rows,all_pages=load(paths)
    report=audit_longitudinal_coverage(rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert report[field]==combined[field]
    for f,label,normalize in [('publication_number','publications',key),('application_number','application_numbers',key),
                              ('family_id','provider_family_ids',family)]:
        old_ids={r['query_id'] for r in all_pages}-{r['query_id'] for r in pages}
        matches={normalize(r[f]) for r in rows if r['_query_id'] in old_ids}&{normalize(r[f]) for r in annual}
        assert len(matches)==combined['cross_window_overlap'][label]
    assert len(all_pages)==combined['pages']
    annual_ids={key(r['publication_number']) for r in annual}
    assert {row['publication_key'] for row in read_csv(folder/'google-2015-publication-list.csv')}==annual_ids

    rows_by_name=defaultdict(list)
    query_slug={r['query_id']:('inc' if r['query']['assignee']=='Google Inc.' else 'llc') for r in pages}
    for row in annual:
        rows_by_name[query_slug[row['_query_id']]].append(row)
    for name, info in rights['provider_name_probes'].items():
        extra, extra_pages=load([str(folder/f'target-{name}.json')])
        rows_by_name[name]=extra
        assert len(extra)==info['rows'] and len(extra_pages)==info['pages']
        assert len(annual_ids&{key(r['publication_number']) for r in extra})==info['mother_publication_overlap']

    applications, skipped=select_applications(rows_by_name)
    assert sorted(skipped)==rights['unparsed_provider_us_application_numbers']
    available={n:history(folder,n) for n in applications if (folder/'registry'/f'application-{n}.json').is_file()}
    assert list(cohort_rows(applications,available))==cohort

    group_file=folder/'registry'/'company-history.json'
    groups=read_json(group_file)
    indexes=read_json(folder/'registry'/'company-reel-index.json')
    targets=selected_reels(groups)
    assert targets-set(indexes)==set(rights['uncaptured_registry_reels'])
    assert set(indexes)<=targets
    for name,info in rights['registry_routes'].items():
        captured=[]
        for page in range(1,info['pages']+1):
            q,r=official(folder/'registry'/f'route-{name}-page{page}.json')
            assert q['searchCriteria']==info['criteria']
            assert r['totalRows']==info['total_reels']
            captured.extend(r['data'] or [])
        assert captured==groups[name]
    assert list(event_rows(groups))==events
    case_paths=[folder/'registry'/f'application-{i}.json' for i in rights['application_history_source_serials']]
    assert list(ledger_rows(folder,indexes,route_provenance(groups,targets),case_paths))==ledger
    for source in rights['archived_sources'].values():
        assert pdf_or_archive_hash(folder/source['file'])==source['sha256']
    nest = rights['epo_nest_control']
    b1 = ElementTree.parse(folder/nest['file']).getroot()
    assert b1.attrib['country']+b1.attrib['doc-number']+b1.attrib['kind']==nest['publication']
    assert b1.attrib['date-publ']==nest['publication_date'].replace('-','')
    assert [p.text for p in b1.findall('.//B730/B731/snm')]==[nest['published_proprietor']]


def check_rights(ledger, cohort, events, rights):
    assert len(ledger)==len({(r['reel_frame'],r['property_sequence'] or r['application_serial']) for r in ledger})
    assert len(cohort)==len({r['application_serial'] for r in cohort})
    assert len(events)==rights['registry_event_count']==len({r['reel_frame'] for r in events})
    assert cohort_totals(cohort)==rights['cohort_totals']
    assert ledger_totals(ledger)==rights['ledger_totals']
    assert rights['reorganization']['effective_time']=='2015-10-02T16:01:00-04:00'
    assert rights['reorganization']['surviving_corporation']=='Google Inc.'
    assert rights['alphabet_direct_search']['identified_2015_patent_transfer_to_parent']==0
    assert all(rights['registry_routes'][route]['total_reels']==0
               for route in rights['alphabet_direct_search']['paired_routes'])
    life=rights['life_sciences']
    assert life['google_to_life_assignment_reels']==47 and life['life_to_verily_rename_reels']==58
    assert life['delaware_certificate_filed_local_time']=='2015-12-07T14:16:00-05:00'
    selected=rights['cohort_totals']['google_two_name_corpus']
    assert selected['application_serials']==2430
    assert selected['same_google_inc_on_all_three_dates']==697
    assert selected['same_google_inc_on_all_three_dates_as_recorded']==611
    assert sum(row['reel_frame']=='036398/0001' and row['property_basis']=='reel_inventory' for row in ledger)==18
    by_serial={p['application_serial']:p for p in cohort}
    assert by_serial['14656314']['before_assignees']==by_serial['14656314']['year_end_assignees']=='Google Inc.'
    assert by_serial['14669424']['before_assignees']=='Google Life Sciences LLC'
    assert by_serial['14669424']['year_end_assignees']=='Verily Life Sciences LLC'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path)
    args=parser.parse_args()
    window=read_json(DERIVED/('google-2015-name-coverage'+STAMP))
    combined=read_json(DERIVED/('google-1996-2015-combined-audit'+STAMP))
    rights=read_json(DERIVED/(PREFIX+'rights'+STAMP))
    ledger=read_csv(DERIVED/(PREFIX+'us-asset-register.csv'))
    cohort=read_csv(DERIVED/(PREFIX+'us-title-snapshots.csv'))
    events=read_csv(DERIVED/(PREFIX+'us-reel-events.csv'))
    check_corpus(window,combined)
    check_rights(ledger,cohort,events,rights)
    if args.source_dir:
        replay(args.source_dir,window,combined,ledger,cohort,events,rights)
    print('Google 2015 / Alphabet:',window['union']['publications'],'publications,',
          combined['pages'],'longitudinal pages,',len(ledger),'USPTO property rows,',
          sum(bool(r['history_event_count']) for r in cohort),'of',len(cohort),'application histories available',
          '(private replay)' if args.source_dir else '(public summaries and ledgers)')


if __name__=='__main__':
    main()
