# Intelligence Output Contract

## Purpose

Define the standard machine-readable output contract for Track A — Comparative Intelligence while retaining Track A-specific descriptive statistics.

## Output files

- `data-science/outputs/intelligence_results.json`
- `data-science/outputs/intelligence_summary.json`
- `data-science/outputs/validation_metrics.json`
- `data-science/outputs/weak_case_review.json`

## Version identifiers

Every result record must identify:

- `data_version`: `phase3-v1.1`
- `method_version`: `track-a-comparative-v1.0.0`
- `generated_at`: ISO 8601 UTC timestamp

## Mandatory common result fields

Each result record must include:

- `result_id`: unique result identifier.
- `result_type`: `ranking`.
- `group_key`: stable city–pollutant–unit group identifier.
- `metric_name`: name of the reported metric.
- `result_value`: numeric sampled mean.
- `priority_rank`: deterministic within-pollutant rank.
- `finding`: short interpretation of the comparison.
- `evidence`: non-empty list of supporting values and factors.
- `quality_status`: `validated`, `conditional`, or `rejected`.
- `limitation`: user-facing limitation statement.
- `method_version`, `data_version`, and `generated_at`.

Conditional standard fields are represented where appropriate:

- `record_id`: `null`, because a grouped city–pollutant result does not represent one canonical record.
- `entity_id`: canonical city/entity identifier.
- `period_start` and `period_end`: earliest and latest observation timestamps in the group.
- `result_unit`: the canonical metric unit.
- `result_category`: `above_baseline`, `below_baseline`, or `at_baseline`.

## Track A-specific fields

The output retains:

- `entity_name`, `pollutant`, and `metric_unit`.
- `observation_count`.
- `mean_value`, `median_value`, `minimum_value`, and `maximum_value`.
- `pollutant_baseline_mean`.
- `difference_from_baseline` and `relative_difference`.
- `rank_within_pollutant`.
- `is_synthetic` and `interpretation`.

`result_value` must equal `mean_value`, and `priority_rank` must equal `rank_within_pollutant`.

The `evidence` array contains the observation count, group statistics, pollutant-wide baseline, baseline gap, relative difference, and synthetic-data indicator.

## Expected result count

The canonical input currently produces 32 city–pollutant groups. A change in this count must be investigated and validated rather than silently accepted.

## Quality interpretation

The `quality_status` is `conditional`: the numerical calculations and structural checks can pass, but the underlying observations are synthetic and have limited temporal coverage. This status does not represent validation of real-world air quality.

## Validation

The validator checks:

- Canonical input dimensions and data version.
- Synthetic provenance and canonical record-ID uniqueness.
- Expected group count and independent means/baseline gaps.
- Group sizes, ranking order, and deterministic ties.
- Presence and consistency of standard contract fields.
- Unique result IDs, non-empty evidence, valid quality status, and limitations.
- Summary consistency and timestamp-sensitivity evidence.

## Interpretation restrictions

All findings are synthetic descriptive comparisons. Do not present these outputs as real-world air-quality measurements, regulatory assessments, health-risk assessments, causal conclusions, or predictive results.
