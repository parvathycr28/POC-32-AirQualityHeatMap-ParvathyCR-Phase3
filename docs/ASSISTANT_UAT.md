# Grounded Data Assistant — User Acceptance Testing (UAT) Report

**Project:** PoC 32 — Aether Pulse Air Quality Heatmap (Phase 3)  
**Component:** Grounded Data Assistant  
**Environment:** Render deployment  
**Backend service:** `poc32-phase3-intelligence-api`  
**Backend URL:** `https://poc32-phase3-intelligence-api.onrender.com`  
**Assistant health endpoint:** `https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health`  
**Data version:** `phase3-v1.1`  
**Analytical method version:** `track-a-comparative-v1.0.0`  
**Configured Gemini model:** `gemini-3.8-flash`  
**Latest diagnostic commit:** `596019b`  
**Last updated:** 31 October 2026

---

## 1. Purpose

This document records the latest user acceptance and deployment validation of the Phase 3 Grounded Data Assistant.

The assistant retrieves approved, existing Track A intelligence results and supporting evidence for supported questions. It uses deterministic retrieval and response construction before attempting an optional Gemini-generated explanation.

The assistant must not independently generate numerical findings, rankings, predictions, or unsupported evidence.

The canonical dataset is synthetic and sparse. Results describe the available sample only and must not be interpreted as verified real-world air-quality observations, health-risk assessments, regulatory conclusions, causal findings, or predictions.

## 2. Test environment

| Item | Configuration |
|---|---|
| Project | PoC 32 — Aether Pulse Air Quality Heatmap |
| Phase | Phase 3 |
| Frontend | Deployed Render application |
| Backend | Render web service |
| Backend framework | FastAPI |
| Assistant mode | `deterministic_plus_llm_explanation` |
| Gemini model setting | `gemini-3.8-flash` |
| Gemini SDK | `google-genai==2.31.0` |
| Request timeout | 60 seconds |
| Dataset version | `phase3-v1.1` |
| Method version | `track-a-comparative-v1.0.0` |
| Dataset type | Synthetic, sparse sample |

## 3. Automated test results

**Latest recorded full test suite: PASS**

- Tests passed: 55
- Tests failed: 0
- Execution time: 18.93 seconds

The suite includes assistant functionality, Gemini explainer/service/API regression coverage, deterministic grounding, and related validation tests.

The focused Gemini explainer tests also passed after the diagnostic logging change:

- Tests passed: 15
- Tests failed: 0
- Execution time: 0.38 seconds

These automated test results validate application behaviour under the tested conditions. They do not establish that Google's live Gemini generation service is currently available.

## 4. UAT results

| ID | Acceptance check | Observed result | Status |
|---|---|---|---|
| UAT-01 | Complete Python test suite | 55 passed, 0 failed, 18.93 seconds | PASS |
| UAT-02 | Focused Gemini explainer regression tests | 15 passed, 0 failed | PASS |
| UAT-03 | Backend Render deployment | Service reports Live | PASS |
| UAT-04 | Backend health endpoint | HTTP 200; status `available` | PASS |
| UAT-05 | Gemini configuration check | `gemini_configured: true` | PASS |
| UAT-06 | Assistant operating mode | `deterministic_plus_llm_explanation` | PASS |
| UAT-07 | Grounded Assistant page loads | User confirmed successful page load | PASS |
| UAT-08 | Main dashboard loads | User confirmed successful operation | PASS |
| UAT-09 | Air-quality data display | User confirmed data appears correctly | PASS |
| UAT-10 | Charts and heatmap rendering | User confirmed correct rendering | PASS |
| UAT-11 | City filters | User confirmed correct operation | PASS |
| UAT-12 | Pollutant filters | User confirmed correct operation | PASS |
| UAT-13 | Supported NO2 city comparison | Deterministic Delhi and Mumbai values returned | PASS |
| UAT-14 | Deterministic fallback | Returned successfully when Gemini failed | PASS |
| UAT-15 | Assistant API response after Gemini failure | POST `/api/assistant/ask` returned HTTP 200 | PASS |
| UAT-16 | Browser CORS preflight | OPTIONS request returned HTTP 200 | PASS |
| UAT-17 | Gemini generation with configured model | Google returned HTTP 504 `DEADLINE_EXCEEDED` | FAIL |
| UAT-18 | Gemini alternative model investigation | `gemini-3.6-flash` also returned 503 in an earlier test | FAIL |
| UAT-19 | Gemini 2.5 model investigation | `gemini-2.5-flash` returned HTTP 404 `NOT_FOUND` | FAIL |
| UAT-20 | Provider error diagnostics | HTTP status, provider status, message and details captured in Render logs | PASS |
| UAT-21 | Diagnostic logging regression | 15 focused tests passed; change deployed successfully | PASS |
| UAT-22 | Final live Gemini explanation validation | Explanation remains unavailable because of provider deadline error | FAIL |

**Status note:** PASS and FAIL describe the specific observed result. The three Gemini-related failures do not mean that deterministic assistant functionality or the complete application is broken.

## 5. Live deployment evidence

### 5.1 Backend health check

Command:

```bash
curl -s https://poc32-phase3-intelligence-api.onrender.com/api/assistant/health
```

Observed response:

```json
{
  "status": "available",
  "mode": "deterministic_plus_llm_explanation",
  "gemini_configured": true
}
```

Interpretation:

- The backend is available.
- The assistant is operating in the expected mode.
- Gemini credentials are configured.
- This endpoint confirms configuration, not successful live text generation.

### 5.2 Deterministic comparison test

Question:

`Compare the average NO2 levels in Delhi and Mumbai.`

Observed values:

| City | NO2 value |
|---|---:|
| Delhi | 52.8933 µg/m³ |
| Mumbai | 40.1067 µg/m³ |

The values were retrieved from existing approved intelligence results. No new metric was calculated by the assistant.

Observed response metadata:

- Gemini attempted: Yes
- LLM used: No
- Explanation validated: No
- Deterministic fallback used: Yes
- Generated findings: No
- Source: `approved_intelligence_results`

The assistant preserved the deterministic answer despite the failed Gemini explanation.

### 5.3 Latest Gemini provider error

Latest relevant Render log:

```text
GEMINI_ERROR: {
  'exception_type': 'ServerError',
  'http_status': 504,
  'provider_status': 'DEADLINE_EXCEEDED',
  'provider_message':
    'Deadline expired before operation could complete.',
  'provider_details':
    "{'error': {'code': 504,
    'message': 'Deadline expired before operation could complete.',
    'status': 'DEADLINE_EXCEEDED'}}"
}
```

The corresponding API request returned:

```text
POST /api/assistant/ask HTTP/1.1 200 OK
```

The observed assistant request took approximately 59.35 seconds, close to the configured 60-second timeout.

Interpretation:

Google Gemini returned a structured 504 deadline error. The backend caught the exception and returned its deterministic fallback successfully.

The exact underlying cause of the provider deadline has not been established. It may involve provider-side capacity, processing delays, or other request-specific conditions. The current evidence does not justify attributing it to an incorrect API key or a broken Render deployment.

## 6. Diagnostic improvement

A diagnostic logging improvement was implemented in:

`assistant/core/gemini_explainer.py`

The updated handler captures:

- Exception type
- HTTP status
- Provider status
- Provider error message
- Provider error details

The logging also includes API-key redaction and limits the logged diagnostic fields to 1,000 characters.

The existing deterministic fallback and retry behaviour were preserved.

**Git evidence:**

- Commit: `596019b`
- Commit message: `Improve Gemini provider error diagnostics`
- Branch: `feature/data-intelligence-page`
- GitHub push: Successful
- Render deployment: Live

## 7. Final acceptance criteria

| Acceptance criterion | Current status |
|---|---|
| Frontend loads | PASS |
| Backend is deployed and available | PASS |
| Assistant page loads | PASS |
| Dashboard functions | PASS |
| Charts and heatmap render | PASS |
| City and pollutant filters work | PASS |
| Deterministic supported answers work | PASS |
| Approved evidence is retrieved | PASS |
| Deterministic fallback works | PASS |
| API handles Gemini failure without failing the request | PASS |
| Gemini API key is configured | PASS |
| Gemini-generated explanation is available | FAIL — provider 504 |
| Gemini provider diagnostics are captured | PASS |
| Automated test suite | PASS |

## 8. Limitations and outstanding issues

1. Gemini-generated explanations are not currently available because the provider returned HTTP 504 `DEADLINE_EXCEEDED`.
2. An earlier test with Gemini 3.6 Flash returned HTTP 503 `UNAVAILABLE`.
3. An earlier test with Gemini 2.5 Flash returned HTTP 404 `NOT_FOUND`.
4. The exact cause of the live Gemini generation failures remains unresolved.
5. The dataset is synthetic and sparse; results must not be represented as verified real-world measurements.
6. The live Gemini generation feature requires a successful provider response and validation before it can receive final acceptance.

## 9. Final UAT assessment

**DETERMINISTIC GROUNDED ASSISTANT — FUNCTIONAL ACCEPTANCE PASSED**

**OPTIONAL GEMINI EXPLANATION — NOT YET ACCEPTED**

The Phase 3 Grounded Data Assistant is deployed and its deterministic functionality has been validated. The dashboard and assistant interface operate correctly, approved intelligence results are retrieved, and the fallback mechanism preserves API availability when Gemini fails.

The optional LLM explanation component remains an outstanding issue. It must not be represented as successfully validated until a live Gemini request completes and its explanation passes the application's validation rules.

**Overall assessment: PARTIAL ACCEPTANCE — DETERMINISTIC FUNCTIONALITY ACCEPTED; GEMINI INTEGRATION PENDING.**