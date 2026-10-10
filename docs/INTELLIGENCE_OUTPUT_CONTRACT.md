# Intelligence Output Contract

## Purpose
Define the expected machine-readable outputs for Track A — Comparative Intelligence.

## Output files
- `data-science/outputs/intelligence_results.json`
- `data-science/outputs/intelligence_summary.json`
- `data-science/outputs/validation_metrics.json`
- `data-science/outputs/weak_case_review.json`

## Version identifiers
Each analytical output must identify:
- `data_version`: `phase3-v1.1`
- `method_version`: `track-a-comparative-v1.0.0`

## Result records
The results file contains one descriptive city/entity-pollutant group per result record. For the current canonical input, the expected number of groups is 32. Records describe sampled observations, not verified ambient measurements.

Group statistics include the sampled record count, mean, median, minimum, and maximum. Comparative fields include the pollutant-wide mean baseline, the difference from that baseline, relative difference where defined, and deterministic ranking information.

## Summary
The summary identifies the project and track, analytical question, decision scope, versions, result count, key descriptive findings, validation result, and limitations.

## Validation
Validation metrics must record the tested input dimensions, expected and actual group counts, independent numerical comparison errors, check outcomes, failed checks, issues, and timestamp-sensitivity case count.

## Weak-case review
The weak-case output must preserve synthetic provenance, temporal-coverage limitations, baseline interpretation limitations, and timestamp-sensitivity results.

## Interpretation
All findings must be explicitly described as synthetic descriptive comparisons. Do not present the outputs as real-world air-quality measurements, regulatory assessments, health-risk assessments, causal conclusions, or predictive results.
