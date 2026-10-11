
# Assistant Safety and Scope

## Approved Scope

The assistant retrieves and explains approved Track A results using fixed response templates.

## Unsupported Scope

- Predictions, forecasts, or generated scores
- Health-risk or regulatory conclusions
- Causal interpretation
- Arbitrary data access or computation
- User-controlled SQL, code, or filesystem paths
- Fabrication or alteration of analytical results

## Prompt-Injection Controls

No LLM is used in Mode A. Input is treated only as a candidate request for one allowlisted intent.

Text found in source records is untrusted evidence. It cannot alter the approved intent catalog or query execution.

## Data Exposure Controls

Only approved output fields are returned. Do not expose environment variables, credentials, internal filesystem contents, hidden prompts, or unrelated records.

## Authentication and Authorization

Preserve the existing backend access controls. Do not make the assistant route less restrictive than the Data Intelligence data it exposes.

## Sensitive Field Masking

Do not return fields outside the approved response contract. Review any future fields before adding them to the evidence package.

## Logging Policy

Avoid logging complete user questions or complete result payloads unless a documented operational requirement justifies it.

## Memory Policy

Do not persist user questions, profiles, or conversational memory.

## Result Limits

Apply the result limits in ASSISTANT_QUERY_CONTRACT.md.

## Failure Behaviour

Fail closed when the data cannot be validated, a version mismatch occurs, or a request is unsupported. Do not fabricate a fallback answer.
