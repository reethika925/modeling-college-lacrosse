# Stage 3: independent odds audit

Audit date: 2026-11-10. Offline, read-only review in `dsf-lacrosse`, Python 3.11. No new dataset, source retrieval, supplier-script execution, model run, main-data merge, or permission clearance.

## Decision

**All 1,995 records were mechanically inspected. Independently authenticated historical odds quotations: 0.** This is an evidence-availability finding, not a finding that all quotes are false. All 101 distinct historical quote-file references are absent from the supplied package, including a basename search. The 40-observation stratified review therefore returns **NOT INDEPENDENTLY VERIFIED** for every quote, bookmaker attribution, and pre-game-content claim. A URL, a hash of an omitted file, supplier prose, or a current HTTP 200 cannot demonstrate what a historical page contained.

The package supports conditional structure/matching estimates below, but does **not yet support a defensible bookmaker-versus-model experiment**. Provisional academic-analysis records approved by this audit: **0**; formally cleared: **0**. Internal academic use of factual observations and redistribution of source content are separate questions. Lack of a redistribution license alone is not treated as proof that all internal academic analysis is prohibited. Evidence and applicable permissions must be resolved before changing quarantine status.

## Inputs and actual inventory

Package root: `data/incoming/grok/stage1_28f5677d90c3/audit_package/`.

* `odds_provenance_audit.csv`: **1,995 × 46**, the combined supplier audit, not an independent raw source.
* `originals/ncaa_lacrosse_historical_odds_2025.csv`: **1,470 × 23**, despite its filename covers **2023–2026**; SHA-256 `a156ba06389acc2a3a4e0eadaaf33af361b081cc942d3f768fdc79b1d5ed42a1`.
* The external original `ncaa_lacrosse_additional_odds_2023_2026.csv` (**525 rows claimed**) was omitted; these observations exist only in the combined supplier-derived audit. Their original decimal fields/event metadata cannot be checked against that omitted CSV.
* `odds/odds_quarantine_permission_required.csv`: **1,983 × 46**; `odds/odds_rejected.csv`: **12 × 46**; `odds/odds_cleared_for_analysis.csv`: **0 × 46**. These are partitions, not additional unique quotes.
* `odds/odds_game_usability.csv` (**306 × 30**), corrected crosswalk (**308 × 17**), corrections (**11 × 7**), and source-permissions audit (**19 × 10**) are supplier claims; this audit recomputes game matches and market groups instead of accepting their totals.
* Evidence consists of policy/robots captures, source URL and live-status lists, and `evidence/odds/raw_odds_evidence_sha256.txt`; **no referenced historical quote HTML/JSON contents** are present. Policy pages, Bet On Lacrosse's homepage, and LegalSportsBetting's about page are not the referenced historical odds articles.

Counts match Grok's partition: **1,887 supplier-verified / 96 supplier-provisional / 12 supplier-rejected; 1,983 permission-required / 0 cleared**. Supplier evidence grades: **A 702, B 1,207, C 86**. Those grades have not been independently authenticated. There are **308 source event-ID strings**, not 308 independently established distinct genuine games. Grok merges two differently dated pairs of 2023 IDs; without the missing original evidence this audit does not accept those postponement attachments automatically.

Sportsbook attributions: DraftKings 889, BetMGM 564, FanDuel 236, Caesars 164, bet365 112, **missing 30**. Five named books; names are normalized string labels, not independently authenticated operator attribution. Markets: spread 711, total 701, moneyline 583. Source-domain counts:

| Source domain | Records |
| --- | --- |
| www.actionnetwork.com | 832 |
| betonlacrosse.com | 428 |
| sports.betmgm.com | 292 |
| sportsbook-nash.draftkings.com | 208 |
| sportsbook.draftkings.com | 204 |
| laxallstars.com | 25 |
| www.legalsportsbetting.com | 6 |

All IDs are unique; full-row duplicates: 0; exact same-observation duplicates under this audit's source/snapshot-aware key: 0. Grok separately marks seven cross-publication repeats as rejected and 50 later observations as repeats. Equal prices at different dates/books/articles do not alone establish duplicate historical observations; missing evidence prevents authenticating those seven cross-publication rejection reasons. No deduplication was applied to originals.

The three status-partition files' actual ID sets agree with the combined audit. For all 1,470 available original rows, American price, line, market, selection, bookmaker and source URL agree with the supplier audit (normalizing only empty/null tokens for comparison). The supplier renamed six original event IDs for Colgate–UAlbany, February 17, 2024, from `2024-02-17_colgate_vs_ualbany` to `2024-02-17_albany_vs_colgate`; `original_odds_game_id` and original row ID are retained in the new ledger. That alias/order normalization is distinct from silently correcting event dates or prices.

## Price, structure, orientation, and timestamps

American prices must be finite signed integer values with absolute value ≥100; decimal prices must exceed 1 and agree with American conversion to half a unit of their printed decimal precision, with a minimum 0.0000001 serialization tolerance, when both exist in the original 1,470 rows. For example, 1.8696 is consistent with −115; ordinary rounding and ~0.00000001 feed-serialization noise are not data errors. Conversion is a validation calculation, never a fabricated source field. Missing prices are not automatically invalid lines: a published unpriced spread/total is useful descriptive information but cannot be used as a priced bet. **No -110 defaults, opposite-side prices, or negated inferred spreads were added.** Actual check counts (overlapping flags):

| Independent check | Records |
| --- | --- |
| ARTICLE_MODIFIED_AT_OR_AFTER_START | 937 |
| MISSING_PRICE | 858 |
| LINE_NOT_EXPLICITLY_QUOTED | 39 |
| MISSING_BOOKMAKER | 30 |
| INVALID_AMERICAN_PRICE | 2 |
| TOTAL_SIDE_UNSPECIFIED | 6 |
| CLAIMED_OBSERVATION_NOT_BEFORE_START | 160 |
| MISSING_OR_INVALID_ORIGINAL_DATE | 10 |

The two ±8 moneylines are independently invalid American prices. Three claimed sign errors and seven claimed cross-source duplicates remain held as supplier rejects; their exact historical source-based reasons cannot be independently confirmed. Supplier's rejected record IDs and explanations:

| record_id | market | american_odds | reason |
| --- | --- | --- | --- |
| O0180 | spread | null | value NOT found in raw evidence (table 'Boston University (-1.5) vs. Vermont' book='Caesars'; header "Boston University (-1.5) vs. Vermont" printed line -1.5 for Boston University) |
| O0191 | spread | null | value NOT found in raw evidence (table 'Richmond University (-2.5) vs. Bucknell' book='DraftKings'; header "Richmond University (-2.5) vs. Bucknell" printed line -2.5 for Richmond University) |
| O0260 | moneyline | -8 | invalid American price -8 ( / price / <100); source printed "-8 (ML N/A)", i.e. a spread value, not a moneyline |
| O0261 | moneyline | +8 | invalid American price +8 ( / price / <100); source printed "+8 (ML N/A)", i.e. a spread value, not a moneyline |
| O0305 | spread | null | value NOT found in raw evidence (table 'St. Joe's (-4.5) vs. Hobart' book='DraftKings'; header "St. Joe's (-4.5) vs. Hobart" printed line -4.5 for St. Joe's  /  archive 20230415044110: header "St) |
| O0505 | spread | null | duplicate: same quote (book/market/selection/line/price) already recorded as N0011 |
| O1430 | moneyline | +260 | duplicate: same quote (book/market/selection/line/price) already recorded as N0284 |
| O1441 | moneyline | +260 | duplicate: same quote (book/market/selection/line/price) already recorded as N0297 |
| N0001 | moneyline | -115 | duplicate: same quote (book/market/selection/line/price) already recorded as O0091 |
| N0003 | moneyline | -115 | duplicate: same quote (book/market/selection/line/price) already recorded as O0092 |
| N0099 | total | null | duplicate: same quote (book/market/selection/line/price) already recorded as O0632 |
| N0236 | moneyline | +125 | duplicate: same quote (book/market/selection/line/price) already recorded as O1098 |

For spread pairing both explicit team selections, valid prices, and opposite signed lines are required. For totals both explicit Over and Under at the same positive total are required; six undirected total entries are not an Over or Under quote. Line-only rows cannot become priced pairs. The 39 supplier-marked inferred spread lines are excluded from priced structural candidates, even if the implied opposite handicap would be mathematically conventional.

Two-sided markets group **same event, book, market, source URL, evidence file, claimed snapshot/version and line type**. Books and distinct snapshot times are never pooled. Publication/modification timestamps identify a claimed editorial version only; they are **not sportsbook quote timestamps**. A complete pair in this table is therefore a **conditional supplied-data pair**, not authenticated historical betting coverage. Multiple books requires ≥2 separately complete moneyline pairs, not simply two bookmaker labels somewhere in a game's rows. Spread lines are attached to the selected team; reversing a publisher's home/away order does not negate the line.

All nonmissing timestamp fields are checked for parseable timezone-aware ISO timestamps. Quotes/archives/publication are separately compared with the supplier's claimed start; starts themselves are not independently authenticated in Stage 3. A pre-game publication does not establish that today's mutable article retained its pre-game odds. A modification at or after start blocks the separate claimed-pre-game subset unless a pre-game capture is also claimed; neither claim authenticates the original. Structural pairs do not imply pre-game availability. Exact sportsbook transaction/quote times cannot be established from the missing snapshots; capture time, even if recovered, is an observation time rather than necessarily the operator's own update time.

## Independent game matching and coverage

Reference: `reports/grok_stage2_game_assessments.csv`. Stage 2 proposed D-I-versus-D-I candidates are **559 / 570 / 578** in 2023 / 2024 / 2025; their full-season completeness and permissions remain unresolved. Match results are candidate joins, not new certification of every game. No reference file for 2026 is supplied, and no 2026 odds are forced onto 2025 games.

Require original date, season, both canonical team identities and a compatible event ID where present. For original rows use the unchanged original odds CSV; for additional rows use the crosswalk's original event fields, whose raw originals are missing. Use Stage 2's closed aliases plus the explicit unambiguous spellings `St. Joe's` → `Saint Joseph's` and `St. John's - New York` → `St. John's (NY)` seen in the crosswalk/reference. No fuzzy matching. Supplier-adjusted NCAA date/teams alone cannot repair an original-date/team conflict. Original home/away order is checked separately; odds selection identity is preserved. The per-row ledger retains IDs, dates, roles, source flags, and all independent findings.

| Season | Rows | Source event IDs | Matched games | Matched nonrejected rows | Unmatched rows | Candidate paired ML games | Candidate multi-book ML games | Candidate paired spreads | Candidate paired totals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023 | 453 | 63 | 55 | 413 | 33 | 37 | 1 | 22 | 22 |
| 2024 | 692 | 116 | 111 | 685 | 5 | 103 | 4 | 17 | 17 |
| 2025 | 636 | 94 | 92 | 621 | 12 | 90 | 4 | 29 | 29 |
| 2026 | 214 | 35 | 0 | 0 | 214 | 0 | 0 | 0 | 0 |

Across supplied reference seasons: **258 distinct matched candidate games**, **1719 nonrejected matched rows**; **264 rows** remain unattached. Candidate complete matched moneylines: **230 games**; candidate multi-book complete moneylines: **9**; candidate complete priced spreads / totals: **68 / 68**. These are structural counts, never verified pre-game coverage. **40 rows** are blocked specifically by original-date/team conflicts; none references an excluded Stage 2 game. Ambiguous candidate joins: **0**. Out-of-reference-season and missing-date observations are unresolved, not automatically false games.

All table market counts are **unverified structural candidates**, with named book, valid supplied price/line/selection/date, no supplier rejection or inferred-line flag, and a same-source/version pair. They do not require successful pre-game authentication. A separately reported **claimed-pre-game** subset additionally requires supplier grade A/B and a claimed observation before the claimed start; post-start modification requires a claimed pre-game capture to retain this lead. Neither subset is cleared for analysis. Differences from Grok's 269 paired-moneyline / 17 multi-book / 105 priced-spread / 105 priced-total game claims reflect game-date matching, filters and snapshot grouping. `grok_stage3_odds_coverage.csv` also gives raw-event candidate counts, one-sided priced spread/total counts, capture-claim counts, denominators, and record-level counts.

**2025:** 92 matched nonrejected candidate games / **578 eligible Stage 2 candidates** = **15.92%**, or 15.86% of the frozen original 580 records. Candidate paired moneylines: **90** (15.57% of 578); candidate multi-book paired moneylines: **4**. None is yet independently authenticated or approved for use. Even after evidence recovery, an article-selected subset may be biased toward prominent games and cannot establish full-season betting coverage.

Original-event rows not safely attached to an eligible result:

| season | game_id | original_game_date | match_status | records | candidate_ids |
| --- | --- | --- | --- | --- | --- |
| 2023 | 2023-02-04_hofstra_vs_merrimack | 2023-02-04 | DATE_CONFLICT | 8 | 6131581 |
| 2023 | 2023-02-04_holy-cross_vs_providence | 2023-02-04 | DATE_CONFLICT | 8 | 6085416 |
| 2023 | 2023-03-04_north-carolina_vs_rutgers | 2023-03-04 | UNMATCHED_TEAMS_DATE | 6 |  |
| 2023 | 2023-03-04_towson_vs_umbc | 2023-03-04 | DATE_CONFLICT | 6 | 6139977 |
| 2023 | undated_albany_vs_syracuse |  | NO_DATE | 1 |  |
| 2023 | undated_binghamton_vs_marist |  | NO_DATE | 2 |  |
| 2023 | undated_dartmouth_vs_merrimack |  | NO_DATE | 1 |  |
| 2023 | undated_hofstra_vs_navy |  | NO_DATE | 1 |  |
| 2024 | undated_air-force_vs_marquette |  | NO_DATE | 1 |  |
| 2024 | undated_army_vs_lafayette |  | NO_DATE | 1 |  |
| 2024 | undated_lindenwood_vs_marquette |  | NO_DATE | 1 |  |
| 2024 | undated_ohio-state_vs_utah |  | NO_DATE | 1 |  |
| 2024 | undated_ohio-state_vs_virginia |  | NO_DATE | 1 |  |
| 2025 | 2025-02-15_binghamton_vs_st.-bonaventure | 2025-02-15 | DATE_CONFLICT | 6 | 6386465 |
| 2025 | 2025-02-16_mercyhurst_vs_umass-lowell | 2025-02-16 | DATE_CONFLICT | 6 | 6439959 |
| 2026 | 2026-04-10_colgate_vs_lehigh | 2026-04-10 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-11_harvard_vs_yale | 2026-04-11 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-11_jacksonville_vs_utah | 2026-04-11 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-11_johns-hopkins_vs_ohio-state | 2026-04-11 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-11_north-carolina_vs_notre-dame | 2026-04-11 | OUT_OF_REFERENCE_SEASONS | 12 |  |
| 2026 | 2026-04-11_penn_vs_princeton | 2026-04-11 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_army_vs_colgate | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_boston-u_vs_holy-cross | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_bucknell_vs_umbc | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_delaware_vs_saint-joseph's | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_denver_vs_marquette | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_drexel_vs_virginia | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_georgetown_vs_villanova | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_hampton_vs_stony-brook | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 4 |  |
| 2026 | 2026-04-24_high-point_vs_richmond | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_hobart_vs_st.-bonaventure | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_lafayette_vs_lehigh | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_loyola-(md)_vs_navy | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_penn_vs_umass | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-24_providence_vs_st.-john's | 2026-04-24 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_air-force_vs_utah | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_bellarmine_vs_queens | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_binghamton_vs_vermont | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_brown_vs_yale | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_bryant_vs_umass-lowell | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_cleveland-state_vs_liu | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_cornell_vs_harvard | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_detroit-mercy_vs_vmi | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_duke_vs_north-carolina | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_hofstra_vs_towson | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_jacksonville_vs_mercer | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_le-moyne_vs_mercyhurst | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_michigan_vs_ohio-state | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_notre-dame_vs_syracuse | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |
| 2026 | 2026-04-25_robert-morris_vs_wagner | 2026-04-25 | OUT_OF_REFERENCE_SEASONS | 6 |  |

The three proposed 2023 one-day postponement corrections (Hofstra–Merrimack, Holy Cross–Providence, Towson–UMBC) are not silently applied. UNC–Rutgers versus Denver–UNC is a team-label conflict: do not substitute Denver just because supplier prose says the table had a typo. Mercyhurst–UMass Lowell has a February 16 versus February 14, 2025 date conflict (reference **6439959**, school-corroborated in Stage 2). **Grok's assertion that no Binghamton–St. Bonaventure game appears in the index is incorrect:** reference **6386465** is a school-corroborated March 25, 2025 game, Binghamton 6–5 St. Bonaventure. The odds event is February 15; without original source evidence, do not assert postponement or match these automatically. Undated picks remain unmatched; publication date is not substituted for game date. No odds reference targets either Stage 2 excluded 2025 game. All unresolved/ambiguous rows, including 2026 events outside the reference, are listed in `grok_stage3_unmatched_odds.csv`. No excluded or incorrect-date event enters the matched market counts.

## Reproducible independent evidence sample

**40 unique observations**; deterministic SHA-256 rank of `519|record_id`, greedy maximum marginal coverage of book/year/market/grade/source-domain/dataset/supplier-status strata, then rank-based fill. This is a diagnostic stratified sample, not a probability sample for estimating a population error rate. It is not the Cartesian product of every stratum.

| Dimension | Values covered |
| --- | --- |
| sportsbook | BetMGM, Caesars, DraftKings, FanDuel, bet365, null |
| season | 2023, 2024, 2025, 2026 |
| market | moneyline, spread, total |
| grade_audited | A, B, C |
| source_domain | betonlacrosse.com, laxallstars.com, sports.betmgm.com, sportsbook-nash.draftkings.com, sportsbook.draftkings.com, www.actionnetwork.com, www.legalsportsbetting.com |
| source_dataset | additional, original |
| technical_status | provisional, rejected, verified |

All referenced originals are absent. Each sample row separately records genuine-game corroboration status inherited from Stage 2, original orientation comparison, missing source evidence, price/book authentication status and pre-game verification status. **0/40 price quotes independently confirmed; 40/40 NOT INDEPENDENTLY VERIFIED.** A Stage 2 school-corroborated result can establish that a game was genuine without establishing that any bookmaker offered the stated price. The other 1,955 rows received mechanical checks and evidence-availability checks, not a successful original-content spot-check. No implication of fabrication or source verification is made from supplier flags alone.

## Permission review: separate questions

`grok_stage3_source_permissions.csv` retains all 19 supplier source rows and adds three bookmaker-attribution rows (FanDuel, Caesars, bet365). It separately records access/retrieval, internal academic use, redistribution, automation, evidence scope and clearance. All direct source classes remain unresolved or restricted pending applicability review; no flag was cleared. All **1,983 nonrejected records** still require appropriate review; the 12 rejects are also retained, not released. Permission review alone would not remedy missing factual evidence.

* **DraftKings:** saved `tos_draftkings2.html` contains automation and personal/content-use restrictions; its fantasy-contest wording makes governing sportsbook/nash scope a question requiring review. The other saved terms attempt is a 404. No new DraftKings access attempted.
* **Action Network:** saved terms restrict automatic and equivalent manual extraction and grant limited personal home copying. No scraping/manual circumvention or new article retrieval attempted. Applicability to the proposed internal research workflow requires provider or university review.
* **BetMGM:** supplied US terms pages are short geolocation shells. Blog or another legal entity's terms cannot prove governing US sportsbook rights. Status unresolved; no bypass attempted.
* **Bet On Lacrosse:** saved homepage invites historical research but does not itself supply a dataset license; attempted terms pages are 404. Copyright notice alone does not settle permissible internal use of factual prices. Review the intended workflow and rights separately.
* **LegalSportsBetting / Lacrosse All Stars:** unavailable/404 terms do not grant permission or prove every internal factual use forbidden. Missing bookmaker attribution and undated content are additional factual problems for some rows.
* **Internet Archive:** supplied terms are historical, not a current clearance. Research/noninfringing-use language is not a general license to every captured third party's material. No archived quote body was supplied; no restricted archival retrieval attempted.
* **Other named books:** no direct FanDuel/Caesars/bet365 source collections or governing policies supplied. Editorial bookmaker attribution does not by itself determine applicable rights. Review publisher permissions and relevant underlying rights rather than assuming every editorial fact requires every operator's written license.
* NCAA/SIDEARM/ESPN rows are reference-source permissions carried forward, not new game audits. Supplier's The Odds API “cleared” label applies to **zero observations** and does not clear this package or verify NCAA coverage. No purchase, credential use, new provider investigation, or odds collection occurred.

This is a forensic review of supplied policy captures, not a current legal opinion. Cached policy presence and robots permission do not establish contractual applicability, historic policy versions, copyright ownership, lawful acquisition, fair use or a redistribution license. Resolve those questions through the appropriate university/provider review. Private factual analysis, source-page copying, publication of derived research and redistribution of raw files should be evaluated separately. Existing quarantine stays intact; no new permission restrictions on already authorized internal auditing are inferred.

## Usability, opening/closing, and next evidence needed

Supplier claims **25 opening rows**, zero closing rows. Only explicit source-text claims count even provisionally; earliest/latest observed price is not automatically opening/closing. No original opening sentence or pre-game snapshot can be authenticated here, so **usable authenticated opening games 0 / closing games 0**. Same-price later captures are observations rather than line movement; authenticated movement cannot be established without evidence. All **1,995** rows have unresolved quote evidence, including the 12 held rejects. Historically supported priced records, authenticated pre-game games, and cleared comparable paired markets are all **0**.

To compare model home-win probabilities with bookmaker probabilities, first obtain the already-collected historical quote HTML/JSON (and original 525-row CSV) with source URL/capture metadata and lawful provenance; authenticate both teams' moneylines at one book and one pre-game observation; resolve original-date/team-label conflicts; obtain appropriate internal-use review. Only then calculate raw implied probabilities and remove overround within that same two-sided market (with method disclosed), mapping selection identity to NCAA home/away. Do not pool different books or times, use closing lines that were not published, invent -110 spread prices, or compute betting returns from unpriced lines. This task does not fetch those missing materials, train models, or merge any odds.

## Missing values (literal null/empty tokens normalized only in this audit view)

| Column | Missing records |
| --- | --- |
| record_id | 0 |
| source_dataset | 0 |
| orig_record_id | 525 |
| season | 0 |
| game_id | 0 |
| ncaa_game_id | 236 |
| ncaa_game_date | 236 |
| ncaa_home_team | 236 |
| ncaa_away_team | 236 |
| sportsbook | 30 |
| market | 0 |
| selection | 0 |
| selection_role | 0 |
| orientation_source | 701 |
| line | 583 |
| american_odds | 858 |
| quote_capture_timestamp | 1451 |
| article_published_at | 704 |
| article_modified_at | 798 |
| archive_capture_timestamp | 1117 |
| start_time_utc_used | 16 |
| start_basis | 16 |
| verified_in_raw | 0 |
| book_supported | 0 |
| url_status | 0 |
| url_authentic | 0 |
| ai_pick_or_projection | 0 |
| duplicate_of | 1988 |
| also_published_in | 1988 |
| repeat_observation_of | 1945 |
| grade_original | 0 |
| grade_audited | 0 |
| grade_reason | 0 |
| line_type | 0 |
| is_opening | 0 |
| is_closing | 0 |
| pre_game_published | 704 |
| independent_capture_pre_game | 0 |
| technical_status | 0 |
| permission_class | 0 |
| status | 0 |
| reason | 0 |
| evidence_file | 0 |
| evidence_detail | 0 |
| source_url | 0 |
| archive_url | 1117 |

Raw files are unchanged. Audit derivations do not fill source fields. A null NCAA reference in 2026 is distinct from a missing original event date; 858 null prices are distinct from malformed ±8 prices. Publication, archive, quote-capture and modification timestamps retain their distinct meanings.

## Reproduction and preservation

Run from the repository root:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python src/audit_grok_odds.py
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q tests/test_grok_stage3_odds.py tests/test_grok_stage2_games_stats.py tests/test_validate_incoming.py
```

The script writes only Stage 3 report artifacts. It has no network path and imports only our existing Stage 2 identity helpers, never scripts from the ZIP. It fails closed if original odds evidence unexpectedly becomes available, because that requires an actual content inspection rather than a filename-based approval. Tests include clearly labeled synthetic examples and read-only actual-package invariants. Final test totals, existence checks and SHA-256 comparison against all **457** pre-existing files are in `reports/grok_stage3_verification.json`; no original dataset, feature/prediction file or earlier report is intentionally changed. Full-season coverage remains unverified, and no research proposal is written.
