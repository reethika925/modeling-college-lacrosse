"""Stage 2: invalid prices, duplicates, manual game resolutions, permission status, outputs, usability.
Run after audit_odds_provenance.py (stage 1)."""
import json,csv,collections,re,sys,datetime as dt
sys.path.insert(0,'/workspace/audit/odds/scripts')
from source_permissions import CLASS,write as write_perm
from audit_odds_provenance_helpers import ct
OUT='/workspace/audit/odds'
R=json.load(open(OUT+'/_recs_stage1.json'))
NG={}
for f in ['ncaa_lacrosse_games_2023.csv','ncaa_lacrosse_games_2024.csv','ncaa_lacrosse_game_index_2025.csv']:
    for g in csv.DictReader(open('/workspace/final_package/'+f)): NG[g['game_id']]=g
def iso(t):
    if not t or t in ('None','null'): return None
    return dt.datetime.fromisoformat(t.replace('Z','+00:00')).astimezone(dt.timezone.utc)
SRC={'dk_snapshot':'draftkings','dk_nash':'draftkings','betmgm':'betmgm','an_article':'actionnetwork','an_archive':'actionnetwork','bol':'betonlacrosse','lsb':'legalsportsbetting','las':'laxallstars'}
corrections=[]
# ---------------- manual game resolutions (documented)
MANUAL={
 '2023-03-04_north-carolina_vs_rutgers':dict(ncaa='6085561',status='resolved_source_label_error',reason='Action Network header reads "North Carolina (-2.5) vs. Denver" and the text says "No. 11 North Carolina facing Denver"; the odds table labels the opponent "Rutgers" (a typo in the source). NCAA 6085561 = Denver @ North Carolina, 2023-03-04. Rutgers played Utah that day (NCAA 6085584).'),
 '2025-02-16_mercyhurst_vs_umass-lowell':dict(ncaa=None,status='candidate_only',reason='BetMGM ld+json start 2025-02-16; the only NCAA meeting found is 6439959 Mercyhurst @ UMass Lowell on 2025-02-14. The date conflict is unresolved, so the game is not matched.'),
 '2025-02-15_binghamton_vs_st.-bonaventure':dict(ncaa=None,status='no_ncaa_record',reason='No Binghamton vs St. Bonaventure game appears in the NCAA 2025 index. The game may have been postponed or cancelled; not verified.'),
}
for r in R:
    m=MANUAL.get(r['game_id'])
    if m:
        r['crosswalk_status']=m['status']; r['game_resolution_note']=m['reason']
        if m['ncaa']:
            r['ncaa_game_id']=m['ncaa']; g=NG[m['ncaa']]; r['ncaa_home'],r['ncaa_away'],r['ncaa_game_date']=g['home_team'],g['away_team'],g['game_date']
            if r['selection_role'] not in ('n/a (total)',):
                s=ct(r['selection']); r['selection_role']='home' if s==ct(g['home_team']) else ('away' if s==ct(g['away_team']) else 'UNMATCHED_TEAM_LABEL'); r['orientation_source']='ncaa_crosswalk (manual resolution)'
    else: r['game_resolution_note']=None
# ---------------- technical problems
for r in R:
    probs=[]; rej=False
    p=r['price']
    if p:
        v=int(p.replace('+',''))
        if -100<v<100: probs.append(f'invalid American price {p} (|price|<100); source printed "{p} (ML N/A)", i.e. a spread value, not a moneyline'); rej=True
    if not r['verified_in_raw'] and not r['implied']:
        probs.append('value NOT found in raw evidence ('+r['detail'][:160]+')'); rej=True
    if r['implied']: probs.append('line not printed in source (implied as negation of the printed favourite line)')
    if r['selection_role']=='UNMATCHED_TEAM_LABEL': probs.append(f'team label "{r["selection"]}" does not match NCAA teams {r.get("ncaa_away")} @ {r.get("ncaa_home")} (source label error)')
    if 'WARNING: pre-game Wayback capture' in r['notes']: probs.append('live-article values differ from pre-game Wayback capture (article edited later); timing not verifiable'); r['grade_audited']='C'; r['grade_reason']+='; live values differ from pre-game capture'
    r['problems']=probs; r['tech_rejected']=rej
# corrections log for wrong values (original file preserved)
SIGN={'O0180':'-1.5','O0191':'-2.5','O0305':'-4.5'}
for r in R:
    if r['record_id'] in SIGN:
        corrections.append(dict(record_id=r['record_id'],field='line',original_value=r['line'],corrected_value=SIGN[r['record_id']],source_url=r['source_url'],evidence_file=r['evidence_file'],reason='Header prints the favourite line with a minus sign; the original parser failed to match the header team name (alias mismatch) and gave the favourite the underdog sign. The original row is rejected; corrected value shown for reference only.'))
    if r['record_id'] in ('O0260','O0261'):
        corrections.append(dict(record_id=r['record_id'],field='market/price',original_value=f"moneyline {r['price']}",corrected_value=f"(spread {r['price']}; moneyline N/A)",source_url=r['source_url'],evidence_file=r['evidence_file'],reason='Source cell reads "Odds -8 (ML N/A)" / "+8 (ML N/A)": no moneyline was published; the value is the spread.'))
    if r['date_vs_ncaa'] and r['date_vs_ncaa'].startswith('DIFFERS'):
        pass
seen=set()
for r in R:
    if r['date_vs_ncaa'] and r['date_vs_ncaa'].startswith('DIFFERS') and r['game_id'] not in seen:
        seen.add(r['game_id'])
        corrections.append(dict(record_id='game:'+r['game_id'],field='game_date',original_value=r['game_id'][:10],corrected_value=r['ncaa_game_date'],source_url=f"https://www.ncaa.com/game/{r['ncaa_game_id']}",evidence_file='final_package/odds_game_to_ncaa_game_crosswalk.csv',
          reason='The listed source date differs from the NCAA game date (likely a postponement or a date the original parser inferred from the publication week). The quote is attached to NCAA game '+str(r['ncaa_game_id'])+'. '+('Two odds game_ids in the original 224 map to this one NCAA game.' if r['game_id'] in ('2023-02-04_hofstra_vs_merrimack','2023-02-04_holy-cross_vs_providence') else '')))
for gid,m in MANUAL.items():
    corrections.append(dict(record_id='game:'+gid,field='ncaa_match',original_value='unmatched',corrected_value=m['ncaa'] or m['status'],source_url=(f"https://www.ncaa.com/game/{m['ncaa']}" if m['ncaa'] else None),evidence_file='final_package NCAA files; raw source',reason=m['reason']))
# ---------------- duplicates (same quote republished across sources) & repeat observations
def fam(r):
    if r['kind'] in ('dk_snapshot','dk_nash','betmgm'): return 'sportsbook_snapshot|'+r['book']
    u=r['source_url'].replace('/lacrosse-lacrosse/','/lacrosse/').rstrip('/')
    return r['kind'].replace('an_archive','an_article')+'|'+u
def obs_time(r): return r['quote_capture_timestamp'] or r['archive_capture_timestamp'] or r['article_published_at'] or ''
GR={'A':0,'B':1,'C':2}
grp=collections.defaultdict(list)
for r in R:
    if r['tech_rejected'] or not r['book']: continue
    gk=r['ncaa_game_id'] or r['game_id']
    grp[(gk,r['book'],r['market'],ct(r['selection']),r['line'],r['price'],r['is_opening'])].append(r)
for r in R: r['duplicate_of']=None; r['also_published_in']=None; r['repeat_observation_of']=None
for k,rs in grp.items():
    fams=collections.defaultdict(list)
    for r in rs: fams[fam(r)].append(r)
    if len(fams)>1:
        reps=[sorted(v,key=lambda r:(GR[r['grade_audited']],obs_time(r)))[0] for v in fams.values()]
        prim=sorted(reps,key=lambda r:(GR[r['grade_audited']],obs_time(r)))[0]
        others=[r for r in reps if r is not prim]
        for o in others: o['duplicate_of']=prim['record_id']
        prim['also_published_in']='; '.join(f"{o['record_id']} ({o['source_url']})" for o in others)
    for v in fams.values():
        v=sorted(v,key=obs_time)
        for o in v[1:]:
            if o['duplicate_of'] is None and obs_time(o)!=obs_time(v[0]): o['repeat_observation_of']=v[0]['record_id']
            elif o['duplicate_of'] is None: o['duplicate_of']=v[0]['record_id']
# ---------------- technical status
for r in R:
    if r['tech_rejected']: ts='rejected'
    elif r['duplicate_of']: ts='rejected'; r['problems'].append(f"duplicate: same quote (book/market/selection/line/price) already recorded as {r['duplicate_of']}")
    elif r['problems'] or r['grade_audited']=='C' or r['crosswalk_status'] in ('unmatched','no_date_in_odds','candidate_only','no_ncaa_record') : ts='provisional'
    else: ts='verified'
    if ts=='provisional' and r['crosswalk_status'] in ('unmatched','no_date_in_odds','candidate_only','no_ncaa_record'): r['problems'].append(f"game not matched to an NCAA game id ({r['crosswalk_status']})")
    if ts=='provisional' and r['grade_audited']=='C' and not any('grade' in p for p in r['problems']): r['problems'].append('grade C: '+r['grade_reason'])
    r['technical_status']=ts
    pc=CLASS[SRC[r['kind']]]
    if r['kind'] in ('dk_snapshot','dk_nash','betmgm','an_archive') or (r['archive_url'] and r['kind'] in ('an_article','bol')): pc_note=f"{SRC[r['kind']]}={pc}; internet_archive={CLASS['internet_archive']}"
    else: pc_note=f"{SRC[r['kind']]}={pc}"
    r['permission_class']=pc; r['permission_note']=pc_note
    r['status']='rejected' if ts=='rejected' else ('requires_permission' if pc!='cleared' else ts)
    r['url_status']=None
LIVE={l.split('\t')[0]:l.rstrip('\n').split('\t')[1:] for l in open(OUT+'/url_status_live.tsv')}
for r in R:
    lv=LIVE.get(r['source_url'],['?',''])
    s=f"live HTTP {lv[0]}"+(f" (redirects to {lv[1]})" if lv[1] and lv[1]!=r['source_url'] else '')
    if r['archive_url']: s+=f"; archive copy saved locally ({r.get('archive_file') or r['evidence_file']})"
    elif r['evidence_file']: s+='; raw copy saved locally'
    r['url_status']=s
    r['url_authentic']= (lv[0]=='200') or bool(r['archive_url'] and r['evidence_file'])
    if not r['url_authentic'] and r['status']!='rejected': r['problems'].append('source URL neither live nor archived'); 
json.dump(R,open(OUT+'/_recs_stage2.json','w'),default=str)
# ---------------- outputs
cols=['record_id','source_dataset','orig_record_id','season','game_id','ncaa_game_id','ncaa_game_date','ncaa_home_team','ncaa_away_team','sportsbook','market','selection','selection_role','orientation_source','line','american_odds',
 'quote_capture_timestamp','article_published_at','article_modified_at','archive_capture_timestamp','start_time_utc_used','start_basis','verified_in_raw','book_supported','url_status','url_authentic','ai_pick_or_projection',
 'duplicate_of','also_published_in','repeat_observation_of','grade_original','grade_audited','grade_reason','line_type','is_opening','is_closing','pre_game_published','independent_capture_pre_game',
 'technical_status','permission_class','status','reason','evidence_file','evidence_detail','source_url','archive_url']
def row(r):
    reason='; '.join(r['problems']) if r['problems'] else ('passes all technical checks; '+r['grade_reason'])
    if r['status']=='requires_permission': reason=f"source permission {r['permission_note']}; "+reason
    if r.get('game_resolution_note'): reason+='; game: '+r['game_resolution_note']
    return dict(record_id=r['record_id'],source_dataset=r['dataset'],orig_record_id=r['orig_record_id'],season=r['season'],game_id=r['game_id'],ncaa_game_id=r['ncaa_game_id'],ncaa_game_date=r.get('ncaa_game_date'),
      ncaa_home_team=r.get('ncaa_home'),ncaa_away_team=r.get('ncaa_away'),sportsbook=r['book'],market=r['market'],selection=r['selection'],selection_role=r['selection_role'],orientation_source=r['orientation_source'],line=r['line'],american_odds=r['price'],
      quote_capture_timestamp=r['quote_capture_timestamp'],article_published_at=r['article_published_at'],article_modified_at=r['article_modified_at'],archive_capture_timestamp=r['archive_capture_timestamp'],
      start_time_utc_used=r['start_utc'],start_basis=r['start_basis'],verified_in_raw=r['verified_in_raw'] if not r['implied'] else 'implied_not_printed',book_supported=r['book_supported'],url_status=r['url_status'],url_authentic=r['url_authentic'],
      ai_pick_or_projection=False,duplicate_of=r['duplicate_of'],also_published_in=r['also_published_in'],repeat_observation_of=r['repeat_observation_of'],grade_original=r['grade_original'],grade_audited=r['grade_audited'],grade_reason=r['grade_reason'],
      line_type=r['line_type'],is_opening=bool(r['is_opening'] and r['verified_in_raw']),is_closing=False,pre_game_published=r['pre_game_published'],independent_capture_pre_game=r['independent_capture_pre_game'],
      technical_status=r['technical_status'],permission_class=r['permission_note'],status=r['status'],reason=reason,evidence_file=(r['evidence_file'] or '').replace('/workspace/',''),evidence_detail=r['detail'][:400],source_url=r['source_url'],archive_url=r['archive_url'])
def W(path,rs):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rs: w.writerow({k:('null' if v in (None,'') else v) for k,v in row(r).items()})
W(OUT+'/odds_provenance_audit.csv',R)
W(OUT+'/odds_cleared_for_analysis.csv',[r for r in R if r['status'] in ('verified','provisional')])
W(OUT+'/odds_quarantine_permission_required.csv',[r for r in R if r['status']=='requires_permission'])
W(OUT+'/odds_rejected.csv',[r for r in R if r['status']=='rejected'])
W(OUT+'/excluded_or_unverified_records.csv',[r for r in R if r['status']=='rejected' or r['technical_status']=='provisional'])
with open(OUT+'/odds_record_corrections.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(corrections[0].keys())); w.writeheader(); w.writerows(corrections)
write_perm(OUT+'/source_permissions_audit.csv')
# ---------------- usability per game
def usab(rs):
    G=collections.defaultdict(list)
    for r in rs: G[r['ncaa_game_id'] or r['game_id']].append(r)
    out=[]
    for g,L in G.items():
        obs=collections.defaultdict(dict)
        for r in L: obs[(r['book'],r['source_url'],obs_time(r),r['market'])].setdefault('sel',[]).append(r)
        def two(mk,need_price=True,need_line=False):
            for (b,u,t,m),d in obs.items():
                if m!=mk or not b: continue
                ss={('O' if r['selection']=='Over' else 'U' if r['selection']=='Under' else r['selection_role'] if r['selection_role'] in ('home','away') else ct(r['selection'])) for r in d['sel'] if (r['price'] or not need_price) and (r['line'] or not need_line)}
                if len(ss)>=2: return True
            return False
        mv=collections.defaultdict(set)
        for r in L:
            if r['book'] and not r['is_opening']: mv[(r['book'],r['market'],ct(r['selection']))].add(obs_time(r))
        x=L[0]
        out.append(dict(game_key=g,ncaa_game_id=x['ncaa_game_id'],odds_game_ids='|'.join(sorted({r['game_id'] for r in L})),season=x['season'],ncaa_game_date=x.get('ncaa_game_date'),ncaa_home_team=x.get('ncaa_home'),ncaa_away_team=x.get('ncaa_away'),
          n_records=len(L),books='|'.join(sorted({r['book'] for r in L if r['book']})),
          two_sided_moneyline=two('moneyline'),spread_both_sides_with_prices=two('spread',True,True),spread_line_only=two('spread',False,True) and not two('spread',True,True),total_with_prices=two('total',True,True),
          multiple_books=len({r['book'] for r in L if r['book']})>=2,movement_2plus_timestamps=any(len(v)>=2 for v in mv.values()),
          pre_game_publication=any(r['pre_game_published'] for r in L),independent_pre_game_capture=any(r['independent_capture_pre_game'] for r in L),
          has_explicit_opening=any(r['is_opening'] and r['verified_in_raw'] for r in L),has_closing=False,
          best_grade=min((r['grade_audited'] for r in L),key=lambda g:GR[g]),statuses='|'.join(sorted({r['status'] for r in L}))))
    return out
valid=[r for r in R if r['technical_status']!='rejected']
verified=[r for r in R if r['technical_status']=='verified']
U=usab(valid); Uv={u['game_key']:u for u in usab(verified)}
for u in U:
    v=Uv.get(u['game_key'])
    for k in ['two_sided_moneyline','spread_both_sides_with_prices','total_with_prices','multiple_books','movement_2plus_timestamps','pre_game_publication','independent_pre_game_capture']:
        u['verified_only_'+k]=v[k] if v else False
    u['verified_records']=v['n_records'] if v else 0
    u['cleared_for_analysis_records']=0
U.sort(key=lambda u:(str(u['season']),str(u['ncaa_game_date']),u['game_key']))
with open(OUT+'/odds_game_usability.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(U[0].keys())); w.writeheader(); w.writerows(U)
# ---------------- same team, same day check
day=collections.defaultdict(set)
for r in valid:
    if r['game_id'].startswith('undated'): continue
    d=r.get('ncaa_game_date') or r['game_id'][:10]
    for t in r['game_id'][11:].split('_vs_'): day[(d,t)].add(r['ncaa_game_id'] or r['game_id'])
sameday=[(k,sorted(v)) for k,v in day.items() if len(v)>1]
# ---------------- original 224 games check
orig_games=collections.defaultdict(set)
for r in R:
    if r['dataset']=='original': orig_games[r['orig_game_id']].add(r['ncaa_game_id'])
ncaa_map={g:list(v)[0] for g,v in orig_games.items()}
inv=collections.defaultdict(list)
for g,n in ncaa_map.items(): inv[n].append(g)
M=dict(
 total=len(R),by_status=dict(collections.Counter(r['status'] for r in R)),by_technical_status=dict(collections.Counter(r['technical_status'] for r in R)),
 by_dataset_technical=dict(collections.Counter(f"{r['dataset']}:{r['technical_status']}" for r in R)),by_dataset_status=dict(collections.Counter(f"{r['dataset']}:{r['status']}" for r in R)),
 grades_original_vs_audited=dict(collections.Counter(f"{r['grade_original']}->{r['grade_audited']}" for r in R)),
 rejected_reasons=dict(collections.Counter(('duplicate' if r['duplicate_of'] else ('invalid price' if any('invalid American' in p for p in r['problems']) else 'value not in raw')) for r in R if r['technical_status']=='rejected')),
 provisional_reasons=dict(collections.Counter(p.split(' (')[0].split(':')[0][:70] for r in R if r['technical_status']=='provisional' for p in r['problems'])),
 verified_in_raw=dict(collections.Counter(str(r['verified_in_raw'] if not r['implied'] else 'implied') for r in R)),
 book_supported=dict(collections.Counter(str(r['book_supported']) for r in R)),url_authentic=dict(collections.Counter(str(r['url_authentic']) for r in R)),
 repeat_observations=sum(1 for r in R if r['repeat_observation_of']),duplicates=sum(1 for r in R if r['duplicate_of']),
 original_224_check=dict(odds_game_ids=len(orig_games),distinct_ncaa_games=len({n for n in ncaa_map.values() if n}),unmatched=[g for g,n in ncaa_map.items() if not n],
   many_to_one=[ (n,v) for n,v in inv.items() if n and len(v)>1]),
 same_team_same_day=sameday,
)
def counts(rs,label):
    G=collections.defaultdict(list)
    for r in rs: G[r['ncaa_game_id'] or r['game_id']].append(r)
    return dict(records=len(rs),games=len(G),records_by_season=dict(sorted(collections.Counter(str(r['season']) for r in rs).items())),games_by_season=dict(sorted(collections.Counter(str(L[0]['season']) for L in G.values()).items())))
M['valid_non_rejected']=counts(valid,'valid'); M['technically_verified']=counts(verified,'verified'); M['provisional']=counts([r for r in R if r['technical_status']=='provisional'],'p')
M['original_only_verified']=counts([r for r in verified if r['dataset']=='original'],''); M['original_only_valid']=counts([r for r in valid if r['dataset']=='original'],'')
M['cleared_for_analysis']=counts([r for r in R if r['status'] in ('verified','provisional')],'c')
for nm_,UU in (('usability_valid',U),('usability_verified',list(Uv.values()))):
    M[nm_]={k:sum(1 for u in UU if u[k]) for k in ['two_sided_moneyline','spread_both_sides_with_prices','total_with_prices','multiple_books','movement_2plus_timestamps','pre_game_publication','independent_pre_game_capture','has_explicit_opening','has_closing']}
    M[nm_]['games']=len(UU)
json.dump(M,open(OUT+'/odds_audit_metrics.json','w'),indent=1,default=str)
print(json.dumps(M,indent=1,default=str)[:6000])
