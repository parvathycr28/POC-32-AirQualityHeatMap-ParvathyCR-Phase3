# Analytical Method Report — Track A Comparative Intelligence

## Project
- Project ID: POC-32
- Project: Infocreon Aether Pulse Air Quality Heatmap
- Track: Track A — Comparative Intelligence
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`

## Analytical question
Within each pollutant, how do sampled city measurements compare with each other and with that pollutant's overall mean?

## Input
The analysis uses the canonical dataset at `data/canonical/intelligence_data.csv`. The current validated input contains 96 records and 20 columns. All observations are synthetic.

## Method
1. Validate required fields, record identifiers, data version, synthetic provenance, timestamps, metric values, and pollutant-unit compatibility.
2. Group records by city/entity and pollutant.
3. Calculate the record count, mean, median, minimum, and maximum for each group.
4. Calculate the pollutant-wide mean as a descriptive baseline.
5. Calculate each city-pollutant group's difference from the pollutant-wide mean and its relative difference where defined.
6. Rank city-pollutant groups by descending sampled mean, using a deterministic entity identifier tie-break.
7. Export machine-readable results and a summary with the data and method versions.

## Validation
The validation run reports `PASS`, with no failed checks or issues. It independently compares group means and baseline gaps, checks group sizes and result counts, verifies ranking order and tie handling, and checks version consistency.

The validation reports 96 input rows, 20 input columns, and 32 result groups. Maximum absolute mean error and baseline-gap error are both zero for the tested comparisons.

## Weak-case and sensitivity review
The leave-one-timestamp-out review records 12 pollutant/timestamp cases. Some NO2 and PM2.5 rankings change when a timestamp is omitted. This indicates sensitivity to the small sample and must be considered when interpreting rankings.

## Interpretation limits
- All records are synthetic.
- The dataset covers only three timestamps on one calendar date in the current evidence.
- Rankings describe only the supplied sample.
- The pollutant-wide mean is not a regulatory threshold.
- Results do not establish real-world air quality, health risk, causation, or predictive performance.
- The analysis does not support operational or public-health decisions.

## Reproducibility
Run the analysis and validation scripts from the repository root as described in `data-science/README.md`. Generated results must retain their data and method version identifiers.

## Status
The current implementation validation reports `PASS`. This is a technical validation result, not independent formal approval of the analytical track.
