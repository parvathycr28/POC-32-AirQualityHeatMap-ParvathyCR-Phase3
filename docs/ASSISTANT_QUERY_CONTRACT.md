
# Assistant Query Contract

## Supported Intents

- summary
- highest_city
- compare_cities
- result_evidence
- methodology

## Allowed Parameters

- pollutant: string, matched against available result group keys
- city_a: string, matched against available result entities
- city_b: string, matched against available result entities
- result_id: string, exact known result ID

## Parameter Types and Limits

- Request text: maximum 500 characters
- Pollutant: must match an available approved result
- City: must match an available approved entity
- Result ID: must match exactly one approved result
- Comparison: both cities must have comparable results for the same pollutant and metric

## Query Functions

- get_summary()
- get_highest_city(pollutant)
- compare_cities(pollutant, city_a, city_b)
- get_result_evidence(result_id)
- get_methodology()

## Approved Sources

- data-science/outputs/intelligence_results.json
- data-science/outputs/intelligence_summary.json
- data-science/outputs/validation_metrics.json, where needed for validated metadata

The runtime must verify that files exist, parse correctly, and contain consistent versions.

## Evidence Fields

Return available result_id, result_type, group_key, entity_id, metric_name, result_value, result_unit, priority_rank, finding, evidence, quality_status, limitation, method_version, data_version, and generated_at fields.

## Result Limits

- Summary: maximum 10 result references
- Comparison: maximum 2 matched results
- Evidence lookup: exactly 1 result
- Highest city: exactly 1 selected result, with tied results handled explicitly if present

## Error Responses

- invalid_request
- unsupported_question
- missing_parameter
- invalid_parameter
- evidence_not_found
- data_unavailable
- version_mismatch

## Out-of-Scope Handling

Unsupported questions must receive a clear refusal and suggestions for supported questions.

## Unsafe Handling

Requests to reveal secrets, bypass controls, execute arbitrary code, or override safety rules must be rejected.

## Version Behaviour

Use versions from validated runtime data. If required versions conflict, block analytical answers and report a version mismatch. Never silently replace missing runtime metadata with hardcoded values.
