#!/usr/bin/env python3
"""Replay the 2017 Google name corpus, Assignment Center schedules and case histories."""

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import re
from xml.etree import ElementTree

from validate_google_2015_alphabet import party_names, serial, title_kind
from validate_google_2016_waymo import ASSIGNEE_CORRECTION, write_csv
from validate_google_2010_acquisition_assets import DERIVED, iso, official, read_json, reel_frame
from validate_google_2011_patent_transfers import read_csv
from validate_google_2012_motorola_assets import pdf_or_archive_hash, reel_data
from patent_evidence.core import family, key, load
from patent_evidence.coverage import audit_longitudinal_coverage

PREFIX = 'google-2017-xxvi-'
STAMP = '-2026-11-22.json'
YEAR = '2017'
DATES = {'before': '2017-09-29', 'conversion_eod': '2017-09-30',
         'first_business_day': '2017-10-02', 'year_end': '2017-12-31'}
CONVERSION = DATES['conversion_eod']
TRANSITION = ('2017-09-25','2017-10-06')
INC, LLC = 'GOOGLEINC', 'GOOGLELLC'
GOOGLE = {INC, LLC}
PARTIES = {
    INC: 'google_inc', LLC: 'google_llc', 'ALPHABETINC': 'alphabet',
    'XXVIHOLDINGSINC': 'xxvi', 'GOOGLETECHNOLOGYHOLDINGSLLC': 'gth',
    'WAYMOLLC': 'waymo', 'LLCWAYMO': 'waymo', 'WAYMOHOLDINGINC': 'waymo_holding',
    'WAYMOHOLDINGSINC': 'waymo_holding', 'WAYMOHOLDIINGINC': 'waymo_holding',
    'INCWAYMOHOLDING': 'waymo_holding', 'XDEVELOPMENTLLC': 'x',
    'VERILYLIFESCIENCESLLC': 'verily', 'BOSTONDYNAMICSINC': 'boston_dynamics',
    'BOSTONDYNAMICS': 'boston_dynamics', 'DEEPMINDTECHNOLOGIESLIMITED': 'deepmind',
    'DEEPMINDTECHNOLOGIESLTD': 'deepmind', 'DANDELIONENERGYINC': 'dandelion',
    'DANDELIONENERGY': 'dandelion', 'DANDELIONINC': 'dandelion',
    'PLANETLABSTBINC': 'planet_tb', 'PLANETLABSINC': 'planet',
    'TERRABELLATECHNOLOGIESINC': 'terra', 'SKYBOXIMAGINGINC': 'skybox',
}
MATCHED_ROUTES = {
    'inc-out', 'llc-out', 'inc-llc', 'gth-assignee', 'gth-assignor', 'terra-planet',
    'google-planet', 'llc-x', 'x-google', 'google-waymo-wide', 'google-x', 'planet-in',
}
EXACT_CONTROLS = ('google-wide-alphabet', 'alphabet-google-wide', 'google-xxvi', 'xxvi-google')
CORRECTED_REF = re.compile(r'(?:AT|ON) REEL:?\s*(\d+)\s+FRAME:?\s*(\d+)', re.I)
APP_NUMBER = re.compile(r'\b(\d{2})/(\d{3}),?(\d{3})\b')
CONVERSION_LABELS = {'CHANGE OF NAME', 'ENTITY CONVERSION', 'CONVERSION', 'CERTIFICATE OF CONVERSION',
                     'CHANGE OF ENTITY'}


def ident(match):
    return f'{int(match[1]):06d}/{int(match[2]):04d}'


def parties(event, side):
    names = event[side + 's']
    return names if names and isinstance(names[0], str) else party_names(event, side)


def party_ids(event, side):
    return {key(name) for name in parties(event, side)}


def received(event):
    return iso(event.get('recordationDate') or event.get('recorded'))


def executed(event):
    return iso(event.get('assignorExecutionDate'))


def name_year(event):
    return executed(event).startswith(YEAR) or received(event).startswith(YEAR)


def selected_reels(index, controls):
    return {
        reel_frame(row) for name in MATCHED_ROUTES for row in index[name] if name_year(row)
    } | set(controls)


def scope(event, originals):
    source = party_ids(event, 'assignor')
    target = party_ids(event, 'assignee')
    original = originals.get(reel_frame(event), {})
    if INC in source and source <= GOOGLE and target == {LLC}:
        if original.get('kind') == 'conversion':
            return 'conversion_original'
        if title_kind(event) == 'correction':
            return 'conversion_correction'
        if event['conveyance'].strip().upper() in CONVERSION_LABELS:
            return 'conversion_indexed'
        return 'same_entity_other_label'
    if event['conveyanceCode'] == 40 or title_kind(event) == 'correction':
        return 'correction'
    if original.get('kind') == 'assignment':
        return 'assignment_original'
    if title_kind(event) == 'assignment':
        return 'assignment_indexed'
    return 'other_instrument'


def read_schedule(folder, ref, meta):
    pages = list(reel_data(folder, ref, meta['pages']))
    event = pages[0]['data']['assignment']
    properties = [p for page in pages for p in page['data']['properties']]
    assert reel_frame(event) == ref
    assert len(properties) == meta['properties'] == len({p['propertySequenceNumber'] for p in properties})
    assert all(page['totalRows'] == len(properties) for page in pages)
    assert all(reel_frame(page['data']['assignment']) == ref for page in pages)
    return event, sorted(properties, key=lambda p: p['propertySequenceNumber'])


def read_application(folder, number):
    request, result = official(folder/'registry'/f'application-{number}.json')
    assert request['searchBy']=='applicationNumber' and request['property']==number
    events, detail = result['data']['assignment'], result['data']['properties'] or {}
    assert len(events)==result['totalRows'] and not result['backendPagination']
    assert not detail or detail['applicationNumber']==number
    return events,detail


def make_events(folder, index, captured, originals, selected):
    by_reel, routes = {}, defaultdict(list)
    for route, rows in sorted(index.items()):
        for row in rows:
            ref = reel_frame(row)
            if ref in selected:
                by_reel[ref] = row
                routes[ref].append(route)
    for ref in sorted(selected):
        schedule = captured.get(ref)
        event, properties = read_schedule(folder, ref, schedule) if schedule else (by_reel.get(ref), [])
        if event is None:
            yield {'reel_frame': ref, **dict.fromkeys(EVENT_FIELDS[1:], ''),
                   'schedule_status': 'unavailable'}, []
            continue
        original = originals.get(ref, {})
        parties_in = parties(event, 'assignee')
        label = original.get('recipient') or ' | '.join(parties_in)
        recordation = received(event)
        corrected = CORRECTED_REF.search(event['conveyance']) if title_kind(event)=='correction' else None
        correction_targets = {p for p,_ in original.get('excluded_pairs',[])}
        if corrected:
            correction_targets.add(ident(corrected))
        item = {
            'reel_frame': ref, 'scope': scope(event, originals),
            'registry_execution_date': executed(event), 'registry_recordation_date': recordation,
            'recordation_period': ('recorded_2017' if recordation.startswith(YEAR) else
                                   'recorded_after_2017' if recordation[:4]>YEAR else 'comparison'),
            'instrument_as_of': original.get('as_of',''),
            'from_names': ' | '.join(parties(event, 'assignor')), 'to_names_as_indexed': ' | '.join(parties_in),
            'to_names_as_read': label,
            'code': str(event['conveyanceCode']), 'conveyance': event['conveyance'].strip(),
            'correction_of_reels': ' | '.join(sorted(correction_targets)),
            'routes': ' | '.join(routes[ref]),
            'schedule_status': 'captured' if schedule else 'search_index_only',
            'property_rows': str(len(properties)) if schedule else '',
            'registry_image_status': ('available' if event['imageAvailableStatusCode'] else 'unavailable')
                if 'imageAvailableStatusCode' in event else 'unknown',
            'source': original.get('source',''),
        }
        yield item, properties


EVENT_FIELDS = (
    'reel_frame', 'scope', 'registry_execution_date', 'registry_recordation_date', 'recordation_period',
    'instrument_as_of',
    'from_names', 'to_names_as_indexed', 'to_names_as_read', 'code', 'conveyance',
    'correction_of_reels', 'routes', 'schedule_status', 'property_rows', 'registry_image_status', 'source',
)


def collect_exclusions(packets, originals):
    removed = {}
    for event, _ in packets:
        if event['scope'] != 'conversion_correction' and event['scope'] != 'correction':
            continue
        text = event['conveyance']
        if 'REMOV' in text.upper() or 'DELETE' in text.upper():
            match = CORRECTED_REF.search(text)
            if match:
                for m in APP_NUMBER.finditer(text):
                    removed[ident(match), ''.join(m.groups())] = event['reel_frame']
    for ref, original in originals.items():
        for previous, number in original.get('excluded_pairs', []):
            removed[previous,number] = ref
    return removed


def property_scope(ref, number, document_scope, originals):
    document = originals.get(ref,{})
    company_schedule = document.get('acknowledged_company_serials',[])
    return 'acknowledged_company_asset' if number in company_schedule else document_scope


def make_assets(packets, originals):
    removed = collect_exclusions(packets, originals)
    for event, properties in packets:
        for p in properties:
            number = (p['applicationNumber'] or '').strip()
            filed = iso(p['fillingDate'])
            role = property_scope(event['reel_frame'],number,event['scope'],originals)
            yield {
                'reel_frame': event['reel_frame'], 'property_sequence': str(p['propertySequenceNumber']),
                'application_serial': number, 'patent_number': (p['patentNumber'] or '').strip(),
                'publication_number': (p['publicationNumber'] or '').strip(),
                'pct_number': (p['pctNumber17'] or p['pctNumber'] or '').strip(),
                'filing_date': filed, 'title': (p['inventionTitle'] or '').strip(),
                'filing_period': ('after_conversion_day' if filed>CONVERSION else
                                  'by_conversion_day' if filed else 'date_unavailable'),
                'scope': role,
                'acknowledged_current_owner': (originals[event['reel_frame']]['acknowledged_company_owner']
                                               if role=='acknowledged_company_asset' else ''),
                'registry_execution_date': event['registry_execution_date'],
                'registry_recordation_date': event['registry_recordation_date'],
                'instrument_as_of': event['instrument_as_of'], 'from_names': event['from_names'],
                'to_names_as_read': event['to_names_as_read'],
                'property_excluded_by_correction': removed.get((event['reel_frame'],number),''),
            }


def case_rows(folder, annual, probes):
    references = [(r['_query_id'], r) for r in annual]
    references += [(name,r) for name,rows in probes.items() for r in rows]
    cases = defaultdict(list)
    for name,row in references:
        if row['country_code'] == 'US' and row['publication_date'].startswith(YEAR):
            number = serial(row['application_number'])
            assert number, row['application_number']
            cases[number].append((name,row))
    public = {r['publication_key'] for r in read_csv(folder/'google-2017-publication-list.csv')}
    assert public == {key(r['publication_number']) for r in annual}
    return cases


def transition_rows(annual):
    rows = defaultdict(list)
    for row in annual:
        if row['country_code']=='US' and TRANSITION[0] <= row['filing_date'] <= TRANSITION[1]:
            number = serial(row['application_number'])
            assert number, row['application_number']
            rows[number].append((row['_query_id'],row))
    return rows


def recipient(event, label):
    names = party_ids(event,'assignee')
    if label:
        names = {key(n) for n in label.split(' | ')}
    if len(names) > 1:
        return 'joint_or_mixed'
    if not names:
        return 'unknown_recipient'
    name = next(iter(names))
    if name == 'ALPHABETINC':
        if not any(key(p.get('city') or '') == 'MOUNTAINVIEW' for p in event['assignees']):
            return 'alphabet_name_homonym'
    return PARTIES.get(name,'other')


def dated_instrument(event, originals):
    as_of = originals.get(reel_frame(event),{}).get('as_of','')
    return as_of[:10] if as_of else executed(event)


def snapshot(events, filed, day, recorded_only, originals, excluded, number):
    if filed and filed > day:
        return 'not_yet_filed', ''
    if events is None:
        return 'history_unavailable', ''
    eligible = [
        e for e in events if not e.get('deleteStatusIndicator') and
        '' < dated_instrument(e,originals) <= day and (not recorded_only or '' < received(e) <= day)
    ]
    titles = {}
    forms = {}
    eligible_refs = {reel_frame(e) for e in eligible}
    for e in eligible:
        ref = reel_frame(e)
        group = property_scope(ref,number,scope(e,originals),originals)
        if (ref,number) in excluded and (not recorded_only or excluded[(ref,number)] in eligible_refs):
            continue
        source = party_ids(e,'assignor')
        target = party_ids(e,'assignee')
        if group in {'conversion_original','conversion_indexed'} or (group == 'same_entity_other_label'
                and title_kind(e) in {'assignment','merger','name_or_form'}):
            forms[ref] = e
        elif group in {'assignment_original','assignment_indexed'} or (
            group == 'other_instrument' and title_kind(e) in {'merger','name_or_form'} and source and target
        ):
            titles[ref] = e
    for e in eligible:
        correction = ASSIGNEE_CORRECTION.search(e['conveyance'])
        if correction and ident(correction) in titles and executed(titles[ident(correction)]) == executed(e):
            titles[ident(correction)] = e
    if not titles:
        return ('conversion_schedule_only' if forms else 'no_title_event'), ''
    order = lambda e: (dated_instrument(e,originals),received(e),reel_frame(e))
    chosen = max(titles.values(),key=order)
    same_day = [e for e in titles.values() if order(e)[0] == order(chosen)[0]]
    # A dated contribution can place both legs on one day. Prefer the endpoint
    # only when the intermediate recipient is itself a documented transferor.
    if len(same_day) > 1:
        intermediate = {PARTIES.get(n,n) for e in same_day for n in party_ids(e,'assignor')
                        if party_ids(e,'assignor') != party_ids(e,'assignee')}
        endpoints = [e for e in same_day if not {PARTIES.get(n,n) for n in party_ids(e,'assignee')} <= intermediate]
        if endpoints:
            same_day = endpoints
            chosen = max(endpoints,key=order)
    groups = {recipient(e,originals.get(reel_frame(e),{}).get('recipient')) for e in same_day}
    if len(groups) != 1:
        return 'multiple_same_day_recipients', reel_frame(chosen)
    owner = next(iter(groups))
    if owner == 'google_inc' and day >= CONVERSION:
        if recorded_only:
            later = [e for e in forms.values() if dated_instrument(e,originals) >= dated_instrument(chosen,originals)]
            if later:
                return 'google_llc', reel_frame(max(later,key=order))
        else:
            return 'google_llc', reel_frame(chosen)
    return owner, reel_frame(chosen)


def make_titles(assets, packets, cases, transition, histories, originals, observations):
    by_app = defaultdict(list)
    for row in assets:
        if row['application_serial']:
            by_app[row['application_serial']].append(row)
    excluded = collect_exclusions(packets, originals)
    exclusions_by_app = defaultdict(set)
    for (previous,number),fix in excluded.items():
        exclusions_by_app[number].add((previous,fix))
    for number in sorted(by_app.keys() | cases.keys() | transition.keys() | histories.keys() | observations.keys() |
                         exclusions_by_app.keys()):
        rows = by_app[number]
        in_year = cases.get(number,[])
        in_transition = transition.get(number,[])
        known = in_year + in_transition
        history_rows, detail = histories.get(number,(None,{}))
        direct_filing = iso(detail.get('fillingDate'))
        other_filing = min([p['filing_date'] for p in rows if p['filing_date']] +
                           [p['filing_date'] for _,p in known if p['filing_date']],default='')
        filed = direct_filing or other_filing
        observed = observations.get(number,{})
        cover = observed.get('native_cover',{})
        scopes = defaultdict(set)
        for row in rows:
            label = 'removed' if row['property_excluded_by_correction'] else row['scope']
            scopes[label].add(row['reel_frame'])
        assigned = {p['to_names_as_read'] for p in rows if p['scope'].startswith('assignment') and
                    p['registry_execution_date'].startswith(YEAR) and not p['property_excluded_by_correction']}
        fix_refs = {fix for _,fix in exclusions_by_app[number]}
        patents = {p['patent_number'] for p in rows if p['patent_number']}
        if detail.get('patentNumber'):
            patents.add(detail['patentNumber'])
        item = {
            'application_serial': number, 'filing_date': filed,
            'filing_date_from_individual_registry': direct_filing,
            'publication_ids_in_2017_cohort': ' | '.join(sorted({key(p['publication_number']) for _,p in in_year})),
            'transition_window_publications': ' | '.join(sorted({key(p['publication_number']) for _,p in in_transition})),
            'cohort_query_ids': ' | '.join(sorted({name for name,_ in known})),
            'inventory_patents': ' | '.join(sorted(patents)),
            'title': detail.get('inventionTitle') or next((p['title'] for p in rows if p['title']),
                                                          next((p['title'] or '' for _,p in known),'')),
            'conversion_reels': ' | '.join(sorted(scopes['conversion_original'] | scopes['conversion_indexed'])),
            'same_entity_other_label_reels': ' | '.join(sorted(scopes['same_entity_other_label'])),
            'assignment_reels': ' | '.join(sorted(scopes['assignment_indexed'] | scopes['assignment_original'])),
            'scheduled_2017_assignment_receipts': ' | '.join(sorted(assigned)),
            'correction_reels': ' | '.join(sorted(scopes['correction'] | scopes['conversion_correction'] | fix_refs)),
            'excluded_claim_reels': ' | '.join(sorted({old for old,_ in exclusions_by_app[number]})),
            'company_owned_disclosure_reels': ' | '.join(sorted(scopes['acknowledged_company_asset'])),
            'history_event_count': '' if history_rows is None else str(len(history_rows)),
            'snapshot_basis': 'assignment_center_application' if history_rows is not None else 'no_case_history',
            'publication_trace_url': observed.get('url',''),
            'publication_legal_reels': ' | '.join(sorted({r['ref'] for r in observed.get('legal_events',[])})),
            'native_publication_2017': cover.get('publication',''),
            'native_first_page_roles': ' | '.join(sorted({f"{r['role']}={r['party']}" for r in cover.get('roles',[])})),
            'native_publication_pdf': cover.get('source',''),
        }
        for label,day in DATES.items():
            owner, ref = snapshot(history_rows,filed,day,False,originals,excluded,number)
            raw_owner, raw_ref = snapshot(history_rows,filed,day,True,originals,excluded,number)
            item.update({label+'_evidence':owner,label+'_reel':ref,
                         label+'_as_recorded':raw_owner,label+'_as_recorded_reel':raw_ref})
        yield item


def counts(events, assets, titles, cases, transition):
    conversions = [r for r in events if (r['scope'].startswith('conversion_') or
                   r['scope'] == 'same_entity_other_label') and
                   (r['registry_execution_date'].startswith(YEAR) or r['registry_recordation_date'].startswith(YEAR))]
    disputed_labels = [r for r in conversions if r['code'] in {'20','23'}]
    by_scope = defaultdict(list)
    conversion_filings = defaultdict(set)
    for row in assets:
        by_scope[row['scope']].append(row)
        if row['application_serial'] and not row['property_excluded_by_correction'] and (
            row['scope'].startswith('conversion_') or row['scope']=='same_entity_other_label'
        ):
            dates = conversion_filings[row['application_serial']]
            if row['filing_date']:
                dates.add(row['filing_date'])
    conversion_filing_buckets = Counter()
    for dates in conversion_filings.values():
        if not dates:
            conversion_filing_buckets['missing'] += 1
        elif max(dates) <= CONVERSION:
            conversion_filing_buckets['filed_by_conversion_day'] += 1
        elif min(dates) > CONVERSION:
            conversion_filing_buckets['filed_after_conversion_day'] += 1
        else:
            conversion_filing_buckets['dates_disagree_across_cutoff'] += 1
    assignments = defaultdict(list)
    for row in assets:
        if row['scope'].startswith('assignment') and row['registry_execution_date'].startswith(YEAR):
            assignments[(row['from_names'],row['to_names_as_read'])].append(row)
    route_counts = [
        {'from': source,'to': target,'reels': len({r['reel_frame'] for r in rows}),
         'application_serials': len({r['application_serial'] for r in rows if r['application_serial'] and
                                      not r['property_excluded_by_correction']}),
         'property_rows': len(rows), 'execution_dates': sorted({r['registry_execution_date'] for r in rows})}
        for (source,target),rows in sorted(assignments.items())
    ]
    cohort = [r for r in titles if r['application_serial'] in cases]
    near = [r for r in titles if r['application_serial'] in transition]
    return {
        'reels': len(events), 'reels_with_complete_schedules': sum(r['schedule_status']=='captured' for r in events),
        'asset_rows': len(assets), 'application_rows':len(titles), 'application_cohort':len(cohort),
        'individual_histories':sum(r['history_event_count']!='' for r in titles),
        'cohort_histories':sum(r['history_event_count']!='' for r in cohort),
        'cohort_snapshot_basis':dict(Counter(r['snapshot_basis'] for r in cohort)),
        'transition_window_cases':len(near),
        'transition_window_histories':sum(r['history_event_count']!='' for r in near),
        'transition_window_evidence':{d:dict(Counter(r[d+'_evidence'] for r in near)) for d in DATES},
        'publication_trace_rows':sum(bool(r['publication_trace_url']) for r in titles),
        'native_cohort_covers':sum(bool(r['native_publication_2017']) for r in cohort),
        'native_cohort_covers_with_named_parties':sum(bool(r['native_first_page_roles']) for r in cohort),
        'removed_property_rows':sum(bool(r['property_excluded_by_correction']) for r in assets),
        'conversion_search_reels':len(conversions),
        'conversion_reels_by_execution_date':dict(Counter(r['registry_execution_date'] for r in conversions)),
        'conversion_reels_by_recordation_year':dict(Counter(r['registry_recordation_date'][:4] for r in conversions)),
        'conversion_schedules_by_recordation_year':dict(Counter(r['registry_recordation_date'][:4] for r in conversions
                                      if r['schedule_status']=='captured')),
        'conversion_raw_labels':dict(Counter(r['conveyance'] for r in conversions)),
        'same_entity_assignment_or_merger_code': {
            'reels':len(disputed_labels),
            'verified_conversion_originals':sum(r['scope']=='conversion_original' for r in disputed_labels),
            'without_verified_conversion_original':[r['reel_frame'] for r in disputed_labels
                                                    if r['scope']!='conversion_original'],
        },
        'asset_scope':{k:{'rows':len(v),'reels':len({r['reel_frame'] for r in v}),
                         'apps':len({r['application_serial'] for r in v if r['application_serial'] and
                                     not r['property_excluded_by_correction']})} for k,v in by_scope.items()},
        'conversion_distinct_us_apps':len(conversion_filings),
        'conversion_dated_inventory':dict(conversion_filing_buckets),
        '2017_assignment_routes':route_counts,
        'cohort_evidence':{d:dict(Counter(r[d+'_evidence'] for r in cohort)) for d in DATES},
        'cohort_as_recorded':{d:dict(Counter(r[d+'_as_recorded'] for r in cohort)) for d in DATES},
    }


def corpus(folder, window, combined, probes):
    paths = [str(folder/'*.batch.json'),*(str(folder.parent/f'round{r}'/'*.batch.json') for r in range(22,30)),
             str(folder.parent/'*.batch.json')]
    annual, pages = load(paths[:1])
    assert audit_longitudinal_coverage(annual,pages,as_of_dates=window['publication_date_snapshots']) == {
        k:v for k,v in window.items() if k not in ('tool','tool_version')}
    all_rows, all_pages = load(paths)
    report = audit_longitudinal_coverage(all_rows,all_pages,as_of_dates=combined['publication_date_snapshots'])
    for field in ('union','sorted_publication_ids_sha256','publication_date_snapshots'):
        assert report[field] == combined[field]
    assert len(all_pages) == combined['pages']
    new = {p['query_id'] for p in pages}
    for field,label,normalize in [('publication_number','publications',key),('application_number','application_numbers',key),
                                  ('family_id','provider_family_ids',family)]:
        prev = {normalize(r[field]) for r in all_rows if r['_query_id'] not in new}
        assert len(prev & {normalize(r[field]) for r in annual}) == combined['cross_window_overlap'][label]
    separate = {}
    annual_ids = {key(p['publication_number']) for p in annual}
    for name,meta in probes.items():
        rows, probe_pages = load([str(folder/f'target-{name}.json')])
        assert (len(rows),len(probe_pages)) == (meta['rows'],meta['pages'])
        assert len(annual_ids & {key(p['publication_number']) for p in rows}) == meta['mother_publication_overlap']
        separate[name] = rows
    return case_rows(folder,annual,separate), transition_rows(annual)


def source_index(folder):
    index = {}
    routes = read_json(folder/'registry'/'route-index.json')
    for name, rows in sorted(routes.items()):
        paths = sorted((folder/'registry').glob(f'route-{name}-page*.json'),
                       key=lambda p:int(p.stem.split('-page')[-1]))
        gathered = []
        criteria = None
        for path in paths:
            request,response = official(path)
            assert response['totalRows'] == len(rows)
            assert criteria is None or request['searchCriteria'] == criteria
            criteria = request['searchCriteria']
            gathered.extend(response['data'] or [])
        assert gathered == rows
        index[name] = {'criteria':criteria,'total_reels':len(rows),'pages':len(paths)}
    return routes,index


def read_observations(folder, mirror_serials, covers):
    observations = {n:read_json(folder/'publication-register'/f'{n}.json') for n in mirror_serials}
    for n in covers:
        item = read_json(folder/'native-cohort-covers'/f'{n}.json')
        assert item['serial']==n and item['date'].startswith(YEAR)
        observations.setdefault(n,{})['native_cover'] = item
    return observations


def result(folder, rights, window, combined):
    cases,transition = corpus(folder,window,combined,rights['provider_probes'])
    assert sorted(cases) == rights['case_serials']
    assert sorted(transition) == rights['transition_serials']
    routes, queries = source_index(folder)
    assert queries == rights['registry_queries']
    wanted = selected_reels(routes,rights['control_reels'])
    assert wanted == set(rights['captured_reels']) | set(rights['unavailable_reels'])
    originals = rights['original_reels']
    packets = list(make_events(folder,routes,rights['captured_reels'],originals,wanted))
    events = [event for event,_ in packets]
    assets = list(make_assets(packets,originals))
    histories = {number:read_application(folder,number) for number in rights['individual_histories']}
    observations = read_observations(folder,rights['published_traces'],rights['native_cohort_covers'])
    titles = list(make_titles(assets,packets,cases,transition,histories,originals,observations))
    for item in rights['archived_sources'].values():
        assert pdf_or_archive_hash(folder/item['file']) == item['sha256']
    for item in rights['epo_as_published']:
        doc = ElementTree.parse(folder/item['file']).getroot()
        assert doc.attrib['doc-number'] + doc.attrib['kind'] == item['publication'][2:]
        assert doc.attrib['date-publ'] == item['publication_date'].replace('-','')
        role = 'B710/B711' if item['role']=='applicant' else 'B730/B731'
        assert [n.text for n in doc.findall(f'.//{role}/snm')] == [item['party']]
    return events,assets,titles


def validate_public(rights, events, assets, titles, window, combined):
    assert [r['page_count'] for r in window['query_audits']] == [37,118]
    assert [r['provider_total'] for r in window['query_audits']] == [1801,5890]
    fields = ('publications','application_numbers','provider_family_ids')
    assert [window['union'][k] for k in fields] == [7689,5050,2775]
    assert [combined['union'][k] for k in fields] == [57845,40849,17724]
    assert (combined['pages'],combined['query_windows']) == (1198,29)
    assert combined['cross_window_overlap'] == {
        'publications':0,'application_numbers':1,'provider_family_ids':1463}
    assert rights['corporate']['delaware_filed_at'] == '2017-09-29T12:42:00-04:00'
    assert rights['corporate']['llc_effective_at'] == '2017-09-30T23:59:00-04:00'
    assert rights['corporate']['xxvi_equity_effective_on'] == CONVERSION
    assert all(rights['registry_queries'][r]['total_reels'] == 0 for r in EXACT_CONTROLS)
    assert len(events) == len({r['reel_frame'] for r in events})
    assert len(assets) == len({(r['reel_frame'],r['property_sequence']) for r in assets})
    assert len(titles) == len({r['application_serial'] for r in titles})
    assert len(events) == len(rights['captured_reels']) == 4823
    assert not rights['unavailable_reels']
    assert {r['reel_frame'] for r in events if r['schedule_status']=='captured'} == set(rights['captured_reels'])
    assert sum(int(r['property_rows'] or 0) for r in events) == len(assets)
    assert rights['epo_as_published'][0]['party'] == 'Google Inc.'
    assert rights['epo_as_published'][1]['party'] == 'Google LLC'
    by_reel = {r['reel_frame']:r for r in events}
    for ref in ('044510/0344','045093/0546','046606/0160'):
        assert by_reel[ref]['scope'] == 'conversion_original'
    assert by_reel['074779/0148']['registry_image_status'] == 'unavailable'
    by_app = {r['application_serial']:r for r in titles}
    assert by_app['15347389']['year_end_evidence'] == 'waymo'
    assert by_app['15347389']['before_evidence'] == 'waymo'
    assert by_app['15347389']['excluded_claim_reels'] == '044144/0001'
    assert by_app['15016851']['scheduled_2017_assignment_receipts'] == 'PLANET LABS, INC.'
    assert by_app['15016851']['before_evidence'] == 'terra'
    assert by_app['15016851']['year_end_evidence'] == 'planet'
    assert by_app['15061851']['excluded_claim_reels'] == '043277/0669'
    terra = rights['terra_bella_schedules']
    assert (len(terra['schedule_a_us_serials']),len(terra['schedule_a_pct']),
            len(terra['schedule_b_us_serials_as_corrected'])) == (8,6,34)
    initial_transfer = {r['application_serial'] for r in assets if r['reel_frame']=='043277/0669'
                        and r['scope']=='assignment_original' and not r['property_excluded_by_correction']}
    assert initial_transfer == set(terra['schedule_a_us_serials'])
    terra_disclosures = {r['application_serial'] for r in assets if r['reel_frame']=='043661/0060'
                         and r['scope']=='acknowledged_company_asset'}
    assert terra_disclosures == set(terra['schedule_b_us_serials_as_corrected'])
    assert by_app['15006290']['year_end_evidence'] == 'x'
    assert by_app['10652131']['year_end_evidence'] == 'gth'
    assert by_app['14669424']['year_end_evidence'] == 'verily'
    assert by_app['15499486']['year_end_evidence'] == 'verily'
    assert counts(events,assets,titles,set(rights['case_serials']),set(rights['transition_serials'])) == rights['registry_totals']
    assert rights['registry_totals']['conversion_search_reels'] == 3991
    assert rights['registry_totals']['same_entity_assignment_or_merger_code'] == {
        'reels':98,'verified_conversion_originals':97,'without_verified_conversion_original':['074779/0148']}
    assert rights['registry_totals']['cohort_histories'] == rights['registry_totals']['application_cohort'] == 770
    assert rights['registry_totals']['transition_window_cases'] == rights['registry_totals']['transition_window_histories'] == 134


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path)
    args = parser.parse_args()
    window = read_json(DERIVED/('google-2017-name-coverage'+STAMP))
    combined = read_json(DERIVED/('google-1996-2017-combined-audit'+STAMP))
    rights = read_json(DERIVED/(PREFIX+'rights'+STAMP))
    files = [DERIVED/(PREFIX+n+'.csv') for n in ('us-reel-events','us-asset-register','us-title-evidence')]
    events,assets,titles = [read_csv(p) for p in files]
    validate_public(rights,events,assets,titles,window,combined)
    if args.source_dir:
        assert result(args.source_dir,rights,window,combined) == (events,assets,titles)
    print('Google 2017 / XXVI:',window['union']['publications'],'publications,',combined['pages'],
          'longitudinal pages,',len(events),'USPTO reel results,',len(assets),'schedule properties,',
          len(titles),'application rows', '(private replay)' if args.source_dir else '(public ledgers)')


if __name__ == '__main__':
    main()
