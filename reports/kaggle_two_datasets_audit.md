# Kaggle two-dataset audit

Audit generated (America/New_York): 2026-11-09T21:39:41-05:00

**Neither dataset solves the 2025 NCAA Division I men's historical sportsbook odds problem.** Both requested releases were downloaded publicly and their actual CSVs inspected. There are zero eligible 2025 NCAA men's lacrosse game records, zero verified matching pre-game odds, and zero matches to the project's 580 games. Professional lacrosse was not substituted for NCAA data.

Existing NCAA CSV SHA-256: `79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3`; rows: 580. All 223 pre-existing files in the preservation manifest retain their checksums.

## Official metadata, access and original files

Metadata and complete file listings came from Kaggle's official `/api/v1/datasets/view/OWNER/SLUG` and `/api/v1/datasets/list/OWNER/SLUG` endpoints. `view.files` was empty, so the separate listing was used; its pagination token was empty. Both public downloads returned an official storage redirect followed by HTTP 200 `application/zip`, without authentication. Archives and extracted CSV bytes remain unchanged under `research/kaggle/raw/`. CRCs, filenames, sizes and SHA-256 checksums were verified. Original metadata, listing responses, download URLs and retrieval timestamps are retained alongside them.

| Dataset | Version | License shown by Kaggle | Archive bytes | CSV bytes | Inspection |
| --- | ---: | --- | ---: | ---: | --- |
| [harsh21x/live-sports-betting-odds-snapshot](https://www.kaggle.com/datasets/harsh21x/live-sports-betting-odds-snapshot) | 1 | CC0: Public Domain | 2703 | 22007 | VERIFIED_FILES_INSPECTED |
| [tjmulderig/professional-lacrosse-statistics-pll-mll](https://www.kaggle.com/datasets/tjmulderig/professional-lacrosse-statistics-pll-mll) | 5 | CC0: Public Domain | 33676 | 136440 | VERIFIED_FILES_INSPECTED |

| Original file | Bytes | Rows | Columns |
| --- | ---: | ---: | ---: |
| `sports.csv` | 22007 | 225 | 10 |
| `2019_postseason_stats.csv` | 22768 | 224 | 37 |
| `2019_stats.csv` | 41114 | 383 | 37 |
| `2020_stats.csv` | 33428 | 318 | 37 |
| `Lacrosse Stats - 2021_postseason_stats.csv` | 14337 | 148 | 35 |
| `Lacrosse Stats - 2021_stats.csv` | 24793 | 260 | 34 |

## 1. Live Sports Betting Odds Snapshot — actual contents

`sports.csv` has 225 rows and 10 columns, including the preserved exported index `Unnamed: 0`. The metadata describes singular `sport_title` and `bookmaker`; the actual headers are `sports_title` and `bookmakers`. Analysis uses the actual headers.

Actual columns: `Unnamed: 0`, `sports_title`, `commence_time`, `home_team`, `away_team`, `bookmakers`, `market`, `team`, `price`, `point`.

One row represents an outcome for a market at a bookmaker. The file has 13 distinct competition/start/home/away event tuples.

### Actual competition and market values

| Competition label | Rows |
| --- | ---: |
| FIFA World Cup | 62 |
| MLB | 54 |
| MiLB | 54 |
| PLL | 24 |
| ATP Halle Open | 16 |
| League of Ireland | 11 |
| MMA | 4 |

Markets: `{'h2h': 137, 'spreads': 88}`. No totals market appears.
Event years: `[2026]`. Start-time range: 2026-06-19T18:08:00+00:00 through 2026-06-19T22:41:00+00:00.
The publisher describes a single snapshot collected June 19, 2026. Every actual event start is on that date. This is not 2025 coverage or a historical price series.

### Lacrosse records

All 24 lacrosse rows are labeled `PLL` and concern New York Atlas (home) versus Boston Cannons (away), scheduled June 19, 2026 at 22:00 UTC. They contain 12 moneyline and 12 spread outcome rows, with two outcomes per market per book. None is labeled NCAA or college lacrosse.

The six PLL bookmakers are: BetMGM, BetOnline.ag, BetRivers, Caesars, DraftKings, FanDuel.
The complete file names eleven bookmakers: FanDuel, Bovada, BetRivers, BetOnline.ag, Caesars, DraftKings, BetMGM, Fanatics, MyBookie.ag, BetUS, LowVig.ag.

Example original PLL moneyline rows: Boston Cannons at DraftKings, decimal price 1.91; New York Atlas at DraftKings, decimal price 1.83. These are source values, not project-generated prices. They were not exported to the project's NCAA odds pilot or matched to NCAA games.

### Provenance, timestamps and quality

Bookmaker-labeled prices and spread points are present. The uploader attributes them to The Odds API via RapidAPI; this attribution is not independent authentication of the original bookmaker capture. The original upstream JSON and capture process are absent.

`commence_time` is an event start time. There is no quote timestamp, bookmaker `last_update`, snapshot/capture timestamp column, source event ID, or live/pre-game flag. Kaggle version/file creation times and the publisher's collection date are available as metadata, but must not be relabeled as per-quote timestamps. Some event starts precede the upload time. Pre-game status of every quote cannot be established, and line movement cannot be reconstructed from a single snapshot.

All 137 moneyline `point` values are null, as expected for that market; all 88 spread rows have points. Four rows have decimal price 1.0, which is not a usable conventional decimal quote above 1.0. They are flagged and preserved. No full-row duplicates were found.

### NCAA compatibility

NCAA/college lacrosse rows: 0. Any-sport 2025 rows: 0. Direct NCAA team-name overlap: []. The competition and year checks eliminate every row before an odds join. Eligible 2025 NCAA pre-game odds: **0**. NCAA game matches: **0**. No fuzzy professional-to-college matching was attempted.

## 2. Professional Lacrosse Statistics — actual contents

The five files contain **1,333 raw rows**, with varying schemas. They are player-season or player-season-segment aggregates, with player/team splits where teamId exists. They are not team-game results. `gamesPlayed` aggregates multiple appearances, and there are no event opponents, game dates, sportsbook names, odds prices or quote timestamps.

2019 and 2020 files explicitly encode `statLeague` values `PLL` and `MLL`. The 2021 files do not have `statLeague` or `teamId`; exact row-level league/team assignment is therefore **UNVERIFIED from those CSVs**. The uploader describes professional outdoor lacrosse and the PLL's third-season context, but that context is not an observed league column. The 2021 regular file also lacks `seasonSegment`; its regular-season label comes from the file context, not a populated column.

### Per-file columns and observed groups

#### 2019_postseason_stats.csv

Actual columns:

```text
Unnamed: 0, player_name, teamId, gamesPlayed, points, goals, twoPointGoals, assists, powerPlayGoals, shortHandedGoals, pim, shots, twoPointShots, shotsOnGoal, twoPointShotsOnGoal, SOFF, groundBalls, faceoffs, faceoffsWon, faceoffsLost, turnovers, causedTurnovers, goalsAgainst, GAA, twoPointGoalsAgainst, twoPtGaa, saves, numPenalties, savePct, goalieWins, goalieLosses, goalieTies, gamesStarted, tof, statLeague, seasonSegment, year
```

Observed year/league/segment groups:

```json
[
  {
    "year": 2019,
    "statLeague": "MLL",
    "seasonSegment": "post",
    "rows": 85
  },
  {
    "year": 2019,
    "statLeague": "PLL",
    "seasonSegment": "post",
    "rows": 139
  }
]
```

Unique player names: 218; gamesPlayed range: [1, 3]; full-row duplicates: 0; duplicate rows after excluding exported index: 4.
#### 2019_stats.csv

Actual columns:

```text
Unnamed: 0, player_name, teamId, gamesPlayed, points, goals, twoPointGoals, assists, powerPlayGoals, shortHandedGoals, pim, shots, twoPointShots, shotsOnGoal, twoPointShotsOnGoal, SOFF, groundBalls, faceoffs, faceoffsWon, faceoffsLost, turnovers, causedTurnovers, goalsAgainst, GAA, twoPointGoalsAgainst, twoPtGaa, saves, numPenalties, savePct, goalieWins, goalieLosses, goalieTies, gamesStarted, tof, statLeague, seasonSegment, year
```

Observed year/league/segment groups:

```json
[
  {
    "year": 2019,
    "statLeague": "MLL",
    "seasonSegment": "regular",
    "rows": 219
  },
  {
    "year": 2019,
    "statLeague": "PLL",
    "seasonSegment": "regular",
    "rows": 164
  }
]
```

Unique player names: 368; gamesPlayed range: [0, 16]; full-row duplicates: 0; duplicate rows after excluding exported index: 0.
#### 2020_stats.csv

Actual columns:

```text
Unnamed: 0, player_name, teamId, gamesPlayed, points, goals, twoPointGoals, assists, powerPlayGoals, shortHandedGoals, pim, shots, twoPointShots, shotsOnGoal, twoPointShotsOnGoal, SOFF, groundBalls, faceoffs, faceoffsWon, faceoffsLost, turnovers, causedTurnovers, goalsAgainst, GAA, twoPointGoalsAgainst, twoPtGaa, saves, numPenalties, savePct, goalieWins, goalieLosses, goalieTies, gamesStarted, tof, statLeague, seasonSegment, year
```

Observed year/league/segment groups:

```json
[
  {
    "year": 2020,
    "statLeague": "MLL",
    "seasonSegment": "regular",
    "rows": 163
  },
  {
    "year": 2020,
    "statLeague": "PLL",
    "seasonSegment": "regular",
    "rows": 155
  }
]
```

Unique player names: 298; gamesPlayed range: [0, 7]; full-row duplicates: 0; duplicate rows after excluding exported index: 0.
#### Lacrosse Stats - 2021_postseason_stats.csv

Actual columns:

```text
player_name, gamesPlayed, points, totalGoals, goals, twoPointGoals, assists, shots, shotPct, shotsOnGoal, SOGpct, twoPointShots, twoPointPct, 2ptShotsOnGoal, faceoffs, faceoffsWon, faceoffsLost, faceoffPct, saves, savePct, goalsAgainst, GAA, twoPointGoalsAgainst, twoPtGaa, tof, numPenalties, pim, powerPlayGoals, Power Play Shots, shortHandedGoals, shortHandedShots, shortHandedGoalsAgainst, powerPlayGoalsAgainst, seasonSegment, year
```

Observed year/league/segment groups:

```json
[
  {
    "year": 2021,
    "seasonSegment": "post",
    "rows": 148
  }
]
```

Unique player names: 148; gamesPlayed range: [1, 5]; full-row duplicates: 0; duplicate rows after excluding exported index: 0.
#### Lacrosse Stats - 2021_stats.csv

Actual columns:

```text
player_name, gamesPlayed, points, totalGoals, goals, twoPointGoals, assists, shots, shotPct, shotsOnGoal, SOGpct, twoPointShots, twoPointPct, 2ptShotsOnGoal, faceoffs, faceoffsWon, faceoffsLost, faceoffPct, saves, savePct, goalsAgainst, GAA, twoPointGoalsAgainst, twoPtGaa, tof, numPenalties, pim, powerPlayGoals, Power Play Shots, shortHandedGoals, shortHandedShots, shortHandedGoalsAgainst, powerPlayGoalsAgainst, year
```

Observed year/league/segment groups:

```json
[
  {
    "year": 2021,
    "rows": 260
  }
]
```

Unique player names: 260; gamesPlayed range: [0, 9]; full-row duplicates: 0; duplicate rows after excluding exported index: 0.

All recorded years are 2019, 2020 and 2021; there are no 2025 rows. `2019_postseason_stats.csv` has four duplicate statistic rows hidden by different exported index values. The two 2021 files have an entirely null `shortHandedGoalsAgainst` column (148 and 260 nulls respectively). No cleaning or deduplication was applied. Full missing-value counts and first-three-row examples for every CSV are in `research/kaggle/audit_summary.json`.

NCAA 2025 game records: **0**. Bookmaker/quote-time coverage: **absent**. Verified NCAA historical pre-game odds: **0**. NCAA game matches: **0**. A player's possible college history does not convert these professional-season statistics into NCAA game observations.

## License and usage limitations

Both Kaggle metadata responses list **CC0: Public Domain** for these releases. This is the uploader's license declaration, not proof that every underlying third-party right has been cleared. In particular, the odds uploader attributes the content to The Odds API; its provider terms restrict standalone raw-data redistribution. The professional dataset credits statistics supplied by a PLL representative, but no additional source-rights documentation was included in the downloaded archive. Preserve these provenance qualifications when citing or redistributing either dataset.

Provider terms reference: https://the-odds-api.com/terms-and-conditions.html

## Reproduce

```bash
conda activate dsf-lacrosse
python src/audit_kaggle.py --download
python src/audit_kaggle.py
python -m pytest -q
```

The downloader fills missing public releases and preserves existing bytes. It pins dataset versions 1 and 5, checks the 10 MB size limit, and rejects unexpected schemas/archives. It does not read credentials. Default mode audits local files without network requests. Metadata/file integrity or access failures must be reported as UNVERIFIED rather than interpreted as empty suitable data.

## Official authentication fallback

Authentication was **not required for this audit**. If Kaggle later requires it, use Kaggle's official browser-based OAuth flow locally; never paste a token or credential file into chat:

```bash
conda activate dsf-lacrosse
python -m pip install kaggle
kaggle auth login
kaggle datasets files harsh21x/live-sports-betting-odds-snapshot
kaggle datasets files tjmulderig/professional-lacrosse-statistics-pll-mll
```

Official authentication instructions: https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication
No CLI installation, account login or token was needed or performed here. Any future authenticated download must still follow the dataset's actual access conditions; do not bypass a login or challenge.

## Decision

The first dataset can illustrate multi-bookmaker PLL odds structure and data-quality issues, but has the wrong league/year and no quote-time history for this project. The second can support professional player-statistics research, but contains no betting odds or 2025 NCAA games. **Neither supplies the historical NCAA odds needed by the current project.**
