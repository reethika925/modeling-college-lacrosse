# Stage 6A: minimum viable sportsbook benchmark

Prepared November 11, 2026. **No appropriately authorized historical sportsbook benchmark is currently available in this project.** This plan uses completed audit reports only; no odds CSV was imported, source was scraped, full audit repeated or source permission cleared.

Primary evidence: [Stage 3 expansion verification](grok_stage3_evidence_expansion_verification.md), [prior Wayback follow-up](grok_stage3_wayback_followup.md), [Stage 3 source-permission findings](grok_stage3_source_permissions.csv), [Stage 5 plan](stage5_modeling_plan.md), and [remaining blockers](stage5_remaining_blockers.md). Counts below are existing findings, not new authentication or matching work.

## Coverage is not approval

| Existing evidence class | 2023 | 2024 | 2025 | Total | Meaning |
|---|---:|---:|---:|---:|---|
| Structurally complete matched moneyline games | 37 | 103 | 90 | 230 | Complete supplied pairs with conditional game matches; not authenticated historical coverage |
| Games with independently reproduced pre-game display/quotation evidence | 9 | 14 | 6 | 29 | Includes separate audit-only observations and editorial quotations |
| Games with direct sportsbook ML evidence | 3 | 14 | 5 | 22 | Prices visible on archived sportsbook pages; executable betting availability unproved |
| Games with editorial-only ML evidence | 6 | 0 | 1 | 7 | Attributed prices in third-party articles |
| Games/odds cleared for analysis | 0 | 0 | 0 | 0 | No approved benchmark |

The 29-game count includes the newly observed Princeton–Syracuse DraftKings ML pair, whose prices differ from the existing unauthenticated article pair. It does not mean 29 newly cleared rows. The audit found 110 existing selection IDs with pre-game price corroboration and six additional DK paired observations; these are overlapping evidence/source units, not additive game counts. Do not invent IDs for the additional observations or overwrite original prices/provenance.

The reconciliation remains **269 −34 out-of-reference 2026 events −1 undated event −2 unresolved 2023 events −2 unresolved 2025 events =230**. None of these structural totals grants approval. The expanded source reports also found mislabeled BetMGM records/URLs in Grok's multi-book table and two nonmatching archive response hashes. Those provenance discrepancies remain unresolved; do not use the mislabeled supplier table as an authoritative sportsbook crosswalk.

## Smallest valid unit of comparison

One valid probability-comparison unit is **one genuine eligible game, one named sportsbook, one market with explicit settlement scope, and one independently evidenced pre-game capture containing both opposing prices**, plus an appropriately authorized model probability constructed using information available at that observation. A single unit can support a case illustration, not meaningful generalization or an estimate of betting profitability. There is no arbitrary fixed sample size that makes a biased or unauthorized sample valid.

For a credible exploratory report, predeclare eligible games, source strata, snapshot selection, metric definitions and uncertainty limits before viewing model-comparison outcomes. Report distinct games separately from bookmaker/capture observations and retain all exclusions. A larger permitted sample would be needed for precise conclusions; no minimum-power claim can be made from current coverage alone.

## Required fields and evidence gates

| Requirement | Minimum evidence and acceptance rule | Current remaining issue |
|---|---|---|
| Exact game join | Corrected date, season, both stable team keys, source game IDs/namespace and independently checked orientation; preserve original IDs and crosswalk evidence | Source-date/team conflicts must not be forced onto Stage 4 games; ESPN-only and NCAA IDs are different namespaces |
| Final result and market scope | Approved final score/winner with market rules covering full game/OT or other stated period | A regulation-only market cannot be scored against an OT-inclusive winner without the correct labels |
| Named sportsbook | Direct page identity or explicit third-party attribution, with original source URL and exact quote/capture reference | Third-party attribution is not a direct operator feed; mislabeled supplier book fields need independent reconciliation |
| Pre-game timing | Exact timezone-aware archive capture corroborated by headers, observed content and official game date/start; evidence must precede game start | Capture time is not operator update/quote time; article date alone and post-game captures do not establish pre-game prices |
| Paired moneyline | Both selections, original odds format/values, same bookmaker, market and capture/version; no mixing times/sources | A complete raw pair without historical price evidence remains only structurally complete |
| Spread comparison | Team-specific signed handicap, both corresponding prices and paired opposite handicap at the same book/capture, plus settlement/OT and push rules | A spread number is not a moneyline or an unpriced probability; no standard −110 may be supplied |
| Model probability at the observation | Frozen permitted model and history cutoff aligned to that capture; preserve prediction timestamp/cutoff and provenance | Game-date predictions may contain post-capture results; current pipeline needs a separate authorized as-of prediction extension |
| Permission | Documented permitted internal use of each game/odds/source/evidence component and output-sharing scope | All current odds remain unapproved; public access, authentication and correct arithmetic are separate from use permission |
| Audit trail | Input/evidence hashes, record/market IDs, match/orientation status, conversion method, quote-time/capture-time distinction and decision log | Do not silently replace differing prices or turn equivalent/repeated snapshots into independent games |

Missing values stay missing. No bookmaker, price, timestamp, handicap, opening/closing label or side may be invented. Pages with disabled/offline options establish displayed content only; they do not prove executable prices or jurisdiction/account availability.

## Probability conversion and margin adjustment

Use original decimal prices where available to avoid unnecessary loss from rounded American conversions. For decimal d>1, raw implied probability q=1/d. For positive American A, q=100/(A+100); for negative American A, q=|A|/(|A|+100). Validate numeric signs/ranges and preserve the original values.

For two opposing outcomes in a compatible no-tie full-game market, calculate overround `q_H+q_A−1`. Predeclare proportional normalization `p_H=q_H/(q_H+q_A)` and the analogous away probability. This is an explicit margin-removal convention, not proof of the bookmaker's beliefs or unbiased true probabilities. Record the overround and flag incompatible/stale/abnormal pairs for review rather than silently correcting them. Never estimate a missing side from an assumed margin.

Use the same game outcomes, matched subset and prediction cutoff for model and sportsbook Brier/log loss, accuracy and calibration. Do not compare model accuracy on all 578 games with bookmaker accuracy on six selected games and interpret the difference as performance superiority. Apply paired uncertainty at the game/date level; repeated captures/books require clustering/deduplication rather than independent-row bootstrap. With only a handful of cases, descriptive paired losses may be all that is defensible.

## Temporal alignment is an additional prerequisite

Several evidenced May 2025 prices were captured May 13 or May 16 for games on May 17–18. A model prediction using all outcomes before the actual game date can include results after the capture. Pre-game evidence by itself does not make that a fair same-information comparison.

Before any benchmark, implement and test an **as-of history path** for authorized games and observations. A conservative date-only convention is to use only corrected result dates strictly before the capture's date in America/New_York, omitting all same-date outcomes where completion/publication times are unavailable. Explicitly preserve the target game's known scheduled date and compute target-date rest from only the last game known at that cutoff; do not infer outcomes of intervening games. Document long-lead history/rest limitations and date/timezone assumptions. If that alignment cannot be established, exclude the observation from a like-for-like benchmark or present a clearly labeled unmatched-time case illustration.

The final 2025 logistic coefficients may use approved 2023–2024 data because those seasons precede 2025 observations. They may not use 2025 labels for refitting or model choice. An observed-capture time remains distinct from a missing actual bookmaker quote-update time; label results as comparisons against archived displayed prices, not authenticated closing or executable quotes.

## Spreads need a different target

Let final home goal margin be m=home_score−away_score, and the explicitly quoted home handicap be h. The home spread covers when m+h>0, loses when m+h<0, and pushes when m+h=0, subject to the stated market/OT rules. Preserve the selected team's sign and confirm opposite-side pairing; do not reverse signs merely because page order differs.

The four Stage 6A models predict **winning**, not covering a handicap. P(home wins) does not determine P(m+h>0). An actual probabilistic spread comparison requires a separately designed, permitted pre-game margin distribution or cover-probability model. No such model is implemented or trained in this stage. A descriptive comparison of a quoted spread with final margin is possible only after authorization and must not be called a win-probability model's spread forecast.

For integer handicaps with push probability, two price reciprocals alone do not identify unconditional win/loss/push probabilities. Conditional-on-no-push normalization must be labeled, or a justified three-outcome/push treatment supplied. No arbitrary probability is assigned to pushes. Profitability/expected-return analysis would also require actual prices, settlement and bet-execution assumptions; it is outside this minimum probability benchmark.

## Multiple books and opening/closing lines

Existing audits identify **three** multi-book moneyline games: Vermont–Syracuse (2023), Georgetown–Maryland (2025), and Notre Dame–Penn State (2025). The Syracuse case combines direct DK with editorial Caesars evidence; the May cases have two direct bookmaker displays. Captures differ by about 9h38m or 4h36m. They are not simultaneous observations and cannot establish an isolated bookmaker effect, arbitrage or a common executable market.

Report book/source/capture strata separately. For any pooled one-observation-per-game summary, predeclare deterministic selection (e.g. a fixed book priority, then the latest eligible independently evidenced pre-game capture) before looking at outcomes. Keep repeat captures in the ledger, but avoid counting them as additional games. A genuine cross-book comparison needs a common eligible observation cutoff, comparable markets/rules and independently supported prices for each book, with time offsets explicitly disclosed. Current asynchronous cases permit illustrations, not a strong bookmaker ranking.

No authenticated opening/closing series exists. The earliest/last available archive capture is not automatically the operator's opening/closing line. Those claims require additional chronological same-book evidence defining the first offered and last pre-start prices, appropriate timestamps/rules and permission. Opening/closing data are optional for the minimum snapshot comparison but mandatory for any movement/closing-line claim. No such evidence is being collected in Stage 6A.

## Minimum viable candidate benchmark, if authorized

The available evidenced cases comprise nine training-season games, fourteen validation-season games and only **six 2025 retrospective-evaluation games**. Pooling all 29 as if they were an untouched logistic test would be incorrect. The 2023 cases overlap parameter fitting, and 2024 is used for selection. Report them separately if used for diagnostics.

The six reported 2025 cases are Navy–High Point, Syracuse–Utah, Richmond–Cornell, Syracuse–Princeton, Georgetown–Maryland and Notre Dame–Penn State. Five have direct sportsbook ML evidence; Syracuse–Utah has editorial-only FanDuel evidence. These are candidate evidence cases, not an approved join table. Their original source IDs, game matching and quote prices must remain traceable to the existing audit ledgers.

The smallest useful next benchmark would therefore be a **tiny authorized direct-evidence 2025 case series**, with the editorial case reported separately if its intended use is also approved. It would require a deterministic book/snapshot policy and model probabilities generated as of each capture, not just the game day. Two games have multiple direct books, so bookmaker observations and unique games must remain separate. Even five or six qualified games are insufficient for broad market-performance conclusions; do not inflate coverage by adding training/validation games, post-game records, duplicate captures or structurally complete unauthenticated pairs.

## Exactly what is still missing

1. Actual intended-use authorization for game-result modeling and the relevant sportsbook/editorial/archive evidence; source-specific restrictions remain unresolved in the existing permission matrix. Internal analysis and raw/evidence redistribution are separate decisions. No authorized benchmark is currently present.
2. A separately approved, immutable benchmark table identifying game/book/market/capture, both original prices, orientation, settlement rules, evidence hashes, timing status and permission decision. Existing quarantined rows and audit-only DK observations have not been promoted or silently merged.
3. A predeclared snapshot/book selection and source-stratification rule, plus capture-time-aligned model features/probabilities from the approved historical cohort. The Stage 6A game-date pipeline alone does not yet provide this path.
4. For any spread-probability experiment: an additional approved target/model design, signed lines and corresponding prices, and explicit push/OT settlement treatment. For opening/closing claims: genuine opening/closing evidence rather than archive-position labels.
5. Acceptance of the limited scientific scope if the assignment requires richer market analysis. The revised proposal presents that conditional scope; instructor acceptance is not documented. No separate communication is initiated by this task.

These are prerequisites for the intended comparison, not a recommendation to purchase a feed, scrape restricted sites or collect another broad dataset. Until they are met, complete synthetic implementation testing and the results-only design; keep every historical odds record quarantined. Current approved sportsbook benchmark count: **zero**.

**Final verification:** 32 synthetic tests passed in `dsf-lacrosse` (Python 3.11.18). SHA-256 checks confirm all 546 pre-existing non-cache project files are unchanged, including original/corrected datasets, prior results/audits, all proposal drafts/backups and PDFs. No historical fit, prediction export, odds import or network collection occurred. See `stage6a_verification.json`.
