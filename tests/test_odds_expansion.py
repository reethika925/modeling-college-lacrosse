"""Synthetic parser fixtures; never fabricated research records.

Final two checks inspect real audit artifacts, without changing or fetching data.
"""
import json
from pathlib import Path

import pytest
from src.verify_odds_expansion import dk_pair, editorial_pair, check_existing_pair


def synthetic_dk(outcomes=None, label='MoneyLine'):
    if outcomes is None:
        outcomes=[dict(label='Synthetic Away', oddsAmerican='+125', criterionName='Away'),
                  dict(label='Synthetic Home', oddsAmerican='−150', criterionName='Home')]
    state={'eventGroups':{'204466':{'name':'College Lacrosse','events':{'1':{
        'eventId':1,'teamName1':'Synthetic Away','teamName2':'Synthetic Home',
        'startDate':'2025-01-02T17:00:00Z'}}}},
        'offers':{'204466':{'a':{'eventId':1,'label':label,'outcomes':outcomes,
        'providerOfferId':'SYNTHETIC','isOpen':True,'updateDate':None}}}}
    return 'window.__INITIAL_STATE__ = '+json.dumps(state)+'; never_execute();'


@pytest.mark.parametrize('label',['MoneyLine','Moneyline','moneyline'])
def test_dk_case_unicode_and_orientation(label):
    pair,meta=dk_pair(synthetic_dk(label=label),'Synthetic Home','Synthetic Away','moneyline')
    assert pair['home']['price']==-150 and pair['away']['price']==125
    assert meta['update_date'] is None  # Capture time cannot fill a quote timestamp.


def test_missing_or_duplicate_side_is_not_a_pair():
    outcome=dict(label='Synthetic Away',oddsAmerican='+125',criterionName='Away')
    for outcomes in [[outcome],[outcome,outcome]]:
        with pytest.raises(ValueError):
            dk_pair(synthetic_dk(outcomes),'Synthetic Home','Synthetic Away','moneyline')


def test_reversed_home_away_is_not_forced():
    with pytest.raises(ValueError):
        dk_pair(synthetic_dk(),'Synthetic Away','Synthetic Home','moneyline')


@pytest.mark.parametrize('price',['ML N/A / -8','-8','N/A'])
def test_spread_or_unavailable_value_never_becomes_moneyline(price):
    html=f'''<title>Synthetic article</title><table>
    <tr><td>Synthetic Home Odds</td><td>{price}</td></tr>
    <tr><td>Synthetic Away Odds</td><td>+140</td></tr>
    </table><p>Odds via Synthetic Book</p>'''
    with pytest.raises(ValueError):
        editorial_pair(html,'Synthetic Home','Synthetic Away','Synthetic Book')


def test_editorial_attribution_required():
    html='''<title>Synthetic</title><table>
    <tr><td>Synthetic Home Odds</td><td>-150</td></tr>
    <tr><td>Synthetic Away Odds</td><td>+140</td></tr></table>
    <p>Model prediction, not a bookmaker attribution.</p>'''
    with pytest.raises(ValueError):
        editorial_pair(html,'Synthetic Home','Synthetic Away','Synthetic Book')


def test_record_book_and_prices_must_match():
    row=dict(odds_record_ids='S1,S2',ncaa_game_id='SYNTHETIC',market='moneyline',
             sportsbook_claimed='Synthetic Book',home='Synthetic Home',away='Synthetic Away')
    prior={rid:dict(ncaa_game_id='SYNTHETIC',market='moneyline',sportsbook='Synthetic Book',
          selection=name,american_odds=str(price)) for rid,name,price in
          [('S1','Synthetic Home',-150),('S2','Synthetic Away',125)]}
    pair,_=dk_pair(synthetic_dk(),'Synthetic Home','Synthetic Away','moneyline')
    check_existing_pair(row,pair,prior)
    prior['S2']['sportsbook']='Different Synthetic Book'
    with pytest.raises(AssertionError):check_existing_pair(row,pair,prior)


def test_actual_audit_counts_and_permission_separation():
    p=json.loads(Path('reports/grok_expansion_independent_checks.json').read_text())
    pre=[r for r in p['checks'] if r['independent_status']=='PREGAME_PRICE_VERIFIED']
    assert len(p['checks'])==53 and len(pre)==48
    assert len({i for r in pre for i in r['odds_record_ids'].split(',')})==96
    assert all(r['permission']=='UNRESOLVED_NOT_APPROVED' for r in p['checks'])
    assert all(r['bookmaker_quote_timestamp'] is None for r in p['checks'])
    assert len(p['omitted_moneyline_evidence'])==6


def test_actual_reconciled_counts_and_distinct_snapshots():
    c=json.loads(Path('reports/grok_expansion_count_checks.json').read_text())
    assert sum(r['supplier_flagged_complete_ml_games'] for r in c['season_coverage'])==269
    assert sum(r['matched_complete_ml'] for r in c['season_coverage'])==269-34-1-2-2==230
    assert [r['matched_complete_ml'] for r in c['season_coverage']]==[37,103,90,0]
    assert c['new_games_over_previous']==25 and c['cumulative_distinct_games']==29
    assert len(c['multi_book_games'])==3
    rows=c['authenticated_observation_inventory']
    assert len(rows)==len({(r['game'],r['book'],r['market'],r['capture']) for r in rows})
    assert len({(r['game'],r['book'],r['capture']) for r in rows})==37
