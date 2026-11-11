# Stage 7: sportsbook proposal-readiness assessment

Prepared November 11, 2026. **Sportsbook comparison can be described as a central, evidence-backed research objective with a bounded existing sample; it cannot yet be described as a completed or permission-cleared experiment.** This task does not edit the finalized proposal or run historical models. Detailed record decisions are in [the verification report](stage7_odds_verification.md) and [all 1,995 original records](../data/review/stage7_odds_record_audit.csv).

## Exact statements supported by the audit

| Statement | Supported quantity / qualification |
|---|---|
| Collected records audited | 1,995 unique original IDs, including 1,983 quarantined non-rejections and 12 retained rejections |
| Original-source/capture verified pre-game selections | **208 records across 39 game candidates**; 188 direct displays and 20 editorial quotations |
| Exact original-source paired ML coverage | **27 games**, represented by 30 paired capture observations; 9 / 14 / 4 games by 2023 / 2024 / 2025 |
| Priced spread and total coverage | **32 paired-spread games and 32 paired-total games**; 37 paired observations for each market. These game counts overlap |
| Broader pre-game price corroboration | **43 games**, combining linked original prices at alternate captures/sources and six previously audited DK pairs; includes one game with only one matching collected ML side |
| Broader paired-ML coverage | **31 games**, 9 / 14 / 8 by season, with 39 paired ML capture observations. Not 31 verified original timestamp claims |
| Multi-book paired ML cases | **3 games**, with different capture times; **0 simultaneous comparisons established** |
| Genuine authenticated opening-to-closing series | **0**; 25 source opening flags and one limited narrative assertion are not a closing series |
| Actual bookmaker quote/update timestamps independently established | **0**; archive observations are a different timestamp type |
| Records currently approved for analysis | **0**; permissions/quarantine are unchanged |

The **230 structurally complete matched ML games** remain a candidate ceiling from the original structural audit, not verified pre-game or approved coverage. The prior **27 versus 29** dispute is resolved in the verification report: Grok omitted two timing-resolved 2023 games and overlooked populated DK ML offers. Stage 7's larger **39/43** counts result from reviewing all original records against already collected pages, including more priced spreads/totals, not from new scraping.

## Recommended wording for a future proposal revision

The following is evidence-summary wording only; it has **not** been inserted into the proposal:

> We assembled 1,995 candidate historical odds records and completed a record-level evidence audit. Exact original-source pre-game prices were verified for 208 selection records across 39 collected NCAA game candidates, including 27 games with paired moneylines. A separately documented alternative-source/capture tier corroborates prices for 43 games and paired moneylines for 31, with provenance and archive-representation caveats. We plan a paired comparison of leakage-safe outcome probabilities with margin-adjusted sportsbook probabilities, conditional on the intended-use assessment and time-aligned model histories. All odds remain quarantined; no sportsbook performance, profitability or opening-to-closing result has been obtained.

For a very short three-page document, the conservative **208 / 39 / 27** figures are the clearest main numbers. If **43 / 31** are used, their alternative-source/audit-only status must be disclosed; they must not silently replace the original-record verification count. The full corpus is not an authenticated 230-game odds dataset.

## Feasible central comparison

After an appropriate intended-use basis is established, a small exploratory **moneyline probability benchmark** is technically plausible. Convert both prices from the same game, book, market and capture to implied probabilities and predeclare proportional overround removal. Preserve original decimal odds when available rather than replacing them with rounded American values. Compare model and bookmaker Brier/log loss, accuracy and calibration on **identical games**, with paired uncertainty and explicit small-sample limits. Evaluate direct displays separately from editorial quotations.

The full 31-game paired-ML figure includes nine games in 2023 and fourteen in 2024. Those overlap training and validation; they are not all independent later-season tests. The original-source strict tier offers only **four 2025 paired-ML games**. The broader tier offers **eight**: the earlier six documented cases plus Penn State–Michigan and LIU–VMI from the existing April capture representations. The single Mercer price cannot supply a collected two-sided pair or a margin adjustment by itself. Do not fill its missing matching original side from a different source/time or assume a standard price.

A first defensible experiment would therefore use an explicitly accepted evidence tier and source strata, freeze its actual IDs/book/snapshot policy before evaluation, and report a **small retrospective case series**. Permission/quality review can reduce the eligible sample further. A few games cannot establish broad sportsbook superiority or betting profitability. More data may ultimately be needed for power, but this task makes no acquisition recommendation or new collection.

## Alignment and market constraints that cannot be skipped

1. **As-of comparison:** several May prices precede the games by days. A model using all results up to game day may know more than the captured book did. The Stage 6A game-date pipeline needs a separately tested capture-time history path, using only results demonstrably available before the quote-observation cutoff. Conservative date-only exclusion of same-capture-date outcomes should be stated where actual publication times are unavailable. Do not fit logistic parameters on 2025 outcomes.
2. **Match/orientation:** use corrected game IDs/dates and stable team keys; retain each quoted selection's handicap sign. A source's nominal home designation does not prove physical home advantage. Date/team conflicts remain outside the supported joins.
3. **Two-sided normalization:** both ML prices must belong to the same book/capture and compatible full-game/OT rules. A public article date is not a quote time, an archive time is not operator update time, and the last known capture is not automatically closing.
4. **Sportsbook differences:** the three cases—Vermont–Syracuse, Georgetown–Maryland, Notre Dame–Penn State—show two books at asynchronous captures. They permit descriptive illustrations with time offsets, not simultaneous market or bookmaker-effect inference. Do not treat multiple books/captures as independent games.
5. **Spreads:** 32 games have priced paired spreads in the strict evidence tier, but the four Stage 6A models predict winning, not covering. A probabilistic spread comparison needs a separately designed margin/cover target and explicit push/OT rules. No cover model is implemented or trained here. Descriptive final-margin-versus-handicap analysis is different and also subject to intended-use scope.
6. **Execution/rights:** many BetMGM controls are marked offline. The evidence supports displayed prices, not that a bet could be placed. Preserve access, internal-use, automation and redistribution assessments separately. An unresolved flag is not itself a legal prohibition, but this evidence audit does not decide a lawful-use basis or authorize bypassing the current workflow.

## Limitations the proposal must retain

- Collection and independently corroborated complete-season coverage are not established; game-result matches are to the corrected candidate cohort, not a new season census.
- The odds sample is selected by public-source/archive availability and is small, uneven across years and books. The 2025 evaluation season has already been examined.
- **1,313 records remain unsupported** in the collected evidence; **299 are partial**, and **163 have exact price support without established pre-game timing for the original claim**. Unsupported does not mean proved fabricated, and partial does not mean usable.
- The original-source tier and broader price-corroboration tier answer different provenance questions. Original timestamps are not repaired by finding the same price elsewhere.
- The two April DK representations match existing independent fetch hashes but differ from the supplier's earlier bodies/empty-page claim. The newly corroborated April cases inherit that caveat. Raw cache expiration would prevent a fresh offline reproduction from manifests alone.
- No operator quote/update times, authenticated closing series or observed executable market is established. One reported narrative opener and 25 original opening flags do not support opening-to-closing movement claims.
- Quarantine and permission flags are unchanged. The project needs a documented intended-use basis for the chosen source/data/output scope, not necessarily a separate written license for every public fact. Instructor acceptance of the scientific scope is a separate question and is not implied by this report.
- The old 580-game model results are preliminary and are not sportsbook comparison results or corrected-cohort results. No new historical model or betting-performance metric was produced here.

## Readiness decision

**Ready to describe an audited, bounded sportsbook research component; not ready to claim completed market comparison results or execute on approved odds.** The exact conservative proposal evidence is **208 original-source pre-game records / 39 games / 27 paired-ML games**. The broader, qualified evidence ceiling for the audited collected values is **43 games / 31 paired-ML games**, with **3 asynchronous two-book cases and no authenticated closing series**. All remain separate from the **zero-approved-record** status.

The next decision is the intended-use assessment and choice of evidence tier; the next engineering step is capture-time alignment and a predeclared matched retrospective comparison. No proposal text, quarantine flag, original file or model is changed by this Stage 7 assessment.

**Final preservation:** all **553 pre-existing non-cache project files** retain their SHA-256 hashes, including original odds/game data, all permission/quarantine files, previous reports/model outputs and every proposal PDF. All 1,995 original IDs and source fields are accounted for; no status or permission flag was changed. The final focused suite passed **42 tests**. Only new Stage 7 review/audit artifacts were written. No network requests or historical model runs occurred. See `stage7_verification.json`.
