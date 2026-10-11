
# Grounded Assistant — Grounding Validation

## Purpose

This document defines the grounding checks for the Phase 3
deterministic data assistant.

The assistant retrieves existing approved intelligence outputs. It must not
recompute analytical-track methods or invent values, ranks, findings,
predictions, or explanations that are not supported by retrieved evidence.

## Approved source

The primary runtime source is the configured
`intelligence_results.json` output. The configured summary output may provide
additional quality and limitation metadata.

The assistant must not use arbitrary filesystem paths supplied by a user,
arbitrary SQL, or unrestricted access to the canonical dataset.

## Evidence package

Each grounded answer should preserve, when available:

- result ID and result type
- entity ID and group key
- metric name, value, and unit
- priority rank and existing finding
- existing evidence field
- quality status and limitations
- data version and method version
- generated timestamp

Unavailable metadata must remain unavailable. The assistant must not fill
gaps with guessed values.

## Validation rules

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
11. User input is treated as data, never as an instruction to bypass the
    allowlist, disclose secrets, or change assistant policy.
12. The response must not disclose filesystem paths, credentials, hidden
    configuration, or internal exception details.

## Important scope boundary

The validator checks record structure, provenance, and version consistency.
It does not prove that every arbitrary natural-language sentence is entailed
by the evidence. For this reason, the initial implementation uses controlled
response templates and source-backed record fields rather than unrestricted
LLM-generated prose.

## Current limitations

- The initial implementation is deterministic and does not use an LLM.
- It is not a predictive model.
- It does not provide health or regulatory advice.
- It does not establish causation.
- Synthetic data must be identified as synthetic when that metadata is
  available in the approved source.
- Missing synthetic-data metadata must not be replaced by an unsupported claim.
- API authentication and authorization must follow the existing application's
  access-control requirements. This router does not independently implement
  an identity system.

## Release gate

Do not mark the assistant ready for acceptance until:

- unit tests pass
- API tests pass
- unsupported and unsafe requests are rejected
- existing Operational View tests still pass
- existing Data Intelligence endpoints still pass
- the frontend integration is tested separately
- source versions, limitations, and synthetic-data status are confirmed
  against the actual generated outputs

