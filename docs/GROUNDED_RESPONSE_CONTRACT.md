
# Grounded Response Contract

Every successful response must contain:

- status: success
- intent: allowlisted intent
- answer: deterministic text based on retrieved evidence
- evidence: references to the source results
- data_version: validated runtime data version
- method_version: validated runtime method version
- quality_status: actual status from the approved source
- limitation: relevant source limitation
- generated_at: source generation timestamp where available

A response must not invent values, ranks, records, versions, validation results, or timestamps.

Numeric values must be copied from approved records without recalculation. If two records cannot be safely compared, return a bounded error instead.

If evidence is missing, inconsistent, or stale according to the project's defined validation rules, do not produce an unsupported analytical answer.

Unsupported requests return status "unsupported" with a brief explanation and supported question suggestions.

No persistent conversational memory is required.
