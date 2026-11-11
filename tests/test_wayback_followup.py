"""Clearly synthetic unit fixtures; these are not lacrosse research observations."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from src.verify_wayback_spotcheck import (
    american_from_decimal, before_start, capture_time, parse_mgm, snapshot_key,
)


@pytest.mark.parametrize('decimal,rounded', [('1.22', -455), ('1.30', -333),
    ('1.06', -1667), ('1.48', -208), ('2.00', 100), ('4.40', 340)])
def test_conversion_and_rounding(decimal, rounded):
    exact, result = american_from_decimal(decimal)
    assert result == rounded
    assert abs(exact - result) <= Decimal('.5')


@pytest.mark.parametrize('value', ['1', '0', '-2', 'NaN', 'Infinity'])
def test_invalid_decimal_rejected(value):
    with pytest.raises(ValueError):
        american_from_decimal(value)


def test_capture_header_and_url_must_agree():
    url = 'https://web.archive.org/web/20250101120000id_/https://example.org/'
    assert capture_time(url, 'Wed, 01 Jan 2025 12:00:00 GMT').hour == 12
    for header in [None, 'Wed, 01 Jan 2025 13:00:00 GMT']:
        with pytest.raises(ValueError):
            capture_time(url, header)


def test_pregame_strict_and_timezone_aware():
    capture = datetime(2025, 1, 1, 12, tzinfo=timezone.utc)
    assert before_start(capture, '2025-01-01T08:00:00-05:00')
    assert not before_start(capture, '2025-01-01T07:00:00-05:00')
    assert not before_start(capture, '2025-01-01T11:00:00Z')
    with pytest.raises(ValueError):
        before_start(capture, '2025-01-01T13:00:00')


def synthetic_html():
    # Deliberately fictional team names; no real source page reproduced here.
    return '''<title>Synthetic BetMGM fixture</title><ms-event-group>
      <div class="grid-group-header">Spread</div><div class="grid-group-header">Total</div>
      <div class="grid-group-header">Money</div><ms-six-pack-event>
      <div class="participant">Synthetic Visitors</div><span class="away-indicator">@</span>
      <div class="participant">Synthetic Hosts</div>
      <a class="grid-info-wrapper" href="/fictional-event"></a>
      <ms-option-group><div class="option-value">1.91</div></ms-option-group>
      <ms-option-group><div class="option-value">1.87</div></ms-option-group>
      <ms-option-group><ms-event-pick class="offline"><div class="option-value">3.00</div></ms-event-pick>
      <ms-event-pick class="offline"><div class="option-value">1.50</div></ms-event-pick></ms-option-group>
      <ms-prematch-timer>Tomorrow</ms-prematch-timer></ms-six-pack-event></ms-event-group>'''


def test_moneyline_market_and_team_orientation():
    observed = parse_mgm(synthetic_html(), 'Synthetic Visitors', 'Synthetic Hosts')
    assert observed['away_decimal'] == '3.00'
    assert observed['home_decimal'] == '1.50'
    assert observed['offline_options'] == 2  # Does not prove an open market.
    with pytest.raises(ValueError):
        parse_mgm(synthetic_html(), 'Synthetic Hosts', 'Synthetic Visitors')
    with pytest.raises(ValueError):
        parse_mgm(synthetic_html().replace('>Money<', '>Other<'), 'Synthetic Visitors', 'Synthetic Hosts')


def test_duplicate_selection_rows_do_not_inflate_snapshots():
    row = {'ncaa_game_id': 'SYNTHETIC', 'sportsbook_claimed': 'Synthetic Book', 'wayback_url': 'capture1'}
    assert len({snapshot_key(row), snapshot_key(dict(row))}) == 1
    assert len({snapshot_key(row), snapshot_key({**row, 'wayback_url': 'capture2'})}) == 2
