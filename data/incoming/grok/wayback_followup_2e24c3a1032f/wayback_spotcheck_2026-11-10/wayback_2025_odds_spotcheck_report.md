# Wayback spot-check of 2025 NCAA D1 men's lacrosse moneylines

Prepared 2026-11-10 (ET) for the CSE 519 project. This is a small, targeted spot-check, not a new audit or collection. No existing file or zip was modified. Permissions and quarantine status are unchanged: every record checked here remains `requires_permission`. No third-party page HTML or screenshots are included. Only short quoted price strings and public Wayback URLs are given.

## 1. Method

1. **Candidate pool.** From `supplement_2026-11-10/priority2_odds_evidence/odds_evidence_to_record_map.csv` I selected every 2025 `moneyline` record that has an `archive_url` on web.archive.org. That gives 66 records: 64 from BetMGM in three captures, and 2 for FanDuel quoted in a Bet On Lacrosse article.
   - **No 2025 DraftKings or Action Network moneyline has a Wayback capture in the evidence map.** The only 2025 DraftKings Wayback records are 6 spread and 6 total records. So sportsbook diversity is limited to BetMGM and FanDuel (via Bet On Lacrosse).
2. **Selection: 15 games.** Each game had to be:
   - matched in the NCAA crosswalk to a `final` NCAA game,
   - not flagged as a duplicate,
   - free of rejected records,
   - backed by both sides of the moneyline.

   I excluded Binghamton–St. Bonaventure and Mercyhurst–UMass Lowell (no NCAA match) and Mercer–VMI (one side rejected). The three May 2025 BetMGM games each appear in two captures, so the 15 games produce **18 page checks covering 36 odds records**. The games are spread across 4 dates (Feb 14, 15 and 16, Mar 1) plus May 17–18.
3. **Fresh fetch.** On 2026-11-10 between about 5:21 and 5:35 PM ET, I fetched the 4 distinct Wayback captures again with curl, about 4–5 s apart. I used both the raw `id_` form and the normal replay form; all returned HTTP 200. `wayback_fetch_log.csv` lists each fetch's HTTP status, bytes, SHA-256, `Memento-Datetime` and the archive's `x-archive-src` WARC name. The three freshly fetched BetMGM captures are byte-identical (same SHA-256) to the copies saved on Nov 10. The Bet On Lacrosse capture differs from the saved copy, because the saved copy was taken from the live site, so it was checked independently.
4. **Independent parse.** I wrote a new parser (`scripts/parse_mgm.py`) and did not reuse the earlier one. For each BetMGM event it reads:
   - the participant names in the "A @ B" layout, where B is home,
   - the start time from the page's own schema.org `SportsEvent.startDate`,
   - the relative timer text,
   - the three option groups (spread, total, moneyline).

   For the Bet On Lacrosse capture it reads the "Syracuse at Utah" odds box and the article's `article:published_time` and `article:modified_time`.
5. **Checks per page.**
   - Both moneyline prices are visible.
   - They equal the record.
   - The sportsbook matches.
   - The teams match the NCAA game, with home/away taken from the NCAA game index.
   - Capture time versus game start. Start times come from the page listing and from ESPN's raw scoreboard; NCAA lists "TBA" for the February and March games.
6. **Three separate times.**
   - `capture_ts` comes from the 14-digit Wayback stamp and is confirmed by `Memento-Datetime`.
   - `publication_time` exists only for the article.
   - `quote_time` is the sportsbook's own quote time. **None of the 4 pages shows one.** Capture time and publication time are never treated as quote time.

## 2. Results

| # | NCAA game id | Game (away @ home) | Book | Record IDs | Record ML (home / away) | Page ML (home / away) | Capture (ET) | Pre-game | Outcome | Wayback URL |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6448511 | Richmond @ Cornell (2025-05-17) | BetMGM | N0272,N0273 | -455 / 340 | 1.22 dec (= -455) / 4.40 dec (= +340) | 2025-05-13 11:28:31 EDT | yes | authenticated | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 2 | 6448511 | Richmond @ Cornell (2025-05-17) | BetMGM | N0278,N0279 | -455 / 340 | 1.22 dec (= -455) / 4.40 dec (= +340) | 2025-05-15 22:41:55 EDT | yes | authenticated | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 |
| 3 | 6448513 | Georgetown @ Maryland (2025-05-18) | BetMGM | N0284,N0285 | -333 / 260 | 1.30 dec (= -333) / 3.60 dec (= +260) | 2025-05-13 11:28:31 EDT | yes | authenticated | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 4 | 6448513 | Georgetown @ Maryland (2025-05-18) | BetMGM | N0290,N0291 | -333 / 260 | 1.30 dec (= -333) / 3.60 dec (= +260) | 2025-05-15 22:41:55 EDT | yes | authenticated | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 |
| 5 | 6448512 | Notre Dame @ Penn St. (2025-05-18) | BetMGM | N0296,N0297 | 260 / -333 | 3.60 dec (= +260) / 1.30 dec (= -333) | 2025-05-13 11:28:31 EDT | yes | authenticated | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 6 | 6448512 | Notre Dame @ Penn St. (2025-05-18) | BetMGM | N0302,N0303 | 260 / -333 | 3.60 dec (= +260) / 1.30 dec (= -333) | 2025-05-15 22:41:55 EDT | yes | authenticated | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 |
| 7 | 6386505 | Syracuse @ Utah (2025-03-01) | FanDuel | O1165,O1166 | 440 / -650 | +440 / -650 | 2025-03-01 13:19:13 EST | yes | authenticated | https://web.archive.org/web/20250301181913/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-4-saturday-bets/ |
| 8 | 6386174 | Towson @ Navy (2025-02-16) | BetMGM | N0266,N0267 | 240 / -303 | 3.40 dec (= +240) / 1.33 dec (= -303) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 9 | 6386158 | Stony Brook @ North Carolina (2025-02-14) | BetMGM | N0112,N0113 | -5000 / 1700 | 1.02 dec (= -5000) / 18.00 dec (= +1700) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 10 | 6386338 | Quinnipiac @ Massachusetts (2025-02-14) | BetMGM | N0118,N0119 | -625 / 450 | 1.16 dec (= -625) / 5.50 dec (= +450) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 11 | 6386293 | Air Force @ Ohio St. (2025-02-15) | BetMGM | N0124,N0125 | -1667 / 850 | 1.06 dec (= -1667) / 9.50 dec (= +850) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 12 | 6386100 | Bellarmine @ Canisius (2025-02-15) | BetMGM | N0130,N0131 | 450 / -625 | 5.50 dec (= +450) / 1.16 dec (= -625) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 13 | 6386091 | Fairfield @ Brown (2025-02-15) | BetMGM | N0142,N0143 | -208 / 170 | 1.48 dec (= -208) / 2.70 dec (= +170) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 14 | 6386419 | Bucknell @ Dartmouth (2025-02-15) | BetMGM | N0154,N0155 | 170 / -208 | 2.70 dec (= +170) / 1.48 dec (= -208) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 15 | 6386509 | Syracuse @ Maryland (2025-02-15) | BetMGM | N0230,N0231 | 260 / -333 | 3.60 dec (= +260) / 1.30 dec (= -333) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 16 | 6386079 | Johns Hopkins @ Loyola Maryland (2025-02-15) | BetMGM | N0214,N0215 | 750 / -1250 | 8.50 dec (= +750) / 1.08 dec (= -1250) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 17 | 6386359 | Yale @ Villanova (2025-02-15) | BetMGM | N0254,N0255 | 550 / -833 | 6.50 dec (= +550) / 1.12 dec (= -833) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
| 18 | 6386280 | Utah @ Denver (2025-02-15) | BetMGM | N0166,N0167 | -357 / 275 | 1.28 dec (= -357) / 3.75 dec (= +275) | 2025-02-16 13:09:23 EST | no | capture_post_game | https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 |
The evidence snippets (short quoted price strings) and per-row notes are in `wayback_2025_odds_spotcheck.csv`.

### Counts

| Outcome | Page checks | Games | Odds records |
|---|---|---|---|
| authenticated | 7 | 4 | 14 |
| partially_authenticated | 0 | 0 | 0 |
| capture_post_game (prices visible and matching, but the archive capture is after the game started) | 11 | 11 | 22 |
| mismatch | 0 | 0 | 0 |
| not_visible | 0 | 0 | 0 |
| fetch_failed (no substitutions were needed) | 0 | 0 | 0 |
| **Total** | **18** | **15** | **36** |

**Prices.** All 36 record prices were found on the archived pages. They are on the correct game, with home/away oriented the same way as NCAA, and attributed to the claimed sportsbook. There were no price mismatches.

**Authenticated games:**
- Cornell vs Richmond (2025-05-17, NCAA 6448511), BetMGM, in captures from 2025-05-13 11:28 AM EDT and 2025-05-15 10:41 PM EDT.
- Maryland vs Georgetown (2025-05-18, 6448513), BetMGM, same two captures.
- Penn State vs Notre Dame (2025-05-18, 6448512), BetMGM, same two captures.
- Utah vs Syracuse (2025-03-01, 6386505), FanDuel as quoted by Bet On Lacrosse:
  - capture 1:19 PM EST,
  - article published 10:13 AM EST and modified 11:54 AM EST,
  - game at 2:00 PM ET.

## 3. Important caveats about what "authenticated" means here

- **BetMGM pages show decimal odds, not American odds.**
  - The archived pages display decimal prices, for example "1.22" / "4.40". The record's American prices (−455 / +340) are the exact arithmetic conversion of those decimals.
  - What is authenticated is the displayed decimal price. American figures such as −1667 or −455 are derived values. BetMGM's internal American price could differ within the rounding of a two-decimal display.
- **No sportsbook quote time is shown anywhere.**
  - Pre-game capture shows only that the price was on the page no later than the capture time. It is not a quote time, and it is not evidence of an opening or closing line.
  - The evidence map's `original_quote_timestamp_utc` for the May BetMGM records equals the capture time. That field should be read as a capture time, not a quote time. The existing file was not changed.
- **BetMGM option cells are all marked CSS class `offline`** in the archived server-rendered HTML. This is probably because the page's scripts never ran in the archive, but whether each market was open to bets at capture time cannot be determined.
- **FanDuel (Syracuse–Utah) is attributed secondhand.** The page is a Bet On Lacrosse editorial that says "Odds via FanDuel". The prices are verified as published by Bet On Lacrosse, not taken from a FanDuel page.
- **The 2025-02-16 BetMGM capture is stale.**
  - The capture (Common Crawl WARC `CC-MAIN-20250216171447…`, replayed by Wayback at 2025-02-16 18:09:23 UTC = 1:09 PM EST) lists only games that started between 2025-02-14 19:00Z and 2025-02-16 17:00Z. All of them had started before the capture time.
  - The page's own relative timers suggest BetMGM served a cached copy rendered around 2025-02-14 18:10 UTC (1:10 PM EST):
    - "Today • 11:00 PM" for the Feb 14 23:00Z game,
    - "Starting in 50 min" for the Feb 14 19:00Z Quinnipiac–UMass game,
    - "Tomorrow • …" for the Feb 15 games.
  - That would make the prices pre-game, but this is an inference from page text. The archive does not certify it, so these 11 games are classed `capture_post_game`, not authenticated.
  - Quinnipiac–UMass was "Starting in 50 min" in that render, so its prices are late pre-match prices.
- **Times shown on BetMGM pages are in UTC.** For example, "5/17/25 4:00 PM" means 16:00Z, which is 12:00 PM ET and matches NCAA's "12:00PM ET".
- For Maryland–Georgetown, the 05-13 capture lists a 16:00Z start, while the 05-16 capture and NCAA list 2:30 PM ET (18:30Z). Both captures are pre-game under either time.

## 4. Odds that cannot be authenticated from this check

- **22 records, 11 games,** captured post-game from the 2025-02-16 BetMGM capture: N0112/N0113, N0118/N0119, N0124/N0125, N0130/N0131, N0142/N0143, N0154/N0155, N0166/N0167, N0214/N0215, N0230/N0231, N0254/N0255, N0266/N0267. Their prices are visible and match, but a pre-game quote cannot be certified from the archive.
- **The same limit applies to every record that rests only on that capture.** That capture backs 52 of the 64 BetMGM 2025 Wayback moneyline records. Its single capture time (2025-02-16 18:09Z) is after every game listed on it. This follows directly from the capture time, not from sampling. The other 30 records from that capture (15 games) were not checked here.
- **No 2025 DraftKings or Action Network moneyline can be checked against a public archive,** because none has a Wayback capture in the evidence map. Those records rest on saved third-party pages that are withheld pending permission, and on live pages.
- **No record anywhere in this sample has an authentic sportsbook quote timestamp.**

## 5. What this implies for the 878 Wayback-linked records (no extrapolation)

- The sample covers 36 of the 66 2025 Wayback-linked moneyline records. It shows that the public Wayback Machine does contain readable, server-rendered historical prices for these BetMGM and Bet On Lacrosse pages: they are not JavaScript-blank. For the 36 records checked, every price matched.
- Whether a given record is authenticated as pre-game depends on that capture's timestamp relative to that game. In this sample, 3 of the 4 captures were pre-game for the games they back, and 1 was not.
- No claim is made about the other 842 Wayback-linked records. They include other seasons, DraftKings spread and total markets, and other captures. They would need the same per-capture check.
- The answer to the user's question: **public archives do authenticate some historical prices**, here 14 records in 4 games, as displayed pre-game prices. They do not supply sportsbook quote times, and they do not authenticate the 22 records whose only capture is after the game started.

## 6. Files

- `wayback_2025_odds_spotcheck.csv`: one row per page check, 18 rows.
- `wayback_fetch_log.csv`: details of each fresh fetch: HTTP status, bytes, SHA-256, Memento-Datetime, WARC source.
- `remaining_unresolved_issues.md`: the 2025 data inconsistencies, reviewed using only evidence already on the box.
- `scripts/parse_mgm.py` and `scripts/build_spotcheck.py`: the parser and build script. They need the fresh fetches, which are not redistributed, under `/tmp/wbfetch`. Anyone can re-fetch them from the URLs in `wayback_fetch_log.csv`.
- `MANIFEST.csv`: SHA-256 and size for each file.
