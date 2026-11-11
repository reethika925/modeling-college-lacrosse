# Data inventory

- Dataset: NCAA Division I Men's Lacrosse 2022–2023 team-season statistics (SCORE)
- Source webpage: https://data.scorenetwork.org/lacrosse/lacrosse_ncaa_div1.html
- Exact download URL: https://data.scorenetwork.org/data/lacrosse_men_ncaa_div1_2022_2023.csv
- Collection attempt (America/New_York): 2026-11-09T20:38:34-05:00
- Date downloaded (America/New_York): 2026-11-09T20:38:36-05:00
- Local file path: `data/raw/score/lacrosse_men_ncaa_div1_2022_2023.csv`
- Source page HTTP status: 200
- CSV HTTP response status: 200
- CSV Content-Type: `text/csv; charset=utf-8`
- Robots.txt HTTP status: {'https://data.scorenetwork.org/robots.txt': 200}
- Collection status: SUCCESS
- SHA-256 (raw file bytes): `fce6600ec0425f0d36228d68399a3e5bd25673f8cb3635569051e7cd8eb70c39`
- Downloaded size in bytes: 9938

- Actual row count: 72
- Actual column count: 23
- Fully duplicate rows: 0
- Total missing cells (pandas default NA recognition): 0
- Rows with at least one missing value: 0
- Publisher reports 72 rows and 22 columns; actual dimensions match: False

## Column names and missing values

| Column | Missing cells |
| --- | ---: |
| `Team` | 0 |
| `Conference` | 0 |
| `avg_assists` | 0 |
| `avg_caused_turnovers` | 0 |
| `clearing_pctg` | 0 |
| `total_faceoffs` | 0 |
| `faceoff_wins` | 0 |
| `faceoff_win_pct` | 0 |
| `avg_goals` | 0 |
| `avg_goals_allowed` | 0 |
| `avg_ground_balls` | 0 |
| `man_down_defence_pctg` | 0 |
| `man_up_offense_pctg` | 0 |
| `avg_scoring_margin` | 0 |
| `opp_clear_pctg` | 0 |
| `avg_points` | 0 |
| `avg_saves` | 0 |
| `shot_pctg` | 0 |
| `avg_turnovers` | 0 |
| `W` | 0 |
| `L` | 0 |
| `win_loss_pctg` | 0 |
| `shots_per_game` | 0 |

Dimension discrepancy: the publisher reports 72 × 22, but the linked CSV contains 72 × 23. All downloaded columns are preserved; the webpage's dimension description may be outdated.

## Provenance and known limitations

- Each record is a team-season aggregate, not an individual game. There are no game dates, opponents, game scores, or sportsbook odds in this collection.
- The publisher labels the coverage 2022–2023. The file itself has no season/year field; do not infer that it contains separate observations for both calendar years.
- The publisher credits Jack Fay, A.J. Dykstra, and Ivan Ramler (published July 24, 2023), and identifies NCAA statistics as its underlying source. This download is from SCORE, not directly from NCAA.
- Raw bytes are preserved without imputation, deduplication, or statistics corrections. Missing values and duplicate rows are reported, not silently changed.
- A successful CSV/schema check verifies format and basic identity, not the accuracy of every statistic. The publisher may revise the file; the checksum identifies this exact download.
- This task collects only the linked men's dataset. No models, additional seasons, or odds have been collected.

<!-- games-collection:start -->
## Task 2 — 2025 game-by-game results

- Dataset: NCAA Casablanca DI men's lacrosse scoreboard
- Source webpage: https://www.ncaa.com/scoreboard/lacrosse-men/d1
- Exact download URLs: `source_url` in each CSV row and the collection log; daily URL pattern in validation report.
- Inventory updated: 2026-11-09T21:00:12-05:00; original per-response retrieval dates are in the raw metadata and collection log.
- Local file: `data/processed/lacrosse_games_2025.csv`
- Status: INCOMPLETE; season completeness: NOT_VERIFIED
- Rows: 580; columns: 34; completed: 580; unique teams: 77
- Verified dates: 81/181; failed or unchecked: 100; HTTP failures: {'404': 100}
- Missing cells: 4572; full column names and by-column counts in `reports/games_2025_validation.md`.
- Duplicate IDs: 0 after 1 documented duplicate removal; raw duplicate IDs: 1
- SHA-256: `79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3`
- Independent NCAA championship validation: PASS; https://www.ncaa.com/history/lacrosse-men/d1
- Parsing: explicit home/away objects, source game IDs and integer scores; raw source bytes unchanged.
- Limitations: failed dates unverified; numeric team IDs, venues and neutral flags absent; TBA times unknown; postseason metadata incomplete.
- Game-level records are distinct from Task 1 team-season aggregates. No additional seasons, boxscores, odds or models collected.
<!-- games-collection:end -->
