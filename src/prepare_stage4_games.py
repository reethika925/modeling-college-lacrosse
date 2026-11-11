"""Offline Stage 4 derivation. Run from the repository root with python -m src.prepare_stage4_games.

Only independently supported result changes are applied. Source files are read-only;
all outputs use exclusive creation. No network, supplier scripts, odds or modeling.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.audit_grok_games_stats import canonical_id, canonical_team

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path('data/incoming/grok/stage1_28f5677d90c3/audit_package')
SUPPLEMENT = Path('data/incoming/grok/ncaa_lacrosse_cse519_supplement_2026-11-10.zip')
ZIP_ROOT = 'supplement_2026-11-10/'
EXCLUSIONS = {
    '6444405': ('DUPLICATE_RESULT', '6386334', 'Extra Hampton–Fairfield listing; retain the March 15, 2025 game.'),
    '6455124': ('WRONG_SEASON_DUPLICATE', '6270089', 'LIU–Quinnipiac is the April 20, 2024 game already retained; not a verified 2025 exhibition.'),
}
LOWER_DIVISION = {'6085550':'Mitchell', '6085551':'St. Andrews', '6085599':'Wabash',
                  '6085638':'Randolph', '6085705':'Saint Joseph (CT)', '6085730':'Gordon',
                  '6085770':'Salem St.', '6085858':'Regis (MA)'}
CORE = ['season','game_date','home_team','away_team','home_score','away_score','status']
DISPLAY = {'penn':'Penn', 'pennst':'Penn State', 'ohiost':'Ohio State',
           'clevelandst':'Cleveland State', 'bostonu':'Boston University', 'umass':'Massachusetts'}


def rows(path):
    with (ROOT / path).open(newline='') as f:
        return list(csv.DictReader(f))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def score(value):
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Missing or invalid final score') from exc
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError('Missing or invalid final score')
    return int(number)


def supported_core(original, audited, assessment, proposals):
    """Refuse any changed result field without the reviewed Stage 2 support."""
    corrected = {k: original[k] for k in CORE}
    changes = []
    for field in CORE:
        old, new = original[field], audited[field]
        if old == new:
            continue
        supports = [p for p in proposals if p['field'] == field
                    and p['action'] == 'CONFIRM_ALREADY_APPLIED_IN_IMPORT'
                    and p['factual_support'] == 'OFFICIAL_SCHEDULE'
                    and p['proposed_value'] == new]
        if not supports or assessment['factual_status'] != 'SCHOOL_CORROBORATED_RESULT':
            raise ValueError(f"Unsupported change {original['game_id']} {field}: {old!r} -> {new!r}")
        corrected[field] = new
        changes.append({'game_id': original['game_id'], 'field': field,
                        'before': old, 'after': new, 'basis':'STAGE2_INDEPENDENT_OFFICIAL_SCHEDULE',
                        'evidence_urls': ';'.join(sorted({p['evidence'] for p in supports}))})
    return corrected, changes


def load_originals():
    """Read only three named CSV members; never extract or execute ZIP contents."""
    sources, manifest = {}, []
    with zipfile.ZipFile(ROOT / SUPPLEMENT) as archive:
        claims = {r['path']:r for r in csv.DictReader(io.StringIO(
            archive.read(ZIP_ROOT+'MANIFEST.csv').decode('utf-8')))}
        for year in (2023, 2024, 2025):
            stem = f'ncaa_lacrosse_games_{year}' if year != 2025 else 'ncaa_lacrosse_game_index_2025'
            relative = f'priority1_originals/recovered_originals/{stem}.csv'
            member = ZIP_ROOT + relative
            matches = [info for info in archive.infolist() if info.filename == member]
            if len(matches) != 1 or matches[0].file_size > 5_000_000:
                raise ValueError('Ambiguous or excessive original CSV member')
            data = archive.read(member)  # ZIP library verifies this member's CRC.
            claim = claims[relative]
            if digest(data) != claim['sha256'] or len(data) != int(claim['bytes']):
                raise ValueError('Recovered original manifest mismatch')
            parsed = list(csv.DictReader(io.StringIO(data.decode('utf-8'))))
            if len(parsed) != int(claim['rows']):
                raise ValueError('Recovered original row-count mismatch')
            ids = [r['game_id'] for r in parsed]
            if len(ids) != len(set(ids)):
                raise ValueError('Duplicate original identifiers')
            sources[year] = (parsed, member, digest(data), stem)
            manifest.append({'path':str(SUPPLEMENT)+'::'+member, 'sha256':digest(data),
                             'bytes':len(data), 'rows':len(parsed), 'supplied_manifest_match':True,
                             'authenticity':'RECOVERED_INTERMEDIATE_NOT_PRIMARY_PAYLOAD'})
    return sources, manifest


def build():
    assessments = {r['game_id']:r for r in rows('reports/grok_stage2_game_assessments.csv')}
    proposals = defaultdict(list)
    for p in rows('reports/grok_stage2_proposed_corrections.csv'):
        if p['dataset'].startswith(str(PACKAGE)+'/corrected/'):
            proposals[p['game_id']].append(p)
    schedules = defaultdict(list)
    for r in rows('reports/grok_stage2_schedule_comparison.csv'):
        if r['game_id'] and r['date_agrees']=='True' and r['score_agrees']=='True':
            schedules[r['game_id']].append(r)
    raw = {r['game_id']:r for r in rows('reports/grok_stage2_local_raw_evidence.csv')}
    local = {}
    for i,r in enumerate(rows('data/processed/lacrosse_games_2025.csv'),2):
        gid=r['game_page_url'].rstrip('/').split('/')[-1]
        if gid in local:raise ValueError('Ambiguous local NCAA URL identifier')
        local[gid]=(r,i)
    evidence_log=json.loads((ROOT/'reports/grok_stage2_official_checks.json').read_text())
    official={f['game_id']:f for f in evidence_log['findings'] if 'game_id' in f}
    permission_claims={r['source_key']:r['classification'] for r in rows(PACKAGE/'source_permissions_audit.csv')
                       if r['source_key'] in ['ncaa','ncaa_sdataprod','espn','espn_games_validation','sidearm','sidearm_games_audit']}
    originals, input_manifest=load_originals()
    names=defaultdict(set)
    for original,_,_,_ in originals.values():
        for r in original:
            for side in ['home','away']:names[canonical_team(r[side+'_team'])].add(r[side+'_team'])
    displays={key:DISPLAY.get(key,sorted(values)[0]) for key,values in names.items()}
    aliases=[dict(source_team=name,team_key=key,standardized_team=displays[key],
                  basis='EXISTING_STAGE2_CLOSED_ALIASES; display expansion only')
             for key,values in sorted(names.items()) for name in sorted(values)]
    allrows, changes, supplier_differences=[],[],[]
    for year,(originals_year,member,member_hash,stem) in originals.items():
        audited_path=PACKAGE/'corrected'/f'{stem}_corrected.csv'
        audited_rows=rows(audited_path); audited={r['game_id']:(r,i) for i,r in enumerate(audited_rows,2)}
        if set(audited)!={r['game_id'] for r in originals_year}:raise ValueError('Original/audited ID sets differ')
        for ordinal,original in enumerate(originals_year,2):
            gid=original['game_id'];a,arow=audited[gid];assessment=assessments[gid]
            if assessment['_source_row']!=str(arow):raise ValueError('Stage 2 row reference mismatch')
            for k in ['season','game_date','home_team','away_team','home_score','away_score']:
                if a[k]!=assessment[k]:raise ValueError('Audited fields disagree with Stage 2 assessment')
            core, applied=supported_core(original,a,assessment,proposals[gid]);changes.extend(applied)
            for field,value in original.items():
                if value!=a[field]:
                    numeric_id = field.endswith('_id') or field.endswith('_id_ncaa')
                    disposition='SUPPORTED_RESULT_CHANGE' if field in CORE else 'PRESERVE_ORIGINAL_METADATA_NOT_ADOPTED'
                    if numeric_id and canonical_id(value)==canonical_id(a[field]):disposition='EQUIVALENT_IDENTIFIER_SERIALIZATION'
                    supplier_differences.append(dict(game_id=gid,field=field,before=value,imported_value=a[field],stage4_disposition=disposition))
            refs=schedules[gid]
            if assessment['factual_status']=='SCHOOL_CORROBORATED_RESULT' and not refs:
                raise ValueError('School corroboration lacks existing comparison rows')
            evfiles={r['evidence_file'] for r in refs}
            if any(not (ROOT/p).is_file() for p in evfiles):raise ValueError('Missing cited school evidence')
            urls={r['source_url'] for r in refs}
            if gid in official:urls.update(evidence_log['urls'][key] for key in official[gid]['evidence'])
            exclusion, canonical, reason = EXCLUSIONS.get(gid,('','',''))
            if gid in LOWER_DIVISION:
                exclusion='OUTSIDE_STRICT_DI_VS_DI_SCOPE'
                reason=f'Opponent {LOWER_DIVISION[gid]} is outside D-I. Hartford itself remained D-I in spring 2023; no claim this result is fictional.'
            eligible=not exclusion
            if eligible != (assessment['proposed_d1_eligible']=='True'):raise ValueError('Unexpected Stage 2 exclusion')
            lr,lrow=local.get(gid,({},''))
            if lr:
                for side in ['home','away']:
                    if score(lr[side+'_score'])!=score(core[side+'_score']) or canonical_team(lr[side+'_team'])!=canonical_team(core[side+'_team']):
                        raise ValueError('Local 2025 score/orientation conflict')
            home_key,away_key=canonical_team(core['home_team']),canonical_team(core['away_team'])
            orientation='SOURCE_NOMINAL_UNCORROBORATED'
            if refs:orientation='SCHOOL_NOMINAL_ORIENTATION_CONFIRMED'
            if any(r['orientation_status']=='CONFLICT' for r in refs):orientation='NEUTRAL_SITE_NOMINAL_ORIENTATION_REVIEW'
            ri=raw.get(gid,{})
            record={
                'game_id':gid, 'original_game_id':original['game_id'],
                'ncaa_game_id':gid if gid.isdecimal() else '',
                'identifier_namespace':'NCAA_GAME_PAGE' if gid.isdecimal() else 'ESPN_ONLY_SOURCE_ID',
                'ncaa_legacy_game_id':canonical_id(original.get('ncaa_legacy_game_id','')),
                'local_2025_game_id':lr.get('game_id',''), 'espn_event_id':canonical_id(original.get('espn_event_id','')),
                'season':int(core['season']), 'game_date':core['game_date'],
                'original_game_date':original['game_date'], 'imported_game_date':a['game_date'],
                'local_2025_game_date':lr.get('game_date',''),
                'home_team':displays[home_key], 'away_team':displays[away_key],
                'home_team_key':home_key,'away_team_key':away_key,
                'original_home_team':original['home_team'],'original_away_team':original['away_team'],
                'home_team_id_ncaa':canonical_id(original['home_team_id_ncaa']),
                'away_team_id_ncaa':canonical_id(original['away_team_id_ncaa']),
                'home_team_seo':original['home_team_seo'],'away_team_seo':original['away_team_seo'],
                'home_score':score(core['home_score']),'away_score':score(core['away_score']),
                'status':core['status'], 'winner':displays[home_key] if score(core['home_score'])>score(core['away_score']) else displays[away_key],
                'original_home_score':original['home_score'],'original_away_score':original['away_score'],
                'original_status':original['status'], 'original_source_url':original['source_url'],
                'original_result_source':original['result_source'],
                'result_basis':'SCHOOL_SUPPORTED_CORRECTION' if applied else 'ORIGINAL_RESULT_RETAINED',
                'original_raw_scoreboard_url':original.get('raw_scoreboard_url',''),
                'local_2025_source_url':lr.get('source_url',''),
                'original_csv':str(SUPPLEMENT)+'::'+member,'original_csv_sha256':member_hash,'original_csv_row':ordinal,
                'imported_csv':str(audited_path),'imported_csv_row':arow,'local_2025_csv_row':lrow,
                'correction_applied':bool(applied),'correction_fields':';'.join(c['field'] for c in applied),
                'correction_reason':'Independently supported Stage 2 school evidence' if applied else '',
                'correction_details_json':json_text(applied),
                'candidate_eligible':eligible,'exclusion_code':exclusion,'exclusion_reason':reason,'retained_canonical_game_id':canonical,
                'independent_corroboration_status':assessment['factual_status'],
                'school_evidence_urls':';'.join(sorted(urls)),'school_evidence_files':';'.join(sorted(evfiles)),
                'raw_ncaa_evidence_files':ri.get('evidence_files',''),
                'raw_ncaa_score_match':ri.get('score_matches_raw',''), 'raw_ncaa_date_match':ri.get('date_matches_any_raw',''),
                'original_artifact_status':'RECOVERED_INTERMEDIATE_MANIFEST_MATCH; not primary-source authentication',
                'permission_status':assessment['permission_status'],'approved_for_modeling':False,
                'supplier_permissions_json':json_text(permission_claims),
                'permission_basis_file':str(PACKAGE/'source_permissions_audit.csv'),
                'season_completeness':'NOT_VERIFIED','division_membership_status':'STAGE2_SCOPE_SCREEN_NOT_COMPLETE_MEMBERSHIP_CERTIFICATION',
                'home_away_status':orientation,'actual_home_advantage_verified':False,
                'original_start_time_utc':original.get('start_time_utc',''),
                'original_start_time_is_tba':original.get('start_time_is_tba',''),
                'imported_start_time_utc_claim':a.get('start_time_utc',''),
                'modeling_start_time_utc':'','time_reliability':'DATE_ONLY_SAME_DAY_BATCH_REQUIRED',
                'day_batch_id':core['game_date'],
                'source_neutral_site':original.get('neutral_site',''),
                'imported_neutral_site_claim':a.get('neutral_site',''),
                'neutral_site':'','neutral_site_status':'NOT_INDEPENDENTLY_CERTIFIED_FOR_FEATURE_USE',
                'original_row_json':json_text(original),
                'supplier_audit_status':a.get('audit_status',''),'supplier_audit_basis':a.get('audit_basis',''),
            }
            allrows.append(record)
    if set(assessments)!={r['game_id'] for r in allrows}:raise ValueError('Incomplete row accounting')
    allrows.sort(key=lambda r:(r['game_date'],r['game_id']))
    candidates=[r for r in allrows if r['candidate_eligible']]
    excluded=[r for r in allrows if not r['candidate_eligible']]
    checks=validate(candidates,excluded)
    checks['original_member_checks']=input_manifest
    checks['supplier_difference_dispositions']=dict(Counter(r['stage4_disposition'] for r in supplier_differences))
    checks['corrected_result_fields']=len(changes)
    checks['corrected_game_ids']=sorted({r['game_id'] for r in changes})
    return candidates,excluded,changes,aliases,supplier_differences,checks


def validate(candidates, excluded):
    allrows=candidates+excluded
    if len({r['game_id'] for r in allrows})!=len(allrows):raise ValueError('Duplicate game ID')
    if candidates!=sorted(candidates,key=lambda r:(r['game_date'],r['game_id'])):raise ValueError('Unsorted games')
    matches=set();appearances=set();idteams=defaultdict(set);teamids=defaultdict(set);repeats=defaultdict(list)
    for r in candidates:
        if date.fromisoformat(r['game_date']).year!=r['season']:raise ValueError('Season/date conflict')
        if r['status']!='final' or score(r['home_score'])==score(r['away_score']):raise ValueError('Nonfinal/tied game')
        if r['home_team_key']==r['away_team_key']:raise ValueError('Same team on both sides')
        key=(r['game_date'],*sorted([r['home_team_key'],r['away_team_key']]))
        if key in matches:raise ValueError('Duplicate same-day matchup')
        matches.add(key);repeats[(r['season'],*key[1:])].append(r['game_id'])
        for side in ['home','away']:
            teamkey=r[side+'_team_key'];appearance=(r['game_date'],teamkey)
            if appearance in appearances:raise ValueError('Team appears twice on same date')
            appearances.add(appearance)
            if r[side+'_team_id_ncaa']:
                idteams[r[side+'_team_id_ncaa']].add(teamkey);teamids[teamkey].add(r[side+'_team_id_ncaa'])
        if r['permission_status']!='NOT_CLEARED_NO_CHANGE' or r['approved_for_modeling']:
            raise ValueError('Unexpected permissions clearance')
        if r['modeling_start_time_utc'] or r['day_batch_id']!=r['game_date']:raise ValueError('Unsafe temporal key')
    idconflicts={k:sorted(v) for k,v in idteams.items() if len(v)>1}
    if idconflicts:raise ValueError(f'Team ID collision: {idconflicts}')
    coverage=[]
    for season in (2023,2024,2025):
        rs=[r for r in candidates if r['season']==season];ex=[r for r in excluded if r['season']==season]
        coverage.append(dict(season=season,source_rows=len(rs)+len(ex),candidate_games=len(rs),excluded_games=len(ex),
            school_corroborated=sum(r['independent_corroboration_status']=='SCHOOL_CORROBORATED_RESULT' for r in rs),
            first_date=min(r['game_date'] for r in rs),last_date=max(r['game_date'] for r in rs),
            distinct_dates=len({r['game_date'] for r in rs}),
            unique_teams=len({r[side+'_team_key'] for r in rs for side in ['home','away']})))
    return dict(coverage=coverage,total_candidates=len(candidates),total_excluded=len(excluded),
        all_source_records_accounted_for=len(allrows),missing_dates=0,duplicate_game_ids=0,
        duplicate_same_day_matchups=0,same_day_repeated_team_appearances=0,
        invalid_or_missing_final_scores=0,team_id_collisions=idconflicts,
        team_keys_with_multiple_numeric_ids={k:sorted(v) for k,v in teamids.items() if len(v)>1},
        legitimate_repeated_pairings=[{'season':k[0],'team1':k[1],'team2':k[2],'game_ids':v} for k,v in repeats.items() if len(v)>1],
        missing_numeric_team_id_games=[r['game_id'] for r in candidates if not r['home_team_id_ncaa'] or not r['away_team_id_ncaa']],
        orientation_review_games=[r['game_id'] for r in candidates if r['home_away_status']=='NEUTRAL_SITE_NOMINAL_ORIENTATION_REVIEW'],
        source_tba_counts={str(y):sum(r['season']==y and r['original_start_time_is_tba']=='True' for r in candidates) for y in (2023,2024,2025)},
        full_row_duplicates=0,approved_for_modeling=0)


def write_csv(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)


def main():
    candidates,excluded,changes,aliases,diffs,checks=build()
    outputs={Path('data/review/lacrosse_games_2023_2025_corrected.csv'):candidates,
             Path('reports/stage4_game_exclusions.csv'):excluded,
             Path('reports/stage4_game_field_changes.csv'):changes,
             Path('reports/stage4_team_aliases.csv'):aliases,
             Path('reports/stage4_supplier_field_differences.csv'):diffs}
    for year in (2023,2024,2025):
        outputs[Path(f'data/review/lacrosse_games_{year}_corrected.csv')]=[r for r in candidates if r['season']==year]
    checkpath=ROOT/'reports/stage4_validation_checks.json'
    for p in [*(ROOT/p for p in outputs),checkpath]:
        if p.exists():raise FileExistsError(f'Refusing overwrite: {p}')
    for path,data in outputs.items():write_csv(ROOT/path,data)
    checks['outputs']={str(p):{'rows':len(rs),'sha256':digest((ROOT/p).read_bytes())} for p,rs in outputs.items()}
    with checkpath.open('x') as f:json.dump(checks,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in checks.items() if k not in ['legitimate_repeated_pairings','outputs']},indent=2))


if __name__=='__main__':main()
