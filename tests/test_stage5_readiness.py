"""Focused design tests. Synthetic mutations remain in memory, never research data.

These check identity, scheduling and the frozen experiment contract, not a trained
model or a future feature-builder implementation.
"""
from copy import deepcopy
import json

import pytest
from src.check_stage5_readiness import (ROOT, FEATURES, assign_split, check,
                                       earlier_same_season, identity_registry, neutral_evidence, read_games)


@pytest.fixture(scope='module')
def reviewed():return check()


def test_split_and_identity_counts(reviewed):
    c,registry,_=reviewed
    assert c['games']==1707 and len(registry)==78
    assert c['split_counts']=={'training':559,'validation':570,'retrospective_evaluation':578}
    assert c['teams_by_season']=={'2023':75,'2024':76,'2025':77}
    assert registry['penn']['numeric_ids']!=registry['pennst']['numeric_ids']


@pytest.mark.parametrize('key,expected',[('umbc','43922'),('mountstmarys','43793'),
                                       ('princeton','43731'),('penn','43935')])
def test_missing_ids_supported_by_existing_earlier_rows(reviewed,key,expected):
    c,_,_=reviewed
    r=next(r for r in c['identity_resolutions'] if r['team_key']==key)
    assert r['proposed_numeric_id']==expected and not r['applied']
    assert r['earlier_support_examples']
    assert all(x['numeric_id']==expected for x in r['earlier_support_examples'])


def test_missing_dataset_cells_and_espn_namespace_stay_unchanged():
    targets=[r for r in read_games() if r['game_id'] in ['6136266','espn_401658258']]
    assert len(targets)==2
    assert all(r['home_team_id_ncaa']==r['away_team_id_ncaa']=='' for r in targets)
    assert next(r for r in targets if r['game_id'].startswith('espn_'))['ncaa_game_id']==''


def test_neutral_evidence_is_explicit_not_just_vs(reviewed):
    c,_,_=reviewed
    assert 'sidearm-schedule-neutral-game' in c['neutral_site_review']['classes']
    assert not c['neutral_site_review']['dataset_changed']
    # Explicitly synthetic fragment used only to ensure 'vs' is insufficient.
    fragment='<title>SYNTHETIC TEST</title><li class="sidearm-schedule-game">May 18 vs Notre Dame Hempstead 11-16</li>'
    with pytest.raises(ValueError,match='explicit neutral'):neutral_evidence(fragment)


def test_identity_collision_rejected_in_synthetic_mutation():
    games=deepcopy(read_games()[:1]);row=games[0]
    row['away_team_id_ncaa']=row['home_team_id_ncaa']
    with pytest.raises(ValueError,match='ID collision'):identity_registry(games)


def synthetic_games():
    return [dict(game_id='SYNTHETIC_'+str(i),season=year,game_date=day,home_score='1',away_score='2')
            for i,(year,day) in enumerate([('2023','2023-12-31'),('2024','2024-01-01'),
                ('2024','2024-01-02'),('2024','2024-01-02'),('2024','2024-01-03')])]


def test_date_batches_exclude_current_same_day_future_and_prior_season():
    games=synthetic_games()
    assert [r['game_id'] for r in earlier_same_season(games,games[2])]==['SYNTHETIC_1']


def test_future_result_and_input_order_do_not_change_history_membership():
    games=synthetic_games();target=games[2]
    expected=earlier_same_season(games,target)
    changed=deepcopy(games);changed[-1]['home_score']='99';changed[2]['home_score']='88'
    assert earlier_same_season(list(reversed(changed)),target)==expected


def test_immutable_experimental_contract(reviewed):
    c,_,plan=reviewed
    saved=json.loads((ROOT/'reports/stage5_experiment_design.json').read_text())
    assert plan==saved and c['input_sha256']==saved['input_sha256']
    assert plan['logistic_feature_whitelist']==FEATURES and len(FEATURES)==8
    assert not plan['logistic_fit_intercept'] and plan['logistic_C_candidates']==[0.1,1.0,10.0]
    assert plan['splits']['final_fit_seasons']==[2023,2024]
    assert 'PREVIOUSLY_EXPOSED' in plan['splits']['evaluation_status']
    assert plan['bootstrap']['pair_models'] and plan['bootstrap']['unit']=='whole calendar-date clusters'


def test_permission_and_model_execution_are_not_upgraded(reviewed):
    c,_,p=reviewed
    assert c['permission_counts']=={'NOT_CLEARED_NO_CHANGE':1707}
    assert not c['modeling_approved'] and c['models_fit']==c['predictions_generated']==0
    assert p['approval_status']=='NOT_CLEARED_NO_CHANGE' and not p['models_run']


def test_saved_evidence_matches_focused_recheck(reviewed):
    c,registry,_=reviewed
    assert c==json.loads((ROOT/'reports/stage5_readiness_checks.json').read_text())
    assert registry==json.loads((ROOT/'reports/stage5_team_identity_registry.json').read_text())
