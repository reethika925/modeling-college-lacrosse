# Historical NCAA Division I men's lacrosse odds feasibility

Research date (America/New_York): 2026-11-09T21:14:02-05:00

**Overall feasibility: NOT CONFIRMED for a free, reproducible 2025 historical pre-game odds dataset.** The paid-provider capability is advertised, but no paid archive was queried and no free quote met all admission rules.

## Pilot results

| Measure | Games | Coverage of 20 |
| --- | ---: | ---: |
| Sampled | 20 | 100% |
| Verified historical pre-game odds | 0 | 0% |
| Moneylines | 0 | 0% |
| Spreads | 0 | 0% |
| Totals | 0 | 0% |
| At least two sportsbooks for the same game | 0 | 0% |
| Multiple pre-game odds timestamps for the same game | 0 | 0% |

Accepted odds records: **0**. Unique matched odds games: **0**. Collected sportsbooks: **0**. Three news-article game references have exact team/date identity matches but were excluded because the present pages were modified after kickoff and the quote's pre-game availability cannot be verified. These are three excluded candidate event references, not three accepted odds records. No invented or header-only `data/processed/lacrosse_odds_2025_pilot.csv` was created.

## Sample design and preservation

The input has 580 completed games and 77 teams. Its SHA-256 is `79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3`. The collector opens it read-only and checks its checksum before and after execution. Task 2's date gaps remain a limitation of this sampling frame; this investigation does not establish whole-season completeness.

Five genuine games were chosen per month, February–May 2025. In February, March and April, two involve a declared prominent-program group and three involve other programs. Dates are spread using fixed positions in date-sorted strata, with SHA-256 of seed 519 and game ID as the tie-break. May deliberately includes both semifinals, the final, and two other-program games. The prominent group is a sampling convenience, not a ranking. Scores are copied after selection and never used to select games or derive odds.

This is a purposive, small feasibility pilot, not a representative random sample. Championship-weekend inclusion favors games likely to receive coverage. Its percentages cannot be extrapolated to all 580 games.

## Sources investigated

| Source | Historical odds available? | Free? | Games matched | Markets available | Limitations |
| --- | --- | --- | ---: | --- | --- |
| [The Odds API](https://the-odds-api.com/sports/ncaa-lacrosse-odds.html) | Advertised; paid archive not queried | Current odds only; historical paid | 0 | Moneylines, spreads, totals advertised | No API key or paid call; documentation JSON excluded |
| [Cradl](https://cradllax.com/results/) | 2025 odds unverified | Website free; scraping prohibited | 0 | Current moneylines, spreads, totals and movement described | Terms prohibit scraping; robots disallows /api |
| [Oddschecker](https://www.oddschecker.com/lacrosse) | 2025 archive not located | Public current page | 0 | Current match result, handicap, totals and futures described | Live odds page is not a 2025 historical export |
| [OddsHub](https://www.oddshub.io/lacrosse) | Closing odds advertised; 2025 NCAA archive unverified | Public delayed comparison; collection restricted | 0 | Moneylines, spreads, totals advertised | Automated collection prohibited; closing-odds link led to soccer |
| [cleveland.com semifinal preview](https://www.cleveland.com/tv/2025/05/how-to-watch-ncaa-mens-lacrosse-final-four-free-live-stream-today-syracuse-vs-maryland-cornell-vs-penn-state.html) | Historical quotes visible; pre-game provenance unverified | Article readable | 0 | Moneylines, spread lines, total lines | Page updated after games; no verified quote timestamp |
| [syracuse.com championship preview](https://www.syracuse.com/tv/2025/05/where-to-watch-cornell-vs-maryland-mens-lacrosse-ncaa-championship-free-stream.html) | Historical quote visible; pre-game provenance unverified | Article readable | 0 | Moneyline | Post-game modifications; no archived pre-game quote verified |
| [Bet On Lacrosse](https://betonlacrosse.com/lacrosse-betting-odds-lines/) | Pro reports and college futures; no eligible game archive found | Public articles; report requires signup | 0 | College championship futures; professional betting reports | Futures and PLL/NLL reports do not match individual NCAA games |
| [GitHub octonion/lacrosse](https://github.com/octonion/lacrosse) | No qualifying 2025 odds found | Public repository | 0 | Results/statistics and predicted spreads; not verified bookmaker odds | NCAA game CSV paths reach 2023; no odds archive identified |
| [GitHub Tpanda03/LacrosseBetting](https://github.com/Tpanda03/LacrosseBetting) | No actual sportsbook archive | Public code | 0 | Generated model moneylines, spreads, totals and props | Statistical odds generation is expressly excluded |
| [SharpAPI open dataset](https://sharpapi.io/datasets) | Real snapshots, wrong sports/year | CC BY 4.0 advertised | 0 | MLB and 2026 soccer snapshots | No 2025 NCAA lacrosse file advertised |
| [Academic/open research: Bet Better](https://betbetter.world/studies/) | Aggregated research, not raw qualifying odds | CC BY 4.0 research advertised | 0 | Margin, calibration and movement aggregates | Publisher explicitly does not redistribute odds/prices/bookmaker identities |
| [PodiumOracle NCAA men's lacrosse](https://podiumoracle.com/ncaamlax/model) | Sportsbook history starts in 2026 on inspected page | Public summary | 0 | Forecast/market evaluation; raw 2025 prices not found | 2025 model forecasts are not 2025 bookmaker prices |

### The Odds API

- Exact URLs: https://the-odds-api.com/sports/ncaa-lacrosse-odds.html; https://the-odds-api.com/historical-odds-data/; https://the-odds-api.com/terms-and-conditions.html
- Access observed: Public documentation read with web tool; no historical API response obtained. Python robots.txt redirected to /404.html; no data endpoint attempted.
- Bulk download: Snapshot JSON API can return multiple events; no free NCAA archive download verified
- Bookmakers: FanDuel appears in the NCAA documentation example; actual 2025 game/book availability unverified
- Dates/games covered: Historical coverage table lists lacrosse_ncaa from 2025-02-01T04:40:38Z. Sport page instead says May 2023; conflict requires provider clarification.
- Historical timestamps: Historical snapshot and bookmaker/market update times advertised; five-minute snapshots advertised for this period
- License/access restrictions: Terms permit storage and research papers but restrict standalone raw-data redistribution. Authentication and paid historical entitlement required.
- Academic reproducibility: Potentially suitable through an existing licensed university archive or authorized academic export; not demonstrated by this free pilot

### Cradl

- Exact URLs: https://cradllax.com/results/; https://cradllax.com/about; https://cradllax.com/terms; https://cradllax.com/robots.txt
- Access observed: Ordinary Python requests returned HTTP 200 for landing, about, terms and robots pages; browsing tool returned 403. Stopped after reading terms; no 2025 filtered pages or game API fetched.
- Bulk download: No permitted public export found
- Bookmakers: About page identifies The Odds API as odds source and DraftKings for locked picks; 2025 book coverage unverified
- Dates/games covered: Results selector offers 2020-2026, including 2025; that does not establish archived 2025 sportsbook quotes
- Historical timestamps: Line movement and locked picks described; historical 2025 quote timestamps not verified
- License/access restrictions: Terms section 8 prohibits scraping; redistribution permission not established
- Academic reproducibility: Requires explicit authorized export/permission; model picks must remain separate from sportsbook prices

### Oddschecker

- Exact URLs: https://www.oddschecker.com/lacrosse
- Access observed: Public page accessible to web tool; no upcoming prices shown at inspection
- Bulk download: No 2025 NCAA export identified
- Bookmakers: No 2025 per-game bookmaker records verified
- Dates/games covered: General lacrosse includes different leagues and genders; no dated 2025 men's D1 archive verified
- Historical timestamps: Real-time updates advertised, not historical 2025 snapshots
- License/access restrictions: No open data license or bulk research permission established
- Academic reproducibility: Not established for this historical pilot

### OddsHub

- Exact URLs: https://www.oddshub.io/lacrosse; https://www.oddshub.io/terms; https://www.oddshub.io/football/england-premier-league/results
- Access observed: Public lacrosse and terms pages read. Generic closing-odds link led to an English soccer results page, which was not used as lacrosse data.
- Bulk download: No permitted 2025 NCAA bulk export found
- Bookmakers: General catalog includes Pinnacle, FanDuel and DraftKings; no 2025 NCAA book/event observations verified
- Dates/games covered: NCAA, PLL and NLL described; no verified 2025 men's D1 game archive
- Historical timestamps: Charts and closing lines advertised; 2025 pre-game snapshots not verified
- License/access restrictions: Terms section 6 prohibits automated odds collection and redistribution; limited public indexing exception is not bulk-data permission
- Academic reproducibility: Provider permission and verified historical coverage would be needed

### cleveland.com semifinal preview

- Exact URLs: https://www.cleveland.com/tv/2025/05/how-to-watch-ncaa-mens-lacrosse-final-four-free-live-stream-today-syracuse-vs-maryland-cornell-vs-penn-state.html
- Access observed: Public article read with web tool; no raw page cached or quote prices exported
- Bulk download: None identified
- Bookmakers: DraftKings attributed in article
- Dates/games covered: Cornell-Penn State and Maryland-Syracuse, May 24, 2025
- Historical timestamps: Published May 24 at 9:15 a.m.; updated August 4, 2025. Publication is not proof of odds-block availability before kickoff.
- License/access restrictions: Footer requires prior permission for caching/reproduction; no open dataset license
- Academic reproducibility: Excluded; needs permitted contemporaneous evidence and collection rights

### syracuse.com championship preview

- Exact URLs: https://www.syracuse.com/tv/2025/05/where-to-watch-cornell-vs-maryland-mens-lacrosse-ncaa-championship-free-stream.html
- Access observed: Public article read; no raw page cached or quote prices exported
- Bulk download: None identified
- Bookmakers: FanDuel attributed in article
- Dates/games covered: Cornell-Maryland, May 26, 2025
- Historical timestamps: Published May 26 at 9:34 a.m.; canonical page updated August 11, 2025, while AMP search display showed a 2026 update
- License/access restrictions: Publisher restricts caching/reproduction without permission; no open data license
- Academic reproducibility: Excluded; original article publication does not verify this quote's pre-game timestamp

### Bet On Lacrosse

- Exact URLs: https://betonlacrosse.com/lacrosse-betting-odds-lines/; https://betonlacrosse.com/draftkings-posts-2025-mens-college-lacrosse-championship-odds/
- Access observed: Public pages read; signup form and human-verification question not submitted
- Bulk download: Reports offered for PLL and NLL after signup, not verified NCAA game odds
- Bookmakers: DraftKings identified for November 1, 2024 college championship futures
- Dates/games covered: Futures for the 2025 title; individual February-May 2025 games unverified
- Historical timestamps: Futures publication date available; no game-level historical snapshots verified
- License/access restrictions: No NCAA odds dataset license established; no registration or verification bypass
- Academic reproducibility: Excluded as wrong market/competition coverage

### GitHub octonion/lacrosse

- Exact URLs: https://github.com/octonion/lacrosse; https://github.com/octonion/lacrosse/tree/679c40999c7c5184dae06806f57ad5c65b60e704/ncaa
- Access observed: Connected GitHub tool inspected complete 3,816-path tree at commit 679c40999c7c5184dae06806f57ad5c65b60e704; scoped odds search returned no files
- Bulk download: Repository files accessible, but no eligible archive
- Bookmakers: None verified
- Dates/games covered: NCAA result CSV filenames 2002-2023; no 2025 odds identified
- Historical timestamps: No historical bookmaker quote times verified
- License/access restrictions: No license path identified in inspected tree; public visibility alone is not an open-data grant
- Academic reproducibility: Pinned inspection reproducible; no matching odds data

### GitHub Tpanda03/LacrosseBetting

- Exact URLs: https://github.com/Tpanda03/LacrosseBetting; https://github.com/Tpanda03/LacrosseBetting/blob/88465b63f32cf83cda924593025bc0bfe48b1c86/README.md
- Access observed: Connected GitHub tool inspected README and tree at pinned commit; no code executed
- Bulk download: Code available; no historical real-odds dataset found
- Bookmakers: None verified
- Dates/games covered: Illinois Tech modeling project, not a demonstrated 2025 D1 sportsbook archive
- Historical timestamps: No genuine pre-game bookmaker snapshot times
- License/access restrictions: README claims MIT for code; that does not make generated prices real sportsbook records
- Academic reproducibility: Rejected as modeled rather than observed odds

### SharpAPI open dataset

- Exact URLs: https://sharpapi.io/datasets
- Access observed: Publisher's dataset page read; no unrelated sport files downloaded
- Bulk download: CSV files advertised through Kaggle
- Bookmakers: 23 source types advertised generally; no NCAA lacrosse book observations
- Dates/games covered: 2026 World Cup and MLB, not sampled lacrosse games
- Historical timestamps: Snapshot schema includes timestamps; not applicable to this sample
- License/access restrictions: CC BY 4.0 attribution required, per publisher
- Academic reproducibility: Open but ineligible; no sport substitution

### Academic/open research: Bet Better

- Exact URLs: https://betbetter.world/studies/; https://doi.org/10.5281/zenodo.21755380; https://doi.org/10.5281/zenodo.21764674; https://doi.org/10.5281/zenodo.21765675
- Access observed: Research landing page read; listed DOI datasets evaluated by publisher descriptions, not downloaded
- Bulk download: DOI-registered aggregate datasets offered
- Bookmakers: Identities not redistributed in the described open data
- Dates/games covered: Research window June 29-August 2, 2026; no 2025 NCAA lacrosse archive verified
- Historical timestamps: Aggregate dates, not game/book/quote snapshots for this pilot
- License/access restrictions: CC BY 4.0 for described open research, per publisher
- Academic reproducibility: Useful methodology context; cannot populate the requested game-level odds file

### PodiumOracle NCAA men's lacrosse

- Exact URLs: https://podiumoracle.com/ncaamlax/model
- Access observed: Public track-record page read; no forecast CSV imported
- Bulk download: No eligible 2025 sportsbook export verified
- Bookmakers: Pinnacle, DraftKings and bet365 named for bookmaker comparisons beginning April 14, 2026
- Dates/games covered: 2024-2026 forecast holdout; bookmaker comparison since April 14, 2026
- Historical timestamps: Pre-start pricing described for 2026 comparison, not 2025 records
- License/access restrictions: No raw historical odds redistribution permission established
- Academic reproducibility: Excluded by year and modeled-vs-observed distinction

## Matching and admission rules

Reviewed, exact aliases for Cornell, Maryland, Penn State/Penn St. and Syracuse are recorded in `reports/odds_2025_team_aliases.csv`. News article team lists are not home/away designations. The candidate audit records source names and IDs as supplied (event IDs remain null), candidate NCAA IDs, and the explicit exclusion reason. No uncertain association enters a real odds dataset.

A collectible record must identify men's Division I lacrosse, the source/bookmaker/market, genuine prices or quoted lines, and enough evidence to show the quote predates kickoff. A retrieval time in 2026 is not an odds time in 2025. An article's original publication time does not prove an odds block was present then if that page was later modified. Documentation examples, model prices, season futures, and other sports or leagues are excluded. Missing fields stay null; no price or timestamp is inferred.

## Acquisition recommendation

The free route is **not confirmed**, rather than proven impossible. The clearest permitted next step is a university-held licensed archive or a provider-authorized academic export from The Odds API or Cradl. Permission or an existing suitable subscription would be needed; none was requested or purchased. Before arranging access, have the archive owner demonstrate these 20 game IDs/team pairs, actual 2025 coverage, at least two books per event, both sides of the markets, pre-kickoff snapshot times and permitted research/redistribution rights. Resolve The Odds API's conflicting advertised start dates first.

For the professor's questions, spreads must retain their team orientation and prices. A bookmaker margin requires both outcomes of the same market/line/book at a comparable timestamp; do not calculate it from a spread number alone or combine prices from different books. Line movement needs two or more verified pre-game snapshots of the same event, book and market. This pilot supplies neither comparison.

If no authorized 2025 archive can be obtained, document that limitation to the professor and seek approval for a future prospective collection or a revised research scope. Prospective collection would not reconstruct 2025 prices. No future season is collected in Task 3.

## Reproduce and audit

```bash
conda activate dsf-lacrosse
python src/pilot_odds.py
python -m pytest -q
python -m pip check
```

The script performs no network requests. It reproduces the sample, audited candidate identities, coverage counts and this report from the saved research register. Website findings are a dated research snapshot, not a claim that access conditions never change. Exact searches and inspected repository commits are recorded separately. Research response files are evidence, not a collected odds database. Cradl scraping was stopped after reading its terms; its API is also disallowed by robots.txt.

## The 20 actual sampled games

| NCAA game ID | Date | Home | Away | Final home–away | Stratum |
| --- | --- | --- | --- | --- | --- |
| 6313182 | 2025-02-01 | Ohio St. | Utah | 13–19 | other_programs |
| 6310110 | 2025-02-08 | Jacksonville | Duke | 9–14 | prominent_program |
| 6309818 | 2025-02-15 | LIU | Iona | 14–9 | other_programs |
| 6310117 | 2025-02-22 | Duke | Michigan | 8–7 | prominent_program |
| 6309876 | 2025-02-28 | UMBC | Towson | 10–17 | other_programs |
| 6310482 | 2025-03-01 | Mercer | Drexel | 6–21 | other_programs |
| 6309494 | 2025-03-08 | Princeton | Rutgers | 11–5 | prominent_program |
| 6310179 | 2025-03-15 | Lafayette | Holy Cross | 13–8 | other_programs |
| 6311565 | 2025-03-22 | Yale | Cornell | 14–19 | prominent_program |
| 6310230 | 2025-03-29 | Saint Joseph's | Massachusetts | 10–11 | other_programs |
| 6313207 | 2025-04-04 | UMBC | UMass Lowell | 14–4 | other_programs |
| 6309806 | 2025-04-05 | Rutgers | Maryland | 8–6 | prominent_program |
| 6309861 | 2025-04-19 | Virginia | Lafayette | 13–8 | prominent_program |
| 6310263 | 2025-04-19 | LIU | Le Moyne | 13–6 | other_programs |
| 6381081 | 2025-04-29 | Lehigh | Colgate | 10–14 | other_programs |
| 6380961 | 2025-05-01 | Bryant | Binghamton | 10–9 | other_programs |
| 589864 | 2025-05-07 | UAlbany | Siena | 11–9 | other_programs |
| 589857 | 2025-05-24 | Cornell | Penn St. | 11–9 | championship_weekend_anchor |
| 589858 | 2025-05-24 | Maryland | Syracuse | 14–8 | championship_weekend_anchor |
| 589856 | 2025-05-26 | Cornell | Maryland | 13–10 | championship_weekend_anchor |
