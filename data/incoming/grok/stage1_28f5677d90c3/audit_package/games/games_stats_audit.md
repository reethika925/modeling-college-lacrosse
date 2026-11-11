# Games & stats audit: data quality and provenance (2023–2025)

Audit date: 2026-11-10. Scope: the NCAA-derived game files (2023, 2024, 2025 index), team game stats, player game stats, the alias table and the odds→NCAA crosswalk in `/workspace/final_package/`.
**I did not modify any original file.** All corrected copies are in this folder and end in `_corrected.csv`. Odds data and permissions are covered separately in `/workspace/audit/odds/`.

## 1. Method
* **Official school schedules.** I fetched 28 school-season pages (Sidearm `/sports/mens-lacrosse/schedule/<yr>`) plus the UMBC 04-12-2025 recap and saved them unmodified in `evidence/`.
  * robots.txt was checked for each host and allowed every page. I waited at least 31 s between requests to the same host (Crawl-delay 30). The fetch log is `evidence/fetch_log.tsv`.
  * gocrimson.com (Harvard) returned an Incapsula bot challenge. I did not try to get past it; the file is saved as `*.BLOCKED_incapsula.html` and was not used. Harvard's games were checked through its opponents' pages (Vermont, Brown) where possible.
  * As noted before, virginiasports.com and gopsusports.com return 404 for these paths, so I did not use them.
* **Matching.** `scripts/a4_compare_schedules.py` matched every game on each school page to our rows by opponent and score. It then compared the date, score and home/away/neutral designation. Output: `school_schedule_comparison.csv`, 411 comparisons covering 379 distinct games.
  * Results: 401 dates agree, 6 disagree; 405 scores agree, 2 disagree (both are the one game that never got a result); 398 home/away agree and 9 are neutral-site designations; 0 home/away conflicts.
  * Every game on every school page matched a row in our data (`school_schedule_games_not_in_our_data.csv` holds only the Princeton–Penn ESPN-only row, which matched by hand).
* **ESPN dates.** I took each ESPN event's date from the raw ESPN scoreboards, converted to America/New_York, and compared it with the NCAA date.
* **Re-validation.** `scripts/a3_revalidate.py` checked sport and division from the raw box JSON, season and date ranges, duplicate ids, score contradictions (NCAA vs ESPN vs box vs summed player goals), impossible stats, alias consistency, missing IDs and join keys. Results are in `revalidation_results.json` and `revalidation_issues.csv`.
* **Build and post-checks.** `scripts/a5_build_outputs.py` builds the corrections, the excluded list and the corrected copies. `scripts/a6_post_checks.py` re-runs the checks on the corrected copies (`post_correction_checks.json`).

Status vocabulary:
* **verified**: an official school schedule confirms the record, or NCAA and ESPN agree on both score and date.
* **provisional**: a single source (the NCAA scoreboard only) or a soft issue. Usable, but flagged.
* **rejected**: not a real or countable game. Excluded from usable counts. The rows stay in the corrected files, flagged.

## 2. Binghamton check (requested)
| game_id | our original | official evidence | finding |
|---|---|---|---|
| 6386469 | 2025-04-05, Binghamton (home) 9 – UAlbany 11 | Binghamton schedule: Apr 5 (Sat), vs University at Albany, Vestal NY, L 9-11; ESPN 401755691 agrees | **Correct, verified** |
| 6449835 | 2025-04-05, UMBC (home) 17 – Binghamton 7 | Binghamton schedule: Apr 12 (Sat) noon, at UMBC, UMBC Stadium, L 7-17. UMBC recap dated 4/12/2025: "17-7 … at UMBC Stadium on Senior Day". The UMBC 2025 schedule agrees. | **Date wrong**: 2025-04-05 → **2025-04-12** (verified). Score and home/away correct. |

* The NCAA scoreboard feed itself lists contest 6449835 on 04-05 and lists nothing for either team on 04-12, so the error came from the source.
* The date is corrected in the 2025 index, both team-stat rows and all 57 player rows. start_time_utc is set to 2025-04-12T16:00Z (noon EDT).
* No odds-crosswalk row involves either game.
* After the fix, UMBC's apparent back-to-back (UMass Lowell on 04-04, Binghamton on 04-05) goes away.

## 3. Corrections (`game_date_corrections.csv`: 27 rows, 14 game-level corrections)
| game_id | season | field | original → corrected | status | evidence |
|---|---|---|---|---|---|
| 6449835 | 2025 | game_date | 2025-04-05 → 2025-04-12 | verified | Binghamton + UMBC schedules, UMBC recap |
| 6454179 Queens (NC)–Stony Brook 6-12 | 2025 | game_date | 2025-02-15 → 2025-02-16 | verified | Stony Brook schedule; ESPN also says 02-16 |
| 6386400 Le Moyne–Lafayette 4-15 | 2025 | game_date | 2025-02-23 → 2025-02-22 | verified | Le Moyne schedule (JMA Wireless Dome); ESPN also says 02-22. NCAA listed it on both dates. |
| 6138525 Detroit Mercy–Marquette 5-10 | 2023 | game_date | 2023-03-01 → 2023-03-02 | verified | Marquette and Detroit Mercy schedules (no ESPN listing) |
| 6136266 UMBC–Mount St. Mary's | 2023 | status / home_score / away_score | pre/NaN/NaN → final 16-6 | verified | UMBC and Mount St. Mary's schedules. NCAA never posted a result and there is no box score. |
| 6085574, 6149819, 6297607, 6299061, 6292101 | 2023/24 | neutral_site | NaN → True | verified | school page marks the game neutral |
| 6085531, 6085658 | 2023 | neutral_site | NaN → True | provisional | Marquette lists "vs" at Naples FL and Levittown NY, venues that are not the home campus |

Each date correction is repeated for the team-stat rows (2 per game) and the player rows of that game. NCAA's nominal home/away is kept for neutral-site games.
Not corrected: **6386269 Merrimack–UMass Lowell**. NCAA says 02-07 and ESPN says 02-08. The UMass Lowell schedule confirms 02-07, so the NCAA date is right and ESPN's is wrong. Neutral-site flags in 2023/24 are still marked only where a checked school page shows them; otherwise only semifinals and the final are flagged.

## 4. Same-day and duplicate audit
**Same team within 1 day (8 candidates).**
* 6 are genuine back-to-backs that appear on the official schedule with the same scores: High Point 2023-02-25/26, Navy 2023-02-04/05, Mercer 2024-02-03/04, Iona 2025-02-08/09, plus Stony Brook 2025 and UMBC 2025, which are only 2+ days apart once the dates are corrected.
* The 2 artefacts: Binghamton (misdated) and **LIU 2025-04-19/20**.
  * **6455124 LIU 10-9 Quinnipiac (OT), 2025-04-20 → rejected.** It appears on neither LIU's nor Quinnipiac's official 2025 schedule, and about 11 of 24 players per side appear in no other 2025 game for their team (other games: 0–2).
  * The most likely explanation is an exhibition or non-countable game that was posted to the NCAA scoreboard with a D-I box score. The rows stay in the corrected stats, flagged `rejected`.

**Repeated pairing with an identical score.**
* **6444405 Hampton 4-29 Fairfield on 2025-03-13 → rejected.** It is a phantom duplicate of 6386334 (03-15): the Hampton and Fairfield schedules show a single meeting on 03-15, and the duplicate has no box score.
* The 3 duplicates already removed in 2024 were re-checked. The kept games' dates are confirmed by official pages: Georgetown–Penn 2024-02-17, UMBC–Richmond 2024-03-08, JHU–Syracuse 2024-03-09. The phantom copies carried different, wrong dates (02-15, 03-07, 03-07).
* After correction, two other repeated pairings are genuine rematches with different box scores: Penn–Princeton 2023 (03-18 and the 05-05 Ivy tournament, two separate ESPN events) and Navy–Loyola 2024 (04-19 won by Loyola, 04-30 won by Navy).

**NCAA vs ESPN date disagreements (2025: 3).** 2 were NCAA errors and are corrected; 1 was an ESPN error.

## 5. Re-validation results
* **Sport, division and season.**
  * All box scores are MLA (men's lacrosse) and every date falls in its season, Feb–May.
  * 8 games in 2023 are not D-I vs D-I: 6 Hartford games (Hartford was moving to D-III and the box lists division 3) plus St. Andrews–Hampton and Hampton–Wabash. They are kept with `usable_d1_vs_d1 = False`, status provisional.
* **Duplicates.**
  * 0 duplicate game_ids.
  * 0 duplicate player rows.
  * Phantom duplicates are as described above.
* **Score contradictions.**
  * NCAA vs ESPN: 1 of 1,039 (LIU–Bellarmine 2025-03-01, NCAA 15-9 vs ESPN 14-9). The LIU schedule says 15-9, so NCAA is right and the game is verified.
  * Box goals vs final score: 3 team-games, all in 2023 NCAA tournament OT games (6147943, 6147954, 6147955), where the box is one goal short. The result is verified by ESPN; the box stats are provisional.
  * Summed player goals vs team goals: 14 team-games mismatch (out of 3,334). Provisional.
  * `saves = opponent SOG − opponent goals` holds exactly in 3,331 of 3,334 rows and within 1 in all of them.
* **Impossible stats.**
  * Team rows: 0 cases of SOG > shots, goals > SOG, faceoffs won > attempted, clears completed > attempted, negative values, or faceoff totals that don't fit the score. 11 team rows have EMO goals > EMO opportunities, exactly as NCAA published them (provisional).
  * Player rows: 1 row has SOG 3 > shots 1 (6269867, Jacksonville), as published (provisional). 0 rows where points ≠ goals + assists.
* **Aliases.**
  * Each NCAA seo maps to one name, one NCAA id and at most one ESPN id. 0 conflicts.
  * 9 non-D-I opponents have no ESPN id, which is expected.
* **Missing IDs.** Only the ESPN-only Princeton 18-11 Penn game (2024-05-05) and the rejected 6444405 lack NCAA team ids or a box score. Princeton's official schedule confirms that game, so it is verified, but it has no stats.
* **Join keys.**
  * Every team-stat game_id is present in the game files.
  * Every player game_id/team_id is present in team stats.
  * Home/away labels are consistent between files (0 mismatches).
  * After correction, team, player and crosswalk dates match game dates (0 mismatches).
  * The crosswalk has 261 matched rows; 0 point to rejected games and none involve a re-dated game.
  * 3 crosswalk matches are off by 1 day: Hofstra–Merrimack 2023-02-04, Holy Cross–Providence 2023-02-04, Towson–UMBC 2023-03-04. In all 3 the official schedule confirms the NCAA date, so the date in the odds source is one day early. I passed this to the odds worker and did not change any odds data.

## 6. Final usable game counts (after validation)
| season | original rows | rejected | **usable games** | D-I vs D-I usable | verified | provisional | games with team box stats* | date fixes |
|---|---|---|---|---|---|---|---|---|
| 2023 | 567 (566 final + 1 "pre") | 0 | **567** (the pre game is now final 16-6) | 559 | 333 | 234 | 533 full box (566 with rows) | 1 |
| 2024 | 570 (+3 duplicates already removed) | 0 in file (3 removed earlier) | **570** | 570 | 296 | 274 | 555 | 0 |
| 2025 index | 580 | 2 (6444405, 6455124) | **578** | 578 | 577 | 1 | 578 | 3 |

\*The second count includes games whose stat rows exist but whose box values are empty.
* Usable team-stat rows: 3,426 of 3,428 (the 2 rejected rows belong to 6455124).
* Usable player rows: 143,834 of 143,882.
* In 2023/24, "provisional" mostly means NCAA-only: ESPN lists only about 230 games per season and the school pages cover about 120. These games are internally consistent (box goals match the score) but have no second independent source.

## 7. Likely impact on your 580-game 2025 file (not inspected; it is not accessible to me)
I have not seen the file, so nothing here is a confirmed match. If it was built from the NCAA scoreboard or a feed that copies it (580 is also the size of our raw NCAA 2025 index), check these:
1. **Hampton–Fairfield 4-29 listed twice** (03-13 and 03-15). Drop the 03-13 copy.
2. **UMBC 17–7 Binghamton dated 2025-04-05.** It should be 04-12. If your file has Binghamton playing twice on 04-05, this is the cause. The UAlbany 11–9 game on 04-05 is correct.
3. **LIU 10–9 Quinnipiac 2025-04-20.** It is on neither official schedule; treat it as non-countable.
4. **Queens–Stony Brook (02-15 → 02-16) and Le Moyne–Lafayette (02-23 → 02-22).** Date fixes. Le Moyne–Lafayette may appear twice if both NCAA scoreboard dates were scraped.
5. If the file was built from ESPN instead, Merrimack–UMass Lowell will show 02-08 (it should be 02-07), and LIU–Bellarmine will show 14-9 (it should be 15-9).
6. After removing items 1 and 3, a correct NCAA-based 2025 set has **578** games, so a 580-row file probably contains those two invalid rows.

## 8. Files
* `game_date_corrections.csv`
* `games_stats_excluded_or_unverified.csv` (70 rows: 5 rejected, 46 provisional, 19 verified resolutions)
* `final_usable_counts.json`
* Corrected copies:
  * `ncaa_lacrosse_games_2023_corrected.csv` and `…_2024_corrected.csv`
  * `ncaa_lacrosse_game_index_2025_corrected.csv`. Added columns: original_game_date, corrections_applied, audit_status, audit_basis, involves_non_d1_opponent_audit, usable_result, usable_d1_vs_d1.
  * `ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv` and `ncaa_lacrosse_player_stats_2023_2025_corrected.csv`. Added columns: original_game_date, date_correction_status, game_audit_status.
  * `odds_game_to_ncaa_game_crosswalk_corrected.csv`. Added columns: original_ncaa_game_date, ncaa_game_audit_status.
* Comparison and check outputs: `school_schedule_comparison.csv`, `school_schedule_games_not_in_our_data.csv`, `audit_candidates.csv`, `revalidation_results.json`, `revalidation_issues.csv`, `post_correction_checks.json`
* `evidence/`: 28 schedule pages, the UMBC recap, the Binghamton .txt extracts, the fetch log and the blocked Harvard response
* `scripts/`: a1–a6 and sidearm_parse.py
