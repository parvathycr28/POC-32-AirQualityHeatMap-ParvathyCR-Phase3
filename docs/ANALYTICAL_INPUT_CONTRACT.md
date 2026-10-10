# Analytical Input Contract — Track A

## 1. Purpose
Define the input expectations for Track A — Comparative Intelligence.

## 2. Authoritative Input
- Path: `data/canonical/intelligence_data.csv`
- Data version: `phase3-v1.1`
- Expected shape: 96 rows and 20 columns
- Dataset status: synthetic

The canonical CSV is the sole analytical input for this track.

## 3. Structural Expectations
- Required analytical fields include record ID, entity ID, entity name, pollutant/subcategory, metric name, metric value, metric unit, timestamp, and data version.
- Record IDs must be unique.
- The dataset must contain eight city entities and four pollutant categories.
- Each city-pollutant group is expected to contain three timestamped observations.
- Metric values must be numeric, finite, and non-negative for this implementation.
- Timestamps must be parseable as UTC timestamps.
- Metric names and pollutant/subcategory values must agree as required by the Track A implementation.
- Units must be compatible within each pollutant group.

## 4. Versioning
- Expected data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`

A version mismatch must be reviewed rather than silently accepted.

## 5. Prohibited Input Handling
- Do not silently substitute another dataset.
- Do not create a second cleaned analytical dataset.
- Do not relabel synthetic records as real-world measurements.
- Do not change the canonical input as part of Track A execution.

## 6. Validation and Failure Handling
Run `data-science/scripts/validate_analytical_track.py` after executing the analysis. Review all failed checks and issues before using the generated outputs. A successful JSON parse alone does not establish analytical correctness.

## 7. Scope Limitation
This contract describes the current Track A implementation. Any change to the canonical schema, data version, grouping, metric definitions, or validation assumptions requires a documented review.
