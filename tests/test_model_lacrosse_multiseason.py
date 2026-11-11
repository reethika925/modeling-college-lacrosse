"""SYNTHETIC TEST FIXTURES ONLY. No historical game CSV or odds data are loaded.

Scores, teams and approval stubs below are invented software fixtures, not research
observations, findings or actual use permissions. Nothing is saved as sports data.
"""
from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.model_lacrosse_multiseason import (
    CORE, FEATURE_COLUMNS, HistoricalAuthorization, L2Logistic, MODEL_COLUMNS,
    build_features, calibration, cohort_fingerprint, constant_probability,
    elo_probability, evaluate, feature_matrix, historical_win_rate, losses,
    paired_uncertainty, performance_by_season, run_experiment, sigmoid, validate_games,
)


def synthetic_games():
    """Four fictional teams; 18 games per season with no same-day appearances."""
    records=[]
    fixtures=[('A','B',10,5),('C','D',4,6),('A','C',7,9),('B','D',12,3),
              ('A','D',11,8),('B','C',5,6),('B','A',4,9),('D','C',10,8),
              ('C','A',5,13),('D','B',11,7),('D','A',4,6),('C','B',3,8),
              ('A','B',9,4),('C','D',14,12),('A','C',6,10),('B','D',11,9),
              ('A','D',10,12),('B','C',8,6)]
    for season in (2023,2024,2025):
        for i,(home,away,hs,aws) in enumerate(fixtures):
            records.append(dict(game_id=f'SYNTHETIC_{season}_{i:02}',season=season,
                game_date=(date(season,1,1)+timedelta(days=(i//2)*3)).isoformat(),
                home_team_key='SYNTHETIC_'+home,away_team_key='SYNTHETIC_'+away,
                home_score=hs,away_score=aws,status='final',data_kind='SYNTHETIC_TEST_ONLY'))
    return pd.DataFrame(records)


@pytest.fixture(scope='module')
def synthetic_run():return run_experiment(synthetic_games())


def test_independent_hand_calculation_of_all_eight_features():
    f=build_features(synthetic_games())
    r=f[f.game_id.eq('SYNTHETIC_2023_02')].iloc[0]
    expected=[0,1/3,6,-1,1/3,0,20/400,0]
    np.testing.assert_allclose(r[list(FEATURE_COLUMNS)].to_numpy(float),expected,atol=1e-14)
    assert r.home_previous_games==r.away_previous_games==1
    assert r.p_home_winrate==pytest.approx(2/3)
    assert r.p_home_elo==pytest.approx(1/(1+10**(-20/400)))
    assert r.home_latest_history_date==r.away_latest_history_date=='2023-01-01'


def test_latest_history_is_strictly_earlier_and_resets_each_season():
    f=build_features(synthetic_games())
    for r in f.itertuples():
        for latest in (r.home_latest_history_date,r.away_latest_history_date):
            assert pd.isna(latest) or latest<r.game_date and latest[:4]==str(r.season)
    first=f[f.game_date.str.endswith('01-01')]
    assert len(first)==6 and first.both_teams_cold.all()
    np.testing.assert_array_equal(first[list(FEATURE_COLUMNS)],0)
    assert (first.home_pregame_elo==1500).all()


def test_prefix_invariance_and_own_result_cannot_predict_itself():
    g=synthetic_games();f=build_features(g)
    cutoff='2024-01-10'
    pd.testing.assert_frame_equal(f[f.game_date<=cutoff].reset_index(drop=True),build_features(g[g.game_date<=cutoff]))
    changed=g.copy();ix=changed.index[changed.game_id.eq('SYNTHETIC_2023_02')][0]
    changed.loc[ix,['home_score','away_score']]=[99,1]
    alt=build_features(changed);key=f.game_id.eq(changed.loc[ix,'game_id'])
    pd.testing.assert_frame_equal(f.loc[key,list(FEATURE_COLUMNS)],alt.loc[key,list(FEATURE_COLUMNS)])
    assert f.loc[key,'label_home_win'].item()!=alt.loc[key,'label_home_win'].item()


def test_same_day_reordering_and_distinct_game_result_isolation():
    g=synthetic_games();expected=build_features(g)
    pd.testing.assert_frame_equal(expected,build_features(g.sample(frac=1,random_state=519)))
    changed=g.copy();changed.loc[1,['home_score','away_score']]=[90,1]
    alt=build_features(changed);day=expected.game_date.eq('2023-01-01')
    pd.testing.assert_frame_equal(expected.loc[day,list(FEATURE_COLUMNS)],alt.loc[day,list(FEATURE_COLUMNS)])


def test_ambiguous_same_team_same_day_and_duplicate_ids_fail():
    g=synthetic_games();changed=g.copy();changed.loc[1,'home_team_key']=changed.loc[0,'home_team_key']
    with pytest.raises(ValueError,match='Repeated team'):build_features(changed)
    with pytest.raises(ValueError,match='Duplicate game'):validate_games(pd.concat([g,g.iloc[:1]]))


@pytest.mark.parametrize('column,value',[
    ('home_score',np.nan),('away_score',-1),('home_score',1.5),('home_score',np.inf),
    ('home_score',1e20),('game_date','2023-02-30'),('game_date','2024-01-01'),('status','pre')])
def test_bad_synthetic_source_fields_fail(column,value):
    g=synthetic_games().astype({'home_score':float,'away_score':float});g.loc[0,column]=value
    with pytest.raises(ValueError):validate_games(g)


def test_season_reset_does_not_import_prior_season_results():
    g=synthetic_games();baseline=build_features(g);altered=g.copy()
    altered.loc[altered.season.eq(2023),['home_score','away_score']]=[99,1]
    f=build_features(altered)
    mask=baseline.season.eq(2024)
    pd.testing.assert_frame_equal(baseline.loc[mask,list(FEATURE_COLUMNS)],f.loc[mask,list(FEATURE_COLUMNS)])


def test_future_season_result_cannot_change_selection_scaling_or_fits(synthetic_run):
    g=synthetic_games();g.loc[g.season.eq(2025),['home_score','away_score']]=[99,1]
    changed=run_experiment(g)
    assert changed['chosen_C']==synthetic_run['chosen_C']
    pd.testing.assert_frame_equal(changed['validation_trials'],synthetic_run['validation_trials'])
    pd.testing.assert_frame_equal(changed['validation_predictions'],synthetic_run['validation_predictions'])
    np.testing.assert_array_equal(changed['final_model'].scale_,synthetic_run['final_model'].scale_)
    np.testing.assert_array_equal(changed['final_model'].coef_,synthetic_run['final_model'].coef_)


def test_fit_ids_and_preprocessing_exclude_validation_or_evaluation(synthetic_run):
    f=synthetic_run['features']
    x=feature_matrix(f[f.season.eq(2023)]);std=x.std(axis=0);std[std==0]=1
    for model in synthetic_run['validation_models'].values():
        np.testing.assert_array_equal(model.scale_,std)
        assert all('_2023_' in game for game in model.fit_game_ids_)
    x=feature_matrix(f[f.season.isin([2023,2024])]);std=x.std(axis=0);std[std==0]=1
    np.testing.assert_array_equal(synthetic_run['final_model'].scale_,std)
    assert not any('_2025_' in game for game in synthetic_run['final_model'].fit_game_ids_)


def test_postgame_columns_are_ignored_by_explicit_matrix_whitelist(synthetic_run):
    frame=synthetic_run['features'].copy();train=frame[frame.season.eq(2023)].copy()
    expected=L2Logistic().fit(train,train.label_home_win)
    train['player_shots_postgame']=1e300;train['winner_from_future']='SYNTHETIC_FUTURE'
    altered=L2Logistic().fit(train,train.label_home_win)
    np.testing.assert_array_equal(expected.coef_,altered.coef_)
    assert feature_matrix(train).shape[1]==8


def test_optimizer_stationarity_probability_complement_and_constant_columns(synthetic_run):
    model=synthetic_run['final_model'];train=synthetic_run['features'].query('season < 2025')
    z=feature_matrix(train)/model.scale_;y=train.label_home_win.to_numpy()
    gradient=z.T@(sigmoid(z@model.coef_)-y)/len(y)+model.coef_/(model.C*len(y))
    assert np.max(np.abs(gradient))<1e-8
    reverse=train.copy();reverse[list(FEATURE_COLUMNS)]*=-1
    np.testing.assert_allclose(model.predict_proba(train)+model.predict_proba(reverse),1,atol=1e-14)
    assert not hasattr(model,'intercept_')
    assert (model.scale_>0).all()


def test_optimizer_failure_is_not_silently_accepted(synthetic_run):
    train=synthetic_run['features'].query('season == 2023')
    with pytest.raises(RuntimeError,match='converge'):L2Logistic(max_iterations=1).fit(train,train.label_home_win)
    with pytest.raises(ValueError):L2Logistic(C=0).fit(train,train.label_home_win)
    model=L2Logistic().fit(train,train.label_home_win)
    model.max_iterations=1
    with pytest.raises(RuntimeError):model.fit(train,train.label_home_win)
    with pytest.raises(RuntimeError,match='Fit model'):model.predict_proba(train)


def test_all_cold_zero_features_choose_smallest_C_in_validation_tie():
    g=synthetic_games()
    for index in g.index:
        g.loc[index,'home_team_key']=f'SYNTHETIC_UNIQUE_HOME_{index}'
        g.loc[index,'away_team_key']=f'SYNTHETIC_UNIQUE_AWAY_{index}'
    run=run_experiment(g)
    assert run['chosen_C']==0.1
    np.testing.assert_array_equal(run['final_model'].coef_,0)
    assert (run['final_model'].scale_==1).all()
    assert (run['evaluation_predictions'].p_home_logistic==0.5).all()


def test_common_ids_probabilities_and_across_season_comparisons(synthetic_run):
    for frame in [synthetic_run['validation_predictions'],synthetic_run['evaluation_predictions']]:
        assert len(frame)==18 and not frame.game_id.duplicated().any()
        values=frame[list(MODEL_COLUMNS.values())].to_numpy()
        assert np.isfinite(values).all() and (values>=0).all() and (values<=1).all()
    table=synthetic_run['performance']
    assert len(table)==8 and set(table.season)=={2024,2025} and set(table.n)=={18}
    assert set(synthetic_run['subgroup_performance'].subgroup)=={'any_cold','both_at_least_five'}
    for _,group in synthetic_run['subgroup_performance'].groupby(['season','subgroup']):assert group.n.nunique()==1


def test_baseline_and_metric_reference_values():
    np.testing.assert_array_equal(constant_probability(3),[.5,.5,.5])
    assert historical_win_rate(0,0,0,0)==.5 and elo_probability(1500,1500)==.5
    r=evaluate([1,0,1],[.5,.5,.5])
    assert r['accuracy']==pytest.approx(2/3) and r['brier']==.25
    assert r['log_loss']==pytest.approx(np.log(2)) and r['half_credit_tie_accuracy']==.5
    assert np.isfinite(evaluate([0,1],[1,0])['log_loss'])


@pytest.mark.parametrize('bad',[[np.nan,.5],[1.1,.5],[-.1,.5],[.5]])
def test_invalid_probabilities_fail(bad):
    with pytest.raises(ValueError):evaluate([0,1],bad)


def test_calibration_boundaries_empty_bins_and_small_count_flags():
    bins=calibration([0,1,0,1],[0,.2,.8,1])
    assert list(bins.n)==[1,1,0,0,2]
    assert bins.iloc[2].mean_probability is None or pd.isna(bins.iloc[2].mean_probability)
    assert bins.unstable.all() and bins.iloc[4].observed_frequency==.5


def paired_fixture():
    a=pd.DataFrame(dict(game_id=['SYNTHETIC_X','SYNTHETIC_Y','SYNTHETIC_Z'],
        game_date=['2025-01-01','2025-01-01','2025-01-09'],label_home_win=[1,0,1],p_home=[.9,.1,.2]))
    b=a.copy();b.p_home=.5
    return a,b


@pytest.mark.parametrize('cluster',['date','week'])
def test_paired_bootstrap_alignment_and_unequal_cluster_weights(cluster):
    a,b=paired_fixture();result=paired_uncertainty(a,b.sample(frac=1,random_state=1),cluster=cluster,replicates=50)
    rng=np.random.Generator(np.random.PCG64(519));draws=rng.integers(0,2,size=(50,2))
    difference=(a.p_home.to_numpy()-a.label_home_win.to_numpy())**2-.25
    sums=np.array([difference[:2].sum(),difference[2:].sum()]);sizes=np.array([2,1])
    means=sums[draws].sum(1)/sizes[draws].sum(1)
    assert result['point']==pytest.approx(difference.mean())
    np.testing.assert_allclose([result['lower'],result['upper']],np.quantile(means,[.025,.975]))
    swapped=paired_uncertainty(b,a,cluster=cluster,replicates=50)
    np.testing.assert_allclose([result['lower'],result['upper']],[-swapped['upper'],-swapped['lower']])


def test_bootstrap_rejects_incompatible_ids_outcomes_and_one_cluster():
    a,b=paired_fixture()
    with pytest.raises(ValueError,match='identical IDs'):paired_uncertainty(a,b.iloc[:2])
    changed=b.copy();changed.loc[0,'label_home_win']=0
    with pytest.raises(ValueError,match='disagree'):paired_uncertainty(a,changed)
    with pytest.raises(ValueError,match='two cluster'):paired_uncertainty(a.iloc[:2],b.iloc[:2])


def test_historical_gate_rejects_unresolved_synthetic_approval_stub():
    # These renamed synthetic rows simulate permission metadata, not historical data.
    g=synthetic_games();g['data_kind']='SYNTHETIC_AUTHORIZATION_TEST'
    g['permission_status']='NOT_CLEARED_NO_CHANGE';g['approved_for_modeling']=False
    with pytest.raises(PermissionError):run_experiment(g)
    stub=HistoricalAuthorization(cohort_fingerprint(g),'SYNTHETIC_NOT_REAL_PERMISSION')
    with pytest.raises(PermissionError,match='Rows are not approved'):run_experiment(g,authorization=stub)
    g['permission_status']='APPROVED_INTERNAL_MODELING';g['approved_for_modeling']=True
    with pytest.raises(PermissionError,match='mismatched'):
        run_experiment(g,authorization=HistoricalAuthorization('wrong','SYNTHETIC_NOT_REAL_PERMISSION'))
    assert run_experiment(g,authorization=stub)['chosen_C'] in [.1,1,10]


def test_stage5_contract_and_no_input_mutation():
    contract=json.loads(Path('reports/stage5_experiment_design.json').read_text())
    assert list(FEATURE_COLUMNS)==contract['logistic_feature_whitelist']
    g=synthetic_games();before=deepcopy(g);run_experiment(g)
    pd.testing.assert_frame_equal(g,before)
