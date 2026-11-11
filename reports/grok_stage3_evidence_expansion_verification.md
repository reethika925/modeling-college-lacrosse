# Focused verification: Grok historical odds evidence expansion

Review date: November 10, 2026. Scope: the newly supplied expansion and reconciliation with the two existing Stage 3 reports. No model run, odds import, new season collection, full audit rerun, proposal edit or permissions clearance.

## Decision and counting units

**The 23 claimed new games have reproducible pre-game displayed-price evidence. Two additional timing-unknown 2023 games can also be resolved using official team previews, giving 25 newly evidenced games: 9 in 2023, 14 in 2024 and 2 in 2025.** The prior spot-check contributed four other 2025 games, so cumulative coverage is **29 distinct games**. This is authentication of historical displayed prices or attributed editorial quotations, not proof of bet execution, bookmaker update time, a closing line or legal clearance.

**Grok incorrectly reports that the inspected DraftKings captures have no moneylines.** Their original HTML contains visible moneyline tables and populated embedded `MoneyLine` offers. Six relevant two-sided offers were independently read, including Princeton–Syracuse. Consequently all 29 cumulatively evidenced games have at least one complete pre-game moneyline observation. Twenty-two have direct sportsbook evidence; seven have only editorial moneyline evidence. Three games have two-book moneylines at different capture times. All remain **UNRESOLVED / NOT APPROVED FOR ANALYSIS** on permissions.

The consistent existing-data structural count remains **230 matched complete-moneyline games, including 90 in 2025**, not 269 / 92. No original row was changed to obtain these findings.

A *record ID* is an existing single selection. A *paired market observation* is two opposing selections from the same game, bookmaker, market and capture/source version. A *game/book/capture snapshot* can contain moneyline, spread and total markets. Distinct archive pages can contain multiple games. Repeated identical prices at different captures are separate observations but do not create extra games.

| Focused verification measure | Result |
|---|---:|
| Supplied additional evidence rows / unique selection IDs | 53 / 106 |
| Supplied pairs with reproducible prices | 52 / 104 selections |
| Supplied pairs verified before scheduled start | 48 / 96 existing IDs |
| Direct / editorial pre-game selection records in new CSV | 78 / 18 |
| Games touched by those 96 records | 28: 25 new, 3 previously evidenced |
| Additional direct DK moneyline observations omitted by supplier | 6 pairs / 12 selections; no odds import or new record IDs |
| Prior spot-check pre-game records carried forward | 14, disjoint from the 96 |
| Cumulative existing IDs whose prices have pre-game corroboration | 110 |
| Cumulative paired market observations, including extra DK evidence | 61 / 122 selection observations |
| Cumulative distinct game/book/capture snapshots / archive pages | 37 / 13 |
| Cumulative distinct ML game/book pairs / ML capture observations | 32 / 37 |
| Cumulative distinct games / multi-book ML games | 29 / 3 |
| New CSV post-game-only pairs / unavailable ML pairs | 4 (8 records) / 1 (2 records) |
| Bookmakers represented / directly observed sportsbook domains | 5 / 2 |
| Exact bookmaker quote timestamps established / approved records | 0 / 0 |

The 122 observations must **not** be described as 122 newly authenticated IDs. Four of the additional DK selections repeat prices already quoted in Action Network, and two further existing IDs have the same Jacksonville–Johns Hopkins prices in a different article. Matching prices do not authenticate those articles' original versions. The new evidence ledger retains separate capture/source identities. The 110-ID count means price corroboration; it does not rewrite the original records' provenance or approve them.

## Supplement integrity and safe handling

Archive: `data/incoming/grok/ncaa_lacrosse_odds_evidence_expansion_2026-11-10.zip`.
Size: **51,589 bytes**. SHA-256: `d76adefe0110aee3e70d7f0267e63eb38f35926de37f3c132709b10621cd6ab2`.
No independently supplied ZIP checksum was available; this is a locally calculated fingerprint, not proof of authorship. ZIP CRC/decompression passed for all **13 files**, totalling **245,249 uncompressed bytes**. Unsafe paths, links, ambiguous/colliding names and excessive expansion were checked before extraction; none was found. Exclusive extraction used the new directory `data/incoming/grok/evidence_expansion_d76adefe0110/` and overwrote nothing. All **12 supplied manifest entries** agree with actual sizes and SHA-256 hashes; the manifest itself is the thirteenth file.

The main files are `additional_verified_odds.csv` (53 × 38), `evidence_checks_detail.csv` (57 × 35), the main Markdown report, `multibookmaker_coverage.csv` (3 rows), `unresolved_odds_evidence.csv` (23 rows), and fetch/query logs (15 / 45 rows). These tables overlap; their row totals are not additive coverage. The five packaged Python scripts were not executed or imported. Inventory and byte-level evidence are in `grok_expansion_inventory.csv` and `grok_expansion_extraction.json`.

## Independent archive and official-source checks

The exact supplied capture URLs were inspected using ordinary HTTPS requests to their `id_` representations, with gentle pacing and no credentials, proxy changes, CAPTCHA handling or access-control bypass. Thirteen pages were freshly fetched; the two May BetMGM captures were reused from the preceding independent spot-check cache. All 15 returned/retained HTTP 200 with capture timestamps corroborated by `Memento-Datetime`. Original embedded HTML/JSON was parsed without executing page scripts or fetching current sportsbook APIs. Raw HTML stayed in `/tmp/dsf_expansion_pages/`; exact URLs, response hashes, byte counts and observed prices are preserved in the audit artifacts, not republished as a raw dataset.

**Thirteen of 15 raw hashes match Grok's fetch log.** The April 4, 2025 DK response is 2,717,210 bytes rather than the supplied 333,723; April 25 is 2,638,717 rather than 329,652. The independently returned embedded states contain 34 events / 102 offers and 28 events / 84 offers respectively. Thus Grok's “empty” assessment and exact bytes could not be reproduced for those two URLs. The reason for representation/content differences is unresolved. No games from those two pages were added to this focused authentication count. The six omitted DK moneylines below come from the February 2023 and May 2025 pages whose hashes **do** match.

| Key | Public capture (exact) | Capture UTC from URL + Memento | Raw bytes | Supplier raw hash agrees |
|---|---|---|---|---|
| A01 | [replay](https://web.archive.org/web/20230204034751/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins) | Sat, 04 Feb 2023 03:47:51 GMT | 214274 | True |
| A02 | [replay](https://web.archive.org/web/20230325141823/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-saturday-week-7-notre-dame-vs-virginia-marquette-vs-st-bonaventure-march-25) | Sat, 25 Mar 2023 14:18:23 GMT | 214714 | True |
| A03 | [replay](https://web.archive.org/web/20230407193556/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-virginia-cavaliers-vs-north-carolina-tar-heels-friday-april-7) | Fri, 07 Apr 2023 19:35:56 GMT | 204704 | True |
| A04 | [replay](https://web.archive.org/web/20230415044110/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-week-10) | Sat, 15 Apr 2023 04:41:10 GMT | 207629 | True |
| A05 | [replay](https://web.archive.org/web/20230514033813/https://www.actionnetwork.com/lacrosse/college-lacrosse-betting-odds-picks-best-bets-for-ncaa-tournament-opening-round-sunday) | Sun, 14 May 2023 03:38:13 GMT | 201879 | True |
| A06 | [replay](https://web.archive.org/web/20260308175741/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-0-bets/) | Sun, 08 Mar 2026 17:57:41 GMT | 128413 | True |
| A07 | [replay](https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | Fri, 03 Feb 2023 18:10:11 GMT | 2047716 | True |
| A08 | [replay](https://web.archive.org/web/20250404065042/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | Fri, 04 Apr 2025 06:50:42 GMT | 2717210 | False |
| A09 | [replay](https://web.archive.org/web/20250425111524/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | Fri, 25 Apr 2025 11:15:24 GMT | 2638717 | False |
| A10 | [replay](https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game) | Tue, 13 May 2025 20:04:21 GMT | 2313037 | True |
| A11 | [replay](https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88) | Fri, 23 Feb 2024 11:37:43 GMT | 293530 | True |
| A12 | [replay](https://web.archive.org/web/20240525152928/https://sports.betmgm.com/en/sports/lacrosse-88) | Sat, 25 May 2024 15:29:28 GMT | 298096 | True |
| A13 | [replay](https://web.archive.org/web/20250121025539/https://sports.betmgm.com/en/sports/lacrosse-88) | Tue, 21 Jan 2025 02:55:39 GMT | 395803 | True |
| A14 | [replay](https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213) | Tue, 13 May 2025 15:28:31 GMT | 404343 | True |
| A15 | [replay](https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88) | Fri, 16 May 2025 02:41:55 GMT | 396418 | True |


Official previews, schedules, game notes and selected box scores were inspected for all 25 newly evidenced games. The three previously evidenced May games reuse the previous independently reviewed official sources. `grok_expansion_official_starts.csv` contains all 28 starts and links. EST/EDT and MST/MDT conversions are explicit; the February 4 Jacksonville game is February 5 in UTC. These are **official scheduled starts**, not a claim of independently observed actual faceoff for every game. Selected official box scores corroborate later actual starts, as noted below; no capture here is near a conflicting earlier actual start.

All supplied pairs were checked against unchanged Stage 2 date, home/away and NCAA ID fields and the unchanged Stage 3 selection/book/market/line/price fields. BetMGM's visible participant order and `@` marker establish away/home; Spread / Total / Money column headers prevent mixing market prices. DK event team fields, outcome team labels and home/away criterion fields agree. Embedded event dates agree with the game dates after timezone conversion. Editorial tables require explicit bookmaker attribution. Neutral-site “home” is dataset orientation, not home-field advantage.

## Newly evidenced games and exact prices

The table lists one verified ML pair per new game; other spread/total observations and repeat captures are in `grok_expansion_independent_checks.json`. American prices derived from decimal BetMGM displays are rounded, not claimed to be printed American odds. Capture keys resolve to the exact URLs above. No fictional missing selections were filled.

| NCAA ID | Game date | Away → home orientation | Moneyline evidence | Home / away American | Capture | Record IDs or status | Official scheduled start UTC |
|---|---|---|---|---|---|---|---|
| 6085420 | 2023-02-04 | Johns Hopkins at Jacksonville | DraftKings (editorial) | -115 / -115 | A01 | O0091,O0092 | [official start](https://hopkinssports.com/news/2023/2/2/johns-hopkins-jacksonville-mens-lacrosse-notes.aspx) 2023-02-05T00:00:00Z |
| 6085415 | 2023-02-04 | Vermont at Syracuse | Caesars (editorial) | -270 / +230 | A01 | O0158,O0159 | [official start](https://cuse.com/news/2023/2/2/mens-lacrosse-opens-2023-saturday) 2023-02-04T18:00:00Z |
| 6085412 | 2023-02-04 | Utah at Denver | DraftKings (editorial) | -250 / +200 | A01 | O0049,O0050 | [official start](https://denverpioneers.com/sports/mens-lacrosse/schedule/text/2023) 2023-02-04T19:00:00Z |
| 6085699 | 2023-03-25 | Virginia at Notre Dame | Caesars (editorial) | -150 / +125 | A02 | O0264,O0265 | [official start](https://fightingirish.com/news/2023/03/24/game-7-preview-3-virginia) 2023-03-25T16:00:00Z |
| 6085771 | 2023-04-07 | Virginia at North Carolina | BetMGM (editorial) | +360 / -600 | A03 | O0282,O0283 | [official start](https://goheels.com/news/2023/4/6/no-10-mens-lacrosse-to-host-no-3-virginia-friday-night) 2023-04-07T22:00:00Z |
| 6085848 | 2023-04-15 | Hobart at Saint Joseph's | DraftKings (editorial) | -525 / +340 | A04 | O0302,O0303 | [official start](https://sjuhawks.com/sports/mens-lacrosse/schedule/2023) 2023-04-15T17:00:00Z |
| 6085853 | 2023-04-15 | Bryant at Vermont | FanDuel (editorial) | -142 / +116 | A04 | O0296,O0297 | [official start](https://uvmathletics.com/sports/mens-lacrosse/schedule/2023) 2023-04-15T19:30:00Z |
| 6147944 | 2023-05-14 | Princeton at Penn St. | DraftKings (editorial) | -120 / -110 | A05 | O0366,O0367 | [official start](https://goprincetontigers.com/news/2023/5/12/mens-lacrosse-princeton-heads-to-penn-state-for-ncaa-tournament-opening-round) 2023-05-14T23:30:00Z |
| 6147942 | 2023-05-14 | Delaware at Duke | bet365 (editorial) | -1600 / +925 | A05 | O0362,O0363 | [official start](https://goduke.com/news/2023/5/14/mens-lacrosse-duke-rallies-for-12-11-victory-over-delaware) 2023-05-14T21:00:00Z |
| 6269740 | 2024-02-23 | Towson at Saint Joseph's | BetMGM (direct) | +100 / -125 | A11 | N0016,N0017 | [official start](https://towsontigers.com/news/2024/2/22/mens-lacrosse-towson-mens-lacrosse-embarks-to-philadelphia-to-play-saint-joseph-s) 2024-02-23T21:00:00Z |
| 6269738 | 2024-02-23 | Siena at UMass Lowell | BetMGM (direct) | +210 / -286 | A11 | N0022,N0023 | [official start](https://goriverhawks.com/sports/mens-lacrosse/schedule/2024) 2024-02-23T20:00:00Z |
| 6269774 | 2024-02-24 | Brown at Providence | BetMGM (direct) | +115 / -154 | A11 | N0044,N0045 | [official start](https://brownbears.com/news/2024/2/24/mens-lacrosse-drops-ocean-state-battle-to-providence-in-overtime) 2024-02-24T17:00:00Z |
| 6269761 | 2024-02-24 | UAlbany at Drexel | BetMGM (direct) | -110 / -120 | A11 | N0028,N0029 | [official start](https://ualbanysports.com/news/2024/2/23/mens-lacrosse-mens-lacrosse-readies-for-drexel.aspx?path=gdac) 2024-02-24T17:00:00Z |
| 6269525 | 2024-02-24 | Johns Hopkins at North Carolina | BetMGM (direct) | +135 / -182 | A11 | N0068,N0069 | [official start](https://goheels.com/news/2024/2/23/mens-lacrosse-hosts-no-9-johns-hopkins-in-home-opener) 2024-02-24T17:00:00Z |
| 6269750 | 2024-02-24 | UMBC at Mount St. Mary's | BetMGM (direct) | +700 / -1667 | A11 | N0076,N0077 | [official start](https://mountathletics.com/news/2024/2/18/mens-lacrosse-atkinsons-hat-trick-peters-saves-come-in-defeat-for-mens-lacrosse-against-njit.aspx) 2024-02-24T17:00:00Z |
| 6269457 | 2024-02-24 | Penn St. at Navy | BetMGM (direct) | +525 / -1000 | A11 | N0082,N0083 | [official start](https://navysports.com/sports/mens-lacrosse/schedule/2024?path=me) 2024-02-24T17:00:00Z |
| 6269772 | 2024-02-24 | Binghamton at Lafayette | BetMGM (direct) | -182 / +140 | A11 | N0038,N0039 | [official start](https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2024) 2024-02-24T17:00:00Z |
| 6269771 | 2024-02-24 | Cornell at Denver | BetMGM (direct) | +155 / -208 | A11 | N0062,N0063 | [official start](https://denverpioneers.com/sports/mens-lacrosse/schedule/2024?grid=true) 2024-02-24T19:00:00Z |
| 6269765 | 2024-02-24 | St. Bonaventure at VMI | BetMGM (direct) | -167 / +125 | A11 | N0092,N0093 | [official start](https://vmikeydets.com/sports/lacrosse/schedule/2024) 2024-02-24T16:00:00Z |
| 6269778 | 2024-02-24 | Quinnipiac at Bryant | BetMGM (direct) | -1000 / +550 | A11 | N0050,N0051 | [official start](https://bryantbulldogs.com/news/2024/2/23/2_23_2024_563) 2024-02-24T17:00:00Z |
| 6269763 | 2024-02-24 | Harvard at Bucknell | BetMGM (direct) | +775 / -2000 | A11 | N0056,N0057 | [official start](https://bucknellbison.com/news/2024/2/22/mens-lacrosse-to-face-harvard-in-neutral-site-contest-in-connecticut) 2024-02-24T18:30:00Z |
| 6292103 | 2024-05-25 | Maryland at Virginia | BetMGM (direct) | -238 / +175 | A12 | N0106,N0107 | [official start](https://umterps.com/news/2024/5/22/mens-lacrosse-no-7-maryland-and-no-6-virginia-to-meet-in-ncaa-semifinals-saturday-afternoon) 2024-05-25T18:30:00Z |
| 6292102 | 2024-05-25 | Denver at Notre Dame | BetMGM (direct) | -769 / +450 | A12 | N0100,N0101 | [official start](https://denverpioneers.com/sports/mens-lacrosse/schedule/2024?grid=true) 2024-05-25T16:00:00Z |
| 6386180 | 2025-02-01 | Navy at High Point | BetMGM (direct) | +100 / -120 | A13 | O1031,O1032 | [official start](https://highpointpanthers.com/news/2025/1/31/mens-lacrosse-high-point-opens-2025-season-welcoming-navy-to-vert-stadium.aspx) 2025-02-01T17:00:00Z |
| 6448514 | 2025-05-17 | Syracuse at Princeton | DraftKings (direct) | -130 / +100 | A10 | new observation; no imported ID | [official start](https://goprincetontigers.com/news/2025/5/15/mens-lacrosse-third-seeded-princeton-sixth-seeded-syracuse-renew-rivalry-in-ncaa-quarterfinals-saturday) 2025-05-17T18:30:00Z |


The two additionally resolved games are Virginia at Notre Dame, March 25, 2023 (**O0264,O0265**, Caesars via Action Network, ND −150 / Virginia +125), and Virginia at North Carolina, April 7 (**O0282,O0283**, BetMGM via Action Network, UNC +360 / Virginia −600). Official previews establish starts of **16:00Z** and **22:00Z**; their captures are **14:18:23Z** and **19:35:56Z** respectively. Grok had left timing unknown; independent official evidence supports pre-game classification.

### Requested 2025 checks

**Navy at High Point, February 1 (6386180):** the January 21 capture at **02:55:39Z** displays BetMGM Navy **1.83 decimal** and High Point **2.00**. These convert to Navy **−120** (unrounded −120.4819277…) and High Point **+100**, matching **O1031,O1032**. High Point's January 31 official preview schedules noon EST (**17:00Z**), earlier than the sportsbook page's stale/generic **18:00Z** start. The capture precedes both by many days. This is direct evidence of that earlier price pair, not proof that a later Bet On Lacrosse article was already present at the earlier capture. The original source linkage remains unchanged.

**Syracuse at Princeton, May 17 (6448514):** DK capture **May 13, 20:04:21Z** displays Princeton −1.5 at **+110**, Syracuse +1.5 at **−140** (**O1416,O1417**); total **25.5**, Over **−120**, Under **−110** (**O1418,O1419**). It also displays the omitted ML **Princeton −130 / Syracuse +100**. Princeton's official preview schedules **18:30Z**, and its [official box score](https://goprincetontigers.com/sports/mens-lacrosse/stats/2025/syracuse/boxscore/20731) records **19:06Z** actual start. The capture predates both. Existing article ML IDs **O1420,O1421** are −115 / −115, a **different price pair**; they are not authenticated by the DK −130 / +100 observation and were not altered.

Other schedule conflicts do not reverse timing findings: Quinnipiac–Bryant was **noon EST**, not Grok's 13:00 EST; Harvard–Bucknell was **18:30Z**, not BetMGM's 17:00Z; Maryland–Virginia on May 25, 2024 was **18:30Z**, not BetMGM's 16:00Z. Maryland's [official box score](https://umterps.com/sports/mens-lacrosse/stats/2024/virginia/boxscore/17524) gives actual 18:58Z. The same May 25 capture at 15:29:28Z is 30m32s before Denver–Notre Dame's official 16:00Z start. Existing May 2025 Maryland–Georgetown metadata also uses an incorrect 16:00Z on BetMGM; the official scheduled time is 18:30Z (previously verified actual 18:54Z). Official schedules, not book page placeholders, drive classifications.

### Omitted DK moneylines and multi-book evidence

| Game | Home / away | Direct DraftKings ML | Capture | Existing IDs with same book/prices (not same provenance) |
|---|---|---|---|---|
| 6085412 | Denver / Utah | -250 / +200 | A07 | O0049, O0050 |
| 6085420 | Jacksonville / Johns Hopkins | -115 / -115 | A07 | O0091, O0092, N0001, N0003 |
| 6085415 | Syracuse / Vermont | -265 / +210 | A07 | None |
| 6448514 | Princeton / Syracuse | -130 / +100 | A10 | None |
| 6448513 | Maryland / Georgetown | -370 / +255 | A10 | None |
| 6448512 | Penn St. / Notre Dame | +220 / -298 | A10 | None |


All six pairs occur in populated `MoneyLine` offers in the original captured state, with visible page tables corroborating the prices. They are not predictions, spread prices or reconstructed opposite sides. Case-sensitive or incomplete market extraction can miss this field; this audit does not claim to have established the exact cause in Grok's unexecuted code.

| Game | First book/capture, home / away ML | Second book/capture, home / away ML | Interpretation |
|---|---|---|---|
| Vermont at Syracuse, 2023-02-04 | DK, Feb 3 18:10:11Z: −265 / +210 | Caesars quoted by Action Network, Feb 4 03:47:51Z: −270 / +230 | 9h37m40s apart; one direct source, one editorial |
| Georgetown at Maryland, 2025-05-18 | BetMGM, May 13 15:28:31Z: −333 / +260; repeats May 16 02:41:55Z | DK, May 13 20:04:21Z: −370 / +255 | Two direct sources; first captures 4h35m50s apart |
| Notre Dame at Penn State, 2025-05-18 | BetMGM, May 13 15:28:31Z: +260 / −333; repeats May 16 02:41:55Z | DK, May 13 20:04:21Z: +220 / −298 | Two direct sources; first captures 4h35m50s apart |

These are **three two-book games, not simultaneous market comparisons**. Repeat May 16 observations do not create more games. DK and BetMGM differ in capture time; true bookmaker quote/update times are missing. No arbitrage, profitability or bookmaker-superiority inference is supported.

Grok's `multibookmaker_coverage.csv` has an additional provenance error: its Maryland and Penn State `book2_record_ids` are **N0286–N0289 / N0298–N0301**, which the actual combined data identify as **BetMGM** spread/total records, and `book2_urls` point to BetMGM. Those rows cannot support DraftKings. The independent findings use the actual DK May 13 capture and its event/outcome data, not the mislabeled columns. Grok's assertion of no second-book moneyline is contradicted by the captured DK content.

## Coverage reconciliation against actual data

All **1,995 rows and 46 supplier columns** in `odds_provenance_audit.csv` equal the corresponding fields in the saved Stage 3 ledger. The existing grouping function was rerun **only to recompute market groups**, without running the full audit or writing its outputs; it reproduces the saved market groups exactly. A complete ML pair requires valid opposing selections from the same event, book, source/version and snapshot; matched coverage additionally requires a supported original date/team join to a Stage 2 candidate game. Structurally complete does not mean pre-game, independently authenticated or licensed.

| Season | Supplier complete-ML flag | Strict dated raw-event ML | Matched games: any market | Matched complete ML | Pre-game evidenced ML games* | Direct / editorial-only ML | Approved |
|---|---|---|---|---|---|---|---|
| 2023 | 40 | 39 | 55 | 37 | 9 | 3 / 6 | 0 |
| 2024 | 103 | 103 | 111 | 103 | 14 | 14 / 0 | 0 |
| 2025 | 92 | 92 | 92 | 90 | 6 | 5 / 1 | 0 |
| 2026 | 34 | 34 | 0 | 0 | 0 | 0 / 0 | 0 |
| Total | 269 | 268 | 258 | 230 | 29 | 22 / 7 | 0 |


*The evidenced columns combine this review and the prior spot-check, including six audit-only DK observations not imported into existing data. The 2023 supplier flag includes one **undated** event; its assignment to season 2023 is a supplied label, not a verified game date. The 230 matched ML total and 258 any-market total remain conditional matches to the existing Stage 2 candidates; comprehensive season validation is not newly asserted here.*

The exact reconciliation is:

**269 − 34 (2026, outside the game-result reference) − 1 (undated) − 2 (2023 conflicts) − 2 (2025 conflicts) = 230.**

| Exclusion from matched complete-ML count | Existing IDs / events | Reason |
|---|---|---|
| 34 supplied 2026 events | 2026 complete-ML groups | No matching season in the existing 2023–2025 game reference; not claimed fictitious |
| 1 undated event | N0519,N0520; `undated_binghamton_vs_marist` | No defensible game date; cannot use article publication as game date |
| 2023 UNC–Rutgers, March 4 | O0230,O0231 | Team conflict; supplier substitution of Denver is not sufficient independent evidence |
| 2023 Towson–UMBC, March 4 | O0236,O0237 | Reference game is March 5; original-date conflict not silently repaired |
| 2025 Binghamton–St. Bonaventure, February 15 | N0136,N0137 | Existing school-corroborated result is March 25, ID 6386465; missing evidence of same-event postponement |
| 2025 Mercyhurst–UMass Lowell, February 16 | N0260,N0261 | Existing school-corroborated result is February 14, ID 6439959; original-date conflict |

Thus **92 − 2 = 90 in 2025**. The difference is primarily denominator and matching scope, not 39 new genuine moneyline games discovered by this expansion. The old strict dated raw-event count was already **268**; Grok's 269 adds the undated pair. The expansion does not add new underlying odds rows to the 1,995-row table. Princeton already had a structurally complete but unauthenticated −115/−115 article pair, so the newly observed different DK prices improve evidential coverage without increasing the structural-game count.

For another distinction, the old matched structural table permits **nine** multi-book ML candidates (1 / 4 / 4 by season), but this limited evidence review establishes only **three**. It neither authenticates nor disproves the other candidates. Grok's stated 23-new / 22-new-ML claim plus the prior four is 27 total / 26 ML under its own assumptions. The two official-start resolutions and omitted Princeton ML raise those cumulative evidential totals to 29 / 29. Within the existing selection-ID evidence alone there are 28 ML games; the 29th relies on the separately documented Princeton DK observation.

## Unverified prices, timing and source limitations

- **Post-game-only:** O1025,O1026 (Colgate–Penn State), O1037,O1038 (Richmond–Maryland), O1043,O1044 (Utah–Ohio State), O1049,O1050 (VMI–St. Bonaventure). Their stated prices reproduce in the Bet On Lacrosse capture of **March 8, 2026**, long after February 2025 games. Article dates do not establish unchanged earlier content. These eight IDs remain without independently reproduced pre-game evidence in this focused review. Earlier BetMGM pages contain different prices for some of these games; different prices cannot authenticate the listed pairs.
- **Not moneylines:** O0260,O0261, St. Bonaventure–Marquette March 25, 2023, are recorded as −8 / +8. The archived editorial table explicitly has moneyline unavailable and spread values. They are not valid American ML prices and remain excluded. No substitute prices were invented.
- **Retrieval differences:** the two April DK pages do not reproduce the supplier's raw bytes/empty-content claim. No associated games enter verified coverage. Other unresolved supplier rows and the earlier spot-check's post-game records were not upgraded merely because new evidence exists for unrelated games.
- **Timestamp precision:** all captures used for pre-game findings have independently resolved archive times and official scheduled starts. Exact actual faceoff is not independently established for every game. Exact bookmaker quote/update times remain unknown for all observations; DK update fields are empty and BetMGM capture headers are not operator timestamps.
- **Availability:** BetMGM options carry `offline` flags. Captured prices are visible, but executable betting availability, jurisdiction, limits and account access are unproved. An open flag in DK state is also not proof that a wager could have been accepted.
- **Market semantics:** no authenticated opening or closing series exists. BetMGM conversions use decimal d: American = 100(d−1) for d ≥ 2, otherwise −100/(d−1), rounded to nearest integer, ties away from zero. Original decimal values and unrounded calculations are retained. All selected BetMGM line prices, not merely the 2025 example, were compared with existing American records. No standard −110 prices were assumed.

## Permissions and research implication

No permissions flags were cleared. The existing `grok_stage3_source_permissions.csv` remains controlling project evidence, not a new legal determination: Internet Archive research-access language does not grant upstream-content rights; saved DraftKings restrictions require applicability review because the supplied terms discuss fantasy products; BetMGM's governing sportsbook policy and permitted reuse remain unresolved; Action Network's supplied terms restrict automated collection and content use; Bet On Lacrosse quotations do not establish a FanDuel data license. Action Network attributions to Caesars, FanDuel and bet365 likewise do not establish operator data-use permission. Current terms and institution/provider authorization were not re-audited in this focused content review. Read access, factual authenticity, internal academic use and redistribution are separate statuses. **No data are approved or imported.**

**Assuming appropriate permission is obtained and a review-only evidence table is approved, the 29-game sample supports a small descriptive exploratory comparison of bookmaker-implied probabilities with outcomes and leakage-safe model probabilities.** There are 22 games with direct ML evidence and seven with editorial-only evidence; report these strata separately. Convert observed two-sided prices to implied probabilities and, if used, document the chosen overround normalization. The sample is selected, small, uneven across seasons and books, and mixes long-lead and near-game captures. It does not support strong generalization, closing-line analysis or profitability claims. The three cross-book cases can be illustrated with their different capture times but cannot estimate a simultaneous bookmaker effect. No such calculation, model evaluation or training was performed here.

## Verification and preservation

Focused command (existing `dsf-lacrosse`, Python 3.11.18):

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q tests/test_odds_expansion.py tests/test_wayback_followup.py tests/test_inspect_grok_package.py
```

**45 tests passed.** Synthetic parser tests cover `MoneyLine` capitalization, Unicode signs, home/away orientation, missing/duplicate sides, absent editorial attribution, spread-versus-ML confusion, and bookmaker mismatches. Existing tests cover decimal rounding, capture-header agreement, strict timezone-aware pre-game classification, duplicate snapshot counting, ZIP traversal/collisions/symlinks and non-overwriting extraction. Real-artifact assertions verify the 96 IDs, 25/29 games, 230 reconciliation and retained permissions. Offline parsing additionally checked every supplied pair against actual captured bytes and existing IDs. Initial count-helper execution required `PYTHONPATH=.:src` for an existing sibling import; the corrected run completed and reproduced saved groups exactly.

The offline parser can be rerun while the temporary source cache exists, with a **new output path** (exclusive creation refuses overwriting):

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m src.verify_odds_expansion --output /tmp/odds_expansion_recheck.json
```

The 498-file pre-review SHA-256 snapshot was checked in `grok_expansion_preservation.json`: **all 497 non-cache files are unchanged**. Pytest updated only `.pytest_cache/v/cache/nodeids`, its test-index cache. No original datasets, reports, modeling outputs, ZIPs, proposal or finalized PDF changed. The finalized PDF retains SHA-256 `948a5ea3dc72892ff0db9cbddbea18216a7fc7c12979c1db6dbb42a82608d21c`. No supplier script executed; no quarantined odds moved into analysis.

New deliverables are this report, extraction/inventory artifacts, official-start CSV, fetch metadata JSON, independent checks JSON, coverage CSV/count-check JSON, preservation JSON, `src/verify_odds_expansion.py`, and `tests/test_odds_expansion.py`, plus the isolated unpacked supplier files. The detailed JSON separates observed prices, original IDs, exact source/capture metadata, official starts, errors and unresolved use permissions. Prior reports retain their historical findings unchanged.
