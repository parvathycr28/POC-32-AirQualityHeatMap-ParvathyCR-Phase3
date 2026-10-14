# Assistant User Acceptance Test (UAT) Report

## 1. Purpose

Validate the Aether Pulse Air Quality Heatmap Assistant for supported questions, evidence grounding, safety boundaries, API behavior, browser end-to-end behavior, and responsive layout.

## 2. Test Environment

- Project: POC-32 Aether Pulse Air Quality Heatmap — Phase 3
- Assistant frontend: http://localhost:3002/assistant
- Dashboard: http://localhost:3002/
- Data Intelligence frontend: http://localhost:3002/data-intelligence
- Assistant backend: http://localhost:8003
- Data Intelligence backend: http://localhost:8000
- Dataset version: phase3-v1.1
- Analytical method version: track-a-comparative-v1.0.0
- Dataset type: Synthetic, sparse sample; not verified real-world observations.

## 3. UAT Results

| ID | Test | Result | Evidence |
|---|---|---|---|
| UAT-01 | Full automated test suite | PASS | 47 passed, 0 failed; latest run completed in 16.13 seconds. |
| UAT-02 | Assistant page loads | PASS | Latest Selenium report confirms page load. |
| UAT-03 | Supported Track A summary question | PASS | HTTP 200; response status `ok`; intent `summary`; 10 evidence records; validation valid with no errors or warnings. |
| UAT-04 | Dashboard route smoke test | PASS | HTTP 200; non-empty HTML response; page title present. |
| UAT-05 | Data Intelligence API smoke test | PASS | OpenAPI endpoint returned HTTP 200, OpenAPI 3.1.0, and 7 routes. |
| UAT-06 | Data Intelligence page smoke test | PASS | HTTP 200; non-empty HTML response; page title present. |
| UAT-07 | Assistant health endpoint | PASS | Health endpoint returned HTTP 200 in prior validation; full test suite also passed the health test. |
| UAT-08 | Supported city comparison | PASS | Selenium displays supporting evidence for Delhi and Mumbai NO2 records; automated API test passed. |
| UAT-09 | Unsupported prediction request | PASS | Selenium confirms status `unsupported` and zero evidence. |
| UAT-10 | Missing question handling | PASS | API returned HTTP 422 in prior validation; automated test passed. |
| UAT-11 | Evidence metadata and limitations | PASS | Responses preserve data/method versions, quality status, limitations, and deterministic grounding metadata. |
| UAT-12 | Prompt injection and secret-disclosure handling | PASS | Both focused API tests passed in the latest full test suite. |
| UAT-13 | Evidence coverage and validation | PASS | Evidence coverage and grounding tests passed in the latest full test suite. |
| UAT-14 | Responsive layout | PASS | Latest Selenium report shows no horizontal overflow at 1440, 768, 390, and 320 px. |
| UAT-15 | Selenium end-to-end suite | PASS | 4 passed, 0 failed. Report: `selenium-test/selenium_artifacts/Assistant_Test_Report.txt`. Screenshot: `selenium-test/selenium_artifacts/assistant_e2e.png`. |

## 4. Evidence and Interpretation

- The summary question routes to the supported `summary` intent and retrieves approved Track A results.
- The summary response contains 10 evidence records and passes evidence validation.
- The supported Delhi–Mumbai NO2 comparison returns existing result records; no new metric is calculated.
- Grounding metadata reports deterministic operation, `llm_used: false`, and `generated_findings: false`.
- The dataset is synthetic and sparse. Results must not be represented as verified real-world measurements or used to claim health risk, regulatory compliance, causal effects, or predictions.
- Dashboard and Data Intelligence HTTP checks confirm that their routes respond. They do not independently verify every chart, filter, or browser-side interaction.

## 5. Final Acceptance Criteria

- [x] Full automated test suite passes.
- [x] Supported summary request returns valid, grounded evidence.
- [x] Supported comparison displays evidence.
- [x] Unsupported prediction request is rejected without evidence.
- [x] Prompt-injection and secret-disclosure tests pass.
- [x] Evidence coverage, versioning, quality metadata, and limitations tests pass.
- [x] Assistant browser end-to-end tests pass.
- [x] Responsive-layout tests pass at all required widths.
- [x] Dashboard and Data Intelligence routes pass HTTP smoke tests.
- [x] Latest Selenium report and screenshot are present.

## 6. Final Acceptance Status

**PASS — Assistant UAT**

All recorded automated tests and Assistant end-to-end checks passed in the latest test run. The supported summary API request also passed with valid evidence validation.

Scope note: dashboard and Data Intelligence checks were HTTP smoke tests only. Full visual and interaction verification of every dashboard/Data Intelligence component is not claimed by this report.

Dataset limitation: Phase 3 data is synthetic and sparse; conclusions are limited to the approved descriptive comparative analysis.
