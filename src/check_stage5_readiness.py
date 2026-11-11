"""Focused offline Stage 5 identity and design checks; no model fitting/prediction.

Reads the immutable Stage 4 cohort and one saved official schedule. Writes new
report artifacts only, refusing overwrites. Does not fill missing dataset cells.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = Path('data/review/lacrosse_games_2023_2025_corrected.csv')
TARGETS = ('6136266', 'espn_401658258')
FEATURES = ['diff_log1p_prior_games','diff_smoothed_win_rate','diff_avg_goals_for',
            'diff_avg_goals_against','diff_smoothed_last5_win_rate',
            'diff_rest_days_capped21','diff_elo_div400','diff_no_history']


def read_games():
    with (ROOT / DATA).open(newline='') as f:
        return list(csv.DictReader(f))


def assign_split(row):
    return {'2023':'training','2024':'validation','2025':'retrospective_evaluation'}[row['season']]


def earlier_same_season(games, target):
    """Design scheduler only: never computes features, fits or predicts."""
    return [r for r in games if r['season']==target['season'] and r['game_date']<target['game_date']]


def identity_registry(games):
    registry = {}
    reverse = defaultdict(set)
    for r in games:
        for side in ('home','away'):
            key=r[side+'_team_key']
            entry=registry.setdefault(key, {'team_key':key,'names':set(),'original_names':set(),
                                           'numeric_ids':set(),'slugs':set(),'seasons':set(),
                                           'appearances':[]})
            entry['names'].add(r[side+'_team']);entry['original_names'].add(r['original_'+side+'_team'])
            entry['seasons'].add(r['season'])
            numeric=r[side+'_team_id_ncaa'];slug=r[side+'_team_seo']
            if numeric:entry['numeric_ids'].add(numeric);reverse[numeric].add(key)
            if slug:entry['slugs'].add(slug)
            entry['appearances'].append({'game_id':r['game_id'],'date':r['game_date'],'side':side,
                                         'numeric_id':numeric,'source_url':r['original_source_url']})
    if any(len(v['numeric_ids'])!=1 or len(v['names'])!=1 or len(v['slugs'])!=1 for v in registry.values()):
        raise ValueError('Missing or inconsistent team identity mapping')
    if any(len(keys)!=1 for keys in reverse.values()):raise ValueError('Numeric ID collision')
    slug_keys=defaultdict(set)
    for key,v in registry.items():
        for slug in v['slugs']:slug_keys[slug].add(key)
    if any(len(keys)!=1 for keys in slug_keys.values()):raise ValueError('SEO slug collision')
    return {key:{k:sorted(v) if isinstance(v,set) else v for k,v in entry.items()}
            for key,entry in sorted(registry.items())}


def neutral_evidence(html):
    soup=BeautifulSoup(html,'html.parser')
    cards=[c for c in soup.select('.sidearm-schedule-game')
           if all(term in c.get_text(' ',strip=True) for term in ['May 18','Notre Dame','Hempstead','11-16'])]
    if len(cards)!=1:raise ValueError('Missing/ambiguous target schedule card')
    card=cards[0]
    if 'sidearm-schedule-neutral-game' not in card.get('class',[]):
        raise ValueError('No explicit neutral-site marker; vs alone is insufficient')
    return {'card_text':card.get_text(' ',strip=True),'classes':card.get('class'),
            'interpretation':'NEUTRAL_SITE_EXPLAINS_NOMINAL_ORIENTATION; do not swap source sides'}


def check():
    games=read_games();registry=identity_registry(games)
    resolutions=[]
    for row in games:
        if row['game_id'] not in TARGETS:continue
        for side in ('home','away'):
            if row[side+'_team_id_ncaa']:raise ValueError('Expected frozen missing ID changed')
            entry=registry[row[side+'_team_key']]
            support=[a for a in entry['appearances'] if a['numeric_id'] and a['date']<row['game_date']]
            if not support:raise ValueError('No earlier existing identity evidence')
            resolutions.append({'game_id':row['game_id'],'side':side,'team':row[side+'_team'],
                'team_key':row[side+'_team_key'],'proposed_numeric_id':entry['numeric_ids'][0],
                'existing_nonmissing_appearances':sum(bool(a['numeric_id']) for a in entry['appearances']),
                'earlier_support_examples':support[:2],
                'school_identity_evidence':row['school_evidence_files'],
                'scope':'UNIQUE_EXISTING_DATASET_MAPPING_NOT_RETRIEVED_GAME_SPECIFIC_PRIMARY_ID',
                'applied':False})
    school=Path('data/incoming/grok/stage1_28f5677d90c3/audit_package/evidence/games/guhoyas.com_2024_schedule.html')
    raw=(ROOT/school).read_bytes();neutral=neutral_evidence(raw.decode('utf-8'))
    neutral.update(game_id='6292098',evidence_file=str(school),sha256=hashlib.sha256(raw).hexdigest(),
        source_url='https://guhoyas.com/sports/mens-lacrosse/schedule/2024',dataset_changed=False)
    years={year:{r[side+'_team_key'] for r in games if r['season']==year for side in ('home','away')}
           for year in ('2023','2024','2025')}
    cold={}
    for year in years:
        seen=set();anycold=bothcold=0
        for day in sorted({r['game_date'] for r in games if r['season']==year}):
            batch=[r for r in games if r['season']==year and r['game_date']==day]
            for row in batch:
                flags=[row[side+'_team_key'] not in seen for side in ('home','away')]
                anycold+=any(flags);bothcold+=all(flags)
            seen.update(r[side+'_team_key'] for r in batch for side in ('home','away'))
        cold[year]={'any_team_cold':anycold,'both_teams_cold':bothcold}
    checks={'input_sha256':hashlib.sha256((ROOT/DATA).read_bytes()).hexdigest(),
        'games':len(games),'split_counts':dict(Counter(assign_split(r) for r in games)),
        'distinct_teams':len(registry),'teams_by_season':{y:len(v) for y,v in years.items()},
        'newly_observed_2024':sorted(years['2024']-years['2023']),
        'newly_observed_2025':sorted(years['2025']-years['2024']),
        'absent_from_2025_vs_2024':sorted(years['2024']-years['2025']),
        'identity_resolutions':resolutions,'neutral_site_review':neutral,'cold_starts_season_reset':cold,
        'numeric_id_conflicts':0,'slug_conflicts':0,'name_conflicts':0,
        'primary_source_counts':dict(Counter(r['original_result_source'] for r in games)),
        'espn_event_id_present':sum(bool(r['espn_event_id']) for r in games),
        'permission_counts':dict(Counter(r['permission_status'] for r in games)),
        'modeling_approved':False,'models_fit':0,'predictions_generated':0}
    plan={'version':'stage5_plan_v1','input_path':str(DATA),'input_sha256':checks['input_sha256'],
        'approval_status':'NOT_CLEARED_NO_CHANGE','models_run':False,
        'splits':{'train_seasons':[2023],'validation_seasons':[2024],
                  'final_fit_seasons':[2023,2024],'evaluation_seasons':[2025],
                  'evaluation_status':'RETROSPECTIVE_PREVIOUSLY_EXPOSED_NOT_UNTOUCHED_HOLDOUT'},
        'history_rule':'strictly earlier calendar dates within current season',
        'state_updates':'all daily predictions fixed before any same-date update',
        'state_reset':'at each season boundary; ratings=1500; counts=0',
        'logistic_feature_whitelist':FEATURES,'logistic_fit_intercept':False,
        'scaling':'fit training-only standard deviations; no mean centering; constant-column divisor 1',
        'logistic_C_candidates':[0.1,1.0,10.0],'logistic_penalty':'L2',
        'C_selection':'lowest 2024 Brier; differences <= 1e-12 tie -> smallest C',
        'sample_weighting':'one equal-weight row per eligible game; no class weighting or mirrored training rows',
        'models':['constant_0.5','win_rate_alpha1','elo_K20_scale400','logistic_regression'],
        'elo_K':20,'elo_scale':400,'elo_initial':1500,'win_rate_alpha':1,
        'accuracy_rule':'home prediction iff p >= 0.5; report exact tie counts',
        'log_loss_epsilon':1e-15,'calibration_bin_edges':[0,0.2,0.4,0.6,0.8,1.0],
        'primary_metric':'Brier','secondary_metrics':['accuracy','natural_log_loss'],
        'primary_comparison':'logistic minus Elo Brier on identical 2025 IDs',
        'bootstrap':{'replicates':50000,'seed':519,'unit':'whole calendar-date clusters',
                     'pair_models':True,'weight':'mean across resampled games, not equal-weight date means',
                     'sensitivity_unit':'whole ISO calendar weeks','interval':'95% percentile; linear quantiles',
                     'scope':'frozen predictions, no retraining; conditional uncertainty only'},
        'no_odds_or_player_stats':True,'source_cohort_changes_require_new_version_before_training':True}
    return checks,registry,plan


def main():
    checks,registry,plan=check()
    outputs={'reports/stage5_readiness_checks.json':checks,
             'reports/stage5_team_identity_registry.json':registry,
             'reports/stage5_experiment_design.json':plan}
    for name in outputs:
        if (ROOT/name).exists():raise FileExistsError(name)
    for name,value in outputs.items():
        with (ROOT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in checks.items() if k not in ['identity_resolutions','neutral_site_review']},indent=2))


if __name__=='__main__':main()
