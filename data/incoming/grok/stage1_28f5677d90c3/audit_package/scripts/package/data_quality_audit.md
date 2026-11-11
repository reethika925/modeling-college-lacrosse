# Data-quality and provenance audit: NCAA D-I men's lacrosse (CSE 519)

Audit date: 2026-11-10 (ET). There were two workstreams: games/stats (`games/games_stats_audit.md`) and odds and permissions (`odds/odds_audit.md`). This file combines them.
**No original file was modified.**
* The original 1,470-record odds CSV still has sha256 `a156ba06389acc2a3a4e0eadaaf33af361b081cc942d3f768fdc79b1d5ed42a1`. An unmodified copy is in `originals/`.
* The original game and stat files stay in `final_package/`. Corrected copies are in `corrected/`.

## Status categories (used in every file)
| status | meaning |
|---|---|
| **verified** | Technically confirmed. For games: an official school schedule agrees, or NCAA and ESPN agree on score and date. For odds: the value is found in saved raw evidence, the book is supported by the source, and the item is grade A/B. |
| **provisional** | Technically plausible but single-source or with a soft issue (for example NCAA-only, implied line, grade C, unmatched game). Usable with a flag. |
| **requires_permission** | Technically verified or provisional, but the source's terms do not clearly permit collection and research reuse. Quarantined; not cleared. |
| **rejected** | Not a real or countable record (duplicate, phantom listing, exhibition, value contradicts the source, invalid price). Excluded. |

## 1. Binghamton finding (owner's report confirmed)
* **6386469: Binghamton 9–11 UAlbany, 2025-04-05, Binghamton home.** Correct. The Binghamton official schedule and ESPN confirm it. Verified.
* **6449835: UMBC 17–7 Binghamton, UMBC home.** The NCAA scoreboard feed lists it on **2025-04-05**. The Binghamton schedule ("Apr 12 (Sat) noon at UMBC, L 7-17"), the UMBC recap dated 4/12/2025 ("17-7 … at UMBC Stadium on Senior Day") and the UMBC schedule all give **2025-04-12**.
  * Corrected to 2025-04-12 (verified) in the 2025 game index, both team-stat rows and all 57 player rows. start_time_utc is set to 2025-04-12T16:00Z.
  * The score, home/away and IDs were already correct.
  * There are no odds records for either game.
* Evidence: `evidence/games/binghamton_2025_schedule.html`, `evidence/games/umbc_recap_2025-04-12.html` and `evidence/games/umbcretrievers.com_2025_schedule.html`.

## 2. Date and result corrections (`game_date_corrections.csv`: 30 rows)
| record | correction | status | basis |
|---|---|---|---|
| 6449835 UMBC–Binghamton 2025 | date 04-05 → 04-12 | verified | Binghamton and UMBC schedules, UMBC recap |
| 6454179 Queens (NC)–Stony Brook 2025 | date 02-15 → 02-16 | verified | Stony Brook schedule (ESPN agrees) |
| 6386400 Le Moyne–Lafayette 2025 | date 02-23 → 02-22 | verified | Le Moyne schedule (ESPN agrees). NCAA listed the game on both dates |
| 6138525 Detroit Mercy–Marquette 2023 | date 03-01 → 03-02 | verified | Marquette and Detroit Mercy schedules |
| 6136266 UMBC–Mount St. Mary's 2023 | "pre", no score → final 16–6 | verified | UMBC and Mount St. Mary's schedules. There is no box score |
| 7 games 2023/24 | neutral_site → True | 5 verified, 2 provisional | the school page marks the game neutral or lists an off-campus venue |
| 3 odds games 2023 (22 odds records: Hofstra–Merrimack, Holy Cross–Providence, Towson–UMBC) | odds-source date is one day early (02-04 → 02-05; 03-04 → 03-05) | verified | school schedules confirm the NCAA date. **Documented only; the odds data are unchanged** |

* Each game-date correction is repeated for its team-stat and player rows (dataset column).
* The odds workstream separately logged 11 odds value and identity corrections (`odds/odds_record_corrections.csv`), for example favourite-sign errors and the "Rutgers" label that is really Denver. All of the corresponding original rows are rejected or provisional.

## 3. Rejected games
| game | why | evidence |
|---|---|---|
| 6444405 Hampton 4–29 Fairfield, 2025-03-13 | Phantom duplicate of 6386334 (03-15). Hampton and Fairfield schedules show one meeting; no box score | `evidence/games/hamptonpirates.com_2025_schedule.html`, `fairfieldstags.com_2025_schedule.html` |
| 6455124 LIU 10–9 Quinnipiac (OT), 2025-04-20 | On neither the LIU nor the Quinnipiac official schedule. About 11 of 24 players per side appear in no other 2025 game for that team. Likely an exhibition posted with a D-I box score | `liuathletics.com_2025`, `gobobcats.com_2025` |
| 6287553, 6291301, 6291605 (2024) | Phantom duplicates already removed from the 2024 file. School pages confirm the kept games' dates (02-17, 03-08, 03-09); the phantoms carried wrong dates | `guhoyas.com_2024`, `umbcretrievers.com_2024`, `hopkinssports.com_2024` |

## 4. Same-day review
* Not every same-day or back-to-back appearance is an error. Of 8 same-team-within-1-day cases:
  * 4 are **genuine** back-to-backs on the official schedules: High Point 2023-02-25/26, Navy 2023-02-04/05, Mercer 2024-02-03/04, Iona 2025-02-08/09.
  * 2 disappear once dates are corrected: Stony Brook 2025 and UMBC 2025.
  * 2 are artefacts: the misdated Binghamton game and the LIU exhibition.
* Repeated pairings with identical scores:
  * 1 phantom (Hampton–Fairfield).
  * 2 genuine rematches with different box scores: Penn–Princeton 2023 (regular season and Ivy tournament) and Navy–Loyola 2024 (different winners).
* NCAA vs ESPN date disagreements: of 3 in 2025, 2 were NCAA errors (corrected) and 1 was an ESPN error (Merrimack–UMass Lowell; the NCAA date of 02-07 is confirmed).
* The odds data has no same-team-same-day case after the two postponed-game id pairs are merged.

## 5. Games and stats re-validation
* **Coverage.** 28 official school-season schedules (robots checked, 31 s per host) were compared with 379 games (411 comparisons): 401 dates agree, 405 scores agree, 0 home/away conflicts.
* **Sport and division.** All MLA. 8 games in 2023 are not D-I vs D-I (6 Hartford games listed as division 3, plus St. Andrews and Wabash). They are kept with `usable_d1_vs_d1 = False`.
* **Duplicates.** 0 duplicate game ids; 0 duplicate player rows.
* **Score contradictions.**
  * NCAA vs ESPN: 1 of 1,039 (LIU–Bellarmine). The LIU schedule confirms NCAA's 15–9.
  * Box goals one short of the final score: 3 overtime NCAA-tournament games (box stats provisional).
  * Player goals do not sum to team goals: 14 of 3,334 team-games (provisional).
  * The identity saves = opponent SOG − opponent goals holds in 3,331 of 3,334 rows and within 1 in all.
* **Impossible stats.** 11 team rows have extra-man goals > opportunities, as NCAA published them. 1 player row has SOG > shots. All flagged provisional; there are no other violations.
* **Aliases and IDs.** Each NCAA seo has 1 name, 1 NCAA id and ≤1 ESPN id. Only the ESPN-only game and the rejected phantom lack NCAA team ids.
* **Join keys.** Results → team stats → player stats → crosswalk all join on game_id and team_id_ncaa. Dates are consistent after correction (0 mismatches). 0 crosswalk rows point to rejected games.

## 6. Odds provenance (all 1,995 rows checked against saved raw evidence)
* **Value presence.** Found in raw evidence: 1,953. Implied (the line is not printed and the other side was filled in as the negation): 39. Not found: 3, all rejected.
* **Attribution and URLs.** Sportsbook attribution is supported for 1,965 records; the other 30 name no book. All 1,995 URLs are authentic: 87 of 93 return 200 live, and the DraftKings pages survive only as Wayback captures.
* **No AI-generated odds or predictions.** Picks, parlays and Cradl's AI content were never recorded as odds.
* **Rejected: 12.** 3 values contradict the source, 2 are invalid prices (a spread recorded as a moneyline), and 7 are cross-source duplicates. Separately, 50 repeat observations are kept and marked.
* **Games.** The original "224 games" are 223 distinct games: 221 NCAA D-I games, 1 from 2026 and 2 postponed-game id pairs. Home/away comes from the NCAA crosswalk; in the original file the listed home team matched NCAA in only 106 of 223 games.
* **Grades re-justified.** 544 A→A, 158 B→A, 56 B→C, 30 C→C, 1,207 B→B.
* **Opening and closing lines.** Lines are labelled "opening" only where the source text says so (25 records). **No closing lines exist.**
* **Usability (verified + provisional records, 306 games):**

| Metric | Games |
|---|---|
| Two-sided moneyline | 269 |
| Spread priced on both sides | 105 |
| Total priced | 105 |
| Multiple books | 17 |
| Movement (2+ timestamps) | 24 |
| Independent pre-game capture timestamp | 101 |

## 7. Permissions (`source_permissions_audit.csv`: 19 sources; robots.txt was never treated as permission)
* **Restricted:**
  * Action Network and DraftKings (explicit scraping/automation bans).
  * ESPN (the Disney ToU bans building data sets).
  * Cradl and USA Lacrosse (not accessed).
  * Massey (robots disallow; not used).
* **Uncertain:**
  * Internet Archive (access layer only).
  * BetMGM, Bet On Lacrosse, Lacrosse All Stars and LegalSportsBetting.
  * NCAA.com / sdataprod.ncaa.com (no automated-access ban; redistribution barred "except as … permitted under United States copyright law").
  * School/SIDEARM sites ("personal, noncommercial use").
* **Blocked by security controls, not circumvented:** Harvard (gocrimson.com, Incapsula challenge) and stats.ncaa.org (403).
* **Cleared:** The Odds API only. Its terms permit research use, but no data was obtained from it (it needs a key; historical data needs a paid plan).

**Every odds record is quarantined pending permission.** `odds/odds_cleared_for_analysis.csv` has 0 rows, and all 1,983 non-rejected records are in `odds/odds_quarantine_permission_required.csv`.

**Games and stats.** Their sources are classified *uncertain*, so under the owner's rule (uncertain → not cleared until authorisation is confirmed) `validated_data_inventory.csv` marks them `cleared_for_analysis = false`, with `requires_permission` counts. This is a conservative reading.
* NCAA's terms contain no scraping ban, and scores and statistics are facts. A single sign-off from the instructor or NCAA for internal, non-redistributed academic use would likely clear them. That is the owner's decision.
* ESPN-derived columns (`espn_*`) come from a restricted source. If ESPN-based verification is discounted, the counts of games verified by an official school page alone are:

| Season | Games verified by school page alone |
|---|---|
| 2023 | 134 |
| 2024 | 115 |
| 2025 | 129 |

  The remaining usable games become provisional (NCAA-only).

### Paths to clearance
1. **Odds.** Written permission from Action Network, DraftKings, BetMGM, Bet On Lacrosse, Lacrosse All Stars and LegalSportsBetting for research use of the specific captured pages. The Internet Archive copies also need the original publisher's permission.
2. **Licensed replacement.** A licensed odds feed whose terms permit research use (for example The Odds API, if it covers NCAA lacrosse; a key or paid plan would need the owner's approval), or the instructor or university library providing licensed odds data.
3. **Games and stats.** Written or instructor confirmation that internal academic analysis of NCAA factual results is acceptable (no redistribution of raw files), or NCAA permission. Drop or re-source the `espn_*` fields unless ESPN/Disney permission is obtained.
4. **Evidence pages.** Keep the saved school pages and odds archives private (verification only). Raw odds archives are not redistributed in this package; only their sha256 hashes are (`evidence/odds/raw_odds_evidence_sha256.txt`).

## 8. Original totals vs validated totals
**Games and stats** (technically usable = not rejected; none cleared, see §7):

| dataset | original rows | rejected | technically usable | verified | provisional | cleared |
|---|---|---|---|---|---|---|
| games 2023 | 567 (566 final + 1 pre) | 0 | 567 (559 D-I vs D-I) | 333 | 234 | 0 |
| games 2024 | 570 (after 3 phantoms removed earlier) | 3 earlier | 570 | 296 | 274 | 0 |
| game index 2025 | 580 | 2 | **578** | 577 | 1 | 0 |
| team game stats | 3,428 | 2 | 3,426 | 2,408 | 1,018 | 0 |
| player game stats | 143,882 | 48 | 143,834 | 96,133 | 47,701 | 0 |

**Odds:**

| dataset | original | rejected | technically verified | provisional | requires_permission | cleared |
|---|---|---|---|---|---|---|
| original file (reported 1,470 rows / 224 games) | 1,470 / 224 | 8 | 1,390 / 221 games | 72 | 1,462 | **0** |
| additional | 525 | 4 | 497 | 24 | 521 | **0** |
| combined | 1,995 / 308 games | 12 | 1,887 / 294 games | 96 | 1,983 / 306 games | **0** |

## 9. Possible effect on the owner's local 580-game 2025 file (not accessed)
The file was not inspected. If it is NCAA-scoreboard-based, it likely contains:
* the Hampton–Fairfield phantom (03-13);
* UMBC–Binghamton dated 04-05;
* the LIU–Quinnipiac exhibition (04-20);
* Queens–Stony Brook on 02-15 and Le Moyne–Lafayette on 02-23, possibly duplicated.

A clean NCAA-based count is 578.
