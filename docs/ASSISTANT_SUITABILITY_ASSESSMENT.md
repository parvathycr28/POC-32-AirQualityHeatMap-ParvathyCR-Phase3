
# Assistant Suitability Assessment

## Target User

Analysts, reviewers, and users exploring the approved Phase 3 Data Intelligence results.

## Existing Operational and Intelligence Experience

The application has an Operational View and a Data Intelligence page. The assistant must complement these interfaces rather than replace them.

The existing Data Intelligence API exposes approved Track A comparative intelligence results.

## User Questions Not Solved Conveniently Today

A guided assistant can help users find existing findings, compare supported entities, inspect evidence, and understand methodology without manually searching tables.

## Proposed Supported Questions

1. Summarize the approved Track A findings.
2. Identify the highest sampled mean city for a selected pollutant.
3. Compare two cities for a selected pollutant.
4. Retrieve evidence for an existing result ID.
5. Explain the approved data version, method version, quality status, and limitations.

## Deterministic Retrieval Mapping

Every supported question maps to an allowlisted intent and a deterministic query function.

The query layer reads the approved intelligence results. It does not rerun the analytical method or invent new scores.

## Evidence Availability

Expected fields include:

- result_id
- result_type
- group_key
- entity_id
- metric_name
- result_value
- result_unit
- priority_rank
- finding
- evidence
- quality_status
- limitation
- method_version
- data_version
- generated_at

Optional fields must not be assumed to exist.

## Security and Privacy

- Reject unsupported requests.
- Restrict access to approved query functions.
- Do not expose environment variables, secrets, filesystem access, or arbitrary queries.
- Do not store conversational history persistently.
- Preserve existing authentication and authorization.
- Treat result text as untrusted evidence, never as executable instructions.

## Deployment Feasibility

The existing Data Intelligence backend is the proposed integration point. The final route and deployment configuration must be confirmed against the current repository before integration.

## Value Beyond Filters and Tables

The assistant provides a guided route to approved findings, comparisons, and evidence. If user testing shows that it merely duplicates existing filters, the suitability decision must be reconsidered.

## Deterministic Versus LLM Decision

Mode A — Deterministic Guided Assistant.

A fixed intent catalog and response templates are sufficient for the initial scope. No LLM is required.

## Limitations

The analytical results use synthetic data. Comparisons describe the available sample only and must not be interpreted as verified real-world pollution rankings, health-risk assessments, regulatory compliance conclusions, or predictions.

## Result

DETERMINISTIC ASSISTANT SUITABLE — LLM NOT REQUIRED

This is an initial design assessment, not final integration approval. Final approval depends on repository integration, security review, and the required test results.
