# Phase 3 — Canonical Data Validation and Analytical Readiness

## Purpose

This workspace implements Post #2 validation, profiling, representativeness assessment, dataset-archetype confirmation, and analytical-readiness assessment.

## Source of Truth

All analytical scripts read the existing canonical dataset:

`data/canonical/intelligence_data.csv`

Do not create a separate cleaned, final, analysis, or model-specific dataset. The operational frontend and backend are outside this workspace's scope.

## Scripts

Run the following commands from the repository root:

```bash
python data-science/scripts/profile_canonical_data.py
python data-science/scripts/assess_data_quality.py
python data-science/scripts/assess_representativeness.py
python data-science/scripts/assess_analytical_readiness.py
```

Run the scripts in this order because the readiness assessment reads the preceding JSON outputs.

## Outputs

The `outputs/` directory contains:

* `canonical_profile.json`
* `quality_assessment.json`
* `representativeness_assessment.json`
* `analytical_readiness.json`

These files are generated evidence, not manually entered results. Regenerate them after relevant source or script changes.

## Notebook

`notebooks/01_canonical_data_validation_and_readiness.ipynb` brings together the profile, quality checks, coverage evidence, and readiness conclusion.

Open it in VS Code or Jupyter and run the cells from top to bottom. The Python kernel needs Pandas and NumPy.

## Dataset Characteristics

The current canonical package is designed for 96 records covering eight cities, four pollutant categories, and three retained timestamps per city–pollutant group. The data is synthetic, and the three timestamps fall on one calendar date.

## Analytical Guardrails

* Do not present synthetic observations as verified real-world measurements.
* Do not claim long-term trends or seasonal patterns from the current temporal coverage.
* Predictive Intelligence is not supported for the current phase.
* Review the five reports in `docs/` before selecting an analytical track.
* A structural quality PASS does not prove accuracy or real-world representativeness.

## Reproducibility

Run the four scripts from the repository root to regenerate the JSON outputs. Keep the scripts, outputs, notebook, and documentation consistent with the canonical data version.
