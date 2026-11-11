"""Offline checks for the November 10 spot-check; never edits source data or fetches URLs.

Inputs are the supplier's 18-row spot-check, independently fetched archive HTML/headers,
and separately reviewed official scheduled starts. This verifies displayed prices, not
market availability or use permissions. Packaged supplier scripts are never imported.
"""
import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from email.utils import parsedate_to_datetime
from pathlib import Path

from bs4 import BeautifulSoup


def american_from_decimal(value):
    d = Decimal(str(value))
    if not d.is_finite() or d <= 1:
        raise ValueError('Decimal odds must be finite and greater than 1')
    exact = 100 * (d - 1) if d >= 2 else -100 / (d - 1)
    return exact, int(exact.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def capture_time(url, memento):
    match = re.search(r'/web/(\d{14})(?:id_)?/', url)
    if not match or not memento:
        raise ValueError('Exact archive URL and Memento-Datetime required')
    stamp = datetime.strptime(match[1], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
    header = parsedate_to_datetime(memento)
    if header.tzinfo is None or header != stamp:
        raise ValueError('Archive URL and capture header disagree')
    return stamp


def before_start(capture, scheduled):
    start = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
    if start.tzinfo is None or capture.tzinfo is None:
        raise ValueError('Timezone-aware times required')
    return capture < start


def team_key(name):
    # Only two page abbreviations observed and manually checked in this sample.
    return {'Penn St.': 'Penn State', 'Penn St': 'Penn State',
            'Ohio St.': 'Ohio State'}.get(name, name)


def parse_mgm(html, away, home):
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.title or 'BetMGM' not in soup.title.get_text():
        raise ValueError('BetMGM identity absent')
    matches = []
    for event in soup.select('ms-six-pack-event'):
        names = [n.get_text(' ', strip=True) for n in event.select('.participant')]
        if [team_key(n) for n in names] != [team_key(away), team_key(home)]:
            continue
        group = event.find_parent('ms-event-group')
        headers = [n.get_text(strip=True) for n in group.select('.grid-group-header')]
        if headers != ['Spread', 'Total', 'Money']:
            raise ValueError('Unrecognized market headers')
        if event.select_one('.away-indicator').get_text(strip=True) != '@':
            raise ValueError('Unknown participant orientation')
        markets = event.select('ms-option-group')
        if len(markets) != 3:
            raise ValueError('Unrecognized market layout')
        ml = markets[headers.index('Money')]
        prices = [n.get_text(strip=True) for n in ml.select('.option-value')]
        if len(prices) != 2:
            raise ValueError('Both moneyline prices required')
        link = event.select_one('a.grid-info-wrapper')['href']
        starts = []
        for script in soup.select('script#ldJson_SportsEvent[type="application/ld+json"]'):
            data = json.loads(script.string or script.get_text())
            for item in data.get('@graph', []):
                if item.get('@type') == 'SportsEvent' and item.get('url', '').endswith(link):
                    starts.append(item.get('startDate'))
        matches.append({'away_decimal': prices[0], 'home_decimal': prices[1],
                        'page_event_path': link, 'page_start_json': ';'.join(starts),
                        'page_timer': event.select_one('ms-prematch-timer').get_text(' ', strip=True),
                        'offline_options': len(ml.select('ms-event-pick.offline')),
                        'evidence_type': 'DIRECT_SPORTSBOOK_DISPLAY'})
    if len(matches) != 1:
        raise ValueError(f'Expected one exact matchup, found {len(matches)}')
    return matches[0]


def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = [h for h in soup.select('h2') if h.get_text(strip=True) == 'Syracuse at Utah']
    if len(headings) != 1:
        raise ValueError('Article matchup missing or ambiguous')
    table = headings[0].find_next('table')
    prices = {}
    for row in table.select('tr'):
        cells = row.select('td')
        if len(cells) == 2:
            label = cells[0].get_text(' ', strip=True)
            if 'Moneyline/Spread' in label:
                prices[label.split(' Moneyline')[0]] = int(cells[1].get_text(strip=True).split('/')[0])
    attribution = table.find_next('p').get_text(' ', strip=True)
    if attribution != 'Odds via FanDuel' or set(prices) != {'Syracuse', 'Utah'}:
        raise ValueError('Unrecognized attribution or prices')
    return {'home_american': prices['Utah'], 'away_american': prices['Syracuse'],
            'publication_time': soup.select_one('meta[property="article:published_time"]')['content'],
            'modification_time': soup.select_one('meta[property="article:modified_time"]')['content'],
            'evidence_type': 'THIRD_PARTY_FANDUEL_QUOTE'}


def snapshot_key(row):
    return (row['ncaa_game_id'], row['sportsbook_claimed'], row['wayback_url'])


def run(package, cache, starts_path, output):
    def rows(path):
        with Path(path).open(newline='') as f:
            return list(csv.DictReader(f))
    source_rows = rows(package / 'wayback_2025_odds_spotcheck.csv')
    fetches = {r['url']: r for r in json.loads((cache / 'fetch.json').read_text())}
    source_fetches = {r['wayback_url']: r for r in rows(package / 'wayback_fetch_log.csv')}
    starts = {r['ncaa_game_id']: r for r in rows(starts_path)}
    prior = {r['record_id']: r for r in rows(Path('reports/grok_stage3_record_checks.csv'))}
    seen, results = set(), []
    for row in source_rows:
        ids = row['odds_record_ids'].split(',')
        if len(ids) != 2 or seen.intersection(ids):
            raise ValueError('Duplicate or incomplete record IDs')
        seen.update(ids)
        supplied_fetch = source_fetches[row['wayback_url']]
        fetch = fetches[supplied_fetch['raw_fetch_url']]
        if fetch['status'] != 200 or fetch['final_url'] != fetch['url']:
            raise ValueError('Failed fetch or redirected capture')
        content = (cache / (fetch['page_key'] + '.html')).read_bytes()
        if hashlib.sha256(content).hexdigest() != fetch['sha256']:
            raise ValueError('Cached bytes changed')
        capture = capture_time(fetch['url'], fetch['memento_datetime'])
        if capture.isoformat() != row['capture_ts_utc'].replace('Z', '+00:00'):
            raise ValueError('Supplier capture timestamp differs')
        if row['sportsbook_claimed'] == 'BetMGM':
            observed = parse_mgm(content, row['away'], row['home'])
            for side in ['home', 'away']:
                exact, rounded = american_from_decimal(observed[side + '_decimal'])
                observed[side + '_american_unrounded'] = str(exact)
                observed[side + '_american'] = rounded
        elif row['sportsbook_claimed'] == 'FanDuel' and row['home'] == 'Utah' and row['away'] == 'Syracuse':
            observed = parse_article(content)
        else:
            raise ValueError('Unexpected source or matchup')
        for side in ['home', 'away']:
            if observed[side + '_american'] != int(row[side + '_ml_record']):
                raise ValueError('Observed price mismatch')
        for record_id in ids:
            old = prior[record_id]
            side = old['selection_role']
            if (old['ncaa_game_id'] != row['ncaa_game_id'] or old['market'] != 'moneyline'
                or old['sportsbook'] != row['sportsbook_claimed'] or old['archive_url'] != row['wayback_url']
                or team_key(old['selection']) != team_key(row[side])
                or int(old['american_odds']) != observed[side + '_american']):
                raise ValueError('Record ID does not match existing audit identity')
        official = starts[row['ncaa_game_id']]
        pregame = before_start(capture, official['scheduled_start_utc'])
        results.append({**row, **observed, 'official_scheduled_start_utc': official['scheduled_start_utc'],
                        'official_source_url': official['official_source_url'],
                        'independent_status': 'VERIFIED_PREGAME_DISPLAY' if pregame else 'DISPLAY_VERIFIED_CAPTURE_AFTER_START',
                        'exact_sportsbook_quote_timestamp': None,
                        'permission_status': 'UNRESOLVED_NOT_APPROVED',
                        'independent_capture_utc': capture.isoformat(), 'fetch_sha256': fetch['sha256']})
    summary = {'records': len(seen), 'games': len({r['ncaa_game_id'] for r in results}),
               'game_book_capture_pairs': len({snapshot_key(r) for r in results}),
               'archive_pages': len({r['wayback_url'] for r in results}),
               'pregame_records': 2 * sum(r['independent_status'] == 'VERIFIED_PREGAME_DISPLAY' for r in results)}
    with output.open('x') as f:
        json.dump({'summary': summary, 'checks': results}, f, indent=2)
        f.write('\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ['package', 'cache', 'starts', 'output']:
        parser.add_argument('--' + arg, type=Path, required=True)
    args = parser.parse_args()
    run(args.package, args.cache, args.starts, args.output)
