# Assistant User Acceptance Test (UAT) Report

## 1. Purpose

Validate the Aether Pulse Air Quality Heatmap Assistant for supported questions, evidence grounding, safety boundaries, API behavior, browser end-to-end behavior, responsive layout, and optional Gemini-generated explanations.

This report records the latest automated test results, Render deployment status, and live Assistant validation evidence.

## 2. Test Environment

- **Project:** PoC 32 – Aether Pulse Air Quality Heatmap, Phase 3
- **Assistant frontend:** `/assistant`
- **Dashboard:** `/`
- **Data Intelligence frontend:** `/data-intelligence`
- **Assistant backend:** Render
- **Backend service:** `poc32-phase3-intelligence-api`
- **Backend URL:** `https://poc32-phase3-intelligence-api.onrender.com`
- **Assistant health endpoint:** `https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health`
- **Dataset version:** `phase3-v1.1`
- **Analytical method version:** `track-a-comparative-v1.0.0`
- **Dataset type:** Synthetic, sparse sample; not verified real-world observations.
- **Configured Gemini model:** `gemini-3.5-flash-lite`
- **Gemini SDK:** `google-genai==2.31.0`
- **Latest deployed commit:** `6e06bfa`
- **Latest commit message:** Fix Selenium E2E test runner compatibility
- **Latest deployment ID:** `dep-dbjf41eq1p3s73am9p60`
- **Latest deployment status:** Live
- **Last updated:** 1 November 2026

## 3. Automated Test Results

### 3.1 Focused Gemini explainer tests

Command:

```bash
python -m pytest -q tests/assistant/test_gemini_explainer.py
```

Recorded result after the qualitative-only prompt change:

```text
............... [100%]
15 passed in 0.49s
```

| Measure | Result |
|---|---:|
| Tests passed | 15 |
| Tests failed | 0 |
| Execution time | 0.49 seconds |
| Status | PASS |

These tests were run after the qualitative-only prompt change. They remain the focused Gemini regression evidence.

### 3.2 Full test suite

The latest full test suite was executed after correcting the Selenium test-runner compatibility issue.

Command:

```bash
python -m pytest -q
```

Latest result:

```text
.................................................................. [100%]
66 passed in 23.86s
```

| Measure | Result |
|---|---:|
| Tests passed | 66 |
| Tests failed | 0 |
| Execution time | 23.86 seconds |
| Status | PASS |

The full suite includes assistant functionality, API and regression coverage, and all four Selenium Assistant end-to-end tests.

### 3.3 Selenium test-runner correction

The Selenium test class in `selenium-test/test_assistant_e2e.py` contained a custom `run()` override that attempted to access `result.errors` and `result.failures`.

Under pytest, the supplied object was a `TestCaseFunction`, which does not expose those attributes. The custom `run()` override was removed while retaining the test cases and reporting functionality.

After the correction, the complete test suite passed:

**66 passed, 0 failed, in 23.86 seconds.**

The correction was committed as:

- **Commit:** `6e06bfa`
- **Commit message:** `Fix Selenium E2E test runner compatibility`

## 4. Assistant Health and Deployment Verification

### 4.1 Latest Render deployment

The following deployment was confirmed Live in Render:

- **Commit:** `6e06bfa5041dcf4cb9b735bfa137a52f1acbb465`
- **Commit message:** `Fix Selenium E2E test runner compatibility`
- **Branch:** `feature/data-intelligence-page`
- **Service:** `poc32-phase3-intelligence-api`
- **Service ID:** `srv-db5du65ckfvc739s9msg`
- **Deployment ID:** `dep-dbjf41eq1p3s73am9p60`
- **Deployment status:** Live

Evidence:

- [Render deployment](https://dashboard.render.com/web/srv-db5du65ckfvc739s9msg/deploys/dep-dbjf41eq1p3s73am9p60)
- [GitHub commit](https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3/commit/6e06bfa5041dcf4cb9b735bfa137a52f1acbb465)

The latest deployment contains the Selenium E2E test-runner compatibility correction. The deployed commit is distinct from the earlier qualitative-only Gemini prompt commit `0555241`.

### 4.2 Assistant health endpoint

Endpoint:

`https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health`

Previously observed response:

```json
{
  "status": "available",
  "mode": "deterministic_plus_llm_explanation",
  "gemini_configured": true
}
```

| Check | Result |
|---|---|
| Backend status | available |
| Assistant mode | deterministic_plus_llm_explanation |
| Gemini configured | true |
| Health check | PASS |

The health endpoint confirms backend availability and Gemini configuration. It does not independently prove that an explanation can be generated or validated; that is covered by the live request test below.

## 5. Live Gemini Explanation UAT

### 5.1 Test question

```text
Compare Delhi and Mumbai for NO2.
```

### 5.2 Deterministic answer

The assistant returned the existing approved NO2 result records:

- Delhi: **52.8933 µg/m³**
- Mumbai: **40.1067 µg/m³**

The deterministic response identified these as retrieved values and stated that no new metric was calculated.

### 5.3 Gemini explanation

The deployed assistant returned:

> Delhi shows a higher mean level of nitrogen dioxide compared to Mumbai within the supplied descriptive sample. Both cities record levels above the baseline mean. This data is a synthetic descriptive comparison only and is not a verified real-world air-quality measurement. Conclusions are limited to the supplied descriptive sample.

### 5.4 Response metadata

| Metadata field | Result |
|---|---|
| Mode | `deterministic_plus_llm_explanation` |
| Gemini attempted | Yes |
| LLM used | Yes |
| Explanation validated | Yes |
| Deterministic fallback used | No |
| Generated findings | No |
| Source | `approved_intelligence_results` |

**Result: PASS for the tested live request.**

The deterministic response retained the approved numerical measurements. Gemini supplied a qualitative explanation without introducing new numerical values or new findings.

The user also confirmed that the live Assistant returned a Gemini result following the latest Render deployment. The detailed response and diagnostic evidence below are the supplied successful comparison evidence; the exact full response and logs from the subsequent deployment smoke check were not separately provided.

### 5.5 Render logs from the successful Gemini request

Recorded diagnostic output:

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

| Numeric validation measure | Result |
|---|---:|
| Allowed numeric tokens | 17 |
| Generated numeric tokens | 0 |
| Unsupported numeric tokens | 0 |
| Unsupported values | None |
| Explanation validation | `valid: True` |
| Validation errors | None |
| API response | HTTP 200 |

**Result: PASS.**

This confirms that the recorded successful explanation introduced no numeric tokens and passed the deployed validator.

### 5.6 Evidence-review note

The generated explanation includes the statement:

> Both cities record levels above the baseline mean.

The live validator returned `valid: True`, but that result alone does not independently establish that the baseline comparison is supported by the approved evidence.

This statement should be checked against the underlying approved evidence before treating it as a fully verified finding. The existing validation result is recorded accurately; no additional evidence claim is made in this report.

## 6. Gemini Reliability and Validation History

### 6.1 Earlier provider failures

Earlier attempts using other Gemini model configurations encountered provider errors, including:

- `gemini-3.8-flash`: 503 UNAVAILABLE and a later 429 free-tier quota response.
- `gemini-3.6-flash`: 503 UNAVAILABLE.
- `gemini-2.5-flash`: 404 response.

These are historical failures. They are not the result of the recorded successful live request using `gemini-3.5-flash-lite`.

### 6.2 Unsupported numeric output

An earlier Gemini explanation introduced the unsupported numeric token `36.2075`.

The numeric validator rejected the explanation with:

```text
Explanation introduced numeric tokens not found in approved evidence or the question.
```

This rejection was intentional. The unsupported value was not added to the approved numeric set, and the validator was not weakened.

### 6.3 Forbidden-claim validation

An earlier generated explanation was rejected with:

```text
Explanation contains a prohibited claim category.
```

The forbidden-claim checks remain in place. They cover forecasting, prediction, causation, health-risk, regulatory-compliance, safe-limit, and disease-risk claim categories.

Temporary diagnostic logging was used to investigate rejected generated sentences. The diagnostic code was reintroduced in commit `9cb5c2f` and is present in the deployed code history.

### 6.4 Qualitative-only prompt improvement

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

**Recorded successful live result:** qualitative explanation generated, validation passed, zero generated numeric tokens, zero unsupported numeric tokens, and no deterministic fallback.

## 7. UAT Acceptance Matrix

| ID | Test | Result | Evidence |
|---|---|---|---|
| UAT-01 | Full automated test suite | PASS — latest | 66 passed, 0 failed, 23.86 seconds. |
| UAT-02 | Assistant page loads | PASS — previously recorded | Earlier Selenium report confirmed page load. |
| UAT-03 | Supported Track A summary question | PASS — previously recorded | Earlier API response returned `ok`, summary intent, and approved evidence. |
| UAT-04 | Dashboard route smoke test | PASS — previously recorded | HTTP 200 and non-empty HTML response. |
| UAT-05 | Data Intelligence API smoke test | PASS — previously recorded | OpenAPI endpoint returned HTTP 200 and OpenAPI 3.1.0. |
| UAT-06 | Data Intelligence page smoke test | PASS — previously recorded | HTTP 200 and non-empty HTML response. |
| UAT-07 | Assistant health endpoint | PASS — previously recorded | Render health response reports available and Gemini configured. |
| UAT-08 | Supported city comparison | PASS — successful live request evidence | Delhi and Mumbai NO2 comparison returned approved values and a validated qualitative explanation. |
| UAT-09 | Unsupported prediction request | PASS — previously recorded | Earlier Selenium test confirmed unsupported status and zero evidence. |
| UAT-10 | Missing question handling | PASS — previously recorded | Earlier API test returned HTTP 422. |
| UAT-11 | Evidence metadata and limitations | PASS — recorded live test | Response preserved the synthetic-data and descriptive-sample limitations. |
| UAT-12 | Prompt injection and secret-disclosure handling | PASS — previously recorded | Earlier focused API tests passed. |
| UAT-13 | Evidence coverage and validation | PASS — previously recorded | Earlier evidence coverage and grounding tests passed. |
| UAT-14 | Responsive layout | PASS — previously recorded | Earlier Selenium report showed no horizontal overflow at 1440, 768, 390, and 320 px. |
| UAT-15 | Selenium end-to-end suite | PASS — latest full suite | Four Selenium Assistant tests were included in the latest full suite; the full suite passed. |
| UAT-16 | Gemini health/configuration | PASS — previously recorded | Health endpoint reports `gemini_configured: true`. |
| UAT-17 | Gemini generation | PASS — successful live request evidence | `FinishReason.STOP` using `gemini-3.5-flash-lite`. User also confirmed a Gemini result after the latest deployment. |
| UAT-18 | Numeric output validation | PASS — successful live request evidence | 0 generated numeric tokens and 0 unsupported numeric tokens. |
| UAT-19 | Forbidden-claim validation | PASS — tested explanation | Explanation passed the deployed validation pipeline with no errors. |
| UAT-20 | Comparison-consistency validation | PASS — validator result; evidence review outstanding | Overall explanation validation returned `valid: True`; baseline wording still requires evidence review. |
| UAT-21 | Gemini response metadata | PASS — successful live request evidence | LLM used, explanation validated, deterministic fallback not used, generated findings false. |
| UAT-22 | Live API request | PASS — successful live request evidence | `POST /api/assistant/ask` returned HTTP 200. |
| UAT-23 | Focused Gemini explainer tests | PASS — previously recorded | 15 passed, 0 failed, in 0.49 seconds. |
| UAT-24 | Latest Render deployment | PASS — latest | Deployment `dep-dbjf41eq1p3s73am9p60` reports Live for commit `6e06bfa`. |
| UAT-25 | Selenium test-runner compatibility | PASS — latest | Custom `run()` override removed; full pytest suite passes. |

*Previously recorded tests are identified as such and are not presented as newly rerun in the latest deployment cycle.*

## 8. Known Limitations

1. The underlying dataset is synthetic and sparse. It must not be treated as verified real-world air-quality observations.
2. The sample is not sufficient for long-term trends, seasonality, or year-over-year conclusions.
3. A successful live Gemini request does not guarantee that every future generated explanation will pass validation.
4. Gemini explanations are optional. If generation or validation fails, the deterministic answer and approved evidence remain available.
5. The qualitative-only prompt reduces numeric-generation risk, while the numeric validator remains active as an independent safeguard.
6. The baseline-mean statement in the recorded successful explanation requires confirmation against the approved evidence.
7. Earlier provider errors remain part of the historical diagnostic record; they are not the outcome of the successful live Gemini request.
8. The latest full automated suite passed locally. The 66-test result is not a claim that 66 tests were executed by Render during deployment.
9. The full live Gemini response and its corresponding diagnostic logs from the subsequent `6e06bfa` deployment smoke check were not separately supplied. The latest successful live response is recorded based on the user's confirmation.

## 9. Overall Assessment

**FUNCTIONAL ACCEPTANCE PASSED FOR THE TESTED GROUNDED ASSISTANT SCOPE.**

**LATEST LIVE GEMINI GENERATION SMOKE TEST — USER CONFIRMED SUCCESSFUL.**

**LATEST FULL AUTOMATED TEST SUITE — PASS (66 PASSED, 0 FAILED).**

**LATEST RENDER DEPLOYMENT — LIVE (`6e06bfa`).**

The deployed assistant successfully returned the deterministic approved NO2 measurements and a qualitative Gemini explanation in the recorded live comparison. The explanation passed the deployed validation pipeline, introduced zero numeric tokens, and did not require deterministic fallback.

The latest full local test suite completed with 66 passed and 0 failed, including all four Selenium Assistant end-to-end tests. The latest Render deployment is confirmed Live for commit `6e06bfa`.

The baseline-mean wording remains subject to evidence review. The historical full-suite and Selenium results have now been superseded by the latest 66-test full-suite result; the focused Gemini result remains 15 passed, 0 failed.

**Latest deployed commit:** `6e06bfa` — Fix Selenium E2E test runner compatibility  
**Previous qualitative-only prompt commit:** `0555241` — Use qualitative-only Gemini explanations  
**Deployment status:** Live  
**Latest live Gemini test:** User confirmed successful result  
**Recorded Gemini validation:** `valid: True`, zero generated numeric tokens, zero unsupported numeric tokens  
**Latest full test suite:** 66 passed, 0 failed  
**Focused Gemini tests:** 15 passed, 0 failed

**Overall assessment: ACCEPTED FOR THE TESTED FUNCTIONAL SCOPE — GROUNDED ASSISTANT, AUTOMATED TEST SUITE, AND LIVE GEMINI GENERATION PASSED. DATASET AND CONTENT-GROUNDING LIMITATIONS REMAIN.**