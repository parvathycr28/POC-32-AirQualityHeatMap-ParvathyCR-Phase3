# Phase 3 Analytical Track Development

## Project
- Project ID: POC-32
- Project title: Infocreon Aether Pulse Air Quality Heatmap
- Selected track: Track A — Comparative Intelligence
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`

## Purpose
This directory contains the analytical validation, comparative intelligence implementation, reproducible execution scripts, outputs, and supporting evidence for Phase 3.

The selected track compares sampled city measurements within each pollutant and compares city-pollutant means with the corresponding pollutant-wide mean.

All canonical observations are synthetic. The outputs do not establish real-world air quality, regulatory compliance, health risk, causation, or predictive performance.

## Canonical input
The only analytical input is:

`data/canonical/intelligence_data.csv`

Do not create a second cleaned analytical dataset or silently alter the canonical input. Changes to the canonical schema or data version require corresponding updates to validation and documentation.

## Scripts
Run these commands from the repository root with the project's Python environment activated.

### Execute Track A
```bash
python data-science/scripts/run_analytical_track.py
```

### Validate the outputs
```bash
python data-science/scripts/validate_analytical_track.py
```

### Verify export metadata and counts
```bash
python data-science/scripts/export_intelligence_results.py
```

Run them in this order. The validation script should run after the analysis script so the validation metrics and weak-case review reflect the latest generated results.

## Generated outputs
- `outputs/intelligence_results.json` — group-level descriptive comparisons.
- `outputs/intelligence_summary.json` — summary, key findings, versions, and limitations.
- `outputs/validation_metrics.json` — validation checks and numerical comparison errors.
- `outputs/weak_case_review.json` — sensitivity cases and interpretation limitations.

The current expected input contains 96 rows and 20 columns, yielding 32 city-pollutant result groups. Confirm these expectations against the canonical dataset and the validation output when the input changes.

## Validation and interpretation
A validation `PASS` means the implemented checks passed for that execution. It is not independent formal approval and does not establish real-world validity.

The weak-case review includes leave-one-timestamp-out comparisons. Ranking changes, especially for NO2 and PM2.5, should be retained and considered during interpretation.

## Supporting documents
See the project-level `docs/` directory:
- `ANALYTICAL_TRACK_EXECUTION_PLAN.md`
- `ANALYTICAL_INPUT_CONTRACT.md`
- `ANALYTICAL_METHOD_REPORT.md`
- `ANALYTICAL_VALIDATION_REPORT.md`
- `WEAK_CASE_AND_LIMITATION_REVIEW.md`
- `INTELLIGENCE_OUTPUT_CONTRACT.md`

## Reproducibility
Record the data version, method version, execution results, and validation status for each run. Review unexpected changes before accepting regenerated outputs. Do not present synthetic descriptive findings as real-world measurements.
