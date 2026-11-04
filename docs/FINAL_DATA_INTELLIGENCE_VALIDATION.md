# Intelligence API Contract

## 1. Purpose

Defines the API connection between the Phase 3 Data Intelligence frontend and the FastAPI backend.

## 2. Endpoint

* **Method:** GET
* **Path:** `/api/intelligence/results`
* **Local URL:** `http://localhost:8000/api/intelligence/results`
* **Frontend page:** `/data-intelligence`
* **Frontend configuration:** `NEXT_PUBLIC_DATA_INTELLIGENCE_API_URL`
* **Cache behavior:** The frontend fetch uses `cache: "no-store"`.

## 3. Response structure

The results endpoint returns:

metadata: data version, method version, count, validation status, synthetic-data flag, quality status, description, and freshness information.

count: number of returned results.

results: array of comparative intelligence records.

Each result must contain the mandatory contract fields, including result_id, result_type, group_key, metric_name, result_value, priority_rank, finding, evidence, quality_status, limitation, method_version, data_version, and generated_at. Track A records also include entity and pollutant information.

Evidence items must contain a non-empty factor and a value of type string, number, boolean, or null. Numeric evidence values must be finite.

## 4. Frontend contract validation and behavior

Before displaying approved intelligence, the frontend validates both the results response and the analytical summary.

Validation includes:

Required response objects, metadata, summary fields, and mandatory result fields.

Expected data version phase3-v1.1 and method version track-a-comparative-v1.0.0.

Analytical validation status PASS.

Expected result count of 32 and consistency between API count, metadata count, summary count, and actual results length.

Matching versions, generated timestamps, and approved-track metadata between results and summary.

Synthetic-data flags and supported quality-status values.

Valid numeric result values, positive integer priority ranks, and unique result IDs.

Non-empty evidence arrays with valid evidence factors and supported evidence value types.

Valid data-freshness metadata.

Both API responses are fetched without caching. The frontend accepts the data only after both responses pass validation. If a request or validation fails, the results and summary are cleared and an error is displayed rather than rendering the invalid response as approved intelligence.

The page provides loading and error states, a Retry action, and filtering by pollutant, city, and text search. Results are sorted by pollutant and priority rank.

## 5. CORS and local integration

The backend CORS configuration includes the configured `FRONTEND_URL` and the local origins `http://localhost:3002` and `http://127.0.0.1:3002`.

A CORS issue was resolved during local integration. The endpoint subsequently returned HTTP 200 and the frontend loaded the results.

## 6. Data limitations

The current dataset is synthetic, with `data_version` `phase3-v1.1`, `method_version` `track-a-comparative-v1.0.0`, and `quality_status` `conditional`. The results are descriptive comparisons, not verified real-world measurements, regulatory assessments, health-risk assessments, or predictions.

## 7. Verification

Frontend contract validation was inspected in frontend/app/data-intelligence/page.tsx. It includes version, result-count, metadata, mandatory-field, rank, duplicate-ID, evidence, and freshness checks. Both results and summary must pass validation before being stored for display.

The endpoint previously returned HTTP 200 with 32 results during local testing. Re-run API, frontend, and browser checks after relevant code or configuration changes. Record the latest test execution and environment in the Phase 3 certification evidence.


## Final Phase 3 Data Intelligence Validation

The local Data Intelligence API returned 32 results with the expected data version `phase3-v1.1` and method version `track-a-comparative-v1.0.0`. The response count, metadata count, required fields, summary, result metadata, and individual result records were checked against the strict frontend contract. The latest local Data Intelligence UAT passed 7/7 checks. The frontend displays results only after the results and summary payloads pass validation. The feature preview and production Data Intelligence page were subsequently deployed and functionally verified on 4 November 2026. Dataset values remain controlled synthetic data and are not real-world measurements or predictive outputs.

**Final status:** PASS FOR LOCAL VALIDATED SCOPE AND VERIFIED PREVIEW/PRODUCTION DEPLOYMENTS.

## Latest Re-verification — 2 November 2026

Environment: Local Docker Compose. Frontend: http://localhost:3002/data-intelligence. Data Intelligence API: http://localhost:8000.

- Results API: HTTP 200; 32 results; metadata count 32.
- Data version: phase3-v1.1; method version: track-a-comparative-v1.0.0.
- API validation: PASS; freshness: CURRENT.
- Summary API: valid, non-empty JSON with required summary fields.
- Frontend route: HTTP 200 OK.
- Browser validation: 7/7 checks passed.
- Evidence: latest-results-response.json, latest-summary-response.json, frontend-response-headers.txt.

**Latest local Data Intelligence re-verification: PASS.** This 2 November record remains a historical local Docker Compose verification. Subsequent preview and production deployment verification was completed on 4 November 2026; see the deployment verification section below.

## Deployment Verification — 4 November 2026

The Data Intelligence frontend enhancement was first deployed to a separate Render preview service. After successful preview testing, the feature branch was merged into `phase3-release-candidate` using a normal merge commit and deployed to the production frontend service.

### Deployment details

| Item | Verified value |
|---|---|
| Feature branch | `feature/data-intelligence-page` |
| Release branch | `phase3-release-candidate` |
| Merge commit | `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb` |
| Preview frontend | `https://poc32-phase3-frontend-preview.onrender.com/data-intelligence` |
| Production frontend | `https://poc32-phase3-frontend.onrender.com/data-intelligence` |
| Production frontend commit | `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb` |
| Backend API | `https://poc32-phase3-intelligence-api.onrender.com` |
| Backend deployed commit | `f401c625db9d75d61591cf0ffff2af1e978231c6` |
| Backend deployment branch | `feature/data-intelligence-page` |

### Contract and integration verification

- The preview backend CORS preflight request returned HTTP 200 and explicitly allowed the preview frontend origin.
- Backend Python compilation completed successfully.
- The backend automated test suite passed: 77 tests.
- The preview and production Data Intelligence pages opened successfully.
- All four pollutant comparison charts displayed eight cities each.
- Pollutant and city filters worked as expected.
- Result-specific Assistant handoff worked and supporting evidence was retrieved.
- Dedicated preview and production Selenium end-to-end test: 26/26 checks passed.

### Approved data and methodology

The deployment continues to use the approved output:
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`
- Published results: 32
- City coverage: 8
- Pollutant coverage: 4
- Dataset: controlled synthetic air-quality data

No new analytical track, predictive model, or dataset expansion was introduced by the chart enhancement.

### Certification preservation and limitations

The original certification tag `phase3-v1.0.0` remains attached to commit `0a051fef8ecb2636261b1e951b22c793d3f91500`. The merge did not rewrite the original certification commit or tag.

This deployment verification records the manual checks, dedicated Selenium end-to-end test (26/26 checks passed), and backend checks listed above. Selenium screenshots are saved under `selenium-test/selenium_artifacts/data_intelligence/`. This does not constitute a full application regression or a new independent security, performance, or data-quality certification.

**Deployment verification result:** PASS for the recorded preview and production checks, including 26/26 dedicated Selenium checks, with documented limitations.
