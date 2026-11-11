"""Stage 4 read-only integration checks plus explicitly synthetic failure fixtures."""
from copy import deepcopy
import csv
from pathlib import Path

import pytest

from src.prepare_stage4_games import ROOT, build, score, supported_core, validate, write_csv


@pytest.fixture(scope='module')
def built():
    return build()  # Existing local evidence only, no writes or downloads.


def read(path):
    with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))


def test_full_accounting_and_exact_season_outputs(built):
    candidates,excluded,*_=built
    assert len(candidates)==1707 and len(excluded)==10
    ids={r['game_id'] for r in candidates}; exids={r['game_id'] for r in excluded}
    assert not ids & exids
    assert ids|exids=={r['game_id'] for r in read('reports/grok_stage2_game_assessments.csv')}
    for year,count in [(2023,559),(2024,570),(2025,578)]:
        saved=read(f'data/review/lacrosse_games_{year}_corrected.csv')
        assert len(saved)==count
        assert {r['game_id'] for r in saved}=={r['game_id'] for r in candidates if r['season']==year}
    combined=read('data/review/lacrosse_games_2023_2025_corrected.csv')
    assert [r['game_id'] for r in combined]==[r['game_id'] for r in candidates]
    assert combined==[{k:str(v) for k,v in r.items()} for r in candidates]
    local_ids={r['game_id'] for r in read('data/processed/lacrosse_games_2025.csv')}
    assert {r['local_2025_game_id'] for r in candidates+excluded if r['season']==2025}==local_ids


@pytest.mark.parametrize('gid,expected',[
    ('6449835','2025-04-12'),('6454179','2025-02-16'),
    ('6386400','2025-02-22'),('6138525','2023-03-02'),
    ('6085416','2023-02-05'),('6131581','2023-02-05'),('6139977','2023-03-05')])
def test_supported_dates_and_already_correct_2023_dates(built,gid,expected):
    rows={r['game_id']:r for r in built[0]}
    assert rows[gid]['game_date']==expected


def test_final_result_repair_preserves_original_nulls_and_ids(built):
    row=next(r for r in built[0] if r['game_id']=='6136266')
    assert (row['home_score'],row['away_score'],row['status'])==(16,6,'final')
    assert row['original_home_score']==row['original_away_score']==''
    assert row['original_status']=='pre'
    assert row['home_team_id_ncaa']==row['away_team_id_ncaa']==''


def test_exclusions_keep_canonical_games_and_hartford_scope(built):
    candidates,excluded,*_=built
    ids={r['game_id'] for r in candidates}; ex={r['game_id']:r for r in excluded}
    assert ex['6444405']['retained_canonical_game_id']=='6386334' in ids
    assert ex['6455124']['retained_canonical_game_id']=='6270089' in ids
    assert ex['6455124']['exclusion_code']=='WRONG_SEASON_DUPLICATE'
    outside=[r for r in excluded if r['season']==2023]
    assert len(outside)==8
    assert all('Hartford itself remained D-I' in r['exclusion_reason'] for r in outside)


def test_corroboration_and_permission_are_not_upgraded(built):
    candidates,excluded,*_=built
    assert sum(r['independent_corroboration_status']=='SCHOOL_CORROBORATED_RESULT' for r in candidates)==378
    for r in candidates+excluded:
        assert r['permission_status']=='NOT_CLEARED_NO_CHANGE'
        assert not r['approved_for_modeling']
        assert r['season_completeness']=='NOT_VERIFIED'


def test_dates_only_and_no_inferred_home_advantage(built):
    candidates=built[0]
    assert candidates==sorted(candidates,key=lambda r:(r['game_date'],r['game_id']))
    for r in candidates:
        assert r['day_batch_id']==r['game_date'] and r['modeling_start_time_utc']==''
        assert not r['actual_home_advantage_verified'] and r['neutral_site']==''
    review=next(r for r in candidates if r['game_id']=='6292098')
    assert review['home_away_status']=='NEUTRAL_SITE_NOMINAL_ORIENTATION_REVIEW'


def test_source_linkage_and_missing_espn_ncaa_namespace(built):
    candidates=built[0]
    for r in candidates:
        assert r['original_csv_row']>=2 and len(r['original_csv_sha256'])==64
        assert r['original_source_url'].startswith('https://')
    espn=next(r for r in candidates if r['game_id']=='espn_401658258')
    assert espn['ncaa_game_id']=='' and espn['identifier_namespace']=='ESPN_ONLY_SOURCE_ID'


def test_no_fuzzy_alias_collisions_and_repeat_pairings_retained(built):
    candidates=built[0];checks=built[-1]
    assert checks['team_id_collisions']=={} and checks['team_keys_with_multiple_numeric_ids']=={}
    assert checks['legitimate_repeated_pairings']
    penn=[r for r in candidates if 'Pennsylvania' in [r['original_home_team'],r['original_away_team']]]
    assert penn and all('Penn' in [r['home_team'],r['away_team']] for r in penn)
    assert any(r['home_team']=='Penn State' for r in candidates)


def test_unsupported_synthetic_correction_fails():
    original=dict(game_id='SYNTHETIC',season='2025',game_date='2025-01-01',
                  home_team='Synthetic A',away_team='Synthetic B',home_score='1',away_score='2',status='final')
    changed={**original,'game_date':'2025-01-02'}
    with pytest.raises(ValueError,match='Unsupported change'):
        supported_core(original,changed,{'factual_status':'SCHOOL_CORROBORATED_RESULT'},[])


@pytest.mark.parametrize('bad',['-1','1.5','NaN','Infinity','','not a score',None])
def test_invalid_synthetic_scores_fail(bad):
    with pytest.raises(ValueError):score(bad)


def test_duplicate_or_same_day_collision_fails(built):
    sample=deepcopy(built[0][:1]);row=deepcopy(sample[0])
    with pytest.raises(ValueError,match='Duplicate game ID'):validate(sample+[row],[])
    row['game_id']='SYNTHETIC_SECOND_GAME'
    with pytest.raises(ValueError,match='Duplicate same-day matchup'):
        validate(sorted(sample+[row],key=lambda r:(r['game_date'],r['game_id'])),[])


def test_write_refuses_overwriting_synthetic_fixture(tmp_path):
    path=tmp_path/'synthetic.csv';path.write_text('SYNTHETIC ORIGINAL\n')
    with pytest.raises(FileExistsError):write_csv(path,[{'test':'SYNTHETIC NEW'}])
    assert path.read_text()=='SYNTHETIC ORIGINAL\n'
