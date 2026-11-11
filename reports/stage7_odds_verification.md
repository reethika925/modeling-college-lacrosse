# Stage 7: record-by-record historical odds verification

Prepared November 11, 2026, in the existing `dsf-lacrosse` environment. **All 1,995 original records are accounted for exactly once.** This is an offline evidence audit, not an odds import, prediction run or use-permission decision. Original and quarantine flags remain unchanged.

## Findings

| Evidence class | Records |
|---|---|
| VERIFIED_PRE_GAME | 208 |
| VERIFIED_PRICE_TIMING_UNKNOWN | 163 |
| PARTIALLY_SUPPORTED | 299 |
| UNSUPPORTED | 1313 |
| REJECTED | 12 |
| TOTAL | 1995 |


**208 priced selection records** have exact claimed-source/capture support and pre-game evidence, across **39 corrected game candidates**. They form **104 paired market/capture observations**: 30 ML, 37 spread and 37 total pairs. Repeated May snapshots reduce the 30 ML observations to **27 distinct ML games**. These are published displays/quotations, not evidence that a bet was executable or that every game result is independently certified.

A separately labeled corroboration tier combines exact alternative-source/capture occurrences of collected prices with six already audited DK ML pairs omitted by the supplier. It contains **227 distinct selection observations across 43 games**, with **31 paired-ML games**, **32 priced-spread games** and **32 priced-total games**. One of the 43 games has only one corroborated collected ML selection in this scope. Original records retain their strict classifications; alternative prices do not repair their original timestamp/source claims. **No records have been approved for analysis.**

The broader counts are a conservative inventory tied to collected record values plus the six documented prior DK exceptions, not a census of every other offer embedded in the cached pages. Other parsed offers are context, not automatically a new verified research dataset. Additional prices outside that scope are not assigned fictional original IDs.

## Inputs, identity and preserved source fields

- `odds_provenance_audit.csv`: original combined audit, 1,995 rows / 46 fields, under `data/incoming/grok/stage1_28f5677d90c3/audit_package/`.
- `originals/ncaa_lacrosse_historical_odds_2025.csv`: 1,470 original rows, covering multiple seasons despite the filename.
- The recovered `ncaa_lacrosse_additional_odds_2023_2026.csv` inside the existing supplement ZIP: 525 rows. Its logical row order maps to N0001–N0525 only after checking season/book/market/selection/price/line/source tuples. The 1,470 rows map to O0001–O1470 through their raw record IDs. No supplier scripts are executed.
- Existing Stage 3 record/market/permission ledgers, the original/follow-up/expansion ZIP manifests, supplement evidence inventory and 1,995-row source map, independent fetch/check JSON, official-start tables, corrected game references, and Stage 6B use assessment.

The actual supplementary evidence-to-record map uses O/N IDs, even though an older prose note mentioned possible A identifiers. Actual quote tuples and IDs, not that note, control this join. All 46 combined-source fields, including original statuses, grades, permissions, source/evidence URLs and quotes, are unchanged in the new CSV. `raw_record_json`, source locators and supplementary IDs retain the earlier-source content too.

The new [record audit](../data/review/stage7_odds_record_audit.csv) has **1,995 rows and 96 columns**. It contains original claims alongside independent price/book/game/timing findings, observed evidence IDs/paths/hashes, current permission evidence, duplicate/contradiction annotations and reasons. Read IDs and quoted fields as strings; CSV booleans are explicit True/False. The new evidence class does not overwrite `technical_status`, `status`, `permission_class` or the independent permission status. `approved_for_modeling=False` throughout.

## What was independently inspected

Seventeen already collected archive pages remain in `/tmp/dsf_expansion_pages/` and `/tmp/dsf_wayback_verified/`. Their bytes, lengths and SHA-256 values were checked against the existing independent fetch metadata; exact URL capture stamps agree with recorded `Memento-Datetime`. **No network request was made**. Raw pages stayed in the temporary cache rather than being republished.

Direct DK College Lacrosse offers were decoded from captured JSON without executing JavaScript; BetMGM participant/market cells and event-specific date metadata were parsed from the captured HTML. Editorial tables require explicit attribution, exact selected team/price/line and contextual game matching. A missing price stays missing. A total without Over/Under direction is not made into two quotes; a favorite's heading handicap is not negated to invent the opponent's line. Prices are not inferred as −110. Four unlabeled, hidden zero-price DK placeholders are logged and omitted, not treated as moneyline offers.

The parser produced **876 context selections** across those pages; that is not a verified-original-record count. Only the source-linked observations in `stage7_summary_checks.json` contribute to the reported coverage. The previous independent 110-ID pre-game **price corroboration** result is retained: 108 now satisfy the stricter original-source/capture definition, while O1031/O1032 have earlier alternative direct evidence but only a late capture of their original editorial source.

The original evidence-file hashes match available cached bytes for **356 source records**. Missing original bytes do not automatically invalidate a price if the exact public pre-game source/capture was independently recovered; conversely, a hash of an absent file authenticates no content. Supplementary excerpts, source URLs, supplier `verified_in_raw=True`, grade A/B and existing file inventories alone never produce a verified class.

### Record classification rules

| Class | Required interpretation |
|---|---|
| VERIFIED_PRE_GAME | Exact selected price, stated line where relevant, named book, matched game, documented source/version and observed pre-game capture. Not an operator quote/update timestamp or permission clearance. |
| VERIFIED_PRICE_TIMING_UNKNOWN | Exact claimed-source price/book/game is reproduced, but pre-game availability for that original claim is not established. Includes known after-start/after-game captures; the separate timing column states that explicitly. |
| PARTIALLY_SUPPORTED | Relevant observed content supports only part of the claim: an unpriced/undirected line, a related event/market, alternative source/capture price, unresolved game matching, or an attributed-price/selection discrepancy. Not a usable verified-price class. |
| UNSUPPORTED | No matching independently inspectable quote is established in the collected evidence. It does not mean the original price is necessarily false. |
| REJECTED | Preserve the 12 prior rejected records, including duplicates. Some rejected prices are genuine repeated quotes; not every prior rejection rationale has been independently reproduced. |

Price verification follows selection identity, not the publisher's nominal home order. Original source URLs with the documented Action Network `/lacrosse-lacrosse/` typo are retained; the separately recorded comparison key normalizes that single path duplication. Query parameters are preserved, and unrelated URLs/captures are not equated.

A record-specific archive/time claim must match the inspected capture. When the same price appears at another source/time, its observation ID is stored separately and the original row is not upgraded to VERIFIED_PRE_GAME. O1031/O1032, for example, reproduce in a 2026 Bet On Lacrosse capture; a January 2025 direct BetMGM display corroborates those prices but does not make the original article's capture pre-game.

### Pre-game timing standard

For **164** VERIFIED_PRE_GAME records, existing independently reviewed official starts establish capture-before-start. The other **44** are from a strictly earlier US Eastern calendar date than the corrected game date, consistent with the stored game-date convention; no hour is invented. Same-day records without independently reviewed starts are not promoted using the sportsbook's own clock alone. Corrected game references retain their Stage 4 factual/corroboration limitations, recorded per row; this is not a new certification of all game outcomes, official dates or exact actual faceoffs.

Operator quote/update time remains independently unknown for **all 1,995 records**. The source data reuse the same timestamp in quote-capture and archive-capture fields on **544 records**. Those fields must not be reported as operator update times merely because they are populated. Article publication/modification times, scheduled start and actual faceoff are also separate quantities.

## Required record summary tables

### By market

| market | VERIFIED_PRE_GAME | VERIFIED_PRICE_TIMING_UNKNOWN | PARTIALLY_SUPPORTED | UNSUPPORTED | REJECTED | Total |
|---|---|---|---|---|---|---|
| moneyline | 60 | 59 | 50 | 407 | 7 | 583 |
| spread | 74 | 52 | 119 | 462 | 4 | 711 |
| total | 74 | 52 | 130 | 444 | 1 | 701 |


### By season

| season | VERIFIED_PRE_GAME | VERIFIED_PRICE_TIMING_UNKNOWN | PARTIALLY_SUPPORTED | UNSUPPORTED | REJECTED | Total |
|---|---|---|---|---|---|---|
| 2023 | 70 | 0 | 119 | 257 | 7 | 453 |
| 2024 | 88 | 4 | 35 | 563 | 2 | 692 |
| 2025 | 50 | 159 | 145 | 279 | 3 | 636 |
| 2026 | 0 | 0 | 0 | 214 | 0 | 214 |


2026 records are outside the current corrected results cohort; none is forced onto a 2023–2025 game.

### By original bookmaker attribution

| sportsbook | VERIFIED_PRE_GAME | VERIFIED_PRICE_TIMING_UNKNOWN | PARTIALLY_SUPPORTED | UNSUPPORTED | REJECTED | Total |
|---|---|---|---|---|---|---|
| BetMGM | 126 | 157 | 59 | 219 | 3 | 564 |
| Caesars | 4 | 0 | 13 | 146 | 1 | 164 |
| DraftKings | 72 | 4 | 157 | 648 | 8 | 889 |
| FanDuel | 4 | 0 | 37 | 195 | 0 | 236 |
| bet365 | 2 | 2 | 30 | 78 | 0 | 112 |
| UNATTRIBUTED | 0 | 0 | 3 | 27 | 0 | 30 |


UNATTRIBUTED preserves the original null-book cases; an adjacent table's bookmaker is not automatically assigned to an unattributed historical opener.

### By independently assessed pre-game timing status

| pregame_timing_status | VERIFIED_PRE_GAME | VERIFIED_PRICE_TIMING_UNKNOWN | PARTIALLY_SUPPORTED | UNSUPPORTED | REJECTED | Total |
|---|---|---|---|---|---|---|
| AFTER_GAME_DATE | 0 | 89 | 6 | 0 | 1 | 96 |
| AFTER_OFFICIAL_SCHEDULED_START | 0 | 66 | 0 | 0 | 0 | 66 |
| ALTERNATIVE_PRE_GAME_PRICE_ONLY | 0 | 2 | 21 | 0 | 4 | 27 |
| BEFORE_CORRECTED_GAME_DATE | 0 | 0 | 4 | 0 | 0 | 4 |
| NO_INDEPENDENT_TIMING_EVIDENCE | 0 | 0 | 262 | 1313 | 7 | 1582 |
| PRE_GAME_VERIFIED | 208 | 0 | 0 | 0 | 0 | 208 |
| SAME_DAY_START_UNRESOLVED | 0 | 6 | 6 | 0 | 0 | 12 |


`ALTERNATIVE_PRE_GAME_PRICE_ONLY` does not authenticate the original source/time. For the price-timing-unknown class specifically, 89 records have original-source captures after the game date, 66 after an officially scheduled start, six have unresolved same-day starts, and two have an alternative earlier price while their original source is only captured later. These 163 must not be called authenticated pre-game originals. The table's categories are mutually exclusive for row accounting; independent context timing is also retained in the CSV.

## Records, games and snapshots

| Unit | Original source/capture verified | Broader price corroboration |
|---|---|---|
| Pre-game selection observations | 208 | 227 |
| Distinct games with ≥1 supported price | 39 | 43 |
| Games with a complete paired market | 39 | 42 |
| Games with two-sided ML | 27 | 31 |
| Games with priced paired spreads | 32 | 32 |
| Games with priced paired totals | 32 | 32 |
| Paired market/capture observations | 104 | 113 |
| Paired ML capture observations | 30 | 39 |
| Game/book/capture/source snapshots | 47 | 51 |
| Distinct archive pages used | 12 | 15 |
| Games with two complete sportsbook MLs | 0 | 3 |
| Simultaneous two-book comparisons established | 0 | 0 |
| Authenticated opening-to-closing series | 0 | 0 |
| Records approved for analysis | 0 | 0 |


| Season | Original-source pre-game games | Original-source paired ML games | Broader price-corrob. games | Broader paired ML games |
|---|---|---|---|---|
| 2023 | 19 | 9 | 19 | 9 |
| 2024 | 15 | 14 | 15 | 14 |
| 2025 | 5 | 4 | 9 | 8 |


The strict 208 records comprise **188 direct sportsbook displays and 20 editorial quotations**. The broader 227 observations comprise 207 direct displays and 20 editorial quotations. Book names, source types and capture identities remain separate. The paired-market counts overlap in their games and cannot be added to get unique games. The broader set has 42 games with a complete paired market and one game with only a matching single collected price.

### Why 27, 29, 39 and 43 are different

1. Grok's 27 archived games were **23 claimed new games plus four prior spot-check games**; only 26 had ML under its own original extraction assumptions.
2. The prior Codex expansion additionally resolved Virginia–Notre Dame (March 25, 2023) and Virginia–UNC (April 7) using already checked official starts, yielding **29 games**. DK's captured Princeton–Syracuse ML was also populated, contrary to the supplier's claim, giving 29 ML game cases with the separately recorded observations. These prior findings are not rewritten.
3. Stage 7 covers every original record, rather than only the earlier spot-check lists. The same February 2023 DK and February 2024 BetMGM pages support priced spread/total records for **11 more games**: ten in 2023 and Mercer–Army in 2024. Original-source strict coverage is **39 games**, because High Point–Navy's collected original-source record still has late editorial capture evidence; its earlier direct evidence is kept in the broader tier. The strict 27-ML-game count is a different unit from Grok's earlier 27-any-market-game count.
4. Including the previously documented alternative/audit-only observations, the old 29 plus those 11 spread/total cases gives 40. Cached April pages also corroborate paired collected ML prices for Penn State–Michigan (April 6, 2025; O1279/O1280, −175/+135 in team orientation) and LIU–VMI (April 26; O1349/O1350, −130/+100), plus a matching **single Mercer +2000** for Mercer–Army (April 26; O1345). This gives **43 broader price-corrob. games / 31 paired-ML games**. The original article versions remain unverified and those original rows remain PARTIALLY_SUPPORTED.

The April 4 and April 25 DK raw responses do not match the supplier's earlier byte hashes/“empty” description. Their current cached hashes do match the existing independent fetch log, whose headers identify the exact captures; no fresh retrieval was attempted. The two new paired ML cases and single Mercer observation rely on those independently retained response representations and inherit that disclosed reproducibility caveat. This tier must not be silently equated with fully authenticated original-record provenance. Other unlinked prices in those pages are not promoted into the 1,995-row dataset.

## Attributions, contradictions, duplicates and opening/closing claims

- **Auxiliary book misattribution:** Grok's multi-book table labels N0286–N0289 and N0298–N0301 as DK and supplies BetMGM URLs. Their actual original rows correctly say **BetMGM** spread/total. DK support instead comes from its separate May 13 capture. This is an error in that auxiliary mapping, not grounds to rewrite the original book fields. No additional incorrect nonmissing bookmaker label is independently established among the matched contexts inspected here; this does not certify every unsupported attribution.
- **Unattributed opener:** O0097's −155 Jacksonville opener is explicitly reported in the cached pre-game article prose, while the current table quotes −115 and names DK. The opener's own book is null. Those are different market stages, not proof that −155 is false or that DK supplied the opener. The narrative evidence and unresolved book/time are recorded; classification remains PARTIALLY_SUPPORTED.
- **Wrong market:** O0260/O0261 are −8/+8 recorded as moneylines. The source explicitly marks ML unavailable and prints spread values. They remain REJECTED, with direct evidence pointers. No American ML price of ±8 is invented.
- **Wrong handicap sign:** O0305 records St. Joe's +4.5; the captured heading explicitly gives −4.5. It remains REJECTED with an independently reproduced contradiction. Two other supplier sign rejections lack their original page bodies here and are retained without claiming that their full reasons were independently re-proven.
- **Different versions are not automatically contradictory:** DK Princeton–Syracuse on May 13 shows −130/+100, whereas O1420/O1421 claim a later editorial −115/−115 pair. The earlier page does not authenticate that different later pair, nor prove it impossible. Keep original values; do not replace them or combine different captures into a pair.
- **Timestamp conflicts:** High Point's official noon EST differs from BetMGM's generic 18:00Z. Maryland–Georgetown's official 18:30Z differs from one sportsbook 16:00Z and a supplier 18:50Z. Quinnipiac–Bryant was noon EST, not the supplier's 13:00 EST. Existing February 16 BetMGM timers are stale/inconsistent; 69 minutes after scheduled start is not necessarily after completion. Independent dates/starts, not relative timers, determine the findings.
- **Duplicates/repeats:** all original record IDs are unique. There are **no additional exact claimed-source/selection/price/capture duplicate rows** under the explicit grouping key; **106 rows** share the same value tuple with another record across sources or times. Same value alone is not a duplicate: retain different captures as observations, not independent games. Seven of the 12 prior rejections are supplier duplicate dispositions. Nine rejection rationales in total remain retained without fully reproduced original-source reasoning; two wrong-market and one sign rejection have independent source support.
- **Opening/closing:** **25 original records are marked opening; zero are marked closing**. One cached narrative supports a reported opening assertion but not a named-book, timestamped, paired opening quote. No authenticated opening-to-closing series is established. Repeated pre-game capture series in the selected evidence show unchanged prices; no selected same-book pre-game price-change series was established. Do not infer opening or closing from first/last archived availability.

## Source use, reproducibility and preservation

Evidence class and data-use status are independent. Existing `requires_permission`, rejected/quarantine and source-specific classifications are preserved. Each row carries the prior source/Archive access, internal-use, automation and redistribution assessment and its documented terms URL/retrieval date. These unresolved/restricted statuses are not automatically legal prohibitions on every factual use; Stage 6B explains the distinction. This audit grants no intended-use clearance. All **1,983 non-rejected records remain quarantined**, and all 12 rejections remain present.

The audit is reproducible offline with `src/audit_stage7_odds.py`; it verifies original mappings/cache integrity, parses content and refuses existing output paths. To rerun without replacing this version, choose fresh paths:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m src.audit_stage7_odds \
  --audit-output /tmp/stage7_recheck.csv \
  --evidence-output /tmp/stage7_recheck_observations.json \
  --summary-output /tmp/stage7_recheck_summary.json
```

If the temporary raw cache expires, the report/JSON observations remain evidence of the completed check but cannot replace fresh inspection of the missing raw bytes. No download is automatically attempted. Exact cached pages and hashes:

| Page ID | Existing public capture | SHA-256 | Supplier expansion hash agreement |
|---|---|---|---|
| P01 | [capture](https://web.archive.org/web/20230204034751/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins) | `8b43f0afce9b8e3f5e9ceb1ea78c62e0f07c06f43fb283873f2186202cf8d6cf` | True |
| P02 | [capture](https://web.archive.org/web/20230325141823/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-saturday-week-7-notre-dame-vs-virginia-marquette-vs-st-bonaventure-march-25) | `5a0e0ca1150fdcd2a7286983200a13cf1915b56c47ac6b9e690129c93b348462` | True |
| P03 | [capture](https://web.archive.org/web/20230407193556/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-odds-picks-best-bets-virginia-cavaliers-vs-north-carolina-tar-heels-friday-april-7) | `a2e1913920e3e2761ce09eb90c421866f567dd5ff8626fd6873d4791043dbe86` | True |
| P04 | [capture](https://web.archive.org/web/20230415044110/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-week-10) | `78923576cc76142c5dd89360598159825d6850a6c70173b2e8b86af144ddd280` | True |
| P05 | [capture](https://web.archive.org/web/20230514033813/https://www.actionnetwork.com/lacrosse/college-lacrosse-betting-odds-picks-best-bets-for-ncaa-tournament-opening-round-sunday) | `04df888ed12dfcf9b50a1a44276f84e1da156eaae4c29582493e815e51664ced` | True |
| P06 | [capture](https://web.archive.org/web/20260308175741/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-0-bets/) | `a63c4b027cb3770319b5c53b7766bb031ed5bfa3f89bf78be3eea5cc09923dd4` | True |
| P07 | [capture](https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | `a135ee8a150325fc13373e32e7eff8e587e87245e832121cf788966266e11792` | True |
| P08 | [capture](https://web.archive.org/web/20250404065042/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | `ca80576eeaaa83d748fba87c23264a5098de95b7154a269805675e6b55b5051b` | False |
| P09 | [capture](https://web.archive.org/web/20250425111524/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse) | `0594e11795234c267926b956f3d42be4eb1a156385f206bb99722a299560331a` | False |
| P10 | [capture](https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game) | `af88030a600e510f85143ab9430c65894c9517b4db662074d8a075bbb088be94` | True |
| P11 | [capture](https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88) | `a66290f80fa918c25424c25b243d4fc7e32786612d538a5a17e6903f8994f47c` | True |
| P12 | [capture](https://web.archive.org/web/20240525152928/https://sports.betmgm.com/en/sports/lacrosse-88) | `67aeccd72e3e7e103b38c626f3d8ca7fa6dad980bdefbe111cd1f8d09ff19f2a` | True |
| P13 | [capture](https://web.archive.org/web/20250121025539/https://sports.betmgm.com/en/sports/lacrosse-88) | `d1f7a1e0b9fca6bb7cfa7be01a2060e00e6d6f2f3b9be8fc4058f6cae5b01d40` | True |
| P14 | [capture](https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213) | `40a81fb7cb4291451d8f0d32b7fd17b5c25b700b407a6b9d3f0537f547905355` | True |
| P15 | [capture](https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88) | `bf7d093f4199e936016b354adca05ad243ba1e5486c6c9aefee4d516901c1a55` | True |
| P16 | [capture](https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213) | `85bc9f7a577ee2819a991583ca292587919ec5bad8b768264897fe51cc744b30` | True |
| P17 | [capture](https://web.archive.org/web/20250301181913/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-4-saturday-bets/) | `8e966236db7d3b37eac197ffbc9818d0241665f653f5c93ccd888b4721bbb0be` | True |


Tests: `python -m pytest -q -p no:cacheprovider tests/test_stage7_odds.py tests/test_wayback_followup.py tests/test_odds_expansion.py`. **42 passed.** They cover synthetic source/capture/price/book/game/timing failures, unpriced markets, URL normalization, retained rejection/permission fields, all 1,995 IDs and original columns, mutually exhaustive summaries, observation units, exact decimal conversion and archive timing. The source parser also corrected a delimiter issue so `N/A` could not be misread as a moneyline/spread separator; the explicit ±8 rejection check now covers both sides. No research data were fabricated by these fixtures.

New outputs: this report; `stage7_odds_proposal_readiness.md`; the 1,995-row review CSV; `stage7_observation_checks.json`; `stage7_summary_checks.json`; `src/audit_stage7_odds.py`; and `tests/test_stage7_odds.py`. No original file, proposal or existing modeling result is modified.

**Final preservation:** all **553 pre-existing non-cache project files** retain their SHA-256 hashes, including original odds/game data, all permission/quarantine files, previous reports/model outputs and every proposal PDF. All 1,995 original IDs and source fields are accounted for; no status or permission flag was changed. The final focused suite passed **42 tests**. Only new Stage 7 review/audit artifacts were written. No network requests or historical model runs occurred. See `stage7_verification.json`.
