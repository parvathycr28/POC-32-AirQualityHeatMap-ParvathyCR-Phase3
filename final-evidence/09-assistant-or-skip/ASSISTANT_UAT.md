# Assistant User Acceptance Test (UAT) Report

## 1. Purpose

Validate the Aether Pulse Air Quality Heatmap Assistant for supported questions, evidence grounding, safety boundaries, API behavior, browser end-to-end behavior, responsive layout, and optional Gemini-generated explanations.

This report records the latest automated test results, Render deployment evidence, Gemini connectivity and generation evidence, deterministic fallback behavior, and the distinction between locally tested and publicly deployed functionality.

## 2. Test Environment

- **Project:** PoC 32 – Aether Pulse Air Quality Heatmap, Phase 3
- **Assistant frontend:** `/assistant`
- **Dashboard:** `/`
- **Data Intelligence frontend:** `/data-intelligence`
- **Assistant backend:** Render
- **Backend service:** `poc32-phase3-intelligence-api`
- **Backend URL:** https://poc32-phase3-intelligence-api.onrender.com
- **Assistant health endpoint:** https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health
- **Dataset version:** `phase3-v1.1`
- **Analytical method version:** `track-a-comparative-v1.0.0`
- **Dataset type:** Synthetic, sparse sample; not verified real-world observations.
- **Configured Gemini model:** `gemini-3.5-flash-lite`
- **Gemini SDK:** `google-genai==2.31.0`
- **Assistant deployment:** Previously confirmed Live in Render.
- **Latest verification update:** 2 November 2026

## 3. Automated Test Results

### 3.1 Full Python test suite — latest run

Command:

```bash
./.venv/Scripts/python.exe -m pytest tests -v
```

Latest result:

```text
62 passed, 0 failed
```

| Measure | Result |
|---|---:|
| Tests passed | 62 |
| Tests failed | 0 |
| Status | PASS |
| Environment | Local Data Intelligence backend |
| Gemini configuration | Temporarily disabled for this test run |

The latest full test suite was executed locally against the Data Intelligence backend. Gemini was temporarily disabled in the local backend container to prevent external provider latency and retry delays from causing integration-test timeouts.

The 62-test result does not include the separately executed Assistant Selenium end-to-end tests.

### 3.2 Focused Gemini explainer tests — historical result

Command:

```bash
python -m pytest -q tests/assistant/test_gemini_explainer.py
```

Previously recorded result:

```text
............... [100%]
15 passed in 0.49s
```

| Measure | Result |
|---|---:|
| Tests passed | 15 |
| Tests failed | 0 |
| Execution time | 0.49 seconds |
| Status | PASS — historical result |

These tests were executed after the qualitative-only prompt change. They remain recorded Gemini regression evidence but were not part of the latest 62-test local run.

### 3.3 Assistant Selenium end-to-end tests — separate run

Command:

```bash
ASSISTANT_URL="https://poc32-phase3-frontend.onrender.com/assistant" HEADLESS=1 ./.venv/Scripts/python.exe selenium-test/test_assistant_e2e.py
```

Recorded result:

| Test | Result |
|---|---|
| Assistant page loads | PASS |
| Supported comparison returns approved evidence | PASS |
| Unsupported prediction is rejected without evidence | PASS |
| Responsive layout at 1440, 768, 390 and 320 px | PASS |

**Result: 4 passed, 0 failed.**

These four Selenium tests were executed separately against the public Render Assistant frontend. They must not be counted as part of the latest 62-test Python suite.

The report is stored at:

`selenium-test/selenium_artifacts/Assistant_Test_Report.txt`

### 3.4 Selenium test-runner correction

The Selenium test class in `selenium-test/test_assistant_e2e.py` previously contained a custom `run()` override that attempted to access `result.errors` and `result.failures`.

Under pytest, the supplied object was a `TestCaseFunction`, which does not expose those attributes. The custom override was removed while retaining the test cases and reporting functionality.

The correction was previously committed as:

- **Commit:** `6e06bfa`
- **Commit message:** `Fix Selenium E2E test runner compatibility`

The latest full Python suite and separate Selenium execution are recorded independently above.

## 4. Assistant Health and Deployment Verification

### 4.1 Render deployment evidence

The Assistant backend was previously confirmed Live in Render.

- **Service:** `poc32-phase3-intelligence-api`
- **Branch:** `feature/data-intelligence-page`
- **Previously recorded deployment commit:** `9bac519c6059ae7da40db039d0059cbc589eb631`
- **Deployment status:** Previously confirmed Live

Evidence:

- [Render backend service](https://dashboard.render.com/web/srv-db5du65ckfvc739s9msg)
- [Phase 3 GitHub repository](https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3)

The latest local test-container changes do not change the public Render deployment. The local Gemini-disabled configuration must not be interpreted as a change to Render's Gemini configuration.

### 4.2 Assistant health endpoint

Endpoint:

https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health

Previously observed response:

```json
{
  "status": "available",
  "mode": "deterministic_plus_llm_explanation",
  "gemini_configured": true
}
```

| Check | Previously observed result |
|---|---|
| Backend status | available |
| Assistant mode | deterministic_plus_llm_explanation |
| Gemini configured | true |
| Health check | PASS |

The health endpoint confirms backend availability and Gemini configuration at the time of the recorded check. It does not independently prove that an explanation can be generated or validated; that is covered by the separately recorded live request.

## 5. Local Gemini Connectivity Test

### 5.1 Test purpose

A direct SDK request was previously performed locally to verify Gemini connectivity independently of the Assistant API, prompt construction, and explanation-validation workflow.

The recorded test used the local environment configuration. No API credential is reproduced in this report.

### 5.2 Successful model test — historical result

- **Model:** `gemini-3.5-flash-lite`
- **SDK:** `google-genai==2.31.0`
- **Request timeout:** 60 seconds
- **Request:** `Reply with exactly: Gemini connection successful`

Previously recorded result:

```text
Testing model: gemini-3.5-flash-lite
RESULT: SUCCESS
RESPONSE: Gemini connection successful
```

| Measure | Result |
|---|---|
| SDK request | Successful |
| API authentication | Successful |
| Model generation | Successful |
| Response received | Yes |
| Status | PASS — historical result |

This confirms that the local Gemini integration successfully generated a response during that earlier test. It is not evidence that Gemini was enabled during the latest 62-test local run.

### 5.3 Earlier model timeout

An earlier direct test using `gemini-3.8-flash` returned:

```text
ERROR TYPE: ServerError
HTTP STATUS: 504
PROVIDER STATUS: DEADLINE_EXCEEDED
ERROR: Deadline expired before operation could complete.
```

The subsequent successful test with `gemini-3.5-flash-lite` is retained as separate historical evidence.

## 6. Live Gemini Explanation UAT

### 6.1 Test question

```text
Compare Delhi and Mumbai for NO2.
```

### 6.2 Deterministic answer

The previously recorded public Assistant API response returned the approved NO2 result records:

- Delhi: **52.8933 µg/m³**
- Mumbai: **40.1067 µg/m³**

The deterministic response identified these as retrieved values and stated that no new metric was calculated.

### 6.3 Gemini explanation

Previously recorded live explanation:

> Delhi shows a higher nitrogen dioxide level compared to Mumbai within the supplied sample, and both cities record levels above the baseline. This is a synthetic descriptive comparison only and is not a verified real-world air-quality measurement. Conclusions are limited to the supplied descriptive sample.

### 6.4 Response metadata

Previously recorded live response metadata:

| Metadata field | Result |
|---|---|
| Mode | `deterministic_plus_llm_explanation` |
| Gemini attempted | Yes |
| LLM used | Yes |
| Explanation validated | Yes |
| Deterministic fallback used | No |
| Generated findings | No |
| Source | `approved_intelligence_results` |

**Result: PASS for the previously tested live request.**

The deterministic response retained the approved numerical measurements. Gemini supplied a qualitative explanation without introducing new numerical values or new findings.

This is historical live-request evidence, not a result from the latest local 62-test run.

### 6.5 Render logs from the successful Gemini request

Previously recorded diagnostic output:

```text
GEMINI_DIAGNOSTIC: {
  'model': 'gemini-3.5-flash-lite',
  'finish_reason': 'FinishReason.STOP',
  'prompt_tokens': 1774,
  'candidate_tokens': 57,
  'total_tokens': 1831,
  'thoughts_tokens': None
}

GEMINI_NUMERIC_CHECK: {
  'allowed_number_count': 17,
  'generated_number_count': 0,
  'unsupported_number_count': 0,
  'unsupported_numbers': []
}

GEMINI_VALIDATION: {
  'model': 'gemini-3.5-flash-lite',
  'valid': True,
  'errors': []
}

INFO: POST /api/assistant/ask HTTP/1.1 200 OK
```

| Numeric validation measure | Recorded result |
|---|---:|
| Allowed numeric tokens | 17 |
| Generated numeric tokens | 0 |
| Unsupported numeric tokens | 0 |
| Unsupported values | None |
| Explanation validation | `valid: True` |
| Validation errors | None |
| API response | HTTP 200 |

**Result: PASS for the recorded live request.**

### 6.6 Baseline evidence verification

The generated explanation included the statement that both cities record levels above the baseline.

The statement was independently checked against the approved NO2 intelligence results:

- Delhi sampled mean: 52.8933
- Mumbai sampled mean: 40.1067
- NO2 baseline mean: 36.2075

Both sampled means are above the recorded NO2 baseline mean.

This comparison is limited to the approved synthetic dataset. The baseline is not a regulatory threshold or a health-risk limit.

## 7. Gemini Reliability and Validation History

### 7.1 Earlier provider failures

Earlier attempts using other Gemini model configurations encountered provider errors, including:

- `gemini-3.8-flash`: 503 UNAVAILABLE, a later 429 free-tier quota response, and a subsequent 504 DEADLINE_EXCEEDED.
- `gemini-3.6-flash`: 503 UNAVAILABLE.
- `gemini-2.5-flash`: 404 response.

These are historical failures and are not the outcome of the previously recorded successful requests using `gemini-3.5-flash-lite`.

### 7.2 Unsupported numeric output

An earlier Gemini explanation introduced the unsupported numeric token `36.2075`.

The numeric validator rejected the explanation with:

```text
Explanation introduced numeric tokens not found in approved evidence or the question.
```

This rejection was intentional. The validator was not weakened to permit the unsupported value.

### 7.3 Forbidden-claim validation

An earlier generated explanation was rejected with:

```text
Explanation contains a prohibited claim category.
```

The forbidden-claim checks remain in place. They cover forecasting, prediction, causation, health-risk, regulatory-compliance, safe-limit, and disease-risk claim categories.

Temporary diagnostic logging was used to investigate rejected generated sentences. The diagnostic code was reintroduced in commit `9cb5c2f` and is present in the recorded deployed code history.

### 7.4 Qualitative-only prompt improvement

Commit `0555241` updated the Gemini prompt to require qualitative-only explanations.

The prompt instructs Gemini to:

- Omit all numeric values from its explanation.
- Keep the explanation qualitative.
- Describe higher/lower relationships only when supported by approved evidence.
- Avoid numerical differences, percentages, averages, ratios, rankings, and derived statistics.
- Avoid repeating measurements, coordinates, timestamps, counts, and IDs.
- Omit unavailable details rather than infer them.

The deterministic response continues to display approved numerical results.

The numeric validator, forbidden-claim checks, and comparison-consistency checks were not removed or relaxed.

**Previously recorded live result:** qualitative explanation generated, validation passed, zero generated numeric tokens, zero unsupported numeric tokens, and no deterministic fallback.

## 8. UAT Acceptance Matrix

| ID | Test | Result | Evidence |
|---|---|---|---|
| UAT-01 | Full automated Python test suite | PASS — latest local run | 62 passed, 0 failed. |
| UAT-02 | Assistant page loads | PASS — previously recorded | Earlier Selenium report confirmed page load. |
| UAT-03 | Supported Track A summary question | PASS — previously recorded | Earlier API response returned `ok`, summary intent, and approved evidence. |
| UAT-04 | Dashboard route smoke test | PASS — previously recorded | HTTP 200 and non-empty HTML response. |
| UAT-05 | Data Intelligence API smoke test | PASS — previously recorded | OpenAPI endpoint returned HTTP 200 and OpenAPI 3.1.0. |
| UAT-06 | Data Intelligence page smoke test | PASS — previously recorded | HTTP 200 and non-empty HTML response. |
| UAT-07 | Assistant health endpoint | PASS — previously recorded | Render health response reported available and Gemini configured. |
| UAT-08 | Supported city comparison | PASS — historical live request | Delhi and Mumbai NO2 comparison returned approved values and a validated qualitative explanation. |
| UAT-09 | Unsupported prediction request | PASS — separate Selenium run | Unsupported request rejected without evidence. |
| UAT-10 | Missing question handling | PASS — previously recorded | Earlier API test returned HTTP 422. |
| UAT-11 | Evidence metadata and limitations | PASS — recorded live test | Response preserved synthetic-data and descriptive-sample limitations. |
| UAT-12 | Prompt injection and secret-disclosure handling | PASS — previously recorded | Earlier focused API tests passed. |
| UAT-13 | Evidence coverage and validation | PASS — previously recorded | Earlier evidence coverage and grounding tests passed. |
| UAT-14 | Responsive layout | PASS — separate Selenium run | No horizontal overflow at 1440, 768, 390, and 320 px. |
| UAT-15 | Assistant Selenium end-to-end suite | PASS — separate run | 4 passed, 0 failed; not included in the 62-test Python suite. |
| UAT-16 | Gemini health/configuration | PASS — previously recorded | Render health response reported `gemini_configured: true`. |
| UAT-17 | Gemini local generation | PASS — historical test | Earlier direct SDK request returned the expected response. |
| UAT-18 | Gemini generation on Render | PASS — historical live request | Recorded `FinishReason.STOP` using `gemini-3.5-flash-lite`. |
| UAT-19 | Numeric output validation | PASS — historical live request | 0 generated numeric tokens and 0 unsupported numeric tokens. |
| UAT-20 | Forbidden-claim validation | PASS — recorded explanation | Explanation passed the deployed validation pipeline with no errors. |
| UAT-21 | Comparison-consistency validation | PASS — recorded validator and evidence review | Validator returned `valid: True`; approved NO2 results confirm both cities are above the recorded baseline. |
| UAT-22 | Gemini response metadata | PASS — historical live request | LLM used, explanation validated, deterministic fallback not used, generated findings false. |
| UAT-23 | Live API request | PASS — historical live request | `POST /api/assistant/ask` returned HTTP 200. |
| UAT-24 | Focused Gemini explainer tests | PASS — historical run | 15 passed, 0 failed, in 0.49 seconds. |
| UAT-25 | Render deployment | Previously confirmed Live | Historical Render deployment evidence. |
| UAT-26 | Selenium test-runner compatibility | PASS — latest local suite | Custom `run()` override removed; latest full Python suite passed. |

*Previously recorded tests are identified as historical evidence and are not presented as newly rerun in the latest verification cycle.*

## 9. Known Limitations

1. The underlying dataset is synthetic and sparse. It must not be treated as verified real-world air-quality observations.
2. The sample is not sufficient for long-term trends, seasonality, or year-over-year conclusions.
3. A successful live Gemini request does not guarantee that every future generated explanation will pass validation.
4. Gemini explanations are optional. If generation or validation fails, the deterministic answer and approved evidence remain available.
5. The qualitative-only prompt reduces numeric-generation risk, while the numeric validator remains active as an independent safeguard.
6. The recorded NO2 baseline comparison is supported by approved synthetic results; the baseline is not a regulatory or health threshold.
7. Earlier provider errors remain part of the historical diagnostic record.
8. The latest full Python test suite passed locally with Gemini temporarily disabled. The 62-test result does not demonstrate live Gemini generation.
9. The four Assistant Selenium tests were run separately against the public Render frontend and are not included in the 62-test result.
10. The public Data Intelligence deployment remains suspended. Data Intelligence UAT was performed locally, not against a live public Data Intelligence deployment.
11. A Gemini API credential was previously exposed in terminal output. It must be rotated, and the replacement must remain private and outside repository documentation. No credential is included in this report.

## 10. Overall Assessment

**FUNCTIONAL ACCEPTANCE: PASS FOR THE TESTED GROUNDED ASSISTANT SCOPE.**

**LATEST LOCAL PYTHON TEST SUITE: PASS — 62 PASSED, 0 FAILED.**

**LOCAL DETERMINISTIC ASSISTANT FALLBACK: PASS.**

**PUBLIC ASSISTANT SELENIUM: PASS — 4/4, EXECUTED SEPARATELY.**

**FOCUSED GEMINI EXPLAINER TESTS: 15 PASSED, 0 FAILED — HISTORICAL RESULT.**

**LOCAL GEMINI GENERATION: PREVIOUSLY VERIFIED.**

**LIVE GEMINI GENERATION: PREVIOUSLY VERIFIED — NOT EXERCISED IN THE LATEST LOCAL TEST RUN.**

**RENDER ASSISTANT DEPLOYMENT: PREVIOUSLY CONFIRMED LIVE.**

The latest local automated test run passed all 62 Python tests with Gemini disabled in the local test container. The deterministic fallback returned HTTP 200 and two approved evidence records for the supported Delhi–Mumbai NO2 comparison.

The public Assistant Selenium suite separately passed all four tests, covering page loading, supported comparison, unsupported prediction rejection, and responsive layout.

Earlier local SDK and public live API tests successfully verified Gemini generation using `gemini-3.5-flash-lite`. Those results remain historical evidence and are not represented as part of the latest local 62-test run.

The synthetic dataset, limited sampling, and content-grounding boundaries remain applicable.

## 11. Latest Verification Update — 2026-11-02

### Automated test suite

- Full local Python test suite: **62 passed, 0 failed**.
- The suite was run against the local Data Intelligence backend.
- Gemini was temporarily disabled in this local test container to prevent external provider latency from causing integration-test timeouts.

### Deterministic assistant fallback

- Local `POST /api/assistant/ask`: HTTP 200.
- Supported Delhi–Mumbai NO2 comparison returned two approved evidence records.
- Data source: `approved_intelligence_results`.
- Gemini attempted: false.
- Deterministic fallback: true.
- Generated findings: false.

### Live assistant and Gemini evidence

- The previously recorded public live API comparison returned HTTP 200.
- The live Gemini explanation was validated successfully in the separately recorded deployment test.
- The public Assistant Selenium suite separately passed all four tests, including supported comparison, unsupported prediction rejection, and responsive layout checks.
- These live results are historical successful checks, not a claim that the latest local 62-test run exercised Gemini.

### Environment and deployment boundary

- The local backend container was recreated with Gemini disabled for deterministic automated testing.
- The public Render assistant deployment was not changed by this local override.
- The public Data Intelligence deployment remains suspended; Data Intelligence UAT was performed locally.
- Gemini credentials must be rotated following the accidental exposure of a key in terminal output. No replacement credential is included in this repository documentation.

### Latest assessment

**LOCAL AUTOMATED TESTS: PASS — 62/62.**

**LOCAL DETERMINISTIC ASSISTANT FALLBACK: PASS.**

**PUBLIC ASSISTANT SELENIUM: PASS — 4/4, SEPARATELY EXECUTED.**

**LIVE GEMINI GENERATION: PREVIOUSLY VERIFIED — NOT EXERCISED IN THE LATEST LOCAL TEST RUN.**


**LATEST STATUS: 62 PYTHON TESTS PASS; 4 SELENIUM TESTS PASS; LIVE GEMINI PREVIOUSLY VERIFIED.**
