"""Build odds evidence expansion deliverables from fresh Wayback fetches in /tmp/exp/pages (fetched 2026-11-10 ET).
Never invents prices: every page value is parsed from the fetched page; every record value from the evidence map."""
import sys,re,csv,json,glob,datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0,'scripts'); from parsers import *
import pandas as pd
ET=ZoneInfo('America/New_York'); UTC=dt.timezone.utc
P='/tmp/exp/pages/'
M=pd.read_csv('/workspace/supplement_2026-11-10/priority2_odds_evidence/odds_evidence_to_record_map.csv')
CW=pd.read_csv('/workspace/lax_data/processed/odds_game_to_ncaa_game_crosswalk.csv').set_index('odds_game_id')
SB={}
for f in glob.glob('/workspace/lax_data/raw/scoreboards/*/*.json'):
    for x in json.load(open(f)).get('games',[]):
        x=x['game']; SB[int(x['url'].split('/')[-1])]=x
ALREADY=set('N0272 N0273 N0278 N0279 N0284 N0285 N0290 N0291 N0296 N0297 N0302 N0303 O1165 O1166 N0266 N0267 N0112 N0113 N0118 N0119 N0124 N0125 N0130 N0131 N0142 N0143 N0154 N0155 N0230 N0231 N0214 N0215 N0254 N0255 N0166 N0167'.split())
OLD_GAMES={6448511,6448513,6448512,6386505,6386174,6386158,6386338,6386293,6386100,6386091,6386419,6386509,6386079,6386359,6386280}
PAGES={ # key: (file, wayback ts, original url, evidence_type, publisher)
 'mgm20250121':('mgm20250121.html','20250121025539','https://sports.betmgm.com/en/sports/lacrosse-88','direct_sportsbook_archive','BetMGM'),
 'mgm20240223':('mgm20240223.html','20240223113743','https://sports.betmgm.com/en/sports/lacrosse-88','direct_sportsbook_archive','BetMGM'),
 'mgm20240525':('mgm20240525.html','20240525152928','https://sports.betmgm.com/en/sports/lacrosse-88','direct_sportsbook_archive','BetMGM'),
 'mgm20250513':('/tmp/wbfetch/mgm0513.html','20250513152831','https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213','direct_sportsbook_archive','BetMGM'),
 'mgm20250516':('/tmp/wbfetch/mgm0516.html','20250516024155','https://sports.betmgm.com/en/sports/lacrosse-88','direct_sportsbook_archive','BetMGM'),
 'dk20250513':('dk20250513.html','20250513200421','https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game','direct_sportsbook_archive','DraftKings'),
 'dk20230203':('dk20230203.html','20230203181011','https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse','direct_sportsbook_archive','DraftKings'),
 'bol_wk0':('bol_wk0_20260308.html','20260308175741','https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-0-bets/','third_party_article_quote','Bet On Lacrosse'),
 'an20230204':('an20230204.html','20230204034751','https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins','third_party_article_quote','Action Network'),
 'an20230325':('an20230325.html','20230325141823','https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-saturday-week-7-notre-dame-vs-virginia-marquette-vs-st-bonaventure-march-25','third_party_article_quote','Action Network'),
 'an20230407':('an20230407.html','20230407193556','https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-virginia-cavaliers-vs-north-carolina-tar-heels-friday-april-7','third_party_article_quote','Action Network'),
 'an20230415':('an20230415.html','20230415044110','https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-week-10','third_party_article_quote','Action Network'),
 'an20230514':('an20230514.html','20230514033813','https://www.actionnetwork.com/lacrosse/college-lacrosse-betting-odds-picks-best-bets-for-ncaa-tournament-opening-round-sunday','third_party_article_quote','Action Network'),
}
def wb(k): f,ts,u,_,_=PAGES[k]; return f"https://web.archive.org/web/{ts}/{u}"
def cap(k):
    ts=PAGES[k][1]; u=dt.datetime.strptime(ts,'%Y%m%d%H%M%S').replace(tzinfo=UTC); return u
def fmt_et(u): return u.astimezone(ET).strftime('%Y-%m-%d %H:%M:%S %Z')
def norm(s): 
    s=s.lower().replace('’',"'").replace('saint ','st. ').replace('st joe','st. joe')
    s={'umass lowell':'umass lowell','penn st':'penn state','ohio st.':'ohio state','penn st.':'penn state','st. joe\'s':"st. joseph's",'ualbany':'albany','pennsylvania':'penn','loyola (md)':'loyola maryland','loyola md':'loyola maryland','umass':'massachusetts',"st. john's - new york":"st. john's"}.get(s.strip(),s.strip())
    return re.sub(r'[^a-z]','',s)
def same(a,b):
    a,b=norm(a),norm(b); return a==b or (len(a)>=5 and len(b)>=5 and (a.startswith(b) or b.startswith(a)))
def am(x):
    x=str(x).strip().replace('−','-')
    return int(x) if re.fullmatch(r'[+-]?\d+',x) else None
def dec2am(d): d=float(d); return round((d-1)*100) if d>=2 else round(-100/(d-1))
def official_start(gid):
    x=SB.get(gid); 
    if not x: return None,'no NCAA scoreboard entry'
    st=x['startTime']; ep=int(x['startTimeEpoch']); e=dt.datetime.fromtimestamp(ep,UTC)
    if st!='TBA':
        return e,f"NCAA scoreboard startTime '{st}' (epoch {ep})"
    if e.minute==0 and e.hour in (4,5,6,7,8):
        return None,f"NCAA scoreboard startTime 'TBA'; epoch {e:%Y-%m-%dT%H:%MZ} is a local-midnight placeholder -> official start unknown"
    return e,f"NCAA scoreboard startTimeEpoch {e:%Y-%m-%dT%H:%MZ} (startTime text 'TBA'; epoch not a midnight placeholder)"
def timing(c,gid,game_date):
    s,src=official_start(gid)
    if s is not None: return ('pre' if c<s else 'post'),s,src
    gd=dt.date.fromisoformat(game_date); cd=c.astimezone(ET).date()
    return ('pre' if cd<gd else ('post' if cd>gd else 'unknown')),None,src+('; capture ET date before game date' if cd<gd else '')
rows=[]
def add(k,gk,recs,market,home_rec,away_rec,home_pg,away_pg,book_pg,snippet,page_start,notes,quote_time='not shown on page',pub='n/a (sportsbook listing page)',visible=True,mismatch_reason=''):
    cw=CW.loc[gk]; gid=int(cw.ncaa_game_id); c=cap(k)
    tm,s,src=timing(c,gid,cw.ncaa_game_date)
    ids=','.join(sorted(recs.record_id)) if len(recs) else ''
    claimed=','.join(sorted(set(recs.sportsbook))) if len(recs) else ''
    match = visible and home_rec is not None and str(home_rec)==str(home_pg) and str(away_rec)==str(away_pg)
    if not len(recs): outcome='archive_quote_not_in_dataset'
    elif not visible: outcome='not_visible'
    elif not match: outcome='mismatch'
    else: outcome={'pre':'authenticated_pre_game','post':'price_match_post_game','unknown':'price_match_timing_unknown'}[tm]
    if len(recs) and claimed and book_pg and not any(same(claimed,b) for b in [book_pg]) and outcome.startswith(('authenticated','price_match')):
        outcome='mismatch'; mismatch_reason=(mismatch_reason+' book attribution differs').strip()
    rows.append(dict(check_key=k,odds_record_ids=ids,season=int(cw.odds_season),odds_game_id=gk,ncaa_game_id=gid,game_date=cw.ncaa_game_date,
        home=cw.ncaa_home_team,away=cw.ncaa_away_team,new_game=('no (game in 15-game spot-check)' if gid in OLD_GAMES else 'yes'),market=market,
        sportsbook_claimed=claimed,sportsbook_on_page=book_pg,evidence_type=PAGES[k][3],evidence_publisher=PAGES[k][4],
        home_or_over_record=home_rec,away_or_under_record=away_rec,home_or_over_page=home_pg,away_or_under_page=away_pg,prices_match=('yes' if match else 'no'),
        wayback_url=wb(k),capture_ts_utc=c.strftime('%Y-%m-%dT%H:%M:%SZ'),capture_ts_et=fmt_et(c),
        official_start_utc=(s.strftime('%Y-%m-%dT%H:%MZ') if s else 'unknown'),official_start_et=(fmt_et(s) if s else 'unknown'),official_start_source=src,
        page_listed_start=page_start,publication_time=pub,quote_time=quote_time,timing_result=tm,outcome=outcome,mismatch_reason=mismatch_reason,
        evidence_snippet=snippet,notes=notes,permission_class=(recs.permission_class.iloc[0] if len(recs) else 'n/a (not a dataset record)'),record_status=(','.join(sorted(set(recs.status))) if len(recs) else '')))
def recs_for(gk,mask): 
    r=M[(M.game_id==gk)&mask]; assert not set(r.record_id)&ALREADY; return r
# ---------- BetMGM direct archives ----------
for k in ['mgm20250121','mgm20240223','mgm20240525']:
    f,ts,u,_,_=PAGES[k]; ev=parse_mgm(f if f.startswith('/') else P+f)
    stale=''
    if k=='mgm20240223': stale="Page timers show 'Tomorrow • …' for 2024-02-23 games although capture is 2024-02-23 11:37Z, so BetMGM served a render from 2024-02-22 (UTC). Content therefore pre-dates the capture; capture itself is pre-game, so pre-game status holds. "
    for eid,e in ev.items():
        if len(e['participants'])!=2 or len(e['groups'])<3 or not e['groups'][2] or None in [o[1] for o in e['groups'][2]]: continue
        pa,ph=e['participants']; dA,dH=e['groups'][2][0][1],e['groups'][2][1][1]
        # find odds game
        cands=[g for g in CW.index if g.startswith(e['start'][1][:4]) and CW.loc[g].match_status=='matched' and same(CW.loc[g].ncaa_home_team,ph) and same(CW.loc[g].ncaa_away_team,pa)]
        cands=[g for g in cands if abs((dt.date.fromisoformat(CW.loc[g].ncaa_game_date)-dt.date.fromisoformat(e['start'][1][:10])).days)<=1]
        if not cands: continue
        gk=cands[0]
        if k=='mgm20250121':
            r=recs_for(gk,(M.market=='moneyline')&(M.sportsbook=='BetMGM'))
        else:
            r=recs_for(gk,(M.market=='moneyline')&M.archive_url.fillna('').str.contains(ts))
        cw=CW.loc[gk]
        rh=[x for _,x in r.iterrows() if same(x.selection,cw.ncaa_home_team)]; ra=[x for _,x in r.iterrows() if same(x.selection,cw.ncaa_away_team)]
        hr=int(rh[0].american_odds) if rh else None; ar=int(ra[0].american_odds) if ra else None
        snip=f"BetMGM event {eid}: \"{pa} @ {ph}\" | \"{e['timer']}\" | moneyline cells \"{dA}\" / \"{dH}\""
        notes=stale+"Page shows decimal odds; page American value = arithmetic conversion of displayed decimal. Option cells carry CSS class 'offline' in the archived render. Page times are UTC."
        mr=''
        if k=='mgm20250121' and len(r):
            notes+=f" Dataset record comes from a Bet On Lacrosse article ({r.evidence_publisher.iloc[0]}, published 2025-02-01 05:28Z) quoting BetMGM; this archive is a direct BetMGM page 11 days earlier."
            if not (hr==dec2am(dH) and ar==dec2am(dA)): mr='different_capture_time: archived BetMGM price is from 2025-01-21, record is the BetMGM price quoted by Bet On Lacrosse on 2025-02-01; line movement is plausible, so this is not evidence the record is wrong, only that it is not authenticated by this archive.'
        if not len(r):
            notes+=" No BetMGM record exists for this game in the dataset (the dataset's record for this game, if any, is for a different book); archived price listed for context only, not added to the dataset."
        add(k,gk,r,'moneyline',hr,ar,dec2am(dH),dec2am(dA),'BetMGM',snip,f"{e['start'][1]} (JSON-LD); timer '{e['timer']}'",notes,mismatch_reason=mr)

# ---------- BetMGM May-2025 spread/total records (ML already checked in the 15-game spot-check) ----------
for k in ['mgm20250513','mgm20250516']:
    f,ts,u,_,_=PAGES[k]; ev=parse_mgm(f)
    r_all=M[M.archive_url.fillna('').str.contains(ts)&M.market.isin(['spread','total'])]
    for gk,r in r_all.groupby('game_id'):
        assert not set(r.record_id)&ALREADY
        cw=CW.loc[gk]; eid=re.search(r'BetMGM event (\d+)',r.evidence_excerpt.iloc[0]).group(1); e=ev[eid]; pa,ph=e['participants']
        sp,tot=e['groups'][0],e['groups'][1]
        for mk in ['spread','total']:
            rr=r[r.market==mk]
            if mk=='spread':
                h=[x for _,x in rr.iterrows() if same(x.selection,ph)]; a=[x for _,x in rr.iterrows() if same(x.selection,pa)]
                hr=f"{float(h[0].line):+g} {int(h[0].american_odds):+d}"; ar=f"{float(a[0].line):+g} {int(a[0].american_odds):+d}"
                hp=f"{float(sp[1][0]):+g} {dec2am(sp[1][1]):+d}"; ap=f"{float(sp[0][0]):+g} {dec2am(sp[0][1]):+d}"
                snip=f"BetMGM event {eid}: \"{pa} @ {ph}\" | spread cells \"{sp[0][0]}\" \"{sp[0][1]}\" / \"{sp[1][0]}\" \"{sp[1][1]}\""
            else:
                h=[x for _,x in rr.iterrows() if x.selection=='Over']; a=[x for _,x in rr.iterrows() if x.selection=='Under']
                hr=f"O {float(h[0].line):g} {int(h[0].american_odds):+d}"; ar=f"U {float(a[0].line):g} {int(a[0].american_odds):+d}"
                hp=f"O {sp and tot[0][0].split()[1]} {dec2am(tot[0][1]):+d}"; ap=f"U {tot[1][0].split()[1]} {dec2am(tot[1][1]):+d}"
                snip=f"BetMGM event {eid}: \"{pa} @ {ph}\" | total cells \"{tot[0][0]}\" \"{tot[0][1]}\" / \"{tot[1][0]}\" \"{tot[1][1]}\""
            add(k,gk,rr,mk,hr,ar,hp,ap,'BetMGM',snip,f"{e['start'][1]} (JSON-LD); timer '{e['timer']}'","Spread/total records for a game whose moneyline was checked in the 15-game spot-check (not a new game). Decimal prices on page; American = conversion. Source map lists capture time as 'quote timestamp' (mislabel).")
# ---------- DraftKings direct archives (spread/total; no ML offers present) ----------
for k,games in [('dk20250513',None),('dk20230203',['2023-02-04_denver_vs_utah','2023-02-04_jacksonville_vs_johns-hopkins','2023-02-04_syracuse_vs_vermont'])]:
    f,ts,u,_,_=PAGES[k]; ev,offers=parse_dk(P+f)
    r_all=M[M.archive_url.fillna('').str.contains(ts)]
    gks=games or sorted(r_all.game_id.unique())
    for gk in gks:
        r=r_all[r_all.game_id==gk]; assert not set(r.record_id)&ALREADY
        cw=CW.loc[gk]
        evid=[i for i,e in ev.items() if same(e['name'].split(' @ ')[1],cw.ncaa_home_team) and same(e['name'].split(' @ ')[0],cw.ncaa_away_team)]
        if not evid: print('no event',gk); continue
        e=ev[evid[0]]; offs=[o for o in offers.values() if o['event']==evid[0]]
        labels=sorted(set(o['label'] for o in offs))
        for mk,lab in [('spread','Spread'),('total','Total')]:
            o=[x for x in offs if x['label']==lab]
            rr=r[r.market==mk]
            if mk=='spread':
                h=[x for _,x in rr.iterrows() if same(x.selection,cw.ncaa_home_team)]; a=[x for _,x in rr.iterrows() if same(x.selection,cw.ncaa_away_team)]
                hr=f"{float(h[0].line):+g} {int(h[0].american_odds):+d}" if h else None; ar=f"{float(a[0].line):+g} {int(a[0].american_odds):+d}" if a else None
                hp=ap=None
                if o:
                    for lbl,odds,ln in o[0]['outcomes']:
                        if same(lbl,cw.ncaa_home_team): hp=f"{float(ln):+g} {int(odds):+d}"
                        if same(lbl,cw.ncaa_away_team): ap=f"{float(ln):+g} {int(odds):+d}"
            else:
                h=[x for _,x in rr.iterrows() if x.selection=='Over']; a=[x for _,x in rr.iterrows() if x.selection=='Under']
                hr=f"O {float(h[0].line):g} {int(h[0].american_odds):+d}" if h else None; ar=f"U {float(a[0].line):g} {int(a[0].american_odds):+d}" if a else None
                hp=ap=None
                if o:
                    for lbl,odds,ln in o[0]['outcomes']:
                        if lbl=='Over': hp=f"O {float(ln):g} {int(odds):+d}"
                        if lbl=='Under': ap=f"U {float(ln):g} {int(odds):+d}"
            snip=f"DK event \"{e['name']}\" start {e['start']} | {lab}: " + '; '.join(f"{l} {ln or ''} {od}" for l,od,ln in (o[0]['outcomes'] if o else []))
            add(k,gk,rr,mk,hr,ar,hp,ap,'DraftKings',snip,e['start'],f"Offer labels present for this event: {labels}. No moneyline offer is present in this archived DraftKings page, so no ML check is possible.",visible=bool(o))
# ---------- Article quotes ----------
def art(k,parser):
    f,ts,u,_,_=PAGES[k]; pub,mod=meta_times(P+f)
    pubs=f"published {pub}; modified {mod}" if pub else 'not shown'
    boxes=parser(P+f)
    r_all=M[(M.market=='moneyline')&(M.archive_url.fillna('').str.contains(ts) if k!='bol_wk0' else (M.source_url==u))]
    for gk,r in r_all.groupby('game_id'):
        assert not set(r.record_id)&ALREADY
        cw=CW.loc[gk]
        b=[x for x in boxes if {same(x['t1'],cw.ncaa_home_team) or same(x['t1'],cw.ncaa_away_team), same(x['t2'],cw.ncaa_home_team) or same(x['t2'],cw.ncaa_away_team)}=={True}]
        rh=[x for _,x in r.iterrows() if same(x.selection,cw.ncaa_home_team)]; ra=[x for _,x in r.iterrows() if same(x.selection,cw.ncaa_away_team)]
        hr=int(rh[0].american_odds) if rh else None; ar=int(ra[0].american_odds) if ra else None
        if not b:
            add(k,gk,r,'moneyline',hr,ar,None,None,'',"(no odds box for this game found on archived page)",'',"",pub=pubs,visible=False); continue
        x=b[0]; pt={x['t1']:x['p1'],x['t2']:x['p2']}
        hp=[am(v) for t,v in pt.items() if same(t,cw.ncaa_home_team)][0]; ap=[am(v) for t,v in pt.items() if same(t,cw.ncaa_away_team)][0]
        book=x['book'].replace(' Sportsbook','')
        notes=f"Third-party article quote; book named by the article ('Odds via {x['book']}'). "
        vis=True; mr=''
        if hp is None or ap is None:
            vis=False
            notes+=f"The article's price cells for this game read '{x['p1']}' / '{x['p2']}', i.e. no two-sided moneyline is shown. "
            if hr is not None and abs(hr)<50: mr="record_value_is_spread_not_moneyline: the dataset's 'moneyline' values equal the spread (" + f"{hr:+d}/{ar:+d}" + ") and the article shows 'ML N/A'."
        if k=='bol_wk0': notes+="Capture is 2026-03-08, a year after the game; article metadata shows publication before the game, but the archive cannot certify the text was unchanged pre-game. "
        add(k,gk,r,'moneyline',hr,ar,(hp if vis else x['p1']+' / '+x['p2']),(ap if vis else ''),book,x['snippet'][:260],x['time'],notes,pub=pubs,visible=vis,mismatch_reason=mr)
        if vis is False and mr: rows[-1]['outcome']='mismatch'
art('bol_wk0',parse_bol)
for k in ['an20230204','an20230325','an20230407','an20230415','an20230514']: art(k,parse_an)
df=pd.DataFrame(rows)
df.to_csv('/tmp/exp/all_checks.csv',index=False)
print(df[['check_key','odds_record_ids','odds_game_id','market','sportsbook_claimed','sportsbook_on_page','home_or_over_record','away_or_under_record','home_or_over_page','away_or_under_page','timing_result','outcome']].to_string())
