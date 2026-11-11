import pandas as pd,re,glob
M=pd.read_csv('/workspace/supplement_2026-11-10/priority2_odds_evidence/odds_evidence_to_record_map.csv')
V=pd.read_csv('additional_verified_odds.csv',dtype=str)
P=pd.read_csv('/workspace/wayback_spotcheck_2026-11-10/wayback_2025_odds_spotcheck.csv',dtype=str)
checked=set(','.join(V.odds_record_ids).split(','))|set(','.join(P.odds_record_ids).split(','))
rows=[]
def add(cat,recs,reason,urls='',games=None):
    recs=recs[~recs.record_id.isin(checked)] if isinstance(recs,pd.DataFrame) else recs
    if isinstance(recs,pd.DataFrame):
        if not len(recs): return
        rows.append(dict(category=cat,n_records=len(recs),n_games=recs.game_id.nunique(),seasons=','.join(map(str,sorted(recs.season.unique()))),
            publishers=','.join(sorted(recs.evidence_publisher.unique())),record_ids=';'.join(recs.record_id),reason=reason,urls=urls))
    else:
        rows.append(dict(category=cat,n_records=0,n_games=games or '',seasons='',publishers='',record_ids='',reason=reason,urls=urls))
# outcomes needing attention from this round
for o in ['mismatch','price_match_post_game','price_match_timing_unknown']:
    for r in V[V.outcome==o].itertuples():
        rows.append(dict(category=f'checked_this_round:{o}',n_records=len(r.odds_record_ids.split(',')),n_games=1,seasons=r.season,publishers=r.evidence_publisher,record_ids=r.odds_record_ids.replace(',',';'),
            reason=f"{r.odds_game_id} {r.market}: {r.mismatch_reason or ''} timing={r.timing_result}; official start {r.official_start_source}. {r.notes[:300]}",urls=r.wayback_url))
for ids,why in [('O1025;O1026','Colgate-Penn State: direct BetMGM archive 2025-01-21 shows Penn State 1.22 (-455) / Colgate 4.25 (+325) vs record -550/+400 quoted by Bet On Lacrosse 2025-02-01; different times, so neither authenticates nor contradicts the record. The only capture showing the record values is the 2026-03-08 Bet On Lacrosse capture (post-game).'),
                ('O1043;O1044','Ohio State-Utah: direct BetMGM archive 2025-01-21 shows Ohio State 1.29 (-345) / Utah 3.50 (+250) vs record -400/+310 (Bet On Lacrosse, 2025-02-01); different times; record only seen in a post-game 2026 capture.')]:
    rows.append(dict(category='different_time_price_not_authenticated',n_records=2,n_games=1,seasons='2025',publishers='Bet On Lacrosse (live) vs BetMGM (via Internet Archive)',record_ids=ids,reason=why,urls='https://web.archive.org/web/20250121025539/https://sports.betmgm.com/en/sports/lacrosse-88 ; https://web.archive.org/web/20260308175741/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-0-bets/'))
add('stale_capture_post_game',M[M.archive_url.fillna('').str.contains('20250216180923')],"Only archive is the 2025-02-16 18:09Z BetMGM capture, which post-dates every game listed (page text implies a cached 2025-02-14 render). Not authenticated by rule; not re-fetched this round.",'https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213')
bol=M[M.evidence_publisher=='Bet On Lacrosse (live)']
add('no_pre_game_archive:Bet On Lacrosse',bol,"Wayback CDX (queried 2026-11-10 for every inventory article URL) shows only captures after the games (2025-04-19 crawl for weeks 5-10, 2025-11/2025-12 and 2026 crawls for the rest); 2025-03-01 week-4 Saturday capture already used. Evidence = live page + withheld saved copy only.",'see cdx_query_log.csv')
las=M[M.evidence_publisher.str.startswith('Lacrosse All')]
add('no_pre_game_archive:Lacrosse All Stars',las,"CDX (all years) shows no captures, or only 2026 captures, for the 7 inventory articles (2023/2024 games).",'see cdx_query_log.csv')
add('no_pre_game_archive:LegalSportsBetting',M[M.evidence_publisher.str.startswith('LegalSports')],"Only CDX capture is 2026-05-13, after the April 2026 game.",'see cdx_query_log.csv')
an_live=M[(M.evidence_publisher=='Action Network (live)')&M.archive_url.isna()]
add('no_archive_examined:Action Network (live)',an_live,"No archive_url in the evidence map. Spot CDX checks for the 4 articles covering 2024-02-23/24 and 2024-05-25 games (multi-book candidates) found only post-game captures (2024-05-22 onward). Other AN articles not queried (beyond sample cap).",'see cdx_query_log.csv')
an_wb=M[M.archive_url.fillna('').str.contains('actionnetwork')]
add('not_examined_cap:Action Network Wayback',an_wb,"Wayback-linked AN article captures not examined this round (30-game cap reached): 2023-04-08, 05-20 x2, 05-21, 05-26 x2, 05-29 and 2024-02-17, 2024-03-09 captures.")
add('not_examined:DraftKings 2026',M[(M.season==2026)&M.evidence_publisher.str.startswith('DraftKings')],"2026 DraftKings Wayback API captures not examined: no 2026 NCAA results/scoreboards exist on the box to confirm the game or official start, and collecting them would be new result collection.")
add('not_examined:DraftKings 2023 spread/total',M[(M.season==2023)&M.evidence_publisher.str.startswith('DraftKings')],"2023 DraftKings spread/total Wayback records other than the 3 games checked (2023-02-03 capture) not examined (no moneylines; cap).")
add('not_examined:BetMGM 2024 spread/total',M[(M.season==2024)&M.evidence_publisher.str.startswith('BetMGM')],"2024 BetMGM spread/total records (and the 3 games with no moneyline offer: Duke-Jacksonville, Army-Mercer, Richmond-St. John's) not examined; moneylines prioritised.")
add('not_examined:BetMGM 2023',M[(M.season==2023)&M.evidence_publisher.str.startswith('BetMGM')],"Not examined (cap).")
rest=M[~M.record_id.isin(checked)&~M.record_id.isin(';'.join(r['record_ids'] for r in rows).split(';'))]
add('other_unchecked',rest,"Remaining records not covered by any category above (live-only or non-archived evidence).")
for u,ts,why in [('https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse','20250404065042','New CDX capture of an inventory URL; fetched: page contains no lacrosse events or odds (not_visible).'),
                 ('https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse','20250425111524','New CDX capture of an inventory URL; fetched: page contains no lacrosse events or odds (not_visible).')]:
    rows.append(dict(category='new_capture_not_visible',n_records=0,n_games='',seasons='2025',publishers='DraftKings',record_ids='',reason=why,urls=f'https://web.archive.org/web/{ts}/{u}'))
rows.append(dict(category='archive_prices_not_in_dataset',n_records=0,n_games=6,seasons='2025',publishers='BetMGM',record_ids='',
  reason="Pre-game BetMGM capture 2025-01-21 shows two-sided moneylines for 9 Feb-1 2025 games; 3 match dataset records (above) and 6 have no BetMGM record (Richmond @ Maryland, Bellarmine @ Duke, Jacksonville @ Syracuse, Johns Hopkins @ Denver, Loyola Maryland @ Georgetown, Marquette @ Michigan). Not added to the dataset (no new collection); available for a future, authorised extension.",urls='https://web.archive.org/web/20250121025539/https://sports.betmgm.com/en/sports/lacrosse-88'))
rows.append(dict(category='out_of_scope_variant_urls',n_records=0,n_games='',seasons='2025',publishers='BetMGM',record_ids='',reason="CDX lists 2025 captures of BetMGM URL variants not in our inventory (e.g. /en/sports/lacrosse-88/betting/usa-9 on 2025-02-13, /es-xl/.../ncaa-79213 on 2025-04-26). Not examined: outside the inventory-only rule.",urls=''))
rows.append(dict(category='no_genuine_quote_timestamps',n_records=int(M.original_quote_timestamp_utc.notna().sum()),n_games='',seasons='2023-2026',publishers='DraftKings/BetMGM via Internet Archive',record_ids='',reason="All 544 non-null original_quote_timestamp_utc values equal archive_capture_timestamp_utc (mislabelled: capture time, not quote time). The other 1,451 records have no quote timestamp. Net: 0 records with a genuine sportsbook quote time.",urls=''))
U=pd.DataFrame(rows); U.to_csv('unresolved_odds_evidence.csv',index=False)
print(U[['category','n_records','n_games']].to_string()); print('total listed records',U.n_records.sum())
