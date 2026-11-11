# CSE 519: Modeling College Lacrosse

This Fall 2026 Project 2 studies **NCAA Division I men's lacrosse game outcomes**. We compare probability forecasts from historical win rates, Elo ratings and logistic regression. Historical sportsbook prices are a second research component: we are checking which collected quotes have reliable game matches, prices and pre-game evidence before designing a benchmark comparison.

**Status: November 11, 2026.** Stages 1–7 cover collection, data review, model implementation and odds verification. Preliminary results exist for the original 2025 collection. The four-model, multi-season pipeline has been tested with synthetic fixtures; the corrected 2023–2025 experiment has not run. No sportsbook-performance results have been produced.

## Read these first

1. [Project structure](docs/PROJECT_STRUCTURE.md): where files live and how to navigate the repository.
2. [Stage 5 modeling plan](reports/stage5_modeling_plan.md): features, chronological splits and evaluation design.
3. [Preliminary results](reports/preliminary_modeling_results.md) and [results index](results/README.md): completed 2025 outputs.
4. [Stage 7 odds verification](reports/stage7_odds_verification.md): the latest record-by-record evidence findings.
5. [Academic references](docs/REFERENCES.md): the eight previously checked bibliographic references.

## Data we have

| Dataset | Location | What it contains |
|---|---|---|
| SCORE 2022–2023 aggregate | [Raw CSV](data/raw/score/lacrosse_men_ncaa_div1_2022_2023.csv) | 72 team-season rows, 23 columns. This is not a game log and is not used as 2025 pre-game information. |
| Original NCAA 2025 collection | [Game CSV](data/processed/lacrosse_games_2025.csv) | 580 completed games involving 77 teams; preserved with its original dates and listings. |
| Corrected 2023–2025 review cohort | [Combined CSV](data/review/lacrosse_games_2023_2025_corrected.csv) | 1,707 game candidates and 78 stable team identities: 559 in 2023, 570 in 2024 and 578 in 2025. |
| External packages and source evidence | [Incoming folder](data/incoming/grok/) | Original ZIPs, isolated extracted files, 3,428 team-game rows and 143,882 player-game rows. Detailed statistics have unresolved quality issues and are not current predictors. |
| Historical odds and record audit | [Original package](data/incoming/grok/stage1_28f5677d90c3/audit_package/) and [Stage 7 CSV](data/review/stage7_odds_record_audit.csv) | All 1,995 original odds IDs are retained, including 12 rejected observations. The review CSV adds evidence assessments without replacing source fields. |

The [exclusion ledger](reports/stage4_game_exclusions.csv) accounts for ten original game listings excluded from the corrected candidates. All 1,717 original game rows are accounted for. See [supported corrections](reports/stage4_game_corrections.md) for the date repairs and duplicate/wrong-season exclusions.

**Candidate counts are not a verified season census.** Stage 2 corroborated 378 results against checked school pages. The original 2025 collection received valid JSON on 81 of 181 requested dates; failed dates are not confirmed empty dates. Read the [collection validation](reports/games_2025_validation.md) and [Stage 4 readiness report](reports/stage4_modeling_readiness.md) before interpreting coverage.

## Folder organization

```text
dsf-project/
├── README.md
├── requirements.txt                 # Initial data-tool dependencies
├── requirements-modeling.txt        # Full environment snapshot
├── src/                             # Collection, validation, audit and modeling code
├── tests/                           # Automated checks and labeled fixtures
├── data/
│   ├── raw/                         # Original SCORE and NCAA responses
│   ├── incoming/grok/               # Original deliveries and isolated extractions
│   ├── processed/                   # Frozen 2025 collection and preliminary outputs
│   ├── review/                      # Corrected candidates and odds audit ledger
│   └── quarantine/                  # Staging location; currently a placeholder
├── reports/                         # Research reports, ledgers, checks and manifests
│   └── figures/                     # Five preserved preliminary-result plots
├── results/                         # Index of completed outputs; future run location
├── research/                        # Earlier investigations and preserved evidence
│   └── odds_evidence/               # Existing archive HTML and fetch metadata
└── docs/                            # Repository guide, bibliography and cleanup log
```

Existing research paths were retained so old reports, manifests and scripts still agree. `results/README.md` links to the frozen metrics, predictions and plots at their original locations. Proposal drafts, PDFs, submission checklists and proposal-only notes have been backed up outside this shared folder. Research evidence reports remain in the project.

## Models and completed results

The original [2025 implementation](src/model_lacrosse.py) created 45 pre-game features and evaluated three baselines on all 580 collected games, including early-season cold starts:

| Model | Accuracy | Brier score | Log loss |
|---|---:|---:|---:|
| Constant 50% | 58.10% | 0.250000 | 0.693147 |
| Smoothed prior win rate | 66.72% | 0.222749 | 0.636925 |
| Elo | 66.03% | 0.232781 | 0.658265 |

These are **preliminary results from the original, uncorrected 2025 collection**, which needs two date corrections and two exclusions. They are not results for the corrected 578-game season. Predictions of exactly 0.5 select the nominal home team, explaining the constant baseline's accuracy. No model has been compared with sportsbook outcomes yet.

The [multi-season pipeline](src/model_lacrosse_multiseason.py) implements four models:

- Constant home-win probability of 0.5.
- Historical win rate with alpha-1 smoothing.
- Elo initialized at 1500, with K=20 and scale=400.
- L2 logistic regression with eight pre-game predictors: differences in prior game counts, smoothed win rate, goals scored, goals conceded, recent form, rest, Elo and missing history.

Histories reset each season. All predictions for a date are fixed before any results from that date update team histories. Logistic scaling uses training data only. The planned split is **2023 training → 2024 validation → retrospective 2025 evaluation**, with regularization selected on 2024 Brier score and final fitting on 2023–2024. The 2025 season has already been examined and is not an untouched test set.

Evaluation functions cover accuracy, Brier score, log loss, calibration tables, season/subgroup comparisons and paired date-cluster uncertainty with week-cluster sensitivity. Historical execution controls remain in place; importing the module or running it directly does not start an experiment.

## What the odds audit established

The latest audit accounts for all 1,995 original records:

| Evidence classification | Records |
|---|---:|
| `VERIFIED_PRE_GAME` | 208 |
| `VERIFIED_PRICE_TIMING_UNKNOWN` | 163 |
| `PARTIALLY_SUPPORTED` | 299 |
| `UNSUPPORTED` | 1,313 |
| `REJECTED` | 12 |
| **Total** | **1,995** |

The strict source/capture-matched tier contains **208 pre-game selection records across 39 game candidates**, including **27 games with paired moneylines**. A broader tier supports prices for **43 games / 31 paired-moneyline games**, using alternative captures/sources and previously documented pairs. That broader tier does not verify every original source or timestamp claim. These overlapping counts must not be added together.

The earlier **230 structurally complete matched moneyline games** describe paired record structure, not authenticated pre-game coverage. Three games have two-book evidence captured at different times; no simultaneous market comparison or authenticated opening-to-closing series is established. Archive capture times are not actual bookmaker quote times.

Odds remain separate from model inputs. A future comparison needs a declared evidence tier, exact game/book/market matching and predictions based only on information available before each capture. Spread evaluation also needs a different prediction target. See [minimum benchmark requirements](reports/stage6_sportsbook_minimum_requirements.md).

## Python setup

Use the existing **`dsf-lacrosse` Conda environment with Python 3.11**. From the project root:

```bash
conda env list
conda activate dsf-lacrosse
python -c 'import sys; print(sys.executable); print(sys.version); assert sys.version_info[:2] == (3, 11)'
```

If the environment is missing, stop and coordinate its setup with the project maintainer. Do not create a `.venv`. The local verified interpreter is `/Users/kiri/miniconda3/envs/dsf-lacrosse/bin/python`.

The environment is already installed. To restore its dependencies when needed:

```bash
python -m pip install -r requirements-modeling.txt
```

The logistic regression implementation uses NumPy; scikit-learn is not required. `requirements.txt` retains the original downloader dependency snapshot.

## Tests and reproducibility

Run all existing checks without creating cache files:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider
```

For the four-model pipeline alone:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_model_lacrosse_multiseason.py
```

Its 32 tests fit only clearly labeled synthetic fixtures. Full-suite integration tests also read local research artifacts and recompute checks in memory. They do not collect data or fit historical logistic models. The data and evidence folders must be present for the full suite; `.gitignore` keeps local data and evidence caches out of automatic Git staging.

Recompute the published 2025 metrics from saved predictions, without training or changing files:

```bash
python -c 'import pandas as pd; from src.model_lacrosse import evaluate_predictions; p = pd.read_csv("data/processed/lacrosse_predictions_2025.csv"); print(evaluate_predictions(p).to_string(index=False))'
```

For the odds-review checks:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_stage7_odds.py tests/test_wayback_followup.py tests/test_odds_expansion.py
```

The [evidence-cache guide](research/odds_evidence/README.md) explains the preserved offline inputs. Original collection and modeling commands can overwrite frozen outputs; use the read-only checks above to reproduce existing findings. Never execute scripts delivered inside external packages. Keep original IDs, raw bytes, correction ledgers and evidence classifications intact.

## Next experiments

- Finalize the multi-season input scope and retain its version/checksum.
- Run the predeclared four-model experiment and save a new run under `results/`.
- Compare calibration and paired uncertainty on identical evaluation games.
- Build a capture-aligned sportsbook benchmark from the supported evidence tier.
- Resolve remaining coverage, source corroboration and detailed-statistics quality gaps.

No new multi-season results, sportsbook comparison or betting-profit claim is implied by these plans. See the [organization log](docs/REPOSITORY_ORGANIZATION.md) for the cleanup inventory and remaining reproducibility gaps.
