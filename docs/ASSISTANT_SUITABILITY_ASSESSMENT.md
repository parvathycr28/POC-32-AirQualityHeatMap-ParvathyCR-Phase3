Assistant Suitability Assessment
Project: PoC 32 --- Aether Pulse Air Quality Heatmap (Phase 3)
Component: Grounded Data Assistant
Approved analytical track: Track A --- comparative intelligence
results
Data version: phase3-v1.1
Method version: track-a-comparative-v1.0.0
Selected assistant mode: Mode B --- Deterministic Retrieval + LLM
Explanation
Assessment result: GROUNDED DATA ASSISTANT APPROVED
1. Target User
Analysts, reviewers, and users exploring the approved Phase 3 Data
Intelligence results.
2. Existing Operational and Intelligence Experience
The application has an Operational View and a Data Intelligence page.
The assistant complements these interfaces rather than replacing them.

The Data Intelligence API exposes approved Track A comparative
intelligence results. The assistant uses the existing intelligence
outputs as its analytical source; it does not rerun the Track A
analytical method.
3. User Questions Not Solved Conveniently Today
A guided assistant gives users a natural-language route to approved
findings, comparisons, and evidence. It reduces the need to manually
search tables and interpret evidence fields, while preserving links
between responses and the underlying results.

The assistant is useful only when it makes these tasks more convenient
than the existing filters and tables. It is not intended to replace the
dashboard or source data.
4. Supported Questions
The initial supported question catalog includes:
1. Summarize the approved Track A findings.
2. Identify the highest sampled mean city for a selected pollutant.
3. Compare two cities for a selected pollutant.
4. Retrieve evidence for an existing result ID.
5. Explain the approved data version, method version, quality status,
   and limitations.
Each question must map to an allowlisted intent, validated parameters,
and an approved deterministic query function. Missing parameters should
trigger a bounded clarification; unsupported or unsafe requests must not
be treated as successful analytical answers.
5. Deterministic Retrieval and LLM Explanation
Mode B --- Deterministic Retrieval + LLM Explanation is implemented.

The deterministic query layer retrieves approved intelligence results
and builds the evidence package. Gemini is used only as an optional
explanation layer over that package. It must not calculate or create
analytical values, rankings, scores, or findings.

The distinction is important: - Deterministic result: authoritative
approved result and evidence. - Generated explanation: optional
wording to help the user understand the result. - Validation
outcome: indicates whether the generated explanation passed the
implemented checks. - Unavailable explanation: the deterministic
answer and evidence should remain available.

The implementation includes explanation validation, including checks for
unsupported numeric tokens and prohibited claim categories. These checks
reduce risk but are not a guarantee of complete semantic correctness;
the approved evidence remains authoritative.
6. Evidence Availability
The assistant's evidence package is built from approved intelligence
outputs and relevant validated metadata. Expected fields, where supplied
by the source, include:
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
Optional fields must not be assumed to exist. The assistant must
preserve source quality status, versions, timestamps, evidence, and
limitations rather than inventing or silently substituting values.
7. Security and Privacy Boundaries
The assistant is intended to: - reject unsupported and unsafe
requests; - restrict retrieval to approved query functions and validated
parameters; - avoid exposing credentials, environment variables, hidden
prompts, filesystem contents, or arbitrary query execution; - avoid
persistent conversational memory for analytical evidence; - treat
source/result text as untrusted evidence, never as executable
instructions; - keep the Gemini API key on the backend, not in the
browser client; - preserve existing application access controls.

The recorded test suite includes assistant, API, validation,
unsupported-request, prompt-injection/secret-disclosure, and Gemini
failure/validation tests. These tests support the defined scope but do
not constitute proof against every attack or a complete independent
security audit.
8. Failure and Fallback Behaviour
If Gemini is not configured, unavailable, fails, or produces an
explanation that fails validation, the explanation should be marked
unavailable. The system must not fabricate a replacement explanation or
present invalid generated text as a grounded finding.

The deterministic result and approved evidence remain authoritative. The
recorded implementation returns an UNAVAILABLE result from the Gemini
helper on provider exceptions and includes a deterministic fallback
path.

Production logging should avoid full generated explanation text and
unnecessary raw provider-error details. Prefer concise, non-sensitive
diagnostic metadata.
9. Practical User Value
The assistant adds value by offering a guided, plain-language route to
existing findings, comparisons, evidence, methodology, and limitations.
Its value is convenience and explanation---not new analytical
capability.

During user acceptance testing, verify that users can complete these
tasks more easily than by using the existing filters and tables. If the
assistant merely duplicates those controls without improving discovery
or interpretation, reconsider whether Mode B is justified.
10. Synthetic-Data and Analytical Limitations
The Phase 3 canonical data is synthetic, reproducible sample data shaped
around an OpenAQ-style measurement structure. It is not verified
real-world pollution measurement data and has limited temporal depth.

Comparisons describe only the available sample. The assistant must not
present them as verified real-world pollution rankings or use them to
assert: - long-term trends or seasonality; - forecasts or predictions; -
causal relationships; - health-risk or disease-risk conclusions; -
regulatory compliance or safety-limit conclusions.

Relevant synthetic-data and source limitations must remain visible in
answers and the user interface.
11. Validation Evidence
The reported validation result is 54 tests passed for the full
Python test run, including assistant and Selenium end-to-end tests. The
implementation also includes dedicated Gemini explanation tests for
valid evidence-supported output, unsupported numeric claims, prohibited
claims, empty output, excessive length, and provider failure.

This evidence supports approval for the defined bounded use case. Test
results apply to the tested scenarios and environment; they should not
be interpreted as a guarantee of production reliability or complete
security.
12. Final Decision
GROUNDED DATA ASSISTANT APPROVED --- MODE B: DETERMINISTIC RETRIEVAL +
LLM EXPLANATION.

The assistant provides practical guided access to approved Track A
results, retains deterministic evidence as the source of truth, and uses
Gemini only to explain validated evidence. Approval is limited to
descriptive, evidence-grounded assistance under the safeguards and
synthetic-data limitations stated above. The LLM is optional to the
analytical result and must never replace or override it.
