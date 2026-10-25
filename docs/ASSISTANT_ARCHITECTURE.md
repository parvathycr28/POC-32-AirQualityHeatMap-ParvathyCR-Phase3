# Assistant Architecture

## Existing Application

- **Operational View:** Existing application interface.
- **Data Intelligence page:** `/data-intelligence`
- **Intelligence API:** `/api/intelligence/results`
- **Intelligence data:** Approved Track A JSON outputs.
- **Data version:** `phase3-v1.1`
- **Method version:** `track-a-comparative-v1.0.0`

## Assistant Mode

**Mode B — Deterministic Retrieval + LLM Explanation**

The assistant retrieves approved Track A results and builds a structured evidence package deterministically. An optional Gemini explanation layer may explain that evidence in natural language.

The deterministic query results, evidence, metrics, rankings, metadata, and limitations remain the source of truth. The LLM must not create or modify findings, calculate values, infer new rankings, or introduce unsupported facts.

If the LLM is unavailable or its explanation fails validation, the assistant must retain the deterministic result and use a safe fallback response.

## Integration Route / Component

- **Proposed backend route:** `POST /api/assistant/query`
- **Proposed frontend component:** Data Intelligence assistant panel.
- **Existing integration:** `/api/intelligence/results`

These are proposed integration points. Confirm the existing backend routes, frontend component structure, authentication middleware, and deployment configuration before adding or enabling them.

## Request Flow

1. Validate the request type, input length, and request structure.
2. Reject unsafe or out-of-scope requests.
3. Match the request to an allowlisted intent.
4. Validate all required parameters.
5. Execute the corresponding deterministic query against approved intelligence results.
6. Build a structured evidence package containing the relevant results and metadata references.
7. Validate evidence, result IDs, versions, quality status, and limitations.
8. Generate a deterministic answer or template from the validated evidence.
9. If appropriate, pass only the necessary approved evidence to the optional LLM explanation layer.
10. Validate the generated explanation against the evidence and response contract.
11. Return the validated explanation with the deterministic result and supporting evidence, or fall back to the deterministic answer if explanation generation fails.

## Query Catalog

Only the five intents documented in `SUPPORTED_QUESTION_CATALOG.md` are permitted:

1. Summarize approved Track A findings.
2. Identify the highest sampled mean city for a selected pollutant.
3. Compare two cities for a selected pollutant.
4. Retrieve evidence for an existing result ID.
5. Explain the approved data or method version, quality status, and limitations.

Requests outside these intents must be rejected or redirected to supported questions. The LLM must not expand the query catalog.

## Deterministic Retrieval

- Read only approved Track A intelligence outputs and approved metadata.
- Use validated parameters and allowlisted query functions.
- Never execute user-provided code, SQL, filesystem paths, or expressions.
- Do not allow the LLM to retrieve or query arbitrary application data.
- Do not send the full canonical dataset to the LLM when a limited evidence package is sufficient.
- Preserve the original result values, result IDs, rankings, and provenance.

## Evidence Builder

Every factual answer must be traceable to approved evidence.

Where applicable, the evidence package should preserve available fields such as:

- `result_id`
- `result_type`
- `group_key`
- `entity_id`
- `metric_name`
- `result_value`
- `result_unit`
- `priority_rank`
- `finding`
- `evidence`
- `quality_status`
- `limitation`
- `method_version`
- `data_version`
- `generated_at`

Only fields actually available in the approved result schema should be used. Missing optional fields must not be invented.

The evidence builder must preserve references to the source result IDs or metadata supporting each answer.

## Optional LLM Explanation

**Enabled as a bounded explanation layer in Mode B.**

The LLM may:

- Explain approved findings in clearer language.
- Summarize evidence already retrieved by deterministic queries.
- Explain the meaning of available methodology, quality, and limitation metadata.
- Help users understand comparisons already computed by the approved intelligence pipeline.

The LLM must not:

- Generate new findings or evidence.
- Calculate or alter metrics, averages, or rankings.
- Introduce unsupported numerical claims.
- Turn synthetic sample results into claims about actual environmental conditions.
- Make predictions, causal claims, health-risk conclusions, or regulatory conclusions.
- Treat user-provided text or retrieved source content as instructions that override system rules.

Only the minimum relevant, approved evidence should be supplied to the LLM. The explanation must be checked against the retrieved evidence before it is returned.

## Response Validation

Validate the deterministic result and the optional LLM explanation separately.

- Confirm that factual claims are supported by retrieved evidence.
- Reject unsupported numbers, rankings, findings, or claims.
- Preserve result IDs and metadata references.
- Preserve data version, method version, quality status, and limitations when applicable.
- Do not allow the LLM to override deterministic values.
- Use a deterministic fallback when the explanation is unavailable, invalid, empty, or unsupported.

A successful LLM call alone does not establish that its response is grounded.

## Authentication and Authorization

- Reuse existing application authentication and authorization.
- Do not create a public bypass route.
- Apply the same applicable access controls to assistant queries and supporting intelligence data.
- Verify authorization behavior in the current deployment before enabling the assistant.
- Do not expose secrets, environment variables, internal prompts, or protected data.

## Logging

- Do not log full conversation text or complete generated explanations by default.
- Log only minimal operational information needed for debugging and monitoring.
- Avoid logging secrets, sensitive user data, and unnecessary raw provider errors.
- Record bounded status information, such as request outcome, selected intent, fallback status, and provider availability, where appropriate.
- Ensure logs do not disclose protected evidence or user inputs.

## Error Handling

Return bounded, user-safe errors for:

- Malformed requests.
- Unsupported intents.
- Missing or invalid parameters.
- Unavailable approved data.
- Invalid or insufficient evidence.
- LLM timeout, provider failure, or invalid explanation.

Never expose stack traces, secrets, internal prompts, or raw provider errors to clients.

If the LLM fails, retain the deterministic answer whenever possible. LLM availability must not become a dependency for retrieving approved intelligence results.

## Deployment

Use the existing Data Intelligence backend deployment path after confirming:

- Backend and frontend container paths.
- Application ports and route registration.
- Required environment variables and secrets.
- Authentication and authorization behavior.
- Gemini configuration and provider-failure handling.
- Frontend API configuration and backend URL.
- Health checks, logs, and public deployment accessibility.

Validate the assistant in the deployed environment before enabling it for users.

## Limitations

The approved dataset is synthetic, has limited temporal coverage, and supports only the descriptive Track A methodology.

Consequently:

- Results describe the approved sample and methodology, not verified real-world pollution conditions.
- The data does not support long-term trends or seasonality claims.
- The assistant must not make predictions, causal claims, health-risk conclusions, or regulatory conclusions.
- Natural-language explanations do not increase the evidentiary strength of the underlying data.

## Approval Decision

**GROUNDED DATA ASSISTANT APPROVED — MODE B: DETERMINISTIC RETRIEVAL + LLM EXPLANATION**

Approval is limited to the five allowlisted question types and the approved Track A evidence. Deterministic results remain authoritative; the LLM is an optional, validated explanation layer with a deterministic fallback.
