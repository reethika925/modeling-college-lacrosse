"""Synthetic classification fixtures plus read-only checks of real Stage 7 outputs."""
import json
from copy import deepcopy
import pytest
from src.audit_stage7_odds import CLASSES, PACKAGE, ROOT, key, match_record, rows, source_key


def synthetic_record():
    return dict(record_id='SYNTHETIC_RECORD',original_game_date='2025-01-02',
        original_home_team='Synthetic Home',original_away_team='Synthetic Away',
        sportsbook='Synthetic Book',market='moneyline',selection='Synthetic Home',
        line='null',american_odds='-120',matched_game_id='SYNTHETIC_GAME',technical_status='verified',
        source_url='https://example.org/synthetic',archive_url='null',
        quote_capture_timestamp='null',archive_capture_timestamp='null')


def synthetic_observation():
    return dict(observation_id='SYNTHETIC_OBSERVATION',game_date='2025-01-02',
        participants=sorted([key('Synthetic Home'),key('Synthetic Away')]),
        selection_key=key('Synthetic Home'),sportsbook='Synthetic Book',market='moneyline',
        line=None,american_price=-120,matched_game_id='SYNTHETIC_GAME',
        source_url='https://example.org/synthetic',archive_url='https://example.org/synthetic-capture',
        timing='BEFORE_OFFICIAL_SCHEDULED_START',stamp='20250101010000',local_path='SYNTHETIC_ONLY')


def test_url_and_supplier_claims_alone_are_unsupported():
    r=synthetic_record();r['verified_in_raw']='True';r['evidence_excerpt']='SYNTHETIC ASSERTION ONLY'
    assert match_record(r,[])['evidence_classification']=='UNSUPPORTED'


def test_full_exact_source_pregame_price_requires_real_observation():
    a=match_record(synthetic_record(),[synthetic_observation()])
    assert a['evidence_classification']=='VERIFIED_PRE_GAME' and a['exact_price_supported']


@pytest.mark.parametrize('field,value',[('source_url','https://example.org/another-synthetic-page'),('stamp','20250101120000')])
def test_alternative_source_or_capture_cannot_authenticate_original_claim(field,value):
    r=synthetic_record();r['archive_url']='https://web.archive.org/web/20250101010000/https://example.org/synthetic'
    o=synthetic_observation();o[field]=value
    a=match_record(r,[o])
    assert a['evidence_classification']=='PARTIALLY_SUPPORTED' and a['alternative_pregame_observation_ids']


def test_post_start_display_is_not_pregame():
    o=synthetic_observation();o['timing']='AFTER_OFFICIAL_SCHEDULED_START'
    a=match_record(synthetic_record(),[o])
    assert a['evidence_classification']=='VERIFIED_PRICE_TIMING_UNKNOWN'
    assert a['pregame_timing_status']=='AFTER_OFFICIAL_SCHEDULED_START'
    assert a['independent_bookmaker_quote_timestamp']==''


def test_wrong_book_and_price_conflict_are_not_verified():
    o=synthetic_observation();o['sportsbook']='Different Synthetic Book'
    a=match_record(synthetic_record(),[o]);assert a['evidence_classification']=='PARTIALLY_SUPPORTED'
    assert not a['sportsbook_supported_in_claimed_context']
    o=synthetic_observation();o['american_price']=-150
    a=match_record(synthetic_record(),[o]);assert not a['exact_price_supported']
    assert a['contradictory_same_capture_observation_ids']


def test_unknown_game_cannot_become_verified_from_price_match():
    r=synthetic_record();r['matched_game_id']=''
    assert match_record(r,[synthetic_observation()])['evidence_classification']=='PARTIALLY_SUPPORTED'


def test_prior_rejected_duplicate_is_kept_even_if_price_exists():
    r=synthetic_record();r['technical_status']='rejected'
    a=match_record(r,[synthetic_observation()])
    assert a['evidence_classification']=='REJECTED' and a['exact_price_supported']


@pytest.mark.parametrize('market,selection,observed_selection',[
    ('spread','Synthetic Home',key('Synthetic Home')),('total','Over','UNSPECIFIED_TOTAL')])
def test_line_only_or_undirected_total_does_not_become_priced_pair(market,selection,observed_selection):
    r=synthetic_record();r.update(market=market,selection=selection,line='23.5',american_odds='null')
    o=synthetic_observation();o.update(market=market,selection_key=observed_selection,line=23.5,american_price=None)
    a=match_record(r,[o]);assert a['evidence_classification']=='PARTIALLY_SUPPORTED' and not a['exact_price_supported']


def test_actual_original_id_and_field_accounting_permission_preservation():
    original=rows(PACKAGE/'odds_provenance_audit.csv');audit=rows('data/review/stage7_odds_record_audit.csv')
    assert len(audit)==len(original)==1995 and len({r['record_id'] for r in audit})==1995
    assert {r['record_id'] for r in audit}=={r['record_id'] for r in original}
    for r,s in zip(audit,original):
        assert all(r[k]==v for k,v in s.items())
        assert r['evidence_classification'] in CLASSES and r['approved_for_modeling']=='False'
    assert sum(r['evidence_classification']=='REJECTED' for r in audit)==12


def test_actual_counts_and_observation_units_do_not_mix():
    s=json.loads((ROOT/'reports/stage7_summary_checks.json').read_text())
    assert s['record_counts']=={'VERIFIED_PRE_GAME':208,'VERIFIED_PRICE_TIMING_UNKNOWN':163,
        'PARTIALLY_SUPPORTED':299,'UNSUPPORTED':1313,'REJECTED':12}
    assert sum(s['record_counts'].values())==1995
    strict=s['strict_original_source'];broader=s['price_corroboration_including_prior_audit_only_DK']
    assert strict['games']==39 and strict['ml_games']==27
    assert broader['games']==43 and broader['ml_games']==31 and len(broader['multi_book_ml_games'])==3
    assert strict['multi_book_ml_games']=={}
    assert s['approved_records']==s['actual_quote_timestamps_verified']==0
    assert s['opening_claim_records']==25 and s['closing_claim_records']==0


def test_every_summary_dimension_accounts_for_1995_rows():
    s=json.loads((ROOT/'reports/stage7_summary_checks.json').read_text())
    for table in s['summary_by_dimension'].values():
        assert sum(sum(counts.values()) for counts in table.values())==1995


def test_known_rejections_and_provenance_caveats_are_explicit():
    r={r['record_id']:r for r in rows('data/review/stage7_odds_record_audit.csv')}
    for rid in ['O0260','O0261']:assert r[rid]['rejection_evidence_basis']=='INDEPENDENT_CAPTURE_PRINTS_SPREAD_NOT_MONEYLINE'
    assert r['O0305']['contradictory_same_capture_observation_ids']
    assert r['O0097']['opening_narrative_evidence'] and r['O0097']['sportsbook']=='null'
    assert r['O1031']['evidence_classification']=='VERIFIED_PRICE_TIMING_UNKNOWN'
    assert r['O1031']['alternative_pregame_observation_ids']


def test_url_normalization_is_limited_to_documented_publisher_typo():
    assert source_key('https://www.actionnetwork.com/lacrosse-lacrosse/example')==source_key('https://www.actionnetwork.com/lacrosse/example')
    assert source_key('https://example.org/a?x=1')!=source_key('https://example.org/a?x=2')
