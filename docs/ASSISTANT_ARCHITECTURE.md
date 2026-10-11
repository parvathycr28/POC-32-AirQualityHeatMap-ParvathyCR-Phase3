
# Assistant Architecture

## Existing Application

- Operational View: existing application interface
- Data Intelligence page: /data-intelligence
- Intelligence API: /api/intelligence/results
- Intelligence data: approved Track A JSON outputs

## Assistant Mode

Mode A — Deterministic Guided Assistant. No LLM is used.

## Integration Route / Component

Proposed backend route: POST /api/assistant/query

Proposed frontend component: Data Intelligence assistant panel.

These are new integration points and must be checked against existing routes before implementation.

## Request Flow

1. Validate request type and input length.
2. Reject unsafe or out-of-scope requests.
3. Match an allowlisted intent.
4. Validate all required parameters.
5. Execute the corresponding deterministic query.
6. Build a structured evidence package.
7. Validate evidence, versions, quality, and limitations.
8. Return a templated response.

## Query Catalog

Only the five intents in SUPPORTED_QUESTION_CATALOG.md are permitted.

## Deterministic Retrieval

Read only the approved intelligence results and approved metadata. Never execute user-provided code, SQL, paths, or expressions.

## Evidence Builder

Every factual answer must include the result IDs or metadata references supporting it.

## Optional LLM Explanation

Not enabled. Reassess only if templates are demonstrably insufficient.

## Response Validation

Check that each answer is derived from retrieved evidence and that version and limitation metadata are present.

## Authentication and Authorization

Reuse existing application authorization. Do not create a public bypass route. Verify behavior in the current deployment before enabling the assistant.

## Logging

Do not log full conversation text by default. Log only minimal operational information needed for debugging, without secrets or sensitive user data.

## Error Handling

Return bounded validation errors for malformed, unsupported, missing-parameter, and unavailable-data cases. Never expose stack traces or secrets to clients.

## Deployment

Use the existing Data Intelligence backend deployment path after confirming container paths, ports, and environment variables.

## Limitations

Synthetic data, limited temporal coverage, and descriptive Track A methodology limit interpretation. No prediction, causal analysis, health-risk conclusion, or regulatory conclusion is supported.
