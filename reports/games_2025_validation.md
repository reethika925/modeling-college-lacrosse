# 2025 NCAA DI men's lacrosse game results validation

- Report generated (America/New_York): 2026-11-09T21:00:12-05:00
- Source: NCAA Casablanca DI men's lacrosse scoreboard
- Official scoreboard: https://www.ncaa.com/scoreboard/lacrosse-men/d1
- Exact daily URL pattern: `https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/YYYY/MM/DD/scoreboard.json`
- Window: 2025-01-01 through 2025-06-30, inclusive
- Output: `data/processed/lacrosse_games_2025.csv`
- SHA-256: `79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3`
- Collection status: INCOMPLETE — unverified dates remain
- Season completeness: NOT_VERIFIED

## Source choice and parsing

Sources were investigated in the requested order. Ordinary Python requests retrieved the NCAA HTML scoreboard with HTTP 200; the browsing tool encountered a JavaScript challenge. NCAA daily Casablanca JSON was selected because actual responses contained regular-season games and the championship, explicit home/away objects, source game IDs, scores, dates and winner flags. ESPN's robots.txt returned HTTP 403, so its candidate scoreboard URLs were not requested. No access restrictions were bypassed.

`reports/games_source_probes.json` records status, content type, event count and actual schema samples. Original probe bodies are cached in `data/raw/games/2025/probes/`. March 15 returned 32 games, May 26 returned one, and January 1 returned HTTP 404 with an XML error.

The parser reads `games[].game`, preserves `gameID` as a string, and uses the explicit `home` and `away` objects. It parses `startDate` and nonempty integer score strings. Source winner flags are retained and checked against scores independently. The `lacrosse-men/d1` URL selects gender and division; individual game objects do not repeat division labels. No other sport or division was queried.

## Results

| Check | Result |
| --- | ---: |
| Raw game records | 581 |
| Raw duplicate game IDs (extra rows) | 1 |
| Evidence-backed duplicate records removed | 1 |
| Processed games | 580 |
| Columns | 34 |
| Completed games | 580 |
| Completed games with valid scores | 580 |
| Unique teams (source SEO slugs) | 77 |
| Remaining duplicate game IDs | 0 |
| Duplicate unordered matchups on same date | 0 |
| Games with negative scores | 0 |
| Games with invalid score formats | 0 |
| Completed games missing scores | 0 |
| Completed tied games | 0 |
| Winner disagreements | 0 |
| Completed games missing winner | 0 |
| Overtime games | 48 |
| Dates requested | 181 |
| Dates with verified JSON | 81 |
| Failed or unchecked dates | 100 |

Actual game dates: 2025-02-01 through 2025-05-26.
Statuses: `{'final': 580}`.

### Games by month

| Month | Games |
| --- | ---: |
| 2025-02 | 159 |
| 2025-03 | 210 |
| 2025-04 | 161 |
| 2025-05 | 50 |

### Missing values

Total missing cells: 4572.

| Column | Missing cells |
| --- | ---: |
| `game_id` | 0 |
| `season` | 0 |
| `game_date` | 0 |
| `game_datetime_utc` | 563 |
| `home_team` | 0 |
| `away_team` | 0 |
| `home_team_id` | 580 |
| `away_team_id` | 580 |
| `home_score` | 0 |
| `away_score` | 0 |
| `winner` | 0 |
| `game_status` | 0 |
| `neutral_site` | 580 |
| `venue` | 580 |
| `postseason` | 563 |
| `source_name` | 0 |
| `source_url` | 0 |
| `home_team_slug` | 0 |
| `away_team_slug` | 0 |
| `home_team_code` | 0 |
| `away_team_code` | 0 |
| `home_winner_flag` | 0 |
| `away_winner_flag` | 0 |
| `bracket_round` | 563 |
| `bracket_id` | 563 |
| `final_message` | 0 |
| `current_period` | 0 |
| `overtime` | 0 |
| `start_time_text` | 0 |
| `start_time_epoch_raw` | 0 |
| `home_score_raw` | 0 |
| `away_score_raw` | 0 |
| `invalid_score_format` | 0 |
| `game_page_url` | 0 |

## Duplicate investigation

The NCAA lists game ID `6311207` (Le Moyne–Lafayette, 4–15) on both February 22 and February 23, with the same game detail URL. Lafayette's official final recap confirms February 22. `reports/games_2025_duplicate_resolutions.json` records that evidence and selects the existing February 22 record. Both raw responses remain unchanged; both duplicate rows are exported to `reports/games_2025_duplicate_records.csv`. No scores, dates, IDs or venues are edited or invented. Other unresolved duplicate IDs would remain visible and fail validation.

Evidence: https://goleopards.com/news/2025/2/22/mens-lacrosse-mens-lacrosse-dominates-le-moyne-on-the-road.aspx

## Independent championship validation

Result: **PASS**.
Source: https://www.ncaa.com/history/lacrosse-men/d1
NCAA history record: 2025 | Cornell (18-1) | Connor Buczek | 13-10 | Maryland | Foxborough, Mass.
Evidence retrieved: 2026-11-09T20:57:05-05:00; HTTP 200.
The dataset must contain exactly one final Cornell–Maryland game on May 26, 2025, with Cornell 13, Maryland 10 and Cornell as winner. This comparison never inserts or corrects a game.

## Coverage and failures

Latest failed HTTP statuses by date: `{'404': 100}`.
HTTP 404 means no daily JSON object was available. It is not counted as a verified empty day. Only a schema-valid HTTP 200 JSON response with `games: []` establishes an empty day. Every requested date has a row in `reports/games_collection_log.csv`; resumed attempts append new rows. Original successful retrieval timestamps, HTTP status and SHA-256 values are retained in the raw metadata files. This report uses the latest state for each requested date, not the count of all historical log rows.

Failed or unchecked dates:

2025-01-01, 2025-01-02, 2025-01-03, 2025-01-04, 2025-01-05, 2025-01-06, 2025-01-07, 2025-01-08, 2025-01-09, 2025-01-10, 2025-01-11, 2025-01-12, 2025-01-13, 2025-01-14, 2025-01-15, 2025-01-16, 2025-01-17, 2025-01-18, 2025-01-19, 2025-01-20, 2025-01-21, 2025-01-22, 2025-01-23, 2025-01-24, 2025-01-25, 2025-01-26, 2025-01-27, 2025-01-28, 2025-01-29, 2025-01-30, 2025-02-03, 2025-02-05, 2025-02-06, 2025-02-13, 2025-02-20, 2025-03-10, 2025-03-20, 2025-03-24, 2025-03-27, 2025-03-30, 2025-03-31, 2025-04-02, 2025-04-03, 2025-04-07, 2025-04-09, 2025-04-10, 2025-04-14, 2025-04-21, 2025-04-22, 2025-04-28, 2025-05-05, 2025-05-06, 2025-05-08, 2025-05-09, 2025-05-12, 2025-05-13, 2025-05-14, 2025-05-15, 2025-05-16, 2025-05-19, 2025-05-20, 2025-05-21, 2025-05-22, 2025-05-23, 2025-05-25, 2025-05-27, 2025-05-28, 2025-05-29, 2025-05-30, 2025-05-31, 2025-06-01, 2025-06-02, 2025-06-03, 2025-06-04, 2025-06-05, 2025-06-06, 2025-06-07, 2025-06-08, 2025-06-09, 2025-06-10, 2025-06-11, 2025-06-12, 2025-06-13, 2025-06-14, 2025-06-15, 2025-06-16, 2025-06-17, 2025-06-18, 2025-06-19, 2025-06-20, 2025-06-21, 2025-06-22, 2025-06-23, 2025-06-24, 2025-06-25, 2025-06-26, 2025-06-27, 2025-06-28, 2025-06-29, 2025-06-30

## Limitations and permitted alternatives

- Date coverage gaps prevent a whole-season completeness claim. Genuine games from successful dates are saved, including postseason. Failed dates cannot be proved empty by this endpoint.
- Numeric team IDs, venue and neutral-site flags are absent from the verified JSON schema and remain missing. Verified SEO slugs and short codes are separate fields. Source home/away labels at neutral sites are retained without assuming the first team is home.
- Regular-season TBA start times have placeholder epochs. UTC timestamps stay missing for TBA games; the raw epoch is retained separately. No actual start time is inferred.
- Postseason=True requires bracket metadata. Missing bracket fields leave postseason unknown; they do not establish a regular-season game. Conference-tournament classification is incomplete.
- Cancellation and postponement records are retained if supplied, with missing scores preserved. The source may omit such contests. Overtime is read from the source's finalMessage/currentPeriod.
- For unresolved dates, consult the official historical scoreboard in a normal browser or public 2025 team schedules. Save any permitted manual export separately with its URL, date and provenance. Do not insert inferred games, bypass a challenge, or save an HTML error as JSON.

## Reproduce

```bash
conda activate dsf-lacrosse
python src/collect_games.py --season 2025 --probe-only
python src/collect_games.py --season 2025 --start-date 2025-01-01 --end-date 2025-06-30 --resume
python src/collect_games.py --season 2025 --start-date 2025-01-01 --end-date 2025-06-30 --offline
python -m pytest -q
```

Exit code 2 means coverage is incomplete or a required data check failed. The partial CSV and reports are still saved. Offline mode validates cache and previous failure logs without making requests.

## First ten actual rows

```csv
game_id,season,game_date,game_datetime_utc,home_team,away_team,home_team_id,away_team_id,home_score,away_score,winner,game_status,neutral_site,venue,postseason,source_name,source_url,home_team_slug,away_team_slug,home_team_code,away_team_code,home_winner_flag,away_winner_flag,bracket_round,bracket_id,final_message,current_period,overtime,start_time_text,start_time_epoch_raw,home_score_raw,away_score_raw,invalid_score_format,game_page_url
6309366,2025,2025-02-01,,Iona,Hofstra,,,2,20,Hofstra,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,iona,hofstra,IONA,HOFSTR,False,True,,,FINAL,FINAL,False,TBA,1738386000,2,20,False,https://www.ncaa.com/game/6386028
6309480,2025,2025-02-01,,Penn St.,Colgate,,,14,9,Penn St.,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,penn-st,colgate,PENNST,COLGAT,True,False,,,FINAL,FINAL,False,TBA,1738386000,14,9,False,https://www.ncaa.com/game/6386042
6309665,2025,2025-02-01,,Georgetown,Loyola Maryland,,,13,6,Georgetown,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,georgetown,loyola-maryland,GTOWN,LOY MD,True,False,,,FINAL,FINAL,False,TBA,1738386000,13,6,False,https://www.ncaa.com/game/6386077
6309779,2025,2025-02-01,,Lehigh,Rutgers,,,6,10,Rutgers,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,lehigh,rutgers,LEHIGH,RUTGER,False,True,,,FINAL,FINAL,False,TBA,1738386000,6,10,False,https://www.ncaa.com/game/6386115
6309860,2025,2025-02-01,,High Point,Navy,,,10,14,Navy,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,high-point,navy,HIGHPT,NAVY,False,True,,,FINAL,FINAL,False,TBA,1738386000,10,14,False,https://www.ncaa.com/game/6386180
6309951,2025,2025-02-01,,Duke,Bellarmine,,,26,7,Duke,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,duke,bellarmine,DUKE,BELLAR,True,False,,,FINAL,FINAL,False,TBA,1738386000,26,7,False,https://www.ncaa.com/game/6386233
6310011,2025,2025-02-01,,Bucknell,Merrimack,,,23,7,Bucknell,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,bucknell,merrimack,BUCKNL,MERMCK,True,False,,,FINAL,FINAL,False,TBA,1738386000,23,7,False,https://www.ncaa.com/game/6386268
6310061,2025,2025-02-01,,Denver,Johns Hopkins,,,10,13,Johns Hopkins,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,denver,johns-hopkins,DENVER,HOPKNS,False,True,,,FINAL,FINAL,False,TBA,1738393200,10,13,False,https://www.ncaa.com/game/6386279
6310104,2025,2025-02-01,,Lafayette,Air Force,,,11,8,Lafayette,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,lafayette,air-force,LAFAYE,AIRFOR,True,False,,,FINAL,FINAL,False,TBA,1738386000,11,8,False,https://www.ncaa.com/game/6386291
6310134,2025,2025-02-01,,Hampton,Mercer,,,3,23,Mercer,final,,,,NCAA Casablanca DI men's lacrosse scoreboard,https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/01/scoreboard.json,hampton,mercer,HAMPTN,MERCER,False,True,,,FINAL,FINAL,False,TBA,1738386000,3,23,False,https://www.ncaa.com/game/6386304
```
