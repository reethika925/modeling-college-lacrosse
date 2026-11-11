"""Stage 6A: pure, date-batched result features, models and evaluation utilities.

No implicit file reads/writes, network requests or historical execution. Importing
or running this module does not fit anything. The experiment entry point permits
explicit synthetic fixtures or a separately authorized cohort only. Generic model
and metric primitives do not establish source permission.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

FEATURE_COLUMNS = (
    'diff_log1p_prior_games', 'diff_smoothed_win_rate', 'diff_avg_goals_for',
    'diff_avg_goals_against', 'diff_smoothed_last5_win_rate',
    'diff_rest_days_capped21', 'diff_elo_div400', 'diff_no_history',
)
MODEL_COLUMNS = {
    'constant': 'p_home_constant', 'win_rate': 'p_home_winrate',
    'elo': 'p_home_elo', 'logistic': 'p_home_logistic',
}
CORE = ('game_id', 'season', 'game_date', 'home_team_key', 'away_team_key',
        'home_score', 'away_score', 'status')
C_GRID = (0.1, 1.0, 10.0)


@dataclass(frozen=True)
class HistoricalAuthorization:
    """Reference to an actual external decision, never evidence of permission itself.

    Historical execution also requires each row to be explicitly approved in a
    new authorized cohort. An old NOT_CLEARED snapshot cannot be overridden here.
    """
    cohort_fingerprint: str
    decision_reference: str
    status: str = 'APPROVED_INTERNAL_MODELING'


def validate_games(games):
    if not isinstance(games, pd.DataFrame) or games.empty:
        raise ValueError('Nonempty DataFrame required')
    if not set(CORE).issubset(games):
        raise ValueError(f'Missing columns: {sorted(set(CORE)-set(games))}')
    g = games.copy(deep=True)
    for column in ('game_id','game_date','home_team_key','away_team_key','status'):
        if g[column].isna().any() or not g[column].map(lambda x: isinstance(x,str) and bool(x.strip())).all():
            raise ValueError('Missing/invalid identity, date or status')
    if g.game_id.duplicated().any():
        raise ValueError('Duplicate game IDs; no silent deduplication')
    for column in ('season','home_score','away_score'):
        values = pd.to_numeric(g[column], errors='raise').to_numpy(dtype=float)
        if (not np.isfinite(values).all() or (values != np.floor(values)).any()
                or (values < 0).any() or (values >= 2**63).any()):
            raise ValueError('Invalid integer season/score')
        g[column] = values.astype(np.int64)
    if not g.season.isin([2023,2024,2025]).all() or not g.status.eq('final').all():
        raise ValueError('Only final 2023–2025 games are supported')
    for year, day in zip(g.season,g.game_date):
        parsed=date.fromisoformat(day)
        if parsed.isoformat()!=day or parsed.year!=year:
            raise ValueError('Invalid calendar date/season')
    if g.home_score.eq(g.away_score).any() or g.home_team_key.eq(g.away_team_key).any():
        raise ValueError('Tied final or identical opponents')
    seen = set()
    for r in g.itertuples():
        for team in (r.home_team_key,r.away_team_key):
            key=(r.game_date,team)
            if key in seen:
                raise ValueError('Repeated team on one date; review before modeling')
            seen.add(key)
    return g.sort_values(['game_date','game_id'],kind='stable').reset_index(drop=True)


def cohort_fingerprint(games):
    g=validate_games(games)
    content=g[list(CORE)].to_json(orient='records',force_ascii=True)
    return hashlib.sha256(content.encode()).hexdigest()


def require_data_use(games, authorization=None):
    """Guard against accidentally running the pipeline on unresolved source rows."""
    synthetic = ('data_kind' in games and games.data_kind.eq('SYNTHETIC_TEST_ONLY').all()
                 and all(games[c].str.startswith('SYNTHETIC_').all()
                         for c in ('game_id','home_team_key','away_team_key')))
    if synthetic:
        return 'SYNTHETIC_TEST_ONLY'
    if not isinstance(authorization,HistoricalAuthorization):
        raise PermissionError('Historical execution requires documented intended-use authorization')
    if (authorization.status!='APPROVED_INTERNAL_MODELING' or not authorization.decision_reference.strip()
            or authorization.cohort_fingerprint!=cohort_fingerprint(games)):
        raise PermissionError('Missing, mismatched or unresolved authorization decision')
    if ('permission_status' not in games or 'approved_for_modeling' not in games
            or not games.permission_status.eq('APPROVED_INTERNAL_MODELING').all()
            or not games.approved_for_modeling.map(lambda x: x is True or isinstance(x,str) and x=='True').all()):
        raise PermissionError('Rows are not approved; preserve old snapshots and version the authorized cohort')
    return authorization.decision_reference


def constant_probability(n):
    if not isinstance(n,int) or n<0:raise ValueError('Nonnegative integer count required')
    return np.full(n,0.5)


def historical_win_rate(home_wins,home_games,away_wins,away_games):
    values=np.asarray([home_wins,home_games,away_wins,away_games],dtype=float)
    if (not np.isfinite(values).all() or (values<0).any() or (values!=np.floor(values)).any()
            or home_wins>home_games or away_wins>away_games):
        raise ValueError('Invalid prior win/game counts')
    home=(home_wins+1)/(home_games+2);away=(away_wins+1)/(away_games+2)
    return float(home/(home+away))


def sigmoid(values):
    z=np.asarray(values,dtype=float)
    if not np.isfinite(z).all():raise ValueError('Nonfinite logistic input')
    exp=np.exp(-np.abs(z))
    return np.where(z>=0,1/(1+exp),exp/(1+exp))


def elo_probability(home_rating,away_rating):
    return float(sigmoid((float(home_rating)-float(away_rating))*np.log(10)/400))


@dataclass
class TeamState:
    games: int = 0
    wins: int = 0
    goals_for: int = 0
    goals_against: int = 0
    elo: float = 1500.0
    last_date: str | None = None
    recent: deque = field(default_factory=lambda: deque(maxlen=5))

    def snapshot(self,day):
        return np.array([
            np.log1p(self.games),(self.wins+1)/(self.games+2),
            self.goals_for/self.games if self.games else 0,
            self.goals_against/self.games if self.games else 0,
            (sum(self.recent)+1)/(len(self.recent)+2),
            min((date.fromisoformat(day)-date.fromisoformat(self.last_date)).days,21) if self.last_date else 0,
            self.elo/400,int(self.games==0),
        ],dtype=float)


def build_features(games, *, authorization=None):
    """Exactly eight pre-game features; labels/sources never enter the matrix.

    Team history resets each season. A whole date's snapshots are fixed before
    results update state. Ambiguous same-team/same-day schedules are rejected.
    """
    g=validate_games(games)
    use=require_data_use(g,authorization)
    states=defaultdict(TeamState);current_season=None;output=[]
    for day,batch in g.groupby('game_date',sort=True):
        season=int(batch.season.iloc[0])
        if season!=current_season:
            states=defaultdict(TeamState);current_season=season
        pending=[]
        for r in batch.itertuples():
            h,a=states[r.home_team_key],states[r.away_team_key]
            delta=h.snapshot(day)-a.snapshot(day)
            y=int(r.home_score>r.away_score);p=elo_probability(h.elo,a.elo)
            row={c:getattr(r,c) for c in CORE}
            row.update(dict(zip(FEATURE_COLUMNS,delta)))
            row.update(label_home_win=y,p_home_constant=0.5,
                p_home_winrate=historical_win_rate(h.wins,h.games,a.wins,a.games),p_home_elo=p,
                home_previous_games=h.games,away_previous_games=a.games,
                home_previous_wins=h.wins,away_previous_wins=a.wins,
                home_pregame_elo=h.elo,away_pregame_elo=a.elo,
                home_latest_history_date=h.last_date,away_latest_history_date=a.last_date,
                both_teams_cold=(h.games==0 and a.games==0),any_team_cold=(h.games==0 or a.games==0))
            output.append(row);pending.append((r,y,p))
        # This update happens only after every snapshot for the date is fixed.
        for r,y,p in pending:
            for team,scored,conceded,won,change in [
                (r.home_team_key,r.home_score,r.away_score,y,20*(y-p)),
                (r.away_team_key,r.away_score,r.home_score,1-y,-20*(y-p))]:
                state=states[team];state.games+=1;state.wins+=won
                state.goals_for+=scored;state.goals_against+=conceded
                state.elo+=change;state.last_date=day;state.recent.append(won)
    result=pd.DataFrame(output)
    for column in ('home_latest_history_date','away_latest_history_date'):
        result[column]=result[column].astype('string')
    result.attrs['data_use_basis']=use
    result.attrs['source_cohort_fingerprint']=cohort_fingerprint(g)
    return result


def feature_matrix(frame):
    if not set(FEATURE_COLUMNS).issubset(frame):raise ValueError('Missing pre-game predictors')
    x=frame[list(FEATURE_COLUMNS)].to_numpy(dtype=float,copy=True)
    if x.ndim!=2 or not len(x) or not np.isfinite(x).all():raise ValueError('Invalid feature matrix')
    return x


def checked_labels(y):
    values=np.asarray(y,dtype=float)
    if values.ndim!=1 or not len(values) or not np.isin(values,[0,1]).all():
        raise ValueError('Nonempty binary labels required')
    return values


@dataclass
class L2Logistic:
    """Small deterministic Newton solver, no intercept, eight whitelisted features.

    Objective: mean(logaddexp(0,z)-y*z) + ||beta||²/(2*C*n).
    Equivalent to sum logistic loss + ||beta||²/(2*C), up to normalization.
    Scaling uses training-only population standard deviations, without centering.
    """
    C: float = 1.0
    tolerance: float = 1e-9
    max_iterations: int = 200

    def fit(self,frame,y):
        # A failed refit must never leave a usable stale model behind.
        for name in ('scale_','coef_','iterations_','fit_game_ids_','objective_'):
            self.__dict__.pop(name,None)
        if (not np.isfinite(self.C) or self.C<=0 or not isinstance(self.max_iterations,int)
                or self.max_iterations<1 or not np.isfinite(self.tolerance) or self.tolerance<=0):
            raise ValueError('Invalid optimizer configuration')
        x=feature_matrix(frame);y=checked_labels(y)
        if len(y)!=len(x):raise ValueError('Label/feature length mismatch')
        scale=x.std(axis=0,ddof=0);scale=np.where(scale==0,1.0,scale)
        z=x/scale;n=len(y);penalty=1/(self.C*n);beta=np.zeros(z.shape[1])
        def objective(b):
            logits=z@b
            return float(np.mean(np.logaddexp(0,logits)-y*logits)+penalty*(b@b)/2)
        for iteration in range(self.max_iterations):
            p=sigmoid(z@beta);gradient=z.T@(p-y)/n+penalty*beta
            if np.max(np.abs(gradient))<=self.tolerance:
                self.scale_=scale;self.coef_=beta;self.iterations_=iteration
                self.fit_game_ids_=tuple(frame.game_id) if 'game_id' in frame else ()
                self.objective_=objective(beta)
                return self
            hessian=(z.T*(p*(1-p)))@z/n+penalty*np.eye(z.shape[1])
            step=np.linalg.solve(hessian,gradient);rate=1.0;old=objective(beta)
            for _ in range(60):
                candidate=beta-rate*step
                if objective(candidate)<=old-1e-4*rate*(gradient@step):break
                rate*=0.5
            else:raise RuntimeError('Logistic line search failed; no metrics accepted')
            beta=candidate
        raise RuntimeError('Logistic failed to converge; no metrics accepted')

    def predict_proba(self,frame):
        if not hasattr(self,'coef_'):raise RuntimeError('Fit model before predicting')
        return sigmoid((feature_matrix(frame)/self.scale_)@self.coef_)


def losses(y,p,metric='brier'):
    y=checked_labels(y);p=np.asarray(p,dtype=float)
    if p.shape!=y.shape or not np.isfinite(p).all() or ((p<0)|(p>1)).any():
        raise ValueError('Finite matching probabilities in [0,1] required')
    if metric=='brier':return (p-y)**2
    if metric=='log_loss':
        q=np.clip(p,1e-15,1-1e-15)
        return -(y*np.log(q)+(1-y)*np.log1p(-q))
    if metric=='accuracy':return ((p>=0.5)==y).astype(float)
    raise ValueError('Unknown metric')


def evaluate(y,p):
    y=checked_labels(y);brier=losses(y,p);p=np.asarray(p,dtype=float)
    correct=losses(y,p,'accuracy');ties=(p==0.5)
    return dict(n=len(y),accuracy=float(correct.mean()),brier=float(brier.mean()),
        log_loss=float(losses(y,p,'log_loss').mean()),exact_ties=int(ties.sum()),
        half_credit_tie_accuracy=float(np.where(ties,0.5,correct).mean()),
        mean_probability_bias=float(np.mean(p-y)))


def calibration(y,p):
    y=checked_labels(y);losses(y,p);p=np.asarray(p,dtype=float)
    edges=np.array([0,.2,.4,.6,.8,1.]);bins=np.searchsorted(edges[1:-1],p,side='right')
    output=[]
    for index in range(5):
        mask=bins==index;n=int(mask.sum())
        output.append(dict(lower=float(edges[index]),upper=float(edges[index+1]),n=n,
            mean_probability=float(p[mask].mean()) if n else None,
            observed_frequency=float(y[mask].mean()) if n else None,unstable=(n<20)))
    return pd.DataFrame(output)


def performance_by_season(predictions,columns=None, *, subgroup='all'):
    columns=MODEL_COLUMNS if columns is None else columns
    if predictions.empty or predictions.game_id.duplicated().any():raise ValueError('Unique prediction IDs required')
    if subgroup not in ('all','any_cold','both_at_least_five'):raise ValueError('Unknown subgroup')
    if subgroup!='all':
        if not {'home_previous_games','away_previous_games'}.issubset(predictions):
            raise ValueError('Prior game counts required for subgroup')
        mask=((predictions.home_previous_games==0)|(predictions.away_previous_games==0)) if subgroup=='any_cold' else (
              (predictions.home_previous_games>=5)&(predictions.away_previous_games>=5))
        predictions=predictions[mask]
    output=[]
    for season,frame in predictions.groupby('season',sort=True):
        for name,column in columns.items():
            output.append(dict(season=int(season),model=name,subgroup=subgroup,**evaluate(frame.label_home_win,frame[column])))
    return pd.DataFrame(output)


def paired_uncertainty(a,b, *, metric='brier', cluster='date',replicates=50000,seed=519):
    """Align two p_home prediction tables by game ID; resample whole date/week groups.

    Frozen-prediction conditional intervals only. No model fitting or replay.
    Paired deltas are A minus B; negative favors A for Brier/log loss, positive
    favors A for accuracy. Unequal cluster sizes are weighted by sampled games.
    """
    required={'game_id','game_date','label_home_win','p_home'}
    for frame in (a,b):
        if not required.issubset(frame) or frame.empty or frame.game_id.isna().any() or frame.game_id.duplicated().any():
            raise ValueError('Unique complete paired prediction records required')
    if set(a.game_id)!=set(b.game_id):raise ValueError('Models must evaluate identical IDs')
    if cluster not in ('date','week') or not isinstance(replicates,int) or replicates<1:
        raise ValueError('Invalid bootstrap configuration')
    a=a.sort_values('game_id').reset_index(drop=True);b=b.sort_values('game_id').reset_index(drop=True)
    if (list(a.game_date)!=list(b.game_date) or
            not np.array_equal(checked_labels(a.label_home_win),checked_labels(b.label_home_win))):
        raise ValueError('Paired dates/outcomes disagree')
    differences=losses(a.label_home_win,a.p_home,metric)-losses(b.label_home_win,b.p_home,metric)
    labels=[]
    for value in a.game_date:
        day=date.fromisoformat(value)
        if day.isoformat()!=value:raise ValueError('ISO calendar dates required')
        labels.append(value if cluster=='date' else tuple(day.isocalendar()[:2]))
    groups=defaultdict(list)
    for index,key in enumerate(labels):groups[key].append(index)
    sums=np.array([differences[ix].sum() for ix in groups.values()]);sizes=np.array([len(ix) for ix in groups.values()])
    rng=np.random.Generator(np.random.PCG64(seed));draws=np.empty(replicates);count=len(groups)
    if count<2:raise ValueError('At least two cluster units required for uncertainty')
    for start in range(0,replicates,1000):
        ix=rng.integers(0,count,size=(min(1000,replicates-start),count))
        draws[start:start+len(ix)]=sums[ix].sum(axis=1)/sizes[ix].sum(axis=1)
    lower,upper=np.quantile(draws,[.025,.975],method='linear')
    return dict(metric=metric,contrast='A minus B',point=float(differences.mean()),
        lower=float(lower),upper=float(upper),n=len(a),clusters=count,cluster=cluster,
        replicates=replicates,seed=seed,conditional_on_frozen_predictions=True)


def run_experiment(games, *, authorization=None):
    """Fixed 2023 train / 2024 validation / 2025 retrospective experiment, in memory.

    This task calls it only with synthetic fixtures. It never reads a default CSV,
    changes source permissions, writes artifacts or imports sportsbook data.
    """
    g=validate_games(games);require_data_use(g,authorization)
    if set(g.season)!={2023,2024,2025}:raise ValueError('All three planned seasons required')
    features=build_features(g,authorization=authorization)
    train=features[features.season.eq(2023)].copy()
    valid=features[features.season.eq(2024)].copy()
    test=features[features.season.eq(2025)].copy()
    trials=[];models={}
    for c in C_GRID:
        model=L2Logistic(C=c).fit(train,train.label_home_win)
        probability=model.predict_proba(valid)
        trials.append(dict(C=c,**evaluate(valid.label_home_win,probability)))
        models[c]=model
    minimum=min(r['brier'] for r in trials)
    chosen=min(r['C'] for r in trials if abs(r['brier']-minimum)<=1e-12)
    valid['p_home_logistic']=models[chosen].predict_proba(valid)
    final_train=features[features.season.isin([2023,2024])].copy()
    final=L2Logistic(C=chosen).fit(final_train,final_train.label_home_win)
    test['p_home_logistic']=final.predict_proba(test)
    predictions=pd.concat([valid,test],ignore_index=True)
    reliability={(int(season),name):calibration(frame.label_home_win,frame[column])
        for season,frame in predictions.groupby('season') for name,column in MODEL_COLUMNS.items()}
    return dict(features=features,validation_predictions=valid,evaluation_predictions=test,
        validation_trials=pd.DataFrame(trials),chosen_C=chosen,validation_models=models,final_model=final,
        performance=performance_by_season(predictions),
        subgroup_performance=pd.concat([performance_by_season(predictions,subgroup=s)
            for s in ('any_cold','both_at_least_five')],ignore_index=True),calibration=reliability,
        evaluation_description='Retrospective 2025; previously exposed, not an untouched holdout')


if __name__=='__main__':
    print('Library only: no data loaded and no model fit. Run synthetic pytest tests; see reports/stage6_modeling_implementation.md.')
