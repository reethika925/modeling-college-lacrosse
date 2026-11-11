# Remaining 2025 data inconsistencies: review using existing evidence only

Scope: these are the 2025 items in `audit_package/games/revalidation_issues.csv`. This was not a new statistics audit, and nothing new was collected. The only evidence used was already on the box:
- raw NCAA box-score and play-by-play JSON in `/workspace/lax_data/raw/{boxscores,pbp}`,
- raw NCAA and ESPN scoreboards,
- the saved school schedule page `audit_package/games/evidence/liuathletics.com_2025_schedule.html`, as recorded in `school_schedule_comparison.csv`.

No dataset was modified. These are findings for a future correction step.

The original list has 29 items. **10 are 2025 items:**
- 1 score conflict,
- 7 player-goal versus team-goal mismatches,
- 2 cases of EMO goals greater than EMO opportunities.

**None of the 3 incomplete box scores is a 2025 game.** They are 6147943, 6147954 and 6147955, all 2023, so they are out of scope.

## Summary

| # | Record | Issue | Result | Reason (existing evidence) |
|---|---|---|---|---|
| 1 | game 6386248, LIU vs Bellarmine, 2025-03-01 | NCAA 15–9 vs ESPN 14–9 | **Resolved: NCAA 15–9 is correct** | The NCAA play-by-play has 15 unique LIU goal plays (3/7/3/2 by quarter), ending "15, 9". NCAA box team goals are 15 and the player sum is 15. The saved LIU schedule page shows "W 15-9". ESPN's linescore has 1 LIU goal in Q4 against 2 in the NCAA play-by-play, so ESPN is missing one Q4 goal. |
| 2 | player rows 6386359 / Villanova (vs Yale, 2025-02-15) | player sum 12 vs team 13 | **Resolved: not an error** | The play-by-play records one Villanova goal as "OWN GOAL", which is credited to the team and no player. 13 goal plays match the team total and the 13–11 final. |
| 3 | player rows 6386399 / Lafayette | 15 vs 16 | **Resolved: not an error** | The play-by-play has "OWN GOAL (MAN-UP)" credited to Lafayette. 16 goal plays match the team total and the 16–9 final. |
| 4 | player rows 6452095 / Towson | 12 vs 13 | **Resolved: not an error** | The play-by-play has "OWN GOAL" credited to Towson. 13 goal plays match the team total and the 13–10 final. |
| 5 | player rows 6386105 / Michigan (vs Canisius) | 15 vs 16 | **Partly resolved** | Team total 16 is confirmed by 16 play-by-play goal plays and the 16–2 final. The play-by-play credits one goal to "Bruno, Dylan", who has no row at all in the NCAA box player list. The player table is missing that player-game row. The data has no third source to settle player-level credit, so the row stays provisional. |
| 6 | player rows 6386488 / Manhattan (at Syracuse) | 3 vs 2 | **Partly resolved** | Team total 2 is confirmed by 2 play-by-play goal plays (Hiner, Miller) and the 18–2 final. The NCAA box also credits Darian Johnstone with 1 goal, which doesn't appear in the play-by-play. That is likely a box-score over-credit, but box and play-by-play are both from NCAA, so player-level credit is unresolved. |
| 7 | player rows 6386490 / Siena (at Manhattan, 2025-04-05) | 13 vs 12 | **Partly resolved** | Team total 12 is confirmed by the NCAA scoreboard (Siena 12–8) and by 12 unique play-by-play goals. The raw play-by-play repeats the Radomski goal at Q3 3:37 identically with the score unchanged; that row is a duplicate. The box credits William Sniffen with 1 goal not in the play-by-play, which explains the extra player goal. Player-level credit is unresolved, as in #6. |
| 8 | player rows 6440943 / Utah (at Vermont, 2025-02-21) | 11 vs 10 | **Partly resolved** | Team total 10 is confirmed by the scoreboard (Vermont 11–10) and by 10 unique play-by-play goals. The raw play-by-play repeats the White goal at Q2 3:20; that row is a duplicate. The box credits Brady Grandstaff with 1 goal not in the play-by-play. Player-level credit is unresolved, as in #6. |
| 9 | team_game 6386486 / Manhattan (at Wagner) | EMO goals 1 > opportunities 0 | **Resolved (cause identified)** | The play-by-play shows "Penalty on WAGNER … Extra-man opportunity" (Q3 9:18), followed by Manhattan's MAN-UP goal at Q3 8:30. The NCAA box field `powerPlay.opportunities` is 0 for both teams, but the play-by-play shows 1 EMO opportunity for each side, so the box under-records opportunities. A play-by-play-derived count would give Manhattan 1 goal on 1 opportunity. The box penalty counts look under-recorded too: 1 per team in the box, versus 2 Manhattan and 2 Wagner penalties in the play-by-play. |
| 10 | team_game 6386541 / UMass Lowell (at Wagner) | EMO goals 1 > opportunities 0 | **Partly resolved** | The play-by-play shows 1 Wagner penalty marked "Extra-man opportunity" (Q2 5:29), so UMass Lowell had at least 1 opportunity and the box's 0 is under-recorded. However, UMass Lowell's MAN-UP goal is at Q3 7:39, with no penalty recorded in the play-by-play just before it. The NCAA box shows 0 penalties for both teams, despite 2 in the play-by-play. The source is internally incomplete, so the exact opportunity count cannot be set from existing evidence. |

**Counts:**
- 5 resolved: #1, plus #2–4 as own goals, plus #9.
- 5 partly resolved: team-level values are confirmed, but the NCAA box and play-by-play disagree on player-level credit (#5–8) or on the EMO opportunity count (#10).
- 0 left completely unexplained.

## Still unresolved (carry forward)

- **Player-level goal credit in games 6386105, 6386488, 6386490 and 6440943.** The NCAA box and NCAA play-by-play disagree. No independent third source (a school box score) is saved for these games, and collecting one is out of scope.
- **EMO opportunities, and penalties in general.** The NCAA box-score fields for these are unreliable in at least these games. Any EMO-rate feature should be derived from the play-by-play ("Extra-man opportunity" penalties plus MAN-UP goals) with caution.
- **Raw play-by-play duplicate rows.** Rows like those in 6386490 and 6440943 should be de-duplicated before counting events. The earlier build already de-duplicated play-by-play rows for faceoffs and clears, through `pbp_duplicate_rows_removed`.
- **Out of scope here:** the 2023/2024 items, including the 3 incomplete 2023 box scores and the 9 non-2025 EMO and player-goal items.
- **ESPN's 2025 score for LIU–Bellarmine** stays wrong at the source. ESPN is restricted and isn't used as a primary source in any case.

## Odds-related items still unresolved (from the spot-check)

- 22 checked 2025 BetMGM records (11 games), and every other record whose only archive is the 2025-02-16 capture, cannot be certified as pre-game from the archive.
- No sportsbook quote timestamps exist for any record in the sample. The May 2025 BetMGM `original_quote_timestamp_utc` values in the evidence map are capture times.
- Archived 2025 BetMGM prices are decimal, so American values are derived conversions.
- No public archive exists in the evidence map for 2025 DraftKings or Action Network moneylines.
- **Permissions:** unchanged. All 1,983 non-rejected odds records remain quarantined (`requires_permission`). Nothing here clears any record for analysis.
