# Grounded Assistant — Grounding Validation

## Purpose

This document defines the grounding checks for the Phase 3 grounded data assistant.

The assistant retrieves existing approved intelligence outputs and may use an optional LLM explanation layer to clarify those results. It must not recompute analytical-track methods or invent values, ranks, findings, predictions, or explanations that are not supported by retrieved evidence.

Deterministic retrieval and approved source records remain authoritative. The LLM may explain validated evidence but must not alter the underlying results.

## Approved Source

The primary runtime source is the configured `intelligence_results.json` output. The configured summary output may provide additional quality and limitation metadata.

The assistant must not use arbitrary filesystem paths supplied by a user, arbitrary SQL, unrestricted access to the canonical dataset, or unrestricted data retrieval through the LLM.

Only approved intelligence outputs and approved metadata may be used to construct answers.

## Evidence Package

Each grounded answer should preserve, when available:

- Result ID and result type.
- Entity ID and group key.
- Metric name, value, and unit.
- Priority rank and existing finding.
- Existing evidence field.
- Quality status and limitations.
- Data version and method version.
- Generated timestamp.
- Synthetic-data status, when explicitly available in the approved source.

Unavailable metadata must remain unavailable. The assistant must not fill gaps with guessed values or unsupported assumptions.

Only the minimum evidence required to answer the user's supported question should be passed to the LLM. The full canonical dataset must not be sent when a limited evidence package is sufficient.

## Validation Rules

1. A non-methodology answer must have at least one matching approved record.
2. Evidence records must have result IDs.
3. Data and method versions must be present.
4. One evidence package must not silently mix data versions or method versions.
5. Metric values must come from the source record.
6. A requested result ID must match an existing result ID exactly.
7. A city comparison must use matching records for the requested pollutant.
8. Missing or ambiguous results must not be replaced with invented answers.
9. Unsupported requests must be declined.
10. Quality status and limitations must not be overstated.
11. User input is treated as data, never as an instruction to bypass the allowlist, disclose secrets, or change assistant policy.
12. The response must not disclose filesystem paths, credentials, hidden configuration, or internal exception details.
13. The LLM must not create, recalculate, or modify findings, metric values, rankings, result IDs, or evidence.
14. Any factual claim in an LLM-generated explanation must be supported by the retrieved evidence or approved metadata.
15. Unsupported numbers, unsupported claims, and claims that contradict source records must be rejected.
16. If the LLM returns an empty, invalid, unsupported, or unavailable explanation, the assistant must fall back to a deterministic response whenever the validated evidence permits one.
17. LLM failure must not invalidate an otherwise valid deterministic retrieval result.
18. Synthetic-data status must be stated when that status is explicitly available in the approved source. If the status is missing, the assistant must not guess whether the data is synthetic or real.

## Grounding and Explanation Validation

The validator checks record structure, provenance, and version consistency. These checks alone do not prove that every arbitrary natural-language sentence is entailed by the evidence.

For Mode B, grounding validation therefore has two distinct responsibilities:

### 1. Deterministic evidence validation

- Confirm that records originate from approved intelligence outputs.
- Validate required identifiers, versions, and relevant metadata.
- Confirm that query parameters match the requested intent.
- Preserve source metric values, existing findings, rankings, and limitations.
- Reject missing, ambiguous, inconsistent, or unsupported evidence.

### 2. LLM explanation validation

- Provide only the relevant validated evidence to the LLM.
- Permit explanation and summarization of existing evidence only.
- Check generated text for unsupported numbers, findings, rankings, and claims.
- Ensure that the explanation does not contradict source records or omit material limitations in a misleading way.
- Do not treat a successful provider response as proof of grounding.
- Use controlled templates or a deterministic fallback if the explanation cannot be validated reliably.

The LLM is an explanation layer, not an analytical engine or source of truth.

## Current Limitations

- The assistant uses deterministic retrieval and may use an LLM only for bounded explanations.
- It is not a predictive model.
- It does not provide health or regulatory advice.
- It does not establish causation.
- Synthetic data must be identified as synthetic when that metadata is available in the approved source.
- Missing synthetic-data metadata must not be replaced by an unsupported claim.
- API authentication and authorization must follow the existing application's access-control requirements. This router does not independently implement an identity system.
- Natural-language explanation does not increase the reliability or evidentiary strength of the underlying dataset.
- Validation cannot guarantee complete semantic entailment for unrestricted prose; therefore, LLM output must remain constrained and subject to evidence checks.

## Error Handling and Logging

- Return bounded validation errors for malformed, unsupported, missing-parameter, and unavailable-data cases.
- Do not expose stack traces, secrets, raw provider exceptions, or internal configuration to clients.
- Do not log full conversation text or complete generated explanations by default.
- Record only minimal operational information needed for debugging and monitoring.
- If the LLM fails, retain the deterministic result when possible and indicate that an explanation could not be generated, without exposing internal error details.

## Authentication and Authorization

The assistant must reuse existing application authentication and authorization.

- Do not create a public bypass route.
- Apply the existing access controls to assistant queries and supporting intelligence data.
- Confirm the deployed route's access-control behavior before enabling the assistant.
- Do not expose protected data, credentials, or internal prompts to users or the LLM.

## Release Gate

Do not mark the assistant ready for acceptance until:

- Unit tests pass.
- API tests pass.
- Unsupported and unsafe requests are rejected.
- Existing Operational View tests still pass.
- Existing Data Intelligence endpoints still pass.
- The frontend integration is tested separately.
- Source versions, limitations, and synthetic-data status are confirmed against the actual generated outputs.
- Evidence validation tests cover missing IDs, missing versions, inconsistent versions, invalid metric provenance, and ambiguous results.
- LLM tests cover supported explanations, unsupported numerical claims, contradictory claims, invalid or empty output, and provider failure.
- Deterministic fallback behavior is verified when the LLM is unavailable or its explanation fails validation.
- Authentication, authorization, and logging behavior are verified in the target deployment.

## Approval Decision

**Grounded Assistant — Mode B: Deterministic Retrieval + LLM Explanation**

The architecture is suitable for bounded, evidence-grounded assistance when the release gates above are satisfied. Approval does not replace implementation testing or deployment verification. Deterministic source records remain authoritative, and unsupported claims must be rejected rather than inferred.
