# Grok Stage 2: historical games and team/player statistics

Generated: 2026-11-10T19:55:42+00:00. Existing environment: `dsf-lacrosse`, Python 3.11.18.

**Conclusion:** Grok's **578 nonduplicate 2025 game candidates** are supported, after two exclusions and the documented date resolutions. The stated **3,426 team rows and 143,834 player rows are arithmetic counts after exclusions, not independently certified valid statistical observations**. Additional missingness, identity, unit and reconciliation issues remain. Complete dataset-level technical approval and data-use authorization are **not granted**.

All 1,717 game rows, 3,428 team rows and 143,882 player rows were checked. No originals, processed datasets, predictions, models, figures or prior reports were modified. No odds were imported; no models were trained; no additional seasons or broad datasets were collected. Stage 1's ZIP/structural audit was not repeated.

## Evidence standard and verified counts

“School-corroborated result” means independently parsed official-school evidence agrees on competing teams, final score and calendar date. It does not automatically authenticate every metadata/statistical field or establish home advantage at a neutral venue. Supplied pages are source artifacts provided with the delivery; they are not independently time-stamped archival proof. Selected live official pages were also checked for the specifically disputed games. **Supplier `audit_status=verified` is never adopted as independent evidence.**

These counts describe independent content comparisons against saved primary-source artifacts. They do not claim that all 28 pages were refetched or that every saved artifact's origin was independently authenticated.

| Season | Physical imported games | Strict D-I vs D-I candidates after exclusions | School-corroborated eligible results | Remaining without checked school corroboration |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 567 | 559 | 134 | 425 |
| 2024 | 570 | 570 | 115 | 455 |
| 2025 | 580 | 578 | 129 | 449 |

There are **378 school-corroborated results**, and **1,329 remaining candidate results without that level of corroboration**. These latter counts do not mean the games are false: 2025 has substantial additional primary-source support described below. Current strict D-I vs D-I screening excludes eight 2023 lower-division-opponent games and two 2025 duplicate/wrong-season records. For a broader cohort of games *involving* a D-I team, the eight 2023 games are a scope decision rather than fictional results; the nonduplicate 2023 total remains 567.

The three season files have 74 / 75 / 72 distinct game dates, respectively. Coverage is **NOT_VERIFIED for all seasons**. Matching a partial schedule set is not a national season census. [Coverage CSV](grok_stage2_coverage.csv) gives the counts, date ranges, scope exclusions and explicit permission status.

### Existing primary NCAA evidence for 2025

This audit also independently read the project's **81 existing raw NCAA daily scoreboard JSON files**, without new requests. All **580 imported 2025 scores and home/away team identities** match raw payloads by NCAA game-page ID; **578 dates** match a raw occurrence. The two exceptions are Queens–Stony Brook and UMBC–Binghamton, whose corrected dates are supported by school evidence. The raw feed itself contains the two false extra listings later excluded; matching an official payload alone does not establish that every listing is a distinct real game.

Thus the 578 candidate 2025 results have local raw-source support plus the targeted correction evidence, while only 129 receive the additional checked-school corroboration. They should remain a **source-backed provisional cohort**, not a claim that 578 games form the complete, independently multi-source-verified season. [Raw-evidence reconciliation](grok_stage2_local_raw_evidence.csv).

## Files, schemas and identifiers

All files below are under `data/incoming/grok/stage1_28f5677d90c3/audit_package/`:

| Dataset | Rows | Columns |
| --- | ---: | ---: |
| `corrected/ncaa_lacrosse_games_2023_corrected.csv` | 567 | 45 |
| `corrected/ncaa_lacrosse_games_2024_corrected.csv` | 570 | 45 |
| `corrected/ncaa_lacrosse_game_index_2025_corrected.csv` | 580 | 26 |
| `corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv` | 3,428 | 44 |
| `corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv` | 143,882 | 37 |

Complete column lists, original-file checksums and per-column missing-value counts are in [the checks JSON](grok_stage2_checks.json), under `schemas`. Source URLs identify NCAA game/box-score pages, daily NCAA scoreboard URLs, and some ESPN-derived result metadata. They identify claimed origins; URL presence alone is not verification.

### Game-field meanings and limits

- `game_id` is the incoming NCAA **game-page identifier**, except the explicit ESPN-only identifier. `ncaa_legacy_game_id`, where supplied, is an alternate source identifier. Our existing CSV's `game_id` is generally a different namespace. Both must remain intact.
- `season`, `game_date`, `original_game_date` and `corrections_applied` describe season/date and supplier-claimed changes. Calendar-year consistency was checked. Missing original CSVs prevent authenticating every claimed before-value.
- `home_team`, `away_team`, associated numeric NCAA IDs, SEO slugs, full names and conference fields describe teams and source-designated orientation. They are not proof of actual home advantage. `neutral_site`, its basis and `venue` are incomplete; the 2025 index does not supply those venue fields.
- Scores are integer-valued counts serialized as strings such as `16.0`. `winner` exists in 2023/2024 and agrees with scores; the 2025 table has no winner column, so the winner is determined from the final scores for audit comparison only.
- `status`, `final_message`, `overtime`, `season_phase` and `bracket_round` are source result/context fields where present. All imported result statuses are final. Metadata such as `season_phase=regular_or_conference_tournament` does not distinguish every conference-tournament game.
- `start_time_utc`, `start_time_local_text` and `start_time_is_tba` require separate reliability checks. **537 games in 2023 and 553 in 2024 are marked TBA while carrying populated UTC times.** These are not certified kickoff times and must not establish pre-game availability. The 2025 index lacks an equivalent TBA flag.
- `espn_*` agreement flags, `audit_status`, `audit_basis`, `usable_result`, `usable_d1_vs_d1`, division flags and `suspected_duplicate_of` are supplier metadata. They are assessed separately and never substitute for original evidence or permission.

Three games lack both numeric team IDs: `6136266` (2023 UMBC–Mount St. Mary's), `espn_401658258` (2024 Princeton–Penn), and the excluded `6444405` (2025 Hampton–Fairfield). The first is newly final after the supplier's result correction and was omitted from its earlier final-game ID-gap list. No numeric IDs were invented. Observed nonblank numeric team IDs do not map to conflicting SEO slugs in the supplied game tables.

For cross-file audit joins only, integer-looking strings such as `43978.0` are converted to `43978` without floating-point rounding. Original strings are preserved. Jersey `0` is valid; `00` is not silently collapsed into `0`. No permanent NCAA player ID is supplied. Name/jersey/team/game keys can support within-game checks, not guaranteed identity tracking across an entire career.

## Game validation and the seven disputed cases

Across all 1,717 imported rows: zero duplicated game IDs, zero duplicate unordered same-date matchups, zero same-day repeated-team appearances after the supplied date fixes, zero missing/negative/noninteger final scores, zero ties, zero season/date-year conflicts, and zero supplied-winner disagreements. These internal checks alone would not detect the misdated LIU duplicate.

The independent parser read **28 usable saved school-season schedules**; the saved Harvard security-challenge response was rejected as evidence. It read **426 schedule cards**, including **408 scored results** and 18 nonscored cards. None of those nonscored/exhibition/cancelled-or-postponed cards overlaps an imported final on the same date and team pair. No scored schedule entry was left unmatched after explicit team-alias handling. This verifies the provided schedule subset only. No challenge was bypassed and no supplied comparison script was executed.

Schedules vary in score display: Vermont sometimes prints the winning score first even on a loss. The parser uses W/L plus the two scores to establish the school's own score, retaining the original display. It does not assume every displayed score is own-team-first. [Independent schedule comparison](grok_stage2_schedule_comparison.csv).

| Claimed correction | Independent finding | Proposed disposition |
| --- | --- | --- |
| UMBC–Binghamton `6449835` | UMBC 17–7 Binghamton belongs to **April 12, 2025**, not April 5. Binghamton–UAlbany `6386469` is correctly April 5. | Retain distinct games; accept imported date; propose the local date fix separately. |
| Hampton–Fairfield `6444405` | School schedules contain one Fairfield 29–4 win on **March 15**, canonical `6386334`. The extra March 13 result lacks independent support and duplicates that matchup/score. | Exclude the extra listing; retain March 15. |
| LIU–Quinnipiac `6455124` | A **genuine April 20, 2024 game**, canonical `6270089`, accounts for the score and statistical observations. The 2025 listing is a wrong-year duplicate. | Exclude the 2025 copy and its statistical copies; retain existing 2024 data. The exhibition explanation is unsupported. |
| Queens–Stony Brook `6454179` | Stony Brook's schedule confirms its 12–6 win at Queens on **February 16, 2025**. | Accept imported date; propose local February 15 → 16. |
| Le Moyne–Lafayette `6386400` | Le Moyne's schedule explicitly shows a date/location change and a 4–15 loss on **February 22, 2025**, at Syracuse's JMA Wireless Dome. | Accept February 22. Our local file already has it; do not change it again. |
| Detroit Mercy–Marquette `6138525` | Both schools' schedules show Marquette's 10–5 road win on **March 2, 2023**. | Current imported date is supported; missing original CSV prevents independently proving every original before-value. |
| UMBC–Mount St. Mary's `6136266` | UMBC and Mount schedules support a **February 24, 2023, 16–6 UMBC final**. | Current final result is supported. Do not invent missing original box statistics or team IDs. |

Official supporting pages: [Binghamton 2025](https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2025), [Hampton 2025](https://hamptonpirates.com/sports/mens-lacrosse/schedule/2025), [Fairfield 2025](https://fairfieldstags.com/sports/mens-lacrosse/schedule/2025), [Stony Brook 2025](https://stonybrookathletics.com/sports/mens-lacrosse/schedule/2025), [Le Moyne 2025](https://lemoynedolphins.com/sports/mens-lacrosse/schedule/2025), [Marquette 2023](https://gomarquette.com/sports/mens-lacrosse/schedule/2023), [Detroit Mercy 2023](https://detroittitans.com/sports/mens-lacrosse/schedule/2023), [UMBC 2023](https://umbcretrievers.com/sports/mens-lacrosse/schedule/2023), [Mount 2023](https://mountathletics.com/sports/mens-lacrosse/schedule/2023). Case-specific observations and access limits are recorded in [the official-check log](grok_stage2_official_checks.json).

### New finding: the LIU game and its 48 player records

Quinnipiac's [April 20, 2024 recap](https://gobobcats.com/news/2024/4/20/mens-lacrosse-qu-drops-matchup-at-liu-in-ot) reports the 10–9 overtime loss, matching scorers and team totals. Its [linked 2024 box-score page](https://gobobcats.com/sports/mens-lacrosse/stats/2024/liu/boxscore/21128) contains the same player lines but has an erroneous 2025 internal game date. This is another example of bad upstream metadata, not proof of a 2025 exhibition.

All **48** wrong-year player rows match existing 2024 identities using team, jersey and conservatively normalized names. All **14 non-time count fields** match numerically, including goals, assists, points, shots, SOG, ground balls, turnovers, caused turnovers, goalie saves/goals allowed, penalties, penalty seconds and faceoffs won/attempted. Both team statistical vectors also duplicate the retained 2024 vectors. The 2024 table already has **110 roster/player rows** for that game; the 48-row 2025 view is a subset, not 48 new players or observations to add.

Only the two goalie-time values differ: wrong-year rows have `3845.0`; retained 2024 rows have `64.0`. The official box shows **64:05** for Sean Gillman and Mason Oak: 3,845 seconds, or 64.083333 minutes. The retained values lose five seconds; the wrong-year values use seconds under a minutes label. Two evidence-backed duration proposals are included, but nothing was changed.

### Non-D-I opponents and repeated matchups

The eight strict D-I-vs-D-I scope exclusions in 2023 are St. Andrews–Hampton, Hampton–Wabash, and Hartford's games with Mitchell, Randolph, Saint Joseph (CT), Gordon, Salem State and Regis (MA). These have NAIA/lower-division opponents; they are retained as factual candidate records but flagged outside this strict modeling cohort.

**Correction to Grok's rationale:** Hartford itself remained Division I during the 2022–23 academic year. The university's [official transition announcement](https://www.hartford.edu/news/press-releases/2022/06/athletics-conference.aspx) places CCC competition in 2023–24. Its six opponents here are outside D-I; that keeps the eight-game D-I-vs-D-I exclusion count unchanged without retroactively calling Hartford D-III. A comprehensive season-specific membership reference was not supplied, so broad division assertions for every remaining team are not independently certified.

Repeated pairings alone are not duplicates. Penn–Princeton in March/May 2023 and Navy–Loyola in April 2024 are separate games with opposite winners, corroborated by schedules. Legitimate back-to-backs such as Navy, High Point, Mercer and Iona should not be removed merely for short rest. Same-date repeated teams are zero in the corrected tables. Georgetown–Notre Dame on May 18, 2024 is a nominal-orientation/neutral-site review: Georgetown's page says `vs` at Hempstead while the incoming nominal home side is Notre Dame. Its date/score are corroborated, but actual home advantage is not inferred.

## Exact comparison with our preserved 2025 CSV

The join uses our `game_page_url` suffix and the imported NCAA page `game_id`, not blindly equating differently named ID namespaces. Both source identifiers remain in [the 580-row comparison](grok_stage2_local_2025_comparison.csv).

| Comparison | Actual count |
| --- | ---: |
| Paired records / unique URL-ID correspondences | 580 / 580 |
| Same teams, orientation, calendar date and numeric final scores | 578 |
| Date conflicts | 2 |
| Score conflicts | 0 |
| Team/orientation conflicts | 0 |
| Imported records absent from our game-page ID set | 0 |
| Our records absent from the imported page-ID set | 0 |
| Propose exclusion in a future derived cohort | 2 |

The two date conflicts are local `6371921` → imported `6449835` (UMBC–Binghamton, April 5 → 12), and local `6383749` → imported `6454179` (Queens–Stony Brook, February 15 → 16). The 578 matching-result rows still include the two exclusions; the future 578-game candidate set therefore consists of **576 unchanged result matches plus two supported date fixes**, after removing two false extra listings. “Exact” here refers to the named result fields, not byte-identical files or identical metadata schemas.

**The 578 usable-count claim is supported as a candidate count, not national completeness or authorization.** No genuine result is found in only one of these two 2025 files after proper ID mapping. The checked school-page subset reveals no missing scored game, but genuine games elsewhere could still be absent from both. The previous collection's failed dates and completeness limitations remain unresolved.

## Team-game statistics: all 3,428 checked

Operational field definitions were checked against observed values, arithmetic and the NCAA statistics rules where applicable. A complete original data dictionary and raw box/PBP records are absent, so parser-specific semantics cannot be certified from names alone.

| Fields | Meaning / validation |
| --- | --- |
| `game_id`, `season`, dates, `start_time_utc` | Game reference, season, current/supplier-claimed original date and claimed clock |
| `team`, `team_id_ncaa`, `team_seo`, opponent/name/ID, `home_away`, `season_phase` | Team/opponent identities and source-designated role/context |
| `goals`, `goals_allowed` | Box/derived team goals for/against; compare with verified result separately |
| `final_score_scoreboard` | Source final score for that team, distinct from box goals |
| `assists` | Credited assists; no excess over team goals found |
| `shots`, `shots_on_goal`, `shooting_pct` | Shot counts and fractional shooting rate; check SOG ≤ shots, goals ≤ SOG and rate in [0,1] |
| `faceoffs_won`, `faceoffs_attempted` | Faceoff wins/attempts; check bounds and reciprocal team totals |
| `ground_balls`, `turnovers`, `caused_turnovers` | Standard credited event counts; do not force every team total to equal summed individual credits |
| `saves`, `goalie_goals_allowed` | Team/goalkeeper defensive counters; compare saves with opposing SOG and box goals where available |
| `clears_completed`, `clears_attempted` | Clear counts; completed ≤ attempted |
| `emo_goals`, `emo_opportunities` | Extra-man offense goals and opportunities, **not penalty counts** |
| `penalties`, `penalty_seconds`, `penalty_minutes` | Penalty count and durations; fractional minutes allowed, minutes × 60 agrees with seconds |
| `free_position_shots` | Generic source field with seven nonzero values (all 1), 3,327 zeros and 94 blanks; its meaning in this men's dataset is undocumented. Hold this field out of modeling until the original schema is obtained; do not infer women's data from the column name alone. |
| `box_team_stats_available`, `pbp_available`, `pbp_duplicate_rows_removed`, `pbp_goal_count_matches_box`, `faceoff_clear_source` | Supplier availability/processing/provenance flags; raw PBP is unavailable for independent reconstruction |
| `source_url`, division/QA/date-correction/game-audit fields | Source and supplier annotations, not independently certified permissions or blanket statistical accuracy |

All team game IDs exist in the supplied results. After derived integer-string key normalization, team and opponent IDs/names, roles, dates and seasons are consistent with the supplied game records. All `(game_id, team_id)` keys are unique. No negative, nonfinite, noninteger-count, faceoff-bound, clear-bound, shot-bound or penalty-duration contradictions were found. Numeric result IDs/roles are internally valid even when individual game provenance remains provisional.

| Nonzero team finding | Rows |
| --- | ---: |
| `EMO_GOALS_EXCEED_OPPORTUNITIES` | 11 |
| `MISSING_CORE_BOX_STATS` | 94 |
| `EXCLUDED_GAME_COPY` | 2 |
| `BOX_GOALS_VS_FINAL_RESULT` | 3 |
| `GOALS_ALLOWED_VS_RESULT` | 3 |
| `SAVES_OPPONENT_SOG_GOALS_RESIDUAL` | 3 |
| `PLAYER_GOAL_SUM_RESIDUAL` | 14 |

These categories can overlap. The ledger identifies **130 distinct team rows** with a review/exclusion flag. Of 3,428 rows, two are wrong-year LIU copies, yielding Grok's **3,426**. However:

- **94** retained rows explicitly have `box_team_stats_available=False` and lack core statistics. They must not be converted to zero-stat games.
- **11** rows violate the extra-man goal/opportunity constraint. NCAA's [2023 statistics manual, Section 9 Article 5](https://fs.ncaa.org/Docs/stats/Stats_Manuals/Lacrosse/mlax23.pdf) accounts for additional opportunities during nonreleasable penalties, so that situation does not justify these ratios. The official indexed text was reviewed; a direct PDF open timed out. No replacement numerator/denominator is invented.
- **Three** box goal totals differ from final results in overtime games `6147943`, `6147954`, `6147955`; the corresponding opposing goals-allowed totals also differ. Three save identities have residuals. This may reflect missing OT events, but missing original source evidence prevents determining the repair. Preserve final results and review the box fields separately.

**3,332** nonexcluded rows have the specified core box fields populated. **3,315** pass the basic numerical/identity screen across the broad supplied scope; **3,299** also pass the strict D-I-vs-D-I scope filter. These screens omit the separate aggregation-review flags and cannot certify source accuracy. **No complete independently source-verified team-stat count can be established.** A corroborated result does not verify every associated statistic.

The seven nonzero `free_position_shots` values are separate field-definition reviews in the proposals CSV. They are not automatically classified as impossible values, wrong-sport records or numerical-screen failures. The row-issue ledger above does not replace this schema-level uncertainty.

## Player-game statistics: all 143,882 checked

| Fields | Meaning / validation |
| --- | --- |
| Game/team/opponent IDs, season/date, `home_away` | Reference and role checks against game/team rows |
| `player_first`, `player_last`, raw-name counterparts, `jersey`, `position` | Supplied normalized/raw names and roster role; no permanent player ID |
| `started`, `participated` | Supplier boolean indicators; not automatically equivalent to independently verified games played |
| `goals`, `assists`, `points` | Individual counts; points = goals + assists wherever present |
| `shots`, `shots_on_goal`, `ground_balls`, `turnovers`, `caused_turnovers` | Individual credits; meaningful bounds checked, team-only attribution considered |
| `goalie_minutes`, `goalie_saves`, `goalie_goals_allowed` | Role-specific fields; missing for most non-goalies; duration units/precision are inconsistent |
| `penalties`, `penalty_seconds` | Count and duration, potentially including bench-related context |
| `faceoffs_won`, `faceoffs_attempted`, `faceoff_source` | Counts reportedly derived from PBP/name matching; raw evidence missing |
| `stat_level`, `source_url`, division/date-correction/game-audit annotations | Scope/source/supplier flags; `stat_level=game` throughout |

All player game/team references, season/date, team/opponent names and home/away roles match the supplied game/team tables. No duplicate within-game identity keys were found, including the derived normalized team-ID/jersey/name key. This does not establish global player identity across seasons. Zero-valued bench/roster rows and role-specific nulls are not treated as fabricated observations.

| Nonzero player finding | Rows |
| --- | ---: |
| `SOG_EXCEEDS_SHOTS` | 1 |
| `GOALS_EXCEED_SOG` | 1 |
| `GOALIE_TIME_LIKELY_SECONDS_NOT_MINUTES` | 966 |
| `EXCLUDED_GAME_COPY` | 48 |
| `MISSING_PLAYER_NAME_OR_TEAM_ID` | 222 |
| `NONPARTICIPANT_WITH_RECORDED_COUNT` | 168 |
| `TEAM_PLAYER_GOAL_AGGREGATE_REVIEW` | 567 |

The ledger flags **1,961 distinct player rows** for exclusion or further review; categories overlap. In addition, the two retained 2024 goalie durations have source-backed precision corrections not caught by the >300 screening threshold.

- Removing the **48 wrong-year duplicates** yields **143,834**, but that is not the number of genuine active-player appearances. There are **51,477 `participated=False` rows** in the original table and **92,357 nonexcluded rows marked participating**. A roster entry must not be counted as an appearance merely because it exists.
- **222 rows lack normalized and raw names**, although team/game/jersey identifiers are present. At least some are jersey-bearing roster rows with real nonzero statistics; they cannot all be dismissed as team-credit rows. Others may involve unattributed entries. Keep them available for team-total reconciliation, but hold player-identity use until source resolution. Jersey zero is valid and is not itself an error.
- **168 nonparticipant flags carry nonzero recorded counts.** Some are assists, shots or defensive credits; penalty-only cases require special care. This is a participation-definition/source issue: do not globally flip all flags or delete the statistical values.
- **One** player has SOG 3 versus shots 1 (`6269867`, Jacksonville jersey 5). **Another** has a goal but zero shots/SOG (`6386382`, Jacksonville jersey 3). Own/team-goal attribution and scorer definitions must be checked before inventing a correction; they are review flags rather than proof the whole game is invalid.
- **966 `goalie_minutes` values exceed 300**, strongly indicating mixed units, illustrated by 3,600 and 3,845. All **3,021 populated durations** need a consistent source-backed unit/precision policy; small values could also have lost seconds. No global divide-by-60 transformation is safe. The targeted official 64:05 example supports only its two proposed retained-row fixes.
- No negative/nonfinite statistics, fractional count values, points-identity violations, faceoff-win bounds or invalid boolean strings were found. Fractional minutes are allowed.

The basic count/identity/participation screen retains **143,442 broad-scope candidates**, or **143,083 with the strict D-I-vs-D-I filter**. It does **not** include clearance of the separate duration-unit and aggregation-review issues. These are screening counts, not independently verified player-stat counts or authorized modeling inputs.

### Player/team aggregation and field-definition caution

There are **3,336 team-game groups with player rows**, and **92 team-game groups without any player rows**. Missing groups remain missing, not zero. Among shared groups, nonzero aggregate differences occur as follows:

| Statistic summed from player rows vs team | Team-game differences |
| --- | ---: |
| goals | 14 |
| assists | 9 |
| shots | 71 |
| shots_on_goal | 40 |
| faceoffs_won | 14 |
| faceoffs_attempted | 24 |
| goalie_saves | 704 |
| goalie_goals_allowed | 676 |

Fourteen goal-sum residual groups affect 567 player rows, but a team-only/own-goal credit, an omitted participant or an OT omission can cause such a residual without making every player row incorrect. NCAA definitions also permit team-only attribution in other event totals. Ground-ball and turnover equality were deliberately not imposed as universal identities. Raw scorer/PBP evidence is required for attribution repairs. No residual was distributed across players or replaced with fictional statistics.

Goalkeeper counters are present in 3,018 team-game groups. Their available player sums differ from team saves in 704 groups and team goalie-goals-allowed in 676. These are **partial-coverage/attribution residuals**, not 704 or 676 proven bad individual records. For example, Penn State game `6085411` supplies Jack Fracyon's goalie line with 51.0 in the duration field and 18 saves, while the team has 21 saves; an omitted backup-goalie line could explain the gap. Neither the available saves nor the team total is overwritten. Goalie duration is deliberately not aggregated because units are mixed, and role-specific missing values remain null.

## Missing source evidence and permissions

The original omissions are not ZIP corruption. Five are directly relevant to this audit:

| Missing supplier original | Claim that cannot be fully independently checked |
| --- | --- |
| `/workspace/final_package/ncaa_lacrosse_games_2023.csv` | Every before/after date/result/status change and original record content |
| `/workspace/final_package/ncaa_lacrosse_games_2024.csv` | Original result content and earlier removal of three claimed phantoms before this delivered 570-row version |
| `/workspace/final_package/ncaa_lacrosse_game_index_2025.csv` | Supplier-original identity/date history and every transformation; our own 580-row file/raw cache is a separate supporting artifact, not an identical substitute for that missing file |
| `/workspace/final_package/ncaa_lacrosse_team_game_stats_2023_2025.csv` | Original box values, date edits, processing and units |
| `/workspace/final_package/ncaa_lacrosse_player_stats_2023_2025.csv` | Raw-to-normalized identities, participation logic, original statistic values and time conversions |

The sixth declared external original is `/workspace/deliverables/ncaa_lacrosse_additional_odds_2023_2026.csv`; it is **outside Stage 2**, was not imported and was not used in these checks.

More importantly, the package lacks the original NCAA box-score/PBP and raw ESPN payloads underlying most claims. Saved school schedules can verify results, but not all player/team cells. Supplier summaries claiming sport/division checks, independent ESPN agreement and PBP reconstruction are not replacements for those underlying artifacts. Hashes of absent files prove neither their contents nor their historical availability. No original alias registry or permanent player-ID mapping was supplied.

The audit used existing source evidence first and made targeted official checks only for the disputed cases and definitions. The LIU 2025 schedule was unavailable in the browsing tool; the saved page and Quinnipiac/2024 evidence were used without bypassing access controls. No broad collection, new seasons or included scripts were run.

**Factual status and permission status remain separate.** Game assessments label school-corroborated results, NCAA-raw-only results, provisional missing-source results, scope exclusions and duplicate/wrong-season exclusions. All retain `permission_status=NOT_CLEARED_NO_CHANGE`. The package's NCAA/SIDEARM uncertainty and ESPN restriction claims are preserved as supplier permission assertions, not automatically accepted legal conclusions or cleared by this audit. Facts that pass checks do not automatically become authorized for use.

## Technical readiness and review outputs

| Dataset | Technical assessment | Authorization |
| --- | --- | --- |
| 2023 results | 559 strict-scope candidates; 134 school-corroborated; remaining 425 require source corroboration. No complete-season certification. | Not cleared; unchanged |
| 2024 results | 570 candidates; 115 school-corroborated; remaining 455 lack checked school corroboration. | Not cleared; unchanged |
| 2025 results | 578 source-backed candidates after two supported exclusions; 129 additionally school-corroborated. Two local date fixes remain unapplied. | Not cleared; unchanged |
| Team statistics | Full table not ready for unqualified modeling: missing boxes, rule violations, OT/reconciliation issues and missing raw evidence. Basic-screen subsets are not certification. | Not cleared; unchanged |
| Player statistics | Full table not ready for unqualified modeling: wrong-year duplicates, identity/participation gaps, mixed time units and attribution/provenance issues. | Not cleared; unchanged |

[Proposed corrections](grok_stage2_proposed_corrections.csv) contains **1,404 review rows**, including 1,090 TBA-time proposals, 222 identity reviews, 50 wrong-year statistical-copy exclusions (2 team + 48 player), seven field-definition reviews, supported date/status confirmations, two local date-fix proposals, two targeted duration fixes, and column-level unit/participation/ID rules. This is **not** a count of 1,404 false games or corrupted research observations. Some proposals confirm an already-correct imported field; others leave the corrected value unknown rather than guessing. Every row has `applied=False` and an unchanged permission status.

`source_csv_row` is the logical CSV record ordinal including the header, not necessarily a physical text line if a field contains a newline. Empty row ordinals denote clearly labeled column-level review rules. No proposed full corrected dataset is generated: uncertain identities, source gaps and unit ambiguities would make a blanket rewrite misleading. Any future statistics must also be aggregated from strictly prior games before becoming pre-game features; same-game box scores are outcomes, not pre-game predictors. No feature generation or training occurred here.

## Tests, preservation and reproduction

Executed in `dsf-lacrosse`:

```bash
python -m pytest -q tests/test_grok_stage2_games_stats.py tests/test_validate_incoming.py
python -m pip check
```

**59 tests passed in 0.77 seconds.** Dependency check: no broken requirements. Tests cover row accounting, two schedule layouts, winner-first loss displays, blocked-page rejection, ID namespaces/jersey zero, exact 2025 correspondence, local raw-source reconciliation, all 48 duplicate identities/count vectors, missing-role fields and fractional minutes, statistical flags, nonzero-vs-missing aggregation, unapplied proposals, unchanged permission flags and protected-output write refusal.

All **442 pre-existing files** retain their checksums, including the uploaded/extracted package, original 580-game CSV, historical aggregate data, existing features, predictions, models, figures and previous reports. Only new Stage 2 audit artifacts were written. [Preservation manifest](grok_stage2_existing_checksums.json), [final verification](grok_stage2_verification.json).

The offline internal audit is reproducible with `python src/audit_grok_games_stats.py`; it regenerates only the new Stage 2 structured checks and review CSVs and refuses to overwrite any path in the pre-audit preservation manifest. Official-check observations, this report and proposed corrections are reviewed evidence documents, not an automated approval or a source-data repair command.

Requested outputs:

- [This report](grok_stage2_games_stats_audit.md).
- [Proposed corrections](grok_stage2_proposed_corrections.csv).
- [Season coverage](grok_stage2_coverage.csv).

Supporting outputs: [record-level game assessments](grok_stage2_game_assessments.csv), [independent school comparisons](grok_stage2_schedule_comparison.csv), [2025 local comparison](grok_stage2_local_2025_comparison.csv), [local raw evidence comparison](grok_stage2_local_raw_evidence.csv), [statistical issues](grok_stage2_statistical_issues.csv), [player/team reconciliation](grok_stage2_player_team_reconciliation.csv), [schema/check summary](grok_stage2_checks.json), [targeted official-source log](grok_stage2_official_checks.json), [audit code](../src/audit_grok_games_stats.py), and [tests](../tests/test_grok_stage2_games_stats.py).

Stage 2 is complete as an audit with explicitly unresolved source/quality/permission statuses. No original dataset or modeling result was replaced.
