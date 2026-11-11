"""Build wayback_2025_odds_spotcheck.csv from freshly fetched Wayback pages (/tmp/wbfetch, fetched 2026-11-10 ~17:21 ET).
Page HTML is NOT redistributed; only short price strings are quoted."""
import csv,re,sys,html,datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0,'scripts'); from parse_mgm import parse
import pandas as pd
ET=ZoneInfo('America/New_York')
M=pd.read_csv('/workspace/supplement_2026-11-10/priority2_odds_evidence/odds_evidence_to_record_map.csv')
GI=pd.read_csv('/workspace/lax_data/processed/ncaa_lacrosse_game_index_2025.csv').set_index('game_id')
CW=pd.read_csv('/workspace/supplement_2026-11-10/priority1_originals/recovered_originals/odds_game_to_ncaa_game_crosswalk.csv').set_index('odds_game_id')
NCAA_TIME={6448511:'12:00PM ET',6448513:'02:30PM ET',6448512:'12:00PM ET'}  # from raw NCAA scoreboard JSON; others 'TBA'
ESPN_START={6448511:'2025-05-17T16:00Z',6448513:'2025-05-18T18:50Z',6448512:'2025-05-18T16:00Z',6386505:'2025-03-01T19:00Z',6386174:'2025-02-16T17:00Z',6386158:'2025-02-14T23:00Z',6386338:'2025-02-14T19:00Z',6386293:'2025-02-15T19:00Z',6386100:'2025-02-15T16:00Z',6386091:'2025-02-15T20:30Z',6386419:'2025-02-15T18:00Z',6386509:'2025-02-15T19:00Z',6386079:'2025-02-15T17:00Z',6386359:'2025-02-15T17:00Z',6386280:'2025-02-15T19:00Z'}
PAGES={'20250216180923':'/tmp/wbfetch/mgm0216.html','20250513152831':'/tmp/wbfetch/mgm0513.html','20250516024155':'/tmp/wbfetch/mgm0516.html'}
PARSED={k:parse(v) for k,v in PAGES.items()}
SEL=['2025-05-17_cornell_vs_richmond','2025-05-18_georgetown_vs_maryland','2025-05-18_notre-dame_vs_penn-state','2025-03-01_syracuse_vs_utah',
 '2025-02-16_navy_vs_towson','2025-02-14_north-carolina_vs_stony-brook','2025-02-14_quinnipiac_vs_umass',
 '2025-02-15_air-force_vs_ohio-state','2025-02-15_bellarmine_vs_canisius','2025-02-15_brown_vs_fairfield','2025-02-15_bucknell_vs_dartmouth',
 '2025-02-15_maryland_vs_syracuse','2025-02-15_johns-hopkins_vs_loyola-(md)','2025-02-15_villanova_vs_yale','2025-02-15_denver_vs_utah']
def dec2am(d):
    d=float(d); return round((d-1)*100) if d>=2 else round(-100/(d-1))
def fmt(a): return f"{int(a):+d}"
def et(ts):
    u=dt.datetime.strptime(ts,'%Y%m%d%H%M%S').replace(tzinfo=dt.timezone.utc); return u.strftime('%Y-%m-%dT%H:%M:%SZ'),u.astimezone(ET).strftime('%Y-%m-%d %H:%M:%S %Z')
def norm(s): return re.sub(r'[^a-z]','',s.lower().replace('’',"'").replace('saint','st'))
out=[]
w=M[(M.season==2025)&(M.market=='moneyline')&M.archive_url.notna()]
for gk in SEL:
    cw=CW.loc[gk]; gid=int(cw.ncaa_game_id); g=GI.loc[gid]
    assert cw.match_status=='matched' and pd.isna(g.suspected_duplicate_of) and g.status=='final'
    for au,recs in w[w.game_id==gk].groupby('archive_url'):
        ts=re.search(r'/web/(\d{14})/',au).group(1); cu,ce=et(ts)
        recs=recs.sort_values('record_id'); ids=','.join(recs.record_id)
        start=ESPN_START[gid]; start_dt=dt.datetime.strptime(start,'%Y-%m-%dT%H:%MZ').replace(tzinfo=dt.timezone.utc)
        cap_dt=dt.datetime.strptime(ts,'%Y%m%d%H%M%S').replace(tzinfo=dt.timezone.utc)
        row=dict(odds_record_ids=ids,ncaa_game_id=gid,game_date=g.game_date,home=g.home_team,away=g.away_team,
                 ncaa_start_time=NCAA_TIME.get(gid,'TBA (NCAA scoreboard)'),
                 sportsbook_claimed=recs.sportsbook.iloc[0],wayback_url=au,capture_ts_utc=cu,capture_ts_et=ce)
        # record prices by NCAA home/away
        def rec_for(team):
            for _,r in recs.iterrows():
                if norm(r.selection)[:5]==norm(team)[:5] or norm(team).startswith(norm(r.selection)[:4]): return r
        if ts in PARSED:
            eid=re.search(r'BetMGM event (\d+)',recs.evidence_excerpt.iloc[0]).group(1); ev=PARSED[ts][eid]
            pa,ph=ev['participants']  # BetMGM layout "A @ B": B = home
            ml=ev['groups'][2]; dA,dH=ml[0][1],ml[1][1]
            pg={norm(pa):dA,norm(ph):dH}
            rh=[r for _,r in recs.iterrows() if norm(r.selection)==norm(ph)][0]; ra=[r for _,r in recs.iterrows() if norm(r.selection)==norm(pa)][0]
            hm_rec,aw_rec=int(rh.american_odds),int(ra.american_odds)
            hm_pg,aw_pg=dec2am(dH),dec2am(dA)
            orient_ok = norm(ph)[:4]==norm(g.home_team)[:4] or (ph=='Penn St' and g.home_team=='Penn St.') or (ph=='Ohio State' and g.home_team=='Ohio St.') or (ph=='Loyola Maryland')
            row.update(sportsbook_on_page='BetMGM (sports.betmgm.com page itself)',home_ml_record=fmt(hm_rec),away_ml_record=fmt(aw_rec),
                home_ml_page=f"{dH} dec (= {fmt(hm_pg)})",away_ml_page=f"{dA} dec (= {fmt(aw_pg)})",
                page_teams=f"{pa} @ {ph}",page_start=f"{ev['start'][1]} (JSON-LD); timer text '{ev['timer']}'",
                publication_time='n/a (sportsbook listing page; no publication time)',quote_time='not shown on page',
                evidence_snippet=f"BetMGM event {eid}: \"{pa} @ {ph}\" | \"{ev['timer']}\" | spread {ml and ev['groups'][0][0][0]}/{ev['groups'][0][1][0]} | moneyline cells \"{dA}\" / \"{dH}\"")
            prices_match = (hm_rec==hm_pg and aw_rec==aw_pg)
        else:  # Bet On Lacrosse article
            hm_rec=int(recs[recs.selection=='Utah'].american_odds.iloc[0]); aw_rec=int(recs[recs.selection=='Syracuse'].american_odds.iloc[0])
            t=open('/tmp/wbfetch/bol0301.html',encoding='utf-8',errors='replace').read()
            txt=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' | ',re.sub(r'<script.*?</script>','',t,flags=re.S))))
            txt=re.sub(r'(\|\s*)+','| ',txt)
            i=txt.find('Syracuse at Utah | Syracuse Moneyline'); snip=txt[i:i+175]
            sm=re.search(r'Syracuse Moneyline/Spread \| ([+-]\d+) /',snip).group(1); um=re.search(r'Utah Moneyline/Spread \| ([+-]\d+) /',snip).group(1)
            book=re.search(r'Odds via \| (\w+)',snip).group(1)
            pub=re.search(r'article:published_time" content="([^"]+)"',t).group(1); mod=re.search(r'article:modified_time" content="([^"]+)"',t).group(1)
            p_et=dt.datetime.fromisoformat(pub).astimezone(ET).strftime('%Y-%m-%d %H:%M %Z'); m_et=dt.datetime.fromisoformat(mod).astimezone(ET).strftime('%Y-%m-%d %H:%M %Z')
            hm_pg,aw_pg=int(um),int(sm); orient_ok=True
            row.update(sportsbook_on_page=f"{book} (named by Bet On Lacrosse article: 'Odds via {book}')",home_ml_record=fmt(hm_rec),away_ml_record=fmt(aw_rec),
                home_ml_page=um,away_ml_page=sm,page_teams='Syracuse at Utah',page_start="'Saturday · 2 p.m. ET' (article)",
                publication_time=f"{pub} ({p_et}); modified {mod} ({m_et})",quote_time='not shown on page',evidence_snippet=snip.strip())
            prices_match=(hm_rec==hm_pg and aw_rec==aw_pg)
        pre = cap_dt < start_dt
        row['game_start_utc_used']=start+' (ESPN raw scoreboard / matches page listing)'
        row['pre_game']='yes' if pre else 'no'
        notes=[]
        if ts in PARSED: notes.append('Page shows decimal odds; record American value is the arithmetic conversion of the displayed decimal (exact match after rounding). The page does not display American odds.')
        if ts=='20250216180923':
            notes.append("Archive capture (Common Crawl WARC CC-MAIN-20250216171447) is AFTER game start. Page-internal relative timers ('Today • 11:00 PM' for the 2025-02-14 23:00Z game, 'Starting in 50 min' for the 2025-02-14 19:00Z game) imply BetMGM served a cached render from about 2025-02-14 18:10 UTC (1:10 PM ET), i.e. probably pre-game for this game, but that is an inference from page text, not an archive-certified time.")
        if gid==6386338: notes.append("Page footer for this event says 'Starting in 50 min'; prices were live pre-match at render time, not an opening/closing line.")
        if ts in ('20250513152831','20250516024155'): notes.append("Source map's original_quote_timestamp_utc for this record equals the capture time; that is a capture time, not a sportsbook quote time.")
        if gid==6448513 and ts=='20250513152831': notes.append('This capture lists start 2025-05-18T16:00Z; the 2025-05-16 capture and NCAA list 2:30 PM ET (18:30Z) — schedule moved; capture pre-game under either time.')
        if ts=='20250301181913': notes.append('Odds attributed to FanDuel by a third-party editorial (Bet On Lacrosse), not a FanDuel page; page published 10:13 AM ET, capture 1:19 PM ET, game 2:00 PM ET.')
        notes.append('All BetMGM option cells carry CSS class "offline" in the archived server-render (likely non-hydrated state); cannot tell whether the market was open.' if ts in PARSED else '')
        notes.append(f"Orientation: page home = NCAA home ({g.home_team})" if orient_ok else 'ORIENTATION MISMATCH')
        if not prices_match: outcome='mismatch'
        elif not pre: outcome='capture_post_game'
        else: outcome='authenticated'
        row['outcome']=outcome; row['prices_match']='yes' if prices_match else 'no'
        row['notes']=' '.join(n for n in notes if n)
        out.append(row)
cols=['odds_record_ids','ncaa_game_id','game_date','home','away','sportsbook_claimed','sportsbook_on_page','home_ml_record','away_ml_record','home_ml_page','away_ml_page','prices_match','wayback_url','capture_ts_utc','capture_ts_et','ncaa_start_time','game_start_utc_used','pre_game','publication_time','quote_time','page_teams','page_start','outcome','evidence_snippet','notes']
with open('wayback_2025_odds_spotcheck.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=cols); wr.writeheader(); wr.writerows(out)
print(len(out)); print(pd.DataFrame(out)[['odds_record_ids','home','away','home_ml_record','away_ml_record','home_ml_page','away_ml_page','capture_ts_et','pre_game','outcome']].to_string())
