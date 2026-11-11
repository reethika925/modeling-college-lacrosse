"""Offline, read-only evidence parsing for the focused November 10 expansion.

No supplier code is executed. Outputs are audit evidence, never modeling inputs.
"""
import csv
import json
import re
from pathlib import Path
from decimal import Decimal
from bs4 import BeautifulSoup
from src.verify_wayback_spotcheck import american_from_decimal, capture_time, before_start

PACKAGE = Path('data/incoming/grok/evidence_expansion_d76adefe0110/odds_evidence_expansion_2026-11-10')
CACHE = Path(__file__).resolve().parents[1] / 'research/odds_evidence/dsf_expansion_pages'

def read_csv(path):
    with Path(path).open(newline='') as f:
        return list(csv.DictReader(f))

def team(name):
    name = name.replace('’', "'").strip()
    return {'Penn St.':'Penn State','Penn St':'Penn State','Ohio St.':'Ohio State',
            'St. Joseph\'s':"Saint Joseph's",'St. Joe\'s':"Saint Joseph's",
            'UMASS Lowell':'UMass Lowell','Albany':'UAlbany','Mount Saint Marys':"Mount St. Mary's"}.get(name,name)

def american(text):
    return int(str(text).replace('−','-').strip())

def dk_state(html):
    marker='window.__INITIAL_STATE__ = '
    if marker not in html: raise ValueError('Missing embedded state')
    # Decode data only; do not evaluate JavaScript.
    return json.JSONDecoder().raw_decode(html.split(marker,1)[1])[0]

def dk_pair(html,home,away,market):
    data=dk_state(html); group=data['eventGroups']['204466']
    assert group['name']=='College Lacrosse'
    events=[e for e in group['events'].values() if team(e['teamName1'])==team(away) and team(e['teamName2'])==team(home)]
    if len(events)!=1: raise ValueError('Ambiguous/missing DK event')
    event=events[0]
    offers=[o for o in data['offers']['204466'].values() if str(o['eventId'])==str(event['eventId']) and o['label'].lower()==market.lower()]
    if len(offers)!=1: raise ValueError('Ambiguous/missing DK market')
    offer=offers[0]; outcomes=offer.get('outcomes',[])
    if len(outcomes)!=2: raise ValueError('Incomplete paired market')
    pair={}
    for o in outcomes:
        name=team(o['label'])
        side=name.lower() if market=='total' else 'home' if name==team(home) else 'away' if name==team(away) else None
        if side not in ['home','away','over','under']: raise ValueError('Unrecognized selection')
        if o.get('criterionName') and o['criterionName'].lower()!=side: raise ValueError('Orientation disagreement')
        pair[side]={'price':american(o['oddsAmerican']),'line':o.get('line'),'display':o['oddsAmerican']}
    if set(pair)!=({'over','under'} if market=='total' else {'home','away'}): raise ValueError('Missing opposite side')
    return pair,{'event_id':event['eventId'],'page_start':event['startDate'],'offer_id':offer['providerOfferId'],'is_open_flag':offer.get('isOpen'),'update_date':offer.get('updateDate'),'type':'direct_sportsbook_display'}

def mgm_pair(html,home,away,market):
    soup=BeautifulSoup(html,'html.parser'); assert 'BetMGM' in soup.title.get_text()
    matches=[e for e in soup.select('ms-six-pack-event') if [team(n.get_text(' ',strip=True)) for n in e.select('.participant')]==[team(away),team(home)]]
    if len(matches)!=1: raise ValueError('Ambiguous/missing BetMGM event')
    event=matches[0]; headers=[x.get_text(strip=True) for x in event.find_parent('ms-event-group').select('.grid-group-header')]
    assert headers==['Spread','Total','Money']
    assert event.select_one('.away-indicator').get_text(strip=True)=='@'
    group=event.select('ms-option-group')[{'spread':0,'total':1,'moneyline':2}[market]]
    options=group.select('ms-option'); assert len(options)==2
    pair={}
    for side,o in zip(['over','under'] if market=='total' else ['away','home'],options):
        value=o.select_one('.option-value').get_text(strip=True); exact,rounded=american_from_decimal(value)
        attr=o.select_one('.option-attribute');line=None
        if market!='moneyline':
            label=attr.get_text(' ',strip=True)
            if market=='total':
                assert label[0].upper()==side[0].upper();label=label[1:].strip()
            line=float(label)
        pair[side]={'price':rounded,'line':line,'display':value,'american_unrounded':str(exact)}
    path=event.select_one('a.grid-info-wrapper')['href']
    starts=[]
    for script in soup.select('script#ldJson_SportsEvent'):
        for item in json.loads(script.get_text()).get('@graph',[]):
            if item.get('@type')=='SportsEvent' and item.get('url','').endswith(path):
                starts.append(item.get('startDate'))
    if len(starts)!=1:raise ValueError('Missing/ambiguous event date')
    return pair,{'page_event_path':path,'page_start':starts[0],'offline_options':len(group.select('.offline')),'type':'direct_sportsbook_display'}

def editorial_pair(html,home,away,book):
    soup=BeautifulSoup(html,'html.parser');found=[]
    for table in soup.find_all('table'):
        entries={}
        for row in table.select('tr'):
            cells=row.find_all(['td','th'])
            if len(cells)<2: continue
            label=cells[0].get_text(' ',strip=True)
            name=re.sub(r'\s+(Odds|Moneyline/Spread)$','',label)
            if team(name) in {team(home),team(away)}:
                entries[team(name)]=cells[1].get_text(' ',strip=True)
        if set(entries)!={team(home),team(away)}:continue
        context=table.get_text(' ',strip=True)
        if 'Odds via' not in context:
            nxt=table.find_next_sibling()
            if nxt:context+=' '+nxt.get_text(' ',strip=True)
            if 'Odds via' not in context:
                nxt=table.find_next('p')
                if nxt:context+=' '+nxt.get_text(' ',strip=True)
        if not re.search(r'Odds via\s+'+re.escape(book),context,re.I):raise ValueError('Book attribution absent from table context')
        pair={}
        for side,name in [('home',home),('away',away)]:
            value=entries[team(name)]
            if 'N/A' in value or 'ML N/A' in value:raise ValueError('No moneyline: price cell explicitly unavailable')
            value=value.split('/')[0].strip()
            if not re.fullmatch(r'[+−-]?\d+',value):raise ValueError('Not an explicit American moneyline')
            price=american(value)
            if abs(price)<100: raise ValueError('Invalid American price')
            pair[side]={'price':price,'line':None,'display':value}
        found.append((pair,{'type':'editorial_quote','publisher_title':soup.title.get_text(strip=True),'attribution_verified':book}))
    if len(found)!=1:raise ValueError('Ambiguous/missing editorial matchup')
    return found[0]

def check_existing_pair(row,pair,prior):
    used=set()
    for rid in row['odds_record_ids'].split(','):
        record=prior[rid]
        assert record['ncaa_game_id']==row['ncaa_game_id']
        assert record['market']==row['market'] and record['sportsbook']==row['sportsbook_claimed']
        if row['market']=='total':side=record['selection'].lower()
        else:side='home' if team(record['selection'])==team(row['home']) else 'away' if team(record['selection'])==team(row['away']) else None
        assert side in pair and side not in used;used.add(side)
        assert american(record['american_odds'])==pair[side]['price'],(rid,record['american_odds'],pair[side])
        if row['market']!='moneyline':assert Decimal(record['line'])==Decimal(str(pair[side]['line'])),(rid,record['line'],pair)
    assert len(used)==2

def main():
    import hashlib, argparse
    from datetime import datetime
    from zoneinfo import ZoneInfo
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('reports/grok_expansion_independent_checks.json'))
    args=parser.parse_args()
    fetch=read_csv(PACKAGE/'wayback_fetch_log.csv'); logs=json.loads((CACHE/'fetch.json').read_text())
    by_stamp={capture_time(x['url'],x['memento_datetime']).strftime('%Y%m%d%H%M%S'):x for x in logs if x.get('status')==200}
    prior={r['record_id']:r for r in read_csv('reports/grok_stage3_record_checks.csv')}
    starts={r['ncaa_game_id']:r for r in read_csv('reports/grok_expansion_official_starts.csv')}
    games={r['game_id']:r for r in read_csv('reports/grok_stage2_game_assessments.csv')}
    results=[]
    for row in read_csv(PACKAGE/'additional_verified_odds.csv'):
        stamp=re.search(r'/web/(\d{14})/',row['wayback_url'])[1];log=by_stamp[stamp]
        content=(CACHE/log['page_file']).read_bytes();assert hashlib.sha256(content).hexdigest()==log['sha256']
        html=content.decode('utf-8');cap=capture_time(log['url'],log['memento_datetime']);official=starts.get(row['ncaa_game_id'])
        g=games[row['ncaa_game_id']]
        assert (g['game_date'],team(g['home_team']),team(g['away_team']))==(row['game_date'],team(row['home']),team(row['away']))
        try:
            if 'sports.betmgm.com' in row['wayback_url']:pair,meta=mgm_pair(html,row['home'],row['away'],row['market'])
            elif 'sportsbook.draftkings.com' in row['wayback_url']:pair,meta=dk_pair(html,row['home'],row['away'],row['market'])
            else:pair,meta=editorial_pair(html,row['home'],row['away'],row['sportsbook_claimed'])
            if meta.get('page_start'):
                event_date=datetime.fromisoformat(meta['page_start'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat()
                assert event_date==row['game_date'],'Archived event date differs'
            check_existing_pair(row,pair,prior)
            status='PREGAME_PRICE_VERIFIED' if official and before_start(cap,official['scheduled_start_utc']) else 'CAPTURE_AFTER_GAME_DATE' if cap.date().isoformat()>row['game_date'] else 'TIMING_UNRESOLVED'
            error=''
        except (ValueError,AssertionError) as e:
            pair={};meta={};status='NOT_VERIFIED';error=str(e)
        results.append({**row,'observed':pair,'independent_metadata':meta,'independent_status':status,'error':error,'official_start':official,'bookmaker_quote_timestamp':None,'permission':'UNRESOLVED_NOT_APPROVED'})
    extras=[]
    for file,gids in [('dk20230203.html',['6085412','6085420','6085415']),('dk20250513.html',['6448514','6448513','6448512'])]:
        html=(CACHE/file).read_text();log=next(x for x in logs if x['page_file']==file);cap=capture_time(log['url'],log['memento_datetime'])
        for gid in gids:
            g=games[gid];pair,meta=dk_pair(html,g['home_team'],g['away_team'],'moneyline');assert before_start(cap,starts[gid]['scheduled_start_utc'])
            ids=[r['record_id'] for r in prior.values() if r['ncaa_game_id']==gid and r['market']=='moneyline' and r['sportsbook']=='DraftKings' and team(r['selection']) in [team(g['home_team']),team(g['away_team'])] and american(r['american_odds'])==pair['home' if team(r['selection'])==team(g['home_team']) else 'away']['price']]
            extras.append({'ncaa_game_id':gid,'season':g['season'],'game_date':g['game_date'],'home':g['home_team'],'away':g['away_team'],'book':'DraftKings','archive_url':log['url'],'capture_utc':cap.isoformat(),'observed':pair,'metadata':meta,'matching_existing_record_ids':ids,'matching_ids_note':'Same game/book/price only; does not authenticate another source or capture. No IDs assigned to these additional observations.','permission':'UNRESOLVED_NOT_APPROVED','status':'PREGAME_PRICE_VERIFIED'})
    with args.output.open('x') as f:json.dump({'checks':results,'omitted_moneyline_evidence':extras},f,indent=2);f.write('\n')
    from collections import Counter
    print(Counter(r['independent_status'] for r in results))
    for r in results:
        if r['error']:print(r['odds_record_ids'],r['error'])
    print('Additional DK moneyline pairs',len(extras))

if __name__=='__main__':main()
