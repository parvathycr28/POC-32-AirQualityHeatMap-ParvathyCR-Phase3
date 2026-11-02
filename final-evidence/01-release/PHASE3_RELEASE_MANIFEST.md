# Phase 3 Release Manifest

## 1. Project identity

| Field | Value |
|---|---|
| Project | Aether Pulse — Air Quality Heatmap |
| Project ID | PoC 32 |
| Repository | https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3 |
| Release branch | feature/data-intelligence-page |
| Application version | 0.1.0 |
| Current baseline commit | 9bac519c6059ae7da40db039d0059cbc589eb631 |
| Certified commit | PENDING — set after final release commit |
| Certified tag | PENDING — phase3-v1.0.0 |

## 2. Data and analytical versions

| Field | Approved value |
|---|---|
| Canonical dataset | Infocreon Aether Pulse Canonical Intelligence Dataset |
| Data version | phase3-v1.1 |
| Dataset type | Controlled synthetic OpenAQ-shaped sample |
| Source records | 192 |
| Canonical records | 96 |
| City coverage | 8 cities |
| Pollutant coverage | 4 pollutants |
| Retained timestamps | 3 per city/pollutant |
| Approved analytical track | Track A — Comparative |
| Method version | track-a-comparative-v1.0.0 |
| Expected intelligence results | 32 |
| Output contract version | No separate version declared; governed by data_version phase3-v1.1 and method_version track-a-comparative-v1.0.0 |

## 3. Application routes and deployment

| Component | Route / target |
|---|---|
| Operational dashboard | / |
| Data Intelligence page | /data-intelligence |
| Assistant page | /assistant |
| Intelligence API | /api/intelligence/results |
| Assistant API | /api/assistant/ask |
| Assistant health | /api/assistant/health |
| Frontend deployment | https://poc32-phase3-frontend.onrender.com |
| Backend deployment | https://poc32-phase3-intelligence-api.onrender.com |
| Data Intelligence validation mode | Local validation; public deployment suspended |

## 4. Assistant configuration

| Field | Value |
|---|---|
| Assistant mode | Deterministic evidence grounding with optional Gemini explanation |
| Gemini model | gemini-3.5-flash-lite |
| Public Assistant validation | Previously validated on Render |
| Latest Assistant Selenium result | 4/4 PASS |
| Latest local Python suite | 62 passed |
| Local Gemini mode during latest suite | Disabled; deterministic fallback tested |
| Credential handling | Replacement key stored privately; never include credentials in release artifacts |

## 5. Validation and certification

| Field | Status |
|---|---|
| Canonical data validation | PASS — 96 rows, 20 columns |
| Analytical validation | PASS — 24 checks |
| Data Intelligence local UAT | PASS — 7/7 |
| Operational regression | PASS — 4/4 |
| Assistant Python tests | PASS — 62 tests |
| Assistant Selenium | PASS — 4/4 |
| Clean-clone validation | PENDING |
| Full application build | PASS — frontend build and Docker Compose image builds verified |
| Assistant automated test report | PASS — 62 Assistant Python tests; see report for test scope |
| Deployment validation report | PARTIAL — public Assistant validated; public Data Intelligence suspended; WorldPop limitation documented |
| Evidence pack | IN PROGRESS — remaining clean-clone and final release evidence pending |
| Final Repomix | PENDING |
| Certified release tag | PENDING |

## 6. Limitations and release boundaries

- The canonical dataset is controlled synthetic data, not live air-quality measurements.
- Results are descriptive and comparative; they are not predictions, regulatory assessments, or health-risk determinations.
- Public Data Intelligence deployment is suspended. Its latest validation was performed locally.
- Public Assistant validation and local deterministic-fallback validation are separate test contexts.
- Gemini availability depends on private runtime configuration and external service availability.

## 7. Final certification record

- Reviewer: PENDING
- Certification date: PENDING
- Final certified commit: PENDING
- Final certified tag: PENDING
- Final result: PENDING

This manifest is a working release record. It does not certify Phase 3 until all mandatory guide validations, reports, evidence, final commit, and tag have been completed.
