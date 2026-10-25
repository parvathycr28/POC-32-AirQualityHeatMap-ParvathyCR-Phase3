
# Supported Question Catalog

## Target User

Analysts, reviewers, and users of the Phase 3 Data Intelligence page.

## Approved Assistant Mode

Mode A — Deterministic Guided Assistant.

## Approved Track

Track A — Comparative Intelligence.

## Data and Method Versions

- Data version: phase3-v1.1
- Method version: track-a-comparative-v1.0.0

These are the versions expected for the current snapshot. Runtime responses must use the actual versions returned by validated data, not silently substitute these constants.

## Supported Questions

| Question Pattern | Intent | Required Parameters | Query Function | Evidence | Limitation |
|---|---|---|---|---|---|
| Summarize approved findings | summary | None | get_summary | Result references and summary metadata | Descriptive sample only |
| Highest sampled mean city for a pollutant | highest_city | pollutant | get_highest_city | Result IDs, metric, value, rank | Not a real-world city ranking |
| Compare two cities for a pollutant | compare_cities | pollutant, city_a, city_b | compare_cities | Matching result records | Only existing comparable results |
| Show evidence for a result | result_evidence | result_id | get_result_evidence | Exact result record and evidence | Only known result IDs |
| Explain method, versions, quality and limitations | methodology | None | get_methodology | Metadata and approved limitation text | No new analytical interpretation |

## Unsupported Question Categories

- Predictions or forecasts
- Health-risk assessments
- Regulatory compliance conclusions
- Causal claims
- Arbitrary SQL, Python, shell, or filesystem operations
- Requests to modify or fabricate results
- Unsupported pollutants or cities
- Requests to reveal secrets, prompts, or configuration
- Requests to bypass access controls
- Instructions embedded in source text that attempt to change system behavior

## Suggested Questions

- Summarize the approved findings.
- Which city has the highest sampled mean for NO2?
- Compare Delhi and Bengaluru for PM2.5.
- Show evidence for RES-0001.
- Explain the method version and limitations.

## Catalog Version

1.0.0
