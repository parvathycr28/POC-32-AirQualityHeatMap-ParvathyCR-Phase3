# Analytical Validation Report — Track A

## Scope
This report records the current validation evidence for Track A — Comparative Intelligence.

## Versions
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`

## Validation results
Source: `data-science/outputs/validation_metrics.json`

- Validation result: `PASS`
- Input rows: 96
- Input columns: 20
- Expected result groups: 32
- Actual result groups: 32
- Maximum absolute mean error: 0.0
- Maximum absolute baseline-gap error: 0.0
- Group-size errors: none
- Ranking errors: none
- Failed checks: none
- Issues: none
- Timestamp-sensitivity cases: 12

## Checks performed
The validation script checks canonical row and column counts, data version, synthetic provenance, unique record identifiers, result-group count, independently recomputed means and baseline gaps, group sizes, result and method version consistency, summary count, Track A designation, and ranking order/tie handling.

## Weak-case review
Source: `data-science/outputs/weak_case_review.json`

The sensitivity review records ranking changes in some NO2 and PM2.5 cases when individual timestamps are omitted. These cases are warnings about sample sensitivity, not model-validation scores.

## Limitations
The input is synthetic and has limited temporal coverage. A passing implementation check does not establish external validity, real-world accuracy, regulatory compliance, health risk, or predictive capability.

## Conclusion
The current scripted validation result is `PASS` for the checks implemented and recorded in the validation output. Formal analytical-track approval remains a separate review decision.
