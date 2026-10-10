# Weak-Case and Limitation Review

## Dataset and method versions
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`

## Recorded weak cases

| Case | Finding | Interpretation |
|---|---|---|
| Synthetic provenance | Every input record is synthetic. | No real-world ranking claim is justified. |
| Limited temporal coverage | Three timestamps on one calendar date are represented in the current evidence. | Rankings may not represent other times or days. |
| Ranking sensitivity | Some NO2 and PM2.5 rankings change when a timestamp is omitted. | Treat rankings cautiously; the sample is small. |
| Baseline interpretation | The pollutant-wide mean is used as a descriptive baseline. | It is not a regulatory threshold. |

## Sensitivity evidence
The machine-readable record `data-science/outputs/weak_case_review.json` contains 12 leave-one-timestamp-out pollutant cases. Consult that file for each omitted timestamp and its recorded ranking-change flag.

## Claims that are not supported
- Real-world city air-quality rankings.
- Regulatory compliance or exceedance conclusions.
- Public-health or individual health-risk conclusions.
- Causal explanations.
- Predictive or forecasting claims.

## Required handling
Retain the sensitivity evidence with the exported results. Do not suppress ranking changes or describe the validation PASS as proof of real-world accuracy. Reassess the method if the canonical input schema, sampling design, or method version changes.
