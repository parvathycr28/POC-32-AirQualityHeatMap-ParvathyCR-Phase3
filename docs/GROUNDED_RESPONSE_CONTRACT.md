# Grounded Response Contract

## 1. Purpose

The Grounded Response Contract defines the structure, validation requirements, and grounding rules for responses produced by the Aether Pulse Grounded Data Assistant.

The assistant operates in **Mode B — Deterministic Retrieval + LLM Explanation**.

Deterministic retrieval is the authoritative source of analytical results. The LLM is used only to generate a natural-language explanation from validated evidence.

The LLM must not replace deterministic retrieval, independently establish analytical results, or expand the evidence beyond what the approved source supports.

---

## 2. Successful Response Contract

Every successful response must contain:

- `status`: `"ok"`
- `intent`: allowlisted intent
- `answer`: grounded response text based on retrieved evidence
- `evidence`: references to the source results
- `data_version`: validated runtime data version
- `method_version`: validated runtime method version
- `quality_status`: actual status from the approved source
- `limitation`: relevant source limitation
- `generated_at`: source generation timestamp where available

The response must preserve the original deterministic result and its supporting evidence.

### Mode B Explanation Metadata

Mode B means deterministic retrieval and answer construction are authoritative, with an optional LLM explanation layer. Gemini is not required to succeed for every question.

The response-level `grounding` object reports the execution status for each question:

- `mode`: configured assistant mode, currently `deterministic_plus_llm_explanation`.
- `gemini_attempted`: `true` when a request was made to the Gemini provider; `false` when Gemini was not attempted, such as when the API key is missing or the evidence is insufficient.
- `llm_used`: `true` only when the explanation provider returns an `AVAILABLE` result.
- `explanation_validated`: `true` only when an available explanation passes the implemented validation checks.
- `deterministic_fallback_used`: `true` when the generated explanation is unavailable or fails validation and the deterministic answer is retained.
- `generated_findings`: remains `false`; the LLM must not create new analytical findings.
- `source`: identifies the approved deterministic source used for the response.

The health endpoint's `gemini_configured` field indicates whether a non-empty `GEMINI_API_KEY` is configured. It does not prove that a Gemini request succeeded, that a particular question used Gemini, or that an explanation passed validation.

An unavailable or invalid LLM explanation must not invalidate an otherwise valid deterministic answer. The response must retain its approved answer, evidence, data and method versions, quality status, and relevant limitations. The explanation and fallback status must accurately describe what happened for that particular question.

Passing the implemented explanation validator means only that its configured checks passed; it is not a guarantee that every natural-language claim is semantically entailed by the evidence.

---

## 3. Deterministic Retrieval Requirements

The deterministic retrieval system is responsible for:

1. Identifying an allowlisted intent.
2. Extracting supported parameters.
3. Retrieving approved source records.
4. Validating the retrieved evidence.
5. Constructing the evidence package.
6. Producing the authoritative analytical result.

The deterministic result must be established before the LLM explanation stage.

The LLM must not determine:

- Whether a record exists
- Which source records are authoritative
- The data version
- The method version
- The quality status
- The source generation timestamp
- Whether evidence is valid
- Whether two records are safely comparable

These values must originate from approved deterministic processing and validated source metadata.

---

## 4. Evidence Requirements

Every successful response must include references to the source results supporting its answer.

Evidence must be:

- Retrieved from approved sources
- Relevant to the requested intent
- Consistent with the validated evidence package
- Traceable to the underlying source records
- Associated with the applicable data and method versions

The assistant must not invent:

- Values
- Ranks
- Records
- Versions
- Validation results
- Timestamps
- Source references

If evidence is missing, inconsistent, or stale according to the project's defined validation rules, the assistant must not produce an unsupported analytical answer.

---

## 5. Numeric Grounding Rules

Numeric values must be copied from approved records without recalculation.

The LLM may include supported numeric values in its explanation, but it must preserve the exact values supplied by the evidence package.

The LLM must not independently calculate:

- Differences
- Ratios
- Percentages
- Averages
- Rankings
- Derived scores
- New measurements

If two records cannot be safely compared, the assistant must return a bounded error rather than an unsupported comparison.

A generated explanation containing unsupported numerical claims must fail grounding validation.

---

## 6. LLM Explanation Requirements

Gemini receives the validated evidence package as its grounding context.

The generated explanation must:

- Answer the supported user question
- Use only information contained in the evidence package
- Preserve source values and supported ranks
- Respect the source quality status
- Respect data and method versions
- Respect source limitations
- Avoid unsupported conclusions
- Avoid unsupported causal claims
- Avoid unsupported predictions
- Avoid presenting synthetic data as verified real-world observations

The LLM must not modify the deterministic result.

The LLM must not generate a new evidence record or source reference.

The LLM must not omit a relevant limitation in a way that makes the result misleading.

---

## 7. Grounding Validation

Every generated explanation must be validated before being returned as an available grounded explanation.

Validation must establish that:

- The response follows the expected structure.
- The explanation is supported by the evidence package.
- Numeric values are supported by approved records.
- Unsupported numerical claims are rejected.
- The explanation respects the source limitations.
- The generated content does not introduce unsupported analytical findings.

A successful LLM API call does not automatically mean that the explanation is grounded.

Only an explanation that passes the applicable validation rules may be represented as validated.

The validation result must reflect the actual validation process. It must not be fabricated or inferred from HTTP success.

---

## 8. Explanation Availability and Failure Handling

The deterministic result remains authoritative when Gemini is unavailable.

An explanation may be unavailable because of:

- Missing Gemini API key
- Gemini API failure
- Empty or incomplete evidence
- Invalid generated output
- Grounding validation failure

When an explanation cannot be generated or validated:

1. Preserve the deterministic result when it is valid.
2. Preserve the evidence package.
3. Mark the explanation as unavailable.
4. Do not present invalid generated content as a grounded finding.
5. Do not fabricate a replacement explanation.

The assistant must distinguish between:

- A valid deterministic result
- An available generated explanation
- A validated generated explanation
- An unavailable explanation
- An unsupported request
- A bounded analytical error

The exact status values must follow the implemented API contract.

---

## 9. Unsupported Requests

Unsupported requests must return:

- `status`: `"unsupported"`
- A brief explanation of why the request is unsupported
- Supported question suggestions

The assistant must not generate an analytical answer for an intent that is not allowlisted.

The LLM must not be used to bypass the supported intent restrictions.

Unsupported requests must not be represented as successful grounded analytical responses.

---

## 10. Data Quality and Limitations

The response must preserve the actual `quality_status` from the approved source.

The assistant must not upgrade, downgrade, or invent source quality status.

The response must include the relevant source limitation.

If the evidence is synthetic, incomplete, stale, or otherwise restricted, the explanation must respect those limitations.

The assistant must not imply that synthetic data represents verified real-world observations.

If the project's validation rules determine that evidence is unsuitable for the requested analysis, the assistant must return a bounded error rather than an unsupported answer.

---

## 11. Version and Timestamp Integrity

The following fields must originate from validated runtime metadata:

- `data_version`
- `method_version`
- `generated_at`

The assistant must not:

- Invent a version
- Substitute a model version for a data version
- Substitute a model version for a method version
- Generate a source timestamp from the current system time
- Claim that a timestamp represents source generation when it does not

If a source generation timestamp is unavailable, the response must follow the contract's defined optional timestamp behavior.

---

## 12. No Persistent Conversational Memory

No persistent conversational memory is required.

Each request must be processed using:

- The current user question
- The allowlisted intent definitions
- Approved retrieval logic
- The current validated evidence package
- The applicable response contract

The assistant must not depend on previous conversations to establish analytical evidence.

---

## 13. Contract Principle

**Deterministic retrieval establishes what the system knows. The LLM explains what the validated evidence supports.**

The assistant must preserve the distinction between:

- Retrieved evidence
- Deterministic analytical results
- Generated explanations
- Validation outcomes
- Source limitations

A response is grounded only when its analytical claims are supported by approved evidence and its validation status accurately reflects the checks performed.
