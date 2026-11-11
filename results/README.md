# Results index

These outputs come from the original 580-game 2025 preliminary experiment. Their bytes and locations were preserved during repository organization. They do not describe the corrected 2023–2025 cohort.

| Output | Existing location |
|---|---|
| Metrics table | [preliminary_model_metrics_2025.csv](../reports/preliminary_model_metrics_2025.csv) |
| Predictions | [lacrosse_predictions_2025.csv](../data/processed/lacrosse_predictions_2025.csv) |
| Features and labels | [lacrosse_model_features_2025.csv](../data/processed/lacrosse_model_features_2025.csv) |
| Feature definitions | [model_feature_schema_2025.json](../reports/model_feature_schema_2025.json) |
| Run summary | [preliminary_modeling_summary.json](../reports/preliminary_modeling_summary.json) |
| Results discussion | [preliminary_modeling_results.md](../reports/preliminary_modeling_results.md) |
| Bootstrap and feature audit | [preliminary_results_audit.json](../reports/preliminary_results_audit.json) |

## Preserved figures

- [Games per month](../reports/figures/games_per_month_2025.png)
- [Total goals](../reports/figures/total_goals_2025.png)
- [Winning margins](../reports/figures/winning_margins_2025.png)
- [Team win rates](../reports/figures/team_win_rates_2025.png)
- [Baseline performance](../reports/figures/model_performance_2025.png)

Older scripts and reports use these paths, so the files have not been moved merely to change the layout. Future experiments should use a separate run directory here, recording the input checksum, parameters, split, predictions, metrics and figure paths. The implemented multi-season models currently have synthetic test results only.
