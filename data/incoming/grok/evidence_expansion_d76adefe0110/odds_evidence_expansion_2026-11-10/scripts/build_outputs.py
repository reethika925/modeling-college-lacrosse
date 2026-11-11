"""Consolidate checks -> deliverables. Inputs: /tmp/exp/all_checks.csv (from build_expansion.py), fresh page headers, CDX results."""
import pandas as pd,re,os,glob,hashlib,csv,sys,datetime as dt
sys.path.insert(0,'scripts'); from parse_mgm import parse as parse_mgm
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
A=pd.read_csv('/tmp/exp/all_checks.csv',dtype=str).fillna('')
A.to_csv('evidence_checks_detail.csv',index=False)
# ---- consolidated per record pair (dedupe repeated snapshots of the same prices) ----
rank={'authenticated_pre_game':0,'price_match_timing_unknown':1,'price_match_post_game':2,'mismatch':3,'not_visible':4,'fetch_failed':5,'archive_quote_not_in_dataset':9}
out=[]
for key,g in A[A.odds_record_ids!=''].groupby(['odds_record_ids','market']):
    g=g.assign(r=g.outcome.map(rank)).sort_values(['r','capture_ts_utc'])
    best=g.iloc[0].to_dict()
    pre=g[g.outcome=='authenticated_pre_game'].sort_values('capture_ts_utc')
    best['first_pre_game_capture']=(pre.iloc[0].wayback_url+' @ '+pre.iloc[0].capture_ts_et) if len(pre) else ''
    best['all_snapshot_checks']=' || '.join(f"{r.wayback_url} [{r.capture_ts_et}; {r.evidence_type}; page {r.home_or_over_page}/{r.away_or_under_page}; {r.outcome}]" for r in g.itertuples())
    best['n_snapshots']=len(g)
    best.pop('r',None); out.append(best)
V=pd.DataFrame(out)
cols=['odds_record_ids','season','odds_game_id','ncaa_game_id','game_date','home','away','new_game','market','sportsbook_claimed','sportsbook_on_page','evidence_type','evidence_publisher',
 'home_or_over_record','away_or_under_record','home_or_over_page','away_or_under_page','prices_match','wayback_url','capture_ts_utc','capture_ts_et','official_start_utc','official_start_et','official_start_source',
 'page_listed_start','publication_time','quote_time','timing_result','outcome','mismatch_reason','first_pre_game_capture','n_snapshots','all_snapshot_checks','evidence_snippet','notes','record_status','permission_class']
V=V.sort_values('capture_ts_utc')
seen={}; dup=[]
for r in V.itertuples():
    key=(r.odds_game_id,r.sportsbook_claimed,r.market,r.home_or_over_record,r.away_or_under_record)
    if key in seen and r.outcome=='authenticated_pre_game': dup.append('repeat snapshot of same book+prices as '+seen[key]+' (counted once)')
    else:
        dup.append('')
        if r.outcome=='authenticated_pre_game': seen.setdefault(key,r.odds_record_ids+' @ '+r.capture_ts_et)
V['dedupe_note']=dup
cols.insert(cols.index('n_snapshots')+1,'dedupe_note')
V=V[cols].sort_values(['season','game_date','odds_game_id','market'],ascending=[False,True,True,True])
V.to_csv('additional_verified_odds.csv',index=False)
print(V.outcome.value_counts()); print('games',V.odds_game_id.nunique(),'new games',V[V.new_game=='yes'].odds_game_id.nunique())
# ---- multi-bookmaker coverage across all authenticated evidence (prior spot-check + new) ----
prior=pd.read_csv('/workspace/wayback_spotcheck_2026-11-10/wayback_2025_odds_spotcheck.csv',dtype=str)
prior=prior[prior.outcome=='authenticated']
auth=V[V.outcome=='authenticated_pre_game']
mgm13=parse_mgm('/tmp/wbfetch/mgm0513.html')
def d2a(x): x=float(x); return round((x-1)*100) if x>=2 else round(-100/(x-1))
def mgm_lines(eid):
    e=mgm13[eid]; s=e['groups'][0]; t=e['groups'][1]; pa,ph=e['participants']
    return (f"{ph} {s[1][0]} {d2a(s[1][1]):+d} / {pa} {s[0][0]} {d2a(s[0][1]):+d}", f"{t[0][0]} {d2a(t[0][1]):+d} / {t[1][0]} {d2a(t[1][1]):+d}")
mb=[]
P13='https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213'
P16='https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88'
for gk,gid,eid,mlh,mla,ids in [('2025-05-18_georgetown_vs_maryland','6448513','17533629','-333','+260','N0284,N0285 (also N0290,N0291 at 05-16 capture)'),('2025-05-18_notre-dame_vs_penn-state','6448512','17533628','+260','-333','N0296,N0297 (also N0302,N0303 at 05-16 capture)')]:
    sp,tot=mgm_lines(eid); dk=auth[auth.odds_game_id==gk]
    dks=dk[dk.market=='spread'].iloc[0]; dkt=dk[dk.market=='total'].iloc[0]
    mb.append(dict(odds_game_id=gk,ncaa_game_id=gid,game_date=gk[:10],home=dks.home,away=dks.away,books_with_authenticated_pre_game_quotes='BetMGM; DraftKings',
      two_book_moneyline='no (DraftKings archive has no moneyline offer)',
      book1='BetMGM',book1_record_ids=ids,book1_moneyline_home_away=f"{mlh} / {mla} (displayed decimal, converted)",book1_spread_on_page=sp,book1_total_on_page=tot,book1_urls=P13+' ; '+P16,book1_capture_et='2025-05-13 11:28:31 EDT; 2025-05-15 22:41:55 EDT',
      book2='DraftKings',book2_record_ids=dks.odds_record_ids+','+dkt.odds_record_ids,book2_moneyline_home_away='not available in archive',book2_spread=f"home {dks.home_or_over_page} / away {dks.away_or_under_page}",book2_total=f"{dkt.home_or_over_page} / {dkt.away_or_under_page}",book2_urls=dks.wayback_url,book2_capture_et=dks.capture_ts_et,
      both_pre_game='yes',time_comparable='partly: BetMGM 2025-05-13 11:28 EDT vs DraftKings 2025-05-13 16:04 EDT (same day, 4h36m apart, both pre-game); still not simultaneous, so book differences are not claimed as meaningful',
      notes=('Spread lines differ (BetMGM 2.5 vs DraftKings 3)' if 'georgetown' in gk else 'Same spread line (2.5), different prices')+'; quotes captured 4.6 h apart, so differences are not claimed as meaningful. BetMGM spread/total values are dataset records verified this round (N0286-N0289 / N0298-N0301 at 05-13; repeats N0292-N0295 / N0304-N0307 at 05-16).'))
sv=auth[auth.odds_game_id=='2023-02-04_syracuse_vs_vermont']
ml=sv[sv.market=='moneyline'].iloc[0]; dks=sv[sv.market=='spread'].iloc[0]; dkt=sv[sv.market=='total'].iloc[0]
mb.append(dict(odds_game_id='2023-02-04_syracuse_vs_vermont',ncaa_game_id=ml.ncaa_game_id,game_date='2023-02-04',home=ml.home,away=ml.away,books_with_authenticated_pre_game_quotes='Caesars (via Action Network article); DraftKings (direct)',
  two_book_moneyline='no (DraftKings archive has no moneyline offer)',book1='Caesars (quoted by Action Network)',book1_record_ids=ml.odds_record_ids,book1_moneyline_home_away=f"{int(ml.home_or_over_page):+d} / {int(ml.away_or_under_page):+d}",
  book1_spread_on_page='Syracuse (-2.5) heading only; no spread price',book1_total_on_page='25.5 (no price)',book1_urls=ml.wayback_url,book1_capture_et=ml.capture_ts_et+' (article published 2023-02-03 21:39 EST)',
  book2='DraftKings',book2_record_ids=dks.odds_record_ids+','+dkt.odds_record_ids,book2_moneyline_home_away='not available in archive',book2_spread=f"home {dks.home_or_over_page} / away {dks.away_or_under_page}",book2_total=f"{dkt.home_or_over_page} / {dkt.away_or_under_page}",book2_urls=dks.wayback_url,book2_capture_et=dks.capture_ts_et,
  both_pre_game='yes',time_comparable='no: DraftKings capture 2023-02-03 13:10 EST vs Action Network capture 2023-02-03 22:47 EST (~9.6 h apart; quote times unknown)',notes='Totals differ (Caesars 25.5 vs DraftKings 26.5) but times differ; not a meaningful book comparison.'))
pd.DataFrame(mb).to_csv('multibookmaker_coverage.csv',index=False)
print(pd.DataFrame(mb)[['odds_game_id','books_with_authenticated_pre_game_quotes','two_book_moneyline']])
