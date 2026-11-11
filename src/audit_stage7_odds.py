"""Stage 7 offline record-by-record audit. No network or modeling imports.

Uses already collected pages, recorded fetch headers and original supplier rows.
Outputs use exclusive creation. Never edits permissions/quarantine/source records.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from src.audit_grok_games_stats import canonical_team
from src.verify_wayback_spotcheck import american_from_decimal, capture_time
from src.verify_odds_expansion import dk_state

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE_CACHE=ROOT/'research/odds_evidence'
PACKAGE=Path('data/incoming/grok/stage1_28f5677d90c3/audit_package')
SUPPLEMENT=Path('data/incoming/grok/ncaa_lacrosse_cse519_supplement_2026-11-10.zip')
CLASSES=['VERIFIED_PRE_GAME','VERIFIED_PRICE_TIMING_UNKNOWN','PARTIALLY_SUPPORTED','UNSUPPORTED','REJECTED']


def rows(path):
    with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))


def missing(value):return value is None or str(value).strip().lower() in ('','null','nan','none')
def key(name):return {'stjoes':'stjosephs','stjoe':'stjosephs'}.get(canonical_team(name),canonical_team(name))
def number(value):
    if missing(value):return None
    try:
        out=float(str(value).replace('−','-'))
        return out if abs(out)!=float('inf') and out==out else None
    except ValueError:return None
def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(data):return hashlib.sha256(data).hexdigest()


def source_key(url):
    p=urlsplit('' if missing(url) else url)
    # Known publisher path duplication is recorded, never silently rewritten in input.
    path=p.path.replace('/lacrosse-lacrosse/','/lacrosse/').rstrip('/')
    return (p.netloc.lower().removeprefix('www.'),path,p.query)


def archive_stamp(row):
    match=re.search(r'/web/(\d{14})',row.get('archive_url',''))
    if match:return match[1]
    for field in ('archive_capture_timestamp','quote_capture_timestamp'):
        value=row.get(field,'')
        if not missing(value):
            try:return datetime.fromisoformat(value.replace('Z','+00:00')).strftime('%Y%m%d%H%M%S')
            except ValueError:pass
    return ''


def originals():
    audit=rows(PACKAGE/'odds_provenance_audit.csv')
    old=rows('reports/grok_stage3_record_checks.csv'); prior={r['record_id']:r for r in old}
    if len(audit)!=1995 or len(prior)!=1995:raise ValueError('Original record count/ID mismatch')
    for row in audit:
        if any(prior[row['record_id']][k]!=v for k,v in row.items()):raise ValueError('Prior ledger source field changed')
    raw=rows(PACKAGE/'originals/ncaa_lacrosse_historical_odds_2025.csv')
    rawmap={f"O{int(r['record_id']):04}":r for r in raw}
    with zipfile.ZipFile(ROOT/SUPPLEMENT) as z:
        prefix='supplement_2026-11-10/'
        extra=list(csv.DictReader(io.StringIO(z.read(prefix+'priority1_originals/recovered_originals/ncaa_lacrosse_additional_odds_2023_2026.csv').decode())))
        maps=list(csv.DictReader(io.StringIO(z.read(prefix+'priority2_odds_evidence/odds_evidence_to_record_map.csv').decode())))
    for i,r in enumerate(extra,1):rawmap[f'N{i:04}']=r
    for rid,r in rawmap.items():
        fields={'season':'season','sportsbook':'sportsbook','market':'market','selection':'side' if rid.startswith('O') else 'selection',
                'american_odds':'price_american' if rid.startswith('O') else 'american_odds','line':'line','source_url':'source_url'}
        for a,b in fields.items():
            if prior[rid][a]!=r[b] and not (missing(prior[rid][a]) and missing(r[b])):
                raise ValueError(f'Original tuple mapping mismatch {rid} {a}')
    mapped={r['record_id']:r for r in maps if r['record_id'].startswith('O')}
    # Retain N IDs in the actual map; support an A alias only after tuple checks.
    for r in maps:
        if r['record_id'].startswith(('A','N')):
            rid='N'+r['record_id'][1:]
            if rid not in prior:raise ValueError('Supplement ID not mappable')
            for field in ('sportsbook','market','selection','line','american_odds','source_url'):
                if r[field]!=prior[rid][field] and not (missing(r[field]) and missing(prior[rid][field])):
                    raise ValueError('Supplement record tuple mismatch')
            mapped[rid]=r
    if len(rawmap)!=1995 or len(mapped)!=1995:raise ValueError('Incomplete source accounting')
    return audit,prior,rawmap,mapped


def cached_pages():
    logs= json.loads((ROOT/'reports/grok_expansion_fetch_checks.json').read_text())
    prior=json.loads((EVIDENCE_CACHE/'dsf_wayback_verified/fetch.json').read_text())
    candidates=[(EVIDENCE_CACHE/'dsf_expansion_pages'/r['page_file'],r) for r in logs]
    candidates += [(EVIDENCE_CACHE/'dsf_wayback_verified'/(r['page_key']+'.html'),r) for r in prior]
    output={}
    for path,r in candidates:
        cap=capture_time(r['url'],r['memento_datetime'])
        url=r['url'].replace('id_/','/');ident=(url,r['sha256'])
        if ident in output:continue
        data=path.read_bytes()
        if r['status']!=200 or len(data)!=r['bytes'] or sha(data)!=r['sha256']:
            raise ValueError('Existing cached evidence failed integrity check')
        original=url.split('/web/',1)[1].split('/',1)[1]
        output[ident]={'page_id':'P'+str(len(output)+1).zfill(2),'local_path':str(path),
            'archive_url':url,'source_url':original,'source_key':source_key(original),
            'capture_utc':cap.isoformat(),'stamp':cap.strftime('%Y%m%d%H%M%S'),
            'memento_datetime':r['memento_datetime'],'sha256':r['sha256'],'html':data.decode('utf-8'),
            'supplier_hash_matches':r.get('supplier_hash_matches',r.get('supplier_hash_match'))}
    return list(output.values())


def source_observations(audit,pages):
    games=rows('data/review/lacrosse_games_2023_2025_corrected.csv')
    gameindex={(r['game_date'],tuple(sorted([r['home_team_key'],r['away_team_key']]))):r for r in games}
    knownteams={r[s+'_team_key'] for r in games for s in ('home','away')}
    starts={r['ncaa_game_id']:r for path in ['reports/grok_wayback_official_starts.csv','reports/grok_expansion_official_starts.csv'] for r in rows(path)}
    quotes=[];errors=[]
    def add(page,book,market,day,participants,selections,*,kind,event='',source_start=''):
        pair=tuple(sorted(key(t) for t in participants))
        game=gameindex.get((day,pair));gid=game['game_id'] if game else ''
        cap=datetime.fromisoformat(page['capture_utc']);official=starts.get(gid)
        if official:
            start=datetime.fromisoformat(official['scheduled_start_utc'].replace('Z','+00:00'))
            timing='BEFORE_OFFICIAL_SCHEDULED_START' if cap<start else 'AFTER_OFFICIAL_SCHEDULED_START'
        elif day:
            local=cap.astimezone(ZoneInfo('America/New_York')).date().isoformat()
            timing='BEFORE_CORRECTED_GAME_DATE' if local<day else 'AFTER_GAME_DATE' if local>day else 'SAME_DAY_START_UNRESOLVED'
        else:timing='GAME_DATE_UNRESOLVED'
        for sel in selections:
            quotes.append(dict(observation_id=f"V{len(quotes)+1:05}",page_id=page['page_id'],
                source_url=page['source_url'],archive_url=page['archive_url'],capture_utc=page['capture_utc'],
                stamp=page['stamp'],sha256=page['sha256'],local_path=page['local_path'],
                sportsbook=book,market=market,game_date=day,participants=list(pair),matched_game_id=gid,
                source_event_id=str(event),source_start=source_start,official_start=official,
                timing=timing,evidence_type=kind,selection_key=sel['selection_key'],
                line=sel.get('line'),american_price=sel.get('price'),display=sel.get('display'),
                decimal_price=sel.get('decimal'),actual_bookmaker_quote_timestamp=None))
    for page in pages:
        html=page['html'];host=urlsplit(page['source_url']).netloc
        if 'draftkings' in host:
            data=dk_state(html);group=data['eventGroups']['204466']
            if group['name']!='College Lacrosse':raise ValueError('Wrong competition')
            for ev in group['events'].values():
                day=datetime.fromisoformat(ev['startDate'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat()
                participants=[ev['teamName1'],ev['teamName2']]
                for offer in data['offers']['204466'].values():
                    if str(offer.get('eventId'))!=str(ev['eventId']):continue
                    market=offer.get('label','').lower()
                    if market not in ('moneyline','spread','total'):
                        errors.append({'page':page['page_id'],'event':str(ev['eventId']),'reason':'NONSTANDARD_OR_MISSING_MARKET_LABEL'})
                        continue
                    sels=[]
                    for o in offer.get('outcomes',[]):
                        label=o['label'].lower() if market=='total' else key(o['label'])
                        price=number(o.get('oddsAmerican'))
                        if price is None or abs(price)<100:continue
                        sels.append(dict(selection_key=label,line=number(o.get('line')),price=int(price),display=o.get('oddsAmerican')))
                    if sels:add(page,'DraftKings',market,day,participants,sels,kind='DIRECT_SPORTSBOOK_DISPLAY',event=ev['eventId'],source_start=ev['startDate'])
        elif 'betmgm' in host:
            soup=BeautifulSoup(html,'html.parser');eventtimes={}
            for script in soup.select('script#ldJson_SportsEvent'):
                for item in json.loads(script.get_text()).get('@graph',[]):
                    if item.get('@type')=='SportsEvent':eventtimes[item.get('url','')]=item.get('startDate','')
            for ev in soup.select('ms-six-pack-event'):
                participants=[e.get_text(' ',strip=True) for e in ev.select('.participant')]
                link=ev.select_one('a.grid-info-wrapper')
                if len(participants)!=2 or link is None:continue
                if ev.select_one('.away-indicator') is None or ev.select_one('.away-indicator').get_text(strip=True)!='@':continue
                header=[x.get_text(strip=True) for x in ev.find_parent('ms-event-group').select('.grid-group-header')]
                if header!=['Spread','Total','Money']:continue
                source_start=next((v for k,v in eventtimes.items() if k.endswith(link['href'])),'')
                if not source_start:continue
                day=datetime.fromisoformat(source_start.replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat()
                for market,og in zip(['spread','total','moneyline'],ev.select('ms-option-group')):
                    options=og.select('ms-option')
                    if len(options)!=2:continue
                    sels=[]
                    for i,opt in enumerate(options):
                        val=opt.select_one('.option-value');attr=opt.select_one('.option-attribute')
                        if val is None:continue
                        display=val.get_text(strip=True)
                        try:_,price=american_from_decimal(display)
                        except ValueError:continue
                        line=None;selection=key(participants[i])
                        if market!='moneyline':
                            if attr is None:continue
                            text=attr.get_text(' ',strip=True)
                            if market=='total':
                                if not text or text[0].upper() not in ('O','U'):continue
                                selection='over' if text[0].upper()=='O' else 'under';text=text[1:].strip()
                            line=number(text)
                            if line is None:continue
                        sels.append(dict(selection_key=selection,line=line,price=price,display=display,decimal=display))
                    if sels:add(page,'BetMGM',market,day,participants,sels,kind='DIRECT_SPORTSBOOK_DISPLAY',event=link['href'],source_start=source_start)
        elif any(h in host for h in ('actionnetwork','betonlacrosse')):
            soup=BeautifulSoup(html,'html.parser')
            for table in soup.find_all('table'):
                entries={};total=None
                for tr in table.find_all('tr'):
                    cells=tr.find_all(['td','th'])
                    if len(cells)<2:continue
                    label=cells[0].get_text(' ',strip=True);value=cells[1].get_text(' ',strip=True)
                    name=re.sub(r'\s+(Odds|Moneyline/Spread)$','',label)
                    if key(name) in knownteams:entries[name]=value
                    elif label=='Total':total=value
                if len(entries)!=2:continue
                context=table.get_text(' ',strip=True)
                sibling=table.find_next_sibling()
                if sibling:context+=' '+sibling.get_text(' ',strip=True)
                nxt=table.find_next('p')
                if nxt:context+=' '+nxt.get_text(' ',strip=True)
                match=re.search(r'Odds via\s+(DraftKings|BetMGM|Caesars|FanDuel|bet365)',context,re.I)
                if not match:errors.append({'page':page['page_id'],'reason':'BOOK_ATTRIBUTION_NOT_FOUND'});continue
                book={'draftkings':'DraftKings','betmgm':'BetMGM','caesars':'Caesars','fanduel':'FanDuel','bet365':'bet365'}[match[1].lower()]
                pair=tuple(sorted(key(n) for n in entries))
                candidates=[r for r in audit if source_key(r['source_url'])==page['source_key'] and
                    tuple(sorted([key(r['original_home_team']),key(r['original_away_team'])]))==pair]
                dates={r['original_game_date'] for r in candidates if not missing(r['original_game_date'])}
                if len(dates)!=1:errors.append({'page':page['page_id'],'reason':'ARTICLE_GAME_DATE_NOT_UNAMBIGUOUS_FROM_EXISTING_REFERENCE','pair':pair});continue
                day=dates.pop();ml=[];spreads=[]
                for name,value in entries.items():
                    # A slash inside N/A is not a moneyline/spread separator.
                    parts=re.split(r'\s+/\s+',value.replace('−','-'))
                    if not ('N/A' in parts[0]):
                        price=number(parts[0].strip())
                        if price is not None and abs(price)>=100:ml.append(dict(selection_key=key(name),price=int(price),display=parts[0].strip()))
                    if len(parts)>1:
                        m=re.fullmatch(r'\s*([+-]?\d+(?:\.\d+)?)(?:\s*\(([+-]?\d+)\))?\s*',parts[1])
                        if m:spreads.append(dict(selection_key=key(name),line=float(m[1]),price=int(m[2]) if m[2] else None,display=parts[1].strip()))
                    elif 'ML N/A' in value:
                        m=re.match(r'([+-]?\d+(?:\.\d+)?)',value)
                        if m:spreads.append(dict(selection_key=key(name),line=float(m[1]),display=value))
                heading=table.find_previous(['h2','h3'])
                if heading:
                    m=re.match(r'(.+?)\s*\(([+-]?\d+(?:\.\d+)?)\)\s*(?:vs\.?|at)',heading.get_text(' ',strip=True))
                    if m and key(m[1]) in pair and not any(s['selection_key']==key(m[1]) for s in spreads):
                        spreads.append(dict(selection_key=key(m[1]),line=float(m[2]),display=heading.get_text(' ',strip=True)))
                if ml:add(page,book,'moneyline',day,list(entries),ml,kind='EDITORIAL_QUOTATION')
                if spreads:add(page,book,'spread',day,list(entries),spreads,kind='EDITORIAL_QUOTATION')
                if total:
                    m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)(?:\s*\(([+-]?\d+)\))?\s*',total)
                    if m:add(page,book,'total',day,list(entries),[dict(selection_key='UNSPECIFIED_TOTAL',line=float(m[1]),price=int(m[2]) if m[2] else None,display=total)],kind='EDITORIAL_QUOTATION')
    return quotes,errors


def match_record(row,observations):
    pair=sorted([key(row['original_home_team']),key(row['original_away_team'])])
    selected=row['selection'].lower() if row['market']=='total' else key(row['selection'])
    related=[o for o in observations if o['game_date']==row['original_game_date'] and o['participants']==pair and o['market']==row['market']
             and o['selection_key'] in (selected,'UNSPECIFIED_TOTAL')]
    context=[o for o in related if source_key(o['source_url'])==source_key(row['source_url']) and
             (not archive_stamp(row) or archive_stamp(row)==o['stamp'])]
    book=[o for o in related if o['sportsbook']==row['sportsbook']]
    def line_agrees(o):return row['market']=='moneyline' or number(row['line'])==o['line']
    def exact(o):return (o['selection_key']==selected and line_agrees(o) and number(row['american_odds']) is not None
                         and number(row['american_odds'])==o['american_price'])
    price=[o for o in book if exact(o)]
    own=[o for o in price if o in context]
    pre=lambda o:o['timing'].startswith('BEFORE_') and bool(o['matched_game_id']) and o['matched_game_id']==row['matched_game_id']
    ownpre=[o for o in own if pre(o)]
    altpre=[o for o in price if pre(o) and o not in own]
    contradictions=[o for o in context if o['sportsbook']==row['sportsbook'] and o['selection_key']==selected and
        (not line_agrees(o) or (o['american_price'] is not None and number(row['american_odds']) is not None and o['american_price']!=number(row['american_odds'])))]
    wrongbook=[o for o in context if o['sportsbook']!=row['sportsbook']]
    if row['technical_status']=='rejected':classification='REJECTED'
    elif ownpre:classification='VERIFIED_PRE_GAME'
    elif own and row['matched_game_id'] and all(o['matched_game_id']==row['matched_game_id'] for o in own):classification='VERIFIED_PRICE_TIMING_UNKNOWN'
    elif related or price or context:classification='PARTIALLY_SUPPORTED'
    else:classification='UNSUPPORTED'
    timing='PRE_GAME_VERIFIED' if ownpre else 'ALTERNATIVE_PRE_GAME_PRICE_ONLY' if altpre else (
        '|'.join(sorted({o['timing'] for o in own})) if own else 'NO_INDEPENDENT_TIMING_EVIDENCE')
    return dict(evidence_classification=classification,
        exact_price_supported=bool(own),price_seen_in_other_source_or_capture=bool(price and not own),
        original_source_capture_supported=bool(context),sportsbook_supported_in_claimed_context=any(o['sportsbook']==row['sportsbook'] for o in context),
        game_identity_supported_in_claimed_context=bool(row['matched_game_id']) and any(o['matched_game_id']==row['matched_game_id'] for o in context),
        matched_game_supported=bool(row['matched_game_id']) and any(o['matched_game_id']==row['matched_game_id'] for o in own),
        pregame_timing_status=timing,verified_original_source_observation_ids=';'.join(o['observation_id'] for o in own),
        source_context_timing_status=';'.join(sorted({o['timing'] for o in context})),
        pregame_original_source_observation_ids=';'.join(o['observation_id'] for o in ownpre),
        alternative_pregame_observation_ids=';'.join(o['observation_id'] for o in altpre),
        line_only_or_partial_observation_ids=';'.join(o['observation_id'] for o in context if o not in own),
        contradictory_same_capture_observation_ids=';'.join(o['observation_id'] for o in contradictions),
        different_book_context_observation_ids=';'.join(o['observation_id'] for o in wrongbook),
        independent_bookmaker_quote_timestamp='',timestamp_assessment='ARCHIVE_CAPTURE_ONLY; operator quote time not independently established' if (context or price) else 'CLAIMED_ONLY_OR_UNKNOWN',
        evidence_local_paths=';'.join(sorted({o['local_path'] for o in context+price})),
        independently_observed_archive_urls=';'.join(sorted({o['archive_url'] for o in context+price})),
        verification_reason=('Retained prior rejection; independent validity of each prior reason is separately scoped' if classification=='REJECTED' else
            'Exact original price/selection/line/book, documented source/version and pre-game capture' if ownpre else
            'Exact claimed-source price verified; pre-game availability not established' if classification=='VERIFIED_PRICE_TIMING_UNKNOWN' else
            'Some related source/line/alternative price evidence; original priced/timed record not fully established' if classification=='PARTIALLY_SUPPORTED' else
            'No independently inspectable matching quote in already collected pages; URLs, hashes and supplier excerpts alone are insufficient'))


def build():
    audit,prior,raw,maps=originals();pages=cached_pages();observations,errors=source_observations(list(prior.values()),pages)
    policies={r['source_key']:r for r in rows('reports/grok_stage3_source_permissions.csv')}
    domains={'actionnetwork.com':'actionnetwork','sportsbook.draftkings.com':'draftkings','sports.betmgm.com':'betmgm',
             'sportsbook-nash.draftkings.com':'draftkings',
             'betonlacrosse.com':'betonlacrosse','laxallstars.com':'laxallstars','legalsportsbetting.com':'legalsportsbetting'}
    policy_fields=['source_key','url','tos_url','retrieved_at','classification','access_or_retrieval',
                   'internal_academic_analysis','redistribution','automated_collection','policy_basis','cleared_in_stage3']
    bygame=defaultdict(list)
    for o in observations:bygame[(o['game_date'],tuple(o['participants']),o['market'])].append(o)
    exactgroups=defaultdict(list);valuegroups=defaultdict(list)
    for r in prior.values():
        group=(r['original_game_date'],tuple(sorted([key(r['original_home_team']),key(r['original_away_team'])])),r['sportsbook'],r['market'],key(r['selection']),r['line'],r['american_odds'])
        valuegroups[group].append(r['record_id']);exactgroups[group+(source_key(r['source_url']),archive_stamp(r))].append(r['record_id'])
    result=[]
    for source in audit:
        r=prior[source['record_id']];rid=r['record_id'];original=raw[rid];mapping=maps[rid]
        pair=tuple(sorted([key(r['original_home_team']),key(r['original_away_team'])]))
        linked=bygame[(r['original_game_date'],pair,r['market'])]
        assessment=match_record(r,linked)
        narrative=''
        if rid=='O0097':
            # Targeted existing prose, separate from the table's current DK prices.
            for page in pages:
                if source_key(page['source_url'])==source_key(r['source_url']):
                    for p in BeautifulSoup(page['html'],'html.parser').find_all('p'):
                        text=p.get_text(' ',strip=True)
                        if 'Jacksonville opened at -155 on the moneyline' in text:narrative=text
            if narrative:
                assessment['exact_price_supported']=True
                assessment['verification_reason']='Exact -155 reported opener is in cached pre-game prose; original book is unattributed and actual opening time is unresolved'
        price_as_line=[o for o in observations if r['technical_status']=='rejected' and r['market']=='moneyline'
            and number(r['american_odds']) is not None and abs(number(r['american_odds']))<100
            and o['market']=='spread' and o['game_date']==r['original_game_date'] and o['participants']==list(pair)
            and o['selection_key']==key(r['selection']) and o['line']==number(r['american_odds'])
            and source_key(o['source_url'])==source_key(r['source_url'])]
        if price_as_line:rejection_basis='INDEPENDENT_CAPTURE_PRINTS_SPREAD_NOT_MONEYLINE'
        elif r['technical_status']=='rejected' and assessment['contradictory_same_capture_observation_ids']:
            rejection_basis='INDEPENDENT_CAPTURE_CONTRADICTS_SIGN_OR_VALUE'
        elif r['technical_status']=='rejected':rejection_basis='PRIOR_REJECTION_RETAINED_NOT_ALL_ORIGINAL_SOURCE_REASONS_INDEPENDENTLY_REPRODUCED'
        else:rejection_basis='NOT_REJECTED'
        source_policy=policies.get(domains.get(source_key(r['source_url'])[0],''),{})
        policy_list=[{k:source_policy.get(k,'') for k in policy_fields}]
        if not missing(r['archive_url']) or assessment['independently_observed_archive_urls']:
            policy_list.append({k:policies['internet_archive'].get(k,'') for k in policy_fields})
        group=(r['original_game_date'],pair,r['sportsbook'],r['market'],key(r['selection']),r['line'],r['american_odds'])
        result.append({**source,**{k:r[k] for k in ['matched_game_id','match_status','candidate_game_ids','original_game_date','original_home_team','original_away_team','original_decimal_price','validation_issues','permission_status_independent']},
            'matched_game_corroboration_status':r['stage2_factual_status'],
            'raw_source_record_locator':('originals/ncaa_lacrosse_historical_odds_2025.csv record_id='+str(original['record_id']) if rid.startswith('O') else str(SUPPLEMENT)+'::additional CSV logical row '+str(int(rid[1:])+1)),
            'raw_record_json':encoded(original),'supplier_supplement_record_id':mapping['record_id'],
            'original_publisher_supplier_label':mapping['evidence_publisher'],
            'supplier_evidence_sha256':mapping['evidence_sha256'],'supplier_evidence_excerpt':mapping['evidence_excerpt'],
            'supplier_evidence_in_package':mapping['evidence_in_zip'],
            'original_evidence_exact_bytes_available':any(p['sha256']==mapping['evidence_sha256'] for p in pages),
            'documented_source_use_status_json':encoded(policy_list),
            'source_url_normalization':'KNOWN_ACTION_NETWORK_DUPLICATED_PATH' if '/lacrosse-lacrosse/' in r['source_url'] else 'NONE',
            'book_context_assessment':('UNATTRIBUTED_ORIGINAL_BOOK; do not assign current-table book to narrative opener' if missing(r['sportsbook']) and assessment['different_book_context_observation_ids'] else
                'DIFFERENT_BOOK_IN_OBSERVED_CONTEXT' if assessment['different_book_context_observation_ids'] else
                'NAMED_BOOK_SUPPORTED' if assessment['sportsbook_supported_in_claimed_context'] else 'NOT_INDEPENDENTLY_ESTABLISHED'),
            'opening_narrative_evidence':narrative,
            'opening_narrative_status':'REPORTED_OPENING_PRICE_SEEN; book and actual opening time unresolved' if narrative else 'NO_INDEPENDENT_OPENING_SERIES_ESTABLISHED',
            'rejection_evidence_basis':rejection_basis,'rejected_price_is_spread_observation_ids':';'.join(o['observation_id'] for o in price_as_line),
            'capture_time_reused_in_quote_field':not missing(r['quote_capture_timestamp']) and r['quote_capture_timestamp']==r['archive_capture_timestamp'],
            'same_value_other_record_ids':';'.join(x for x in valuegroups[group] if x!=rid),
            'exact_claim_duplicate_record_ids':';'.join(x for x in exactgroups[group+(source_key(r['source_url']),archive_stamp(r))] if x!=rid),
            **assessment,'permission_assessment':'UNCHANGED_SOURCE_SPECIFIC_RESTRICTIONS_OR_APPLICABILITY_REVIEW; evidence class is not legal clearance',
            'approved_for_modeling':False})
    if len(result)!=1995 or len({r['record_id'] for r in result})!=1995:raise ValueError('Bad record accounting')
    for r,s in zip(result,audit):
        if any(r[k]!=v for k,v in s.items()):raise ValueError('Original field changed')
    return result,observations,[{k:v for k,v in p.items() if k not in ('html','source_key')} for p in pages],errors


def summarize(result, observations):
    """Separate original-record verification from alternative price corroboration."""
    obs={o['observation_id']:o for o in observations}
    games={r['game_id']:r for r in rows('data/review/lacrosse_games_2023_2025_corrected.csv')}
    def ids(r,f):return [i for i in r[f].split(';') if i]
    strict={i for r in result if r['evidence_classification']=='VERIFIED_PRE_GAME' for i in ids(r,'pregame_original_source_observation_ids')}
    broader={i for r in result if r['evidence_classification']!='REJECTED' for f in
             ['pregame_original_source_observation_ids','alternative_pregame_observation_ids'] for i in ids(r,f)}
    extras=json.loads((ROOT/'reports/grok_expansion_independent_checks.json').read_text())['omitted_moneyline_evidence']
    for e in extras:
        for side,v in e['observed'].items():
            found=[o for o in observations if o['matched_game_id']==e['ncaa_game_id'] and o['sportsbook']=='DraftKings'
                and o['market']=='moneyline' and o['capture_utc']==e['capture_utc']
                and o['selection_key']==key(e[side]) and o['american_price']==v['price']]
            if len(found)!=1:raise ValueError('Prior audit-only DK price not reproduced')
            broader.add(found[0]['observation_id'])
    def coverage(selected):
        os=[obs[i] for i in sorted(selected)];groups=defaultdict(list)
        for o in os:
            groups[(o['matched_game_id'],o['sportsbook'],o['market'],o['page_id'],
                    None if o['market']=='moneyline' else abs(o['line']))].append(o)
        complete=[]
        for group,vs in groups.items():
            expected={'over','under'} if group[2]=='total' else {games[group[0]][s+'_team_key'] for s in ['home','away']}
            if {v['selection_key'] for v in vs}!=expected:continue
            if group[2]=='spread' and abs(sum(v['line'] for v in vs))>1e-9:continue
            complete.append(dict(game_id=group[0],book=group[1],market=group[2],page_id=group[3],line=group[4],observation_ids=[v['observation_id'] for v in vs]))
        books=defaultdict(set);changes=defaultdict(set)
        for g in complete:
            if g['market']=='moneyline':books[g['game_id']].add(g['book'])
        for o in os:changes[(o['matched_game_id'],o['sportsbook'],o['market'],o['selection_key'],o['line'])].add(o['american_price'])
        return dict(selection_observations=len(os),games=len({o['matched_game_id'] for o in os}),
            paired_markets=len(complete),paired_market_counts=dict(Counter(g['market'] for g in complete)),
            complete_any_market_games=len({g['game_id'] for g in complete}),
            ml_games=len({g['game_id'] for g in complete if g['market']=='moneyline'}),
            spread_games=len({g['game_id'] for g in complete if g['market']=='spread'}),
            total_games=len({g['game_id'] for g in complete if g['market']=='total'}),
            game_book_capture_snapshots=len({(o['matched_game_id'],o['sportsbook'],o['capture_utc'],o['page_id']) for o in os}),
            pages=len({o['page_id'] for o in os}),multi_book_ml_games={g:sorted(v) for g,v in books.items() if len(v)>1},
            pregame_price_change_selection_series=sum(len(v)>1 for v in changes.values()),
            games_by_season=dict(Counter(games[g]['season'] for g in {o['matched_game_id'] for o in os})),
            ml_games_by_season=dict(Counter(games[g]['season'] for g in {g['game_id'] for g in complete if g['market']=='moneyline'})),
            paired_market_inventory=complete,selected_observation_ids=sorted(selected))
    summary=dict(record_counts=dict(Counter(r['evidence_classification'] for r in result)),
        strict_original_source=coverage(strict),price_corroboration_including_prior_audit_only_DK=coverage(broader),
        summary_by_dimension={},contradictory_same_capture_records=[r['record_id'] for r in result if r['contradictory_same_capture_observation_ids']],
        differing_or_unattributed_book_context_records=[r['record_id'] for r in result if r['different_book_context_observation_ids']],
        demonstrably_incorrect_nonmissing_book_records=[r['record_id'] for r in result if r['different_book_context_observation_ids'] and not missing(r['sportsbook'])],
        original_quote_bytes_available_records=sum(r['original_evidence_exact_bytes_available'] is True for r in result),
        capture_reused_as_quote_field_records=sum(r['capture_time_reused_in_quote_field'] is True for r in result),
        actual_quote_timestamps_verified=0,opening_claim_records=sum(r['is_opening']=='True' for r in result),
        closing_claim_records=sum(r['is_closing']=='True' for r in result),approved_records=0,
        exact_claim_duplicate_rows=[r['record_id'] for r in result if r['exact_claim_duplicate_record_ids']],
        same_value_repeat_rows=sum(bool(r['same_value_other_record_ids']) for r in result),
        prior_rejection_basis=dict(Counter(r['rejection_evidence_basis'] for r in result if r['evidence_classification']=='REJECTED')))
    for field in ['market','season','sportsbook','pregame_timing_status']:
        groups=defaultdict(Counter)
        for r in result:groups[r[field]][r['evidence_classification']]+=1
        summary['summary_by_dimension'][field]={k:dict(v) for k,v in sorted(groups.items())}
    return summary


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-output',default='data/review/stage7_odds_record_audit.csv')
    parser.add_argument('--evidence-output',default='reports/stage7_observation_checks.json')
    parser.add_argument('--summary-output',default='reports/stage7_summary_checks.json')
    args=parser.parse_args()
    result,observations,pages,errors=build()
    summary=summarize(result,observations)
    targets=[args.audit_output,args.evidence_output,args.summary_output]
    for name in targets:
        if (ROOT/name).exists():raise FileExistsError(name)
    with (ROOT/targets[0]).open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result[0]));writer.writeheader();writer.writerows(result)
    with (ROOT/targets[1]).open('x') as f:json.dump(dict(observations=observations,pages=pages,parser_limits=errors),f,indent=2);f.write('\n')
    with (ROOT/targets[2]).open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
    print('Classifications',dict(Counter(r['evidence_classification'] for r in result)))
    print('Observations',len(observations),'pages',len(pages),'parser limits',len(errors))


if __name__=='__main__':main()
