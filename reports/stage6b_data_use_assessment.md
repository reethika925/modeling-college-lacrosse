# Stage 6B: existing-data use assessment

Prepared November 11, 2026. **Recommendation: obtain a focused intended-use/terms-applicability review for a specified 1,706-game NCAA-led, facts-only modeling scope.** A defensible candidate scope can be identified from existing records, but this report does not clear it, declare it unlawful, or require written provider permission as the only possible basis for proceeding. Existing flags, datasets, outputs and proposal PDFs remain unchanged. No historical model was fit and no new data were collected.

## What the existing permission labels mean

`NOT_CLEARED_NO_CHANGE` is a project workflow status recording an unresolved decision. It is **not a finding that a source legally prohibits all use**. Similarly, a supplier's `restricted` classification is a lead to the actual language and applicable circumstances, not an adjudication of every internal factual analysis. Previous reports and flags remain historical records; the distinctions below qualify how to interpret them without rewriting them.

Five separate questions must be considered:

1. **Individual factual values:** scores, dates, opponents and game outcomes are factual information, distinct from a publisher's prose, photographs or page design. A copyright claim over a page/compilation does not automatically establish ownership of every underlying fact.
2. **Presentation or compilation:** articles, HTML presentation, original expressive content and potentially original selection/arrangement require separate analysis. A source's claimed compilation rights are not necessarily rights over individual facts; wholesale page/raw-package redistribution is different from independently arranged numerical features or aggregate findings.
3. **Access and acquisition:** robots rules, authentication, API scope and contractual automation terms concern how material was obtained. Public access or a permissive robots file is not an all-purpose license. A missing robots file is not affirmative content-use permission. Conversely, an acquisition restriction is not automatically proof that every later use of factual information is prohibited.
4. **Private academic analysis:** the actual intended use, binding contractual scope and applicable legal basis matter. Depending on the material and circumstances, use may require no copyright permission, may fall within an exception, may already be licensed, or may require permission. Educational purpose alone does not settle the question. An exception for copyrighted material and the noncopyrightability of particular facts are different possible bases, not interchangeable assumptions.
5. **Redistribution:** sharing original pages, supplier packages or source-derived datasets is a separate decision from processing facts privately and reporting model metrics. An unresolved redistribution license does not automatically veto internal analysis; permission for internal analysis does not authorize public raw-data release.

This is an assessment of existing project evidence, not a determination that particular contracts bind the student, that a fair-use defense is established, or that all facts can be reused regardless of source terms. No live policy version, new sports records, historical access or legal conclusion was collected in Stage 6B.

## Documented policy evidence and dates

The main cached terms are under `data/incoming/grok/stage1_28f5677d90c3/audit_package/evidence/odds/raw_terms/`. Their location under an odds-evidence directory does not limit the game-source clauses' relevance. Existing retrieval metadata are in `source_permissions_audit.csv` and `reports/grok_stage3_source_permissions.csv`. Most policy captures were recorded on **November 10, 2026, 16:55–16:57 UTC / 11:55–11:57 EST**. Supplier assertions are distinguished from actual cached language below.

| Source and documented URL | Existing terms artifact / displayed update | What is explicit | What remains unresolved |
|---|---|---|---|
| NCAA.com; `data.ncaa.com`; `sdataprod.ncaa.com`; [NCAA.com terms](https://www.ncaa.com/tos) | `tos_ncaa.com.html`; displayed February 21, 2023; retrieved Nov 10, 2026 | Claims content/compilation rights; restricts reproduction, exploitation and related uses, with exceptions including what US copyright law permits | Application to individual result facts, private analysis and particular data endpoints; binding notice/assent and acquisition context; whether applicable rights/exceptions already permit the proposed use |
| ESPN / Disney; [terms](https://disneytermsofuse.com/english/); public site API `https://site.api.espn.com/apis/site/v2/sports/lacrosse/mens-college-lacrosse/scoreboard` | `tos_disney.html`; displayed May 24, 2024; retrieved Nov 10, 2026 | Personal/noncommercial scope; express automated extraction/database restrictions; express language addressing ML creation, training, testing, benchmarking and validation | Actual applicability to the particular endpoint/material/use and acquisition circumstances; whether an existing exception/license/permission applies. A historic game year does not determine the version governing a later acquisition |
| Official school sites, e.g. `https://umbcretrievers.com/`, `https://mountathletics.com/`, `https://goprincetontigers.com/`; [SIDEARM terms](https://sidearmsports.com/terms-of-service) | `tos_sidearm.html`; displayed April 11, 2023; retrieved Nov 10, 2026; school evidence fetched Nov 10, approximately 11:55–12:09 EST per supplier log | Personal-use copying language and a written-permission condition for copying/storage outside that scope | Whether these terms govern each partner school page, whether this particular private factual verification/analysis falls within permitted use, and applicable rights in the material actually reused |
| SCORE; [lacrosse dataset page](https://data.scorenetwork.org/lacrosse/lacrosse_ncaa_div1.html); [CSV](https://data.scorenetwork.org/data/lacrosse_men_ncaa_div1_2022_2023.csv) | `reports/data_inventory.md`; publisher date July 24, 2023; downloaded Nov 9, 2026 at 20:38:36 EST | Public CSV was provided and successfully downloaded; credits/source recorded; no applicable license text was preserved in the reviewed project materials | Dataset-specific license and reuse scope are **not documented here**. This is not a finding that no license exists online, that written permission is necessarily required, or that the data are public domain |

The SCORE file has 72 rows × 23 columns and is a team-season aggregate, not game results. The recorded underlying source is NCAA statistics and the credited authors are Jack Fay, A.J. Dykstra and Ivan Ramler. A downloadable educational dataset provides context about intended access but is not itself proof of every reuse right. It is outside the Stage 5/6A feature plan, so its unresolved licensing is **not a blocker to the game-result-only experiment**.

A 2023/2024 event date is not a terms-retrieval date or proof of the policy effective when a supplier collected the record. The saved NCAA and SIDEARM documents have broad content-use clauses; absence of an explicit ML clause in the reviewed text does not prove that no other clause or endpoint agreement applies. The named NCAA.com terms must not be silently substituted with a different NCAA.org site's terms. An MIT license for an API client/query implementation, mentioned by the supplier, licenses software, not automatically NCAA data.

## Source-by-source assessment

### NCAA-led result facts

The proposed material is team identities, dates, final goals and winners, used to calculate prior-game summaries and fit interpretable prediction models. No original article prose, photos, page layout, player biographies or full source JSON is needed as a predictor. Presentation/compilation copying and private numerical processing should therefore not be treated as the same use.

The cached NCAA terms explicitly limit content uses while acknowledging statutory permission. The relevant passage includes **“except as otherwise expressly permitted under United States copyright law”**. The project has not established a categorical NCAA ML prohibition in the reviewed text, nor a blanket affirmative license. Its `uncertain` status records a real applicability question. A reasonable scope-specific review may support private modeling of lawfully held result facts without a separate written license; that possibility is not established merely by the current public URLs, and this report does not make that determination.

The existing local NCAA raw cache gives additional provenance support for 2025. For most older records the source label and recovered intermediate CSV are not a complete primary-response chain. That is a factual/provenance limitation, distinct from a legal prohibition. Removing article/ESPN metadata from model input does not retrospectively resolve how a supplier acquired or revised a record.

### ESPN: explicit restrictions deserve separate treatment

ESPN's saved Disney terms contain materially more direct language about automation and ML than the unresolved NCAA assessment. This is an **explicit restriction in documented text**, not a conclusion inferred from a missing license. Whether that text binds this particular use remains an applicability question; it cannot simply be ignored because the scores are factual or the work is academic.

Only one candidate, **`espn_401658258` (Princeton–Penn, May 5, 2024)**, is labeled ESPN-only as its original result source. It also has school corroboration, so it is not a fictitious or inherently unusable game. Excluding it from the proposed primary scope is a conservative provenance choice, not a ruling that the fact itself requires ESPN's permission. A later independently justified school-source route could be considered without erasing its original ESPN provenance.

There are **1,040** nonempty ESPN event-ID fields in the complete 1,707-game cohort, including **1,039** among the 1,706 NCAA-led records. Their presence does **not** establish that all those final scores originated from ESPN. The proposed projection omits ESPN IDs, cross-check fields and serialized original metadata. Nevertheless, field omission alone does not establish a clean independent acquisition history or negate a binding term; this point must be addressed in the scoped review rather than by a blanket 1,040-game exclusion or a blanket clearance.

### Official school evidence

Saved schedules are factual corroboration but also contain copyrighted presentation and source-use language. SIDEARM's documented personal-use wording is explicit; whether it applies to these school pages and this use is unresolved. Do not replace that uncertainty with a rule that every numeric score requires written school permission, and do not assume the term is irrelevant merely because a school site is public.

A useful correction to the supplier's description is necessary: school pages were **not only passive cross-checks**. Five NCAA-labeled game records have independently supported core repairs:

- `6136266`: UMBC–Mount St. Mary's, 2023; the final 16–6 result/status is supplied from school evidence because the original listing was pre-game with missing scores.
- `6138525`: Detroit Mercy–Marquette, 2023; supported date correction.
- `6454179`, `6386400`, `6449835`: Queens–Stony Brook, Le Moyne–Lafayette and UMBC–Binghamton, 2025; supported date corrections.

The proposed 1,706 records are therefore **NCAA-led with school-supported corrections**, not an exclusively NCAA-origin set of every core value. Removing these repairs or reverting to known wrong dates would be scientifically unsound. Include their source role in the intended-use assessment. The 378 school-corroborated result count measures evidence, not an automatically better license.

### SCORE aggregate data

No source-specific license conclusion can be drawn from the existing CSV inventory alone. The recorded HTTP/robots success documents the download process, not redistribution rights or a universal license. Conversely, lack of a recorded license does not establish that academic analysis is prohibited. The file is not needed for this experiment, and the pipeline should continue to exclude it both for scope and temporal-validity reasons. No new SCORE site/license lookup or aggregate-data analysis was performed.

## Sportsbook and editorial sources remain separate

All existing odds remain quarantined. This task makes no source clearance or odds import, and the historical game recommendation does not depend on clearing these sources. Existing audited coverage remains 230 structurally complete matched ML games, 29 games with reproduced pre-game evidence, and zero odds approved for analysis.

| Source | Existing documented terms/evidence and dates | Assessment for this task |
|---|---|---|
| Action Network; [terms](https://www.actionnetwork.com/terms) | `tos_actionnetwork.html`, displayed February 8, 2018; retrieved Nov 10, 2026 | Explicit automation/equivalent-manual extraction and content-use restrictions. Do not interpret permissive robots paths as permission or bypass instructions. Individual price facts and article expression still require distinct analysis; applicability and intended-use basis remain unapproved |
| DraftKings; [saved terms route](https://myaccount.draftkings.com/documents/us-terms-of-use) | `tos_draftkings2.html`, displayed June 30, 2026 and headed DAILY FANTASY terms; retrieved Nov 10 | Explicit automation/personal-content-use limits in that text, but sportsbook/nash endpoint and archived-content applicability is unresolved. Do not call a fantasy document verified governing sportsbook authorization |
| BetMGM; [NJ terms](https://help.nj.betmgm.com/en/general-information/legal-matters/general-terms-and-conditions), [MA terms](https://help.ma.betmgm.com/en/general-information/legal-matters/general-terms-and-conditions) | Supplement ZIP `priority3_permissions/terms_retrieved_2026-11-10/`; NJ displayed Sept 16, 2026, MA Sept 3, 2026; existing supplement records retrieval Nov 10, about 16:51 EST | Account/service/personal-entertainment and commercial-use language is explicit. Jurisdiction, entity, account-holder/visitor and archive-reuse scope remain unresolved. Initial geolocation shells were not full terms. A heading about reproduction/resale is not proof that every noncommercial use is banned |
| USA Lacrosse; [terms](https://www.usalacrosse.com/terms) | `tos_usalacrosse.html`; displayed March 3, 2026; project policy review Nov 10 at 08:39 EST and supplier capture later that day | Explicit harvesting/automated-collection restrictions recorded in `editorial_odds_permissions.json`. This restricts the documented collection workflow; it is not an independent conclusion on all later factual analysis. No new collection |
| Bet On Lacrosse; `https://betonlacrosse.com/` | Saved homepage; attempted terms URLs returned 404 on Nov 10 | Terms/license not located, not proven nonexistent. Copyright notice is not proof every price fact requires permission; research invitations do not establish a blanket license. Status unresolved |
| Lacrosse All Stars; `https://laxallstars.com/articles/terms-of-use` | Saved broken/404 terms route, Nov 10 | No operative terms established by the saved error body; unresolved, not automatically permitted or forbidden |
| LegalSportsBetting; `https://www.legalsportsbetting.com/` | Saved attempted terms/about pages, Nov 10 | Missing terms and some missing bookmaker attribution are separate rights and evidence gaps. No automatic clearance |
| Internet Archive; [terms](https://archive.org/about/terms.php) | Existing historical [June 6, 2020 capture](https://web.archive.org/web/20200606021003/https://archive.org/about/terms.php), retrieved Nov 10, 2026 | Research/noninfringing-use language concerns archive access and does not convey all underlying publisher/bookmaker rights. Do not treat a capture timestamp as an operator quote timestamp |
| FanDuel, Caesars, bet365 attributed in articles | No direct governing operator-policy evidence established by the reviewed game-source materials | Attribution is neither operator permission nor proof that a separate operator license is required for every quoted fact. Assess publisher/source chain and intended use; no clearance here |
| The Odds API | Supplier terms/permission row concerns zero imported observations | A vendor's general permitted-use status cannot clear another source's quarantined records or establish NCAA coverage. No purchase or API collection |

The supplement's drafted messages are not approvals. Its claim that an unlocated terms page means no terms exist is not adopted. Restrictions of these unrelated odds publishers must not be propagated as a blanket ban on independently sourced NCAA game facts.

## Proposed scopes from existing records

A read-only provenance count—not a repeated data audit or model run—establishes:

| Review scope | 2023 | 2024 | 2025 | Total | Interpretation |
|---|---:|---:|---:|---:|---|
| Current corrected candidates | 559 | 570 | 578 | 1,707 | Existing frozen cohort; flags unchanged |
| **Proposed NCAA-led facts-only scope** | **559** | **569** | **578** | **1,706** | Keep `original_result_source=ncaa_scoreboard`, with the five supported school repairs; exclude the one ESPN-only original |
| School-corroborated portion of that scope | 134 | 114 | 129 | 377 | Higher corroboration for sensitivity review, not separate license clearance |

The proposed 1,706-game membership rule is exact and reproducible from the current CSV. No subset file or new approval manifest was created. The nonempty ESPN ID fields are not used to classify the actual score source. The result/source labels remain supplier/intermediate provenance claims, with local raw corroboration where already present, not comprehensive proof of exclusive source independence.

The planned facts-only projection is `game_id`, `season`, corrected `game_date`, `home_team_key`, `away_team_key`, `home_score`, `away_score`, and `status`, with necessary lineage and the intended-use decision retained outside estimator inputs. Exclude ESPN metadata, original-row JSON, source page text, photographs, SCORE aggregates, all detailed player/team-statistics tables and all sportsbook data. The eight Stage 5 pre-game features remain transformations of strictly earlier admitted game facts. Do not use excluded/unapproved rows covertly as history.

The 377-game school-corroborated scope is an evidence sensitivity option, not the recommended sole training corpus: it is selected, has much thinner histories, and does not automatically avoid school-use questions. If used, clearly specify whether histories come only from those records or an independently allowed broader cohort. Rights status and factual corroboration are separate axes.

## Human decisions that remain, with a bounded recommendation

**Obtain further review of the specified 1,706-game scope, rather than treating the whole project as legally prohibited or demanding provider letters for every source.** A useful written project decision could document a lawful internal-use basis without obtaining new provider permission if the facts, applicable rights/exceptions and terms support that conclusion. It must not merely relabel `uncertain` as `approved`.

The remaining questions are specific:

1. Which NCAA.com/endpoint and school terms govern the actual acquisition and private processing, given notice/assent, host/entity and available collection evidence?
2. Does processing this narrowly projected factual material require a source license, already have an applicable lawful basis, or fall within an appropriate exception? Decide the actual workflow, not all imaginable redistribution.
3. Does ESPN's role in cross-check metadata affect the proposed NCAA-led factual values, or can independent provenance sufficiently support the projection? The one ESPN-only original is excluded by design pending a separate route.
4. What may be shared: derived aggregate metrics/figures, trained coefficients, numerical feature tables, raw facts, or full source/evidence files? Decide each needed output; no public raw-data release is required for the first internal experiment.

The existing university copyright guidance discussed in Stage 5 does not itself decide these questions. See the previously reviewed [Stony Brook Libraries permissions guide](https://guides.library.stonybrook.edu/copyright/permissions) and [university policy](https://www.stonybrook.edu/policy/_policies/policy-on-duplication-of-material-protected-by-copyright.html). Instructor acceptance of scientific scope is separate from source-use analysis and does not itself grant third-party rights. No contact was initiated.

**Current operational recommendation:** keep the existing flags and odds quarantine intact; document a focused human determination for the 1,706-game facts-only scope; then, if that basis supports proceeding, version the execution scope and run the existing chronological experiment. No categorical prohibition of NCAA factual modeling is established by this review. No source permission, university approval or historical execution is claimed today.

## Final preservation check

All **551 pre-existing non-cache files** retain their SHA-256 hashes: no missing or changed datasets, corrected review files, permission matrices/flags, pipeline code, prior reports, modeling outputs or proposal PDFs. The combined review dataset remains `980f190af9d05b5fb94ee1f0909dbb58ec6d0d33956db767c22c42f0c4aa0f30`; the revised proposal PDF remains `6e583b3be3b69fba9fe67a70352df689ef37808f87a2afb48779441f7925a47b`. Only the two requested Stage 6B Markdown reports were added. The existing synthetic pipeline suite passed **32 tests**; zero historical fits, new datasets, network requests or odds imports occurred.
