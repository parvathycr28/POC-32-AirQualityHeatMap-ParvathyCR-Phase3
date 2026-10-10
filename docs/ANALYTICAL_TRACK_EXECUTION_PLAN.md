# Analytical Track Execution Plan — Track A

## 1. Project and Track
- Project: Infocreon Aether Pulse Air Quality Heatmap
- Track: Track A — Comparative Intelligence
- Data version: phase3-v1.1
- Method version: track-a-comparative-v1.0.0

## 2. Analytical Question
How do the sampled air-quality metric values compare across cities for each pollutant in the canonical synthetic dataset?

## 3. Input
Use only `data/canonical/intelligence_data.csv`.
The canonical dataset is the single analytical input. Do not create a second cleaned analytical dataset or modify the operational frontend/dashboard.

## 4. Method
1. Validate required columns, data version, synthetic-data labels, record ID uniqueness, numeric values, timestamps, and compatible units.
2. Group observations by city and pollutant.
3. Calculate observation count, mean, median, minimum, and maximum for each group.
4. Calculate the pollutant-wide mean baseline.
5. Calculate each city-pollutant group's difference from that baseline and relative difference where defined.
6. Rank city groups within each pollutant by mean, using a deterministic tie-break.
7. Export machine-readable results and a summary.

## 5. Execution
Run from the repository root:
- `python data-science/scripts/run_analytical_track.py`
- `python data-science/scripts/validate_analytical_track.py`
- `python data-science/scripts/export_intelligence_results.py`

## 6. Expected Evidence
- `data-science/outputs/intelligence_results.json`
- `data-science/outputs/intelligence_summary.json`
- `data-science/outputs/validation_metrics.json`
- `data-science/outputs/weak_case_review.json`

## 7. Limitations and Guardrails
- The dataset is synthetic and must not be represented as real-world measurements.
- Results are descriptive comparisons, not causal conclusions or health advice.
- Do not build predictive models under this track.
- Do not modify the operational frontend/dashboard.
- Passing technical validation does not, by itself, constitute final project approval.

## 8. Current Status
Track A execution and technical validation have reported PASS in the current run. Final approval remains subject to the complete required evidence and review process.
