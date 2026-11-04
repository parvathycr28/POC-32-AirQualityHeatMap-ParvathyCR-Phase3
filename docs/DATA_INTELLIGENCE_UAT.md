# Data Intelligence — User Acceptance Testing (UAT)

## 1. Objective

Verify that the Phase 3 Data Intelligence page displays approved comparative intelligence results, validates the results contract before rendering, provides filtering and search, exposes methodology and data provenance, and preserves the existing Operational View functionality.

## 2. Test environment and scope

**Project:** Aether Pulse — Air Quality Heatmap
**Phase:** Phase 3 — Data Science and Decision Intelligence
**Feature branch:** `feature/data-intelligence-page`
**Release branch:** phase3-release-candidate

### Local application URLs

* Operational View: `http://localhost:3002`
* Data Intelligence page: `http://localhost:3002/data-intelligence`
* Intelligence results API: `http://localhost:8000/api/intelligence/results`
* Intelligence summary API: `http://localhost:8000/api/intelligence/summary`

### Approved analytical output

* Canonical dataset: 96 records and 20 columns
* Data version: `phase3-v1.1`
* Analytical method: `track-a-comparative-v1.0.0`
* Published intelligence results: 32
* Expected city coverage: 8 cities
* Expected pollutant coverage: 4 pollutants
* Data type: Controlled synthetic air-quality data
* Primary analytical track: Track A — Comparative Intelligence

### Test scope

This UAT covers the local application, intelligence API contracts, published analytical output, page completeness, and regression of the existing Operational View. Public deployment verification is recorded separately and is not inferred from successful local tests.

## 3. Test cases

| ID     | Test                                        | Expected result                                                                                      | Actual result                                                                                                                            | Status |
| ------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| UAT-01 | Open the Data Intelligence page             | Page loads without a fatal error                                                                     | Local Data Intelligence page opened successfully and displayed the results                                                               | PASS   |
| UAT-02 | Request the intelligence APIs               | Results and summary endpoints return successful responses                                            | Both local endpoints returned HTTP 200                                                                                                   | PASS   |
| UAT-03 | Check result count and versions             | Result count matches the approved summary; data and method versions are consistent                   | 32 results; data version `phase3-v1.1`; method version `track-a-comparative-v1.0.0`                                                      | PASS   |
| UAT-04 | Filter by pollutant                         | Results match the selected pollutant                                                                 | Pollutant filter behaved as expected during testing                                                                                      | PASS   |
| UAT-05 | Filter by city                              | Results match the selected city                                                                      | City filter behaved as expected during testing                                                                                           | PASS   |
| UAT-06 | Search results                              | Search narrows results correctly                                                                     | Search behaved as expected during testing                                                                                                | PASS   |
| UAT-07 | Check loading behavior                      | Loading state appears while the request is pending                                                   | Loading state passed the reported test                                                                                                   | PASS   |
| UAT-08 | Check API error behavior                    | Error message and Retry action work                                                                  | Error state and Retry recovery passed the reported test                                                                                  | PASS   |
| UAT-09 | Check data-quality notice                   | Synthetic-data and conditional-quality notices are visible                                           | Synthetic-data warning was visible on the page                                                                                           | PASS   |
| UAT-10 | Open the existing Operational View          | Existing dashboard loads                                                                             | Operational dashboard opened successfully during local regression testing                                                                | PASS   |
| UAT-11 | Check the existing map and data             | Map and existing data requests continue to work                                                      | Map and air-quality data loaded after the API configuration correction                                                                   | PASS   |
| UAT-12 | Check analytical contract and export        | Required output contract, versions, counts, evidence, and approved results pass validation           | Analytical validation reported 24 successful checks, no failed checks, and no reported issues; export verification passed for 32 results | PASS   |
| UAT-13 | Check methodology and provenance            | Approved track, data version, method version, analytical question, and decision scope are accessible | Methodology and provenance section displayed on the local Data Intelligence page                                                         | PASS   |
| UAT-14 | Check timestamp, freshness, and limitations | Generated timestamp, freshness status, and analytical limitations are accessible                     | Timestamp, freshness information, and limitations were displayed on the local page                                                       | PASS   |
| UAT-15 | Check Operational View navigation           | A navigation link back to the Operational View is available                                          | Operational View navigation link was visible on the Data Intelligence page                                                               | PASS   |

## 4. Execution notes

The analytical validation script completed with `validation_result: PASS`, 24 successful checks, no failed checks, and no reported issues. Export verification passed for 32 records using data version `phase3-v1.1` and method version `track-a-comparative-v1.0.0`. The local results and summary API endpoints both returned HTTP 200. The Data Intelligence page displayed the published results, filters, methodology, timestamp, freshness status, limitations, and Operational View navigation link. The Operational View and map were also visually checked after the frontend API configuration was corrected.

The backend and frontend implement contract checks for required fields, data and method versions, count consistency, timestamps, unique result identifiers, quality status, synthetic-data flags, and evidence. The successful analytical validation and local rendering establish the valid-data path; a separate deliberately malformed-payload test is not claimed by this record.

## 5. Acceptance criteria

The feature is accepted for the local environment when:

1. The Data Intelligence page opens and retrieves both approved API responses.
2. The frontend validates the summary and results contracts before displaying approved results.
3. Result counts, data versions, method versions, timestamps, and required result fields are consistent.
4. City and pollutant filters and text search behave as expected.
5. Loading and API error/retry states behave as expected.
6. Synthetic-data warnings and analytical limitations are visible.
7. Methodology, generated timestamp, freshness status, and provenance are accessible.
8. Navigation back to the existing Operational View is available.
9. The existing Operational dashboard, map, and data retrieval remain operational.
10. Analytical validation and export verification pass for the approved output.

## 6. Final result

**Local Data Intelligence UAT:** PASS

* Confirmed passing test cases: 15
* Confirmed failing test cases: 0
* Pending local UAT cases: 0
* Analytical validation: PASS
* Export verification: PASS
* Local results API: HTTP 200
* Local summary API: HTTP 200
* Local page rendering: PASS

**Public deployment status:** PASS — separately verified on 4 November 2026. The feature preview and the production Data Intelligence page were tested after the feature branch was merged into `phase3-release-candidate`. See Section 9 for deployment details and verification results.

**Overall local acceptance:** PASS, based on the recorded local test results.

## 7. Final certification re-verification — 2 November 2026

A fresh local verification was performed after regenerating the approved analytical outputs and rebuilding the Data Intelligence backend container.

**Execution environment:**
- Frontend: `http://localhost:3002/data-intelligence`
- Results API: `http://localhost:8000/api/intelligence/results`
- Backend container: `infocreon-data-intelligence-backend`
- Data Intelligence public deployment: Suspended; public availability was not tested.
- UAT mode: Local application and local API.

**API verification:**
- HTTP response: Successful
- Data version: `phase3-v1.1`
- Method version: `track-a-comparative-v1.0.0`
- Top-level count: 32
- Metadata count: 32
- Actual results array length: 32
- Validation result: `PASS`
- Generated timestamp: `2026-11-02T10:45:28.724712+00:00`
- Freshness status: `CURRENT`
- Freshness age at verification: 1.13 hours

The API uses `count` at the top level and `metadata.count`; `metadata.result_count` is not part of the response contract.

**Latest frontend verification:**

| Check | Actual result | Status |
|---|---|---|
| Page loads without an error | Passed | PASS |
| All 32 analytical results displayed | 32 published results | PASS |
| Data version | `phase3-v1.1` | PASS |
| Method version | `track-a-comparative-v1.0.0` | PASS |
| Freshness indicator | `CURRENT` | PASS |
| Search, filters, and sorting | Passed during local verification | PASS |
| Contract validation and approved-result display | Validation `PASS`; results displayed | PASS |

The screenshot evidence confirms the published result count, eight-city coverage, four-pollutant coverage, conditional quality status, approved analytical track, versions, generation timestamp, current freshness, and synthetic-data decision limitations.

**Container refresh:** The Data Intelligence backend image was rebuilt from the current repository outputs and its container was recreated. The container's bundled summary timestamp matches the regenerated local analytical summary.

**Latest re-verification result:** 7/7 checks passed; no reported failures.

## 8. Updated acceptance status

**Local Data Intelligence certification re-verification:** PASS

**Public Data Intelligence deployment:** PASS — feature preview and production deployment verified on 4 November 2026, including 26/26 dedicated Selenium end-to-end checks. The original certification record and tag remain unchanged. See Section 9 for deployment SHAs and verification details.

**Overall Data Intelligence acceptance:** PASS for the recorded local, preview, and production checks.

## 9. Preview and production deployment verification — 4 November 2026

The Data Intelligence feature was first deployed to a separate Render preview service and verified before being merged into the release branch. Following successful preview verification, the feature branch was merged into `phase3-release-candidate` using a normal `--no-ff` merge.

**Deployment details:**

| Item | Verified value |
|---|---|
| Feature branch | `feature/data-intelligence-page` |
| Release branch | `phase3-release-candidate` |
| Merge commit | `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb` |
| Preview frontend | `https://poc32-phase3-frontend-preview.onrender.com/data-intelligence` |
| Production frontend | `https://poc32-phase3-frontend.onrender.com/data-intelligence` |
| Production frontend commit | `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb` |
| Production backend commit | `f401c625db9d75d61591cf0ffff2af1e978231c6` |
| Backend API | `https://poc32-phase3-intelligence-api.onrender.com` |

**Preview and production functional verification:**

| Check | Actual result | Status |
|---|---|---|
| Preview Data Intelligence page | Opened successfully | PASS |
| Production Data Intelligence page | Opened successfully after release deployment | PASS |
| NO2 city comparison | All 8 cities displayed | PASS |
| O3 city comparison | All 8 cities displayed | PASS |
| PM10 city comparison | All 8 cities displayed | PASS |
| PM2.5 city comparison | All 8 cities displayed | PASS |
| Pollutant filter | Worked as expected | PASS |
| City filter | Worked as expected | PASS |
| Result-specific Assistant handoff | Worked and supporting evidence was retrieved | PASS |
| Preview backend CORS preflight | HTTP 200; preview origin allowed | PASS |
| Backend Python compilation | Successful | PASS |
| Backend automated test suite | 77 tests passed | PASS |
| Dedicated preview and production Selenium E2E | 26/26 checks passed | PASS |

**Release history preservation:**

The original certification tag `phase3-v1.0.0` continues to point to the original certified commit `0a051fef8ecb2636261b1e951b22c793d3f91500`. The feature branch was merged without rewriting the original commit or tag.

**Verification scope and limitations:**

This record covers the reported preview and production page checks, chart coverage, filters, Assistant handoff, the dedicated Selenium end-to-end test (26/26 checks), CORS verification, compilation, and automated backend tests. Selenium screenshots are saved under `selenium-test/selenium_artifacts/data_intelligence/`. It does not claim a new full application regression, security, performance, or independent data-quality certification. The approved synthetic dataset and Track A methodology remain unchanged.

**Final deployment result:** Preview and production verification PASS, including 26/26 dedicated Selenium end-to-end checks, with documented limitations.
