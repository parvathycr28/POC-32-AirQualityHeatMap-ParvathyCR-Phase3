# Post-Certification Deployment Verification

**Project:** Aether Pulse — Air Quality Heatmap
**PoC:** 32
**Rail:** Data & Intelligence
**Latest verification date:** 4 November 2026
**Release branch:** `phase3-release-candidate`
**Production merge commit:** `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb`

## 1. Purpose

This report records post-certification deployment verification following the navigation, Assistant UI, and approved Data Intelligence chart updates. It supplements the original Phase 3 certification records and does not replace or modify the certified release.

## 2. Public Deployment URLs

| Application page | Public URL |
|---|---|
| Main Air Quality Dashboard | https://poc32-phase3-frontend.onrender.com/ |
| Data Intelligence | https://poc32-phase3-frontend.onrender.com/data-intelligence |
| Grounded Assistant | https://poc32-phase3-frontend.onrender.com/assistant |
| Data Intelligence preview | https://poc32-phase3-frontend-preview.onrender.com/data-intelligence |
| Backend API | https://poc32-phase3-intelligence-api.onrender.com |

## 3. Deployment and Version Details

| Deployment item | Verified value |
|---|---|
| Production frontend branch | `phase3-release-candidate` |
| Production frontend commit | `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb` |
| Preview frontend branch | `feature/data-intelligence-page` |
| Preview frontend commit | `28b9ac796a84304ed8dfd183090bd39035d31461` |
| Backend deployment branch | `feature/data-intelligence-page` |
| Backend deployed commit | `f401c625db9d75d61591cf0ffff2af1e978231c6` |
| Approved data version | `phase3-v1.1` |
| Approved method version | `track-a-comparative-v1.0.0` |
| Approved result count | 32 |

## 4. Verification Results

### Earlier navigation verification — 3 November 2026

| Verification item | Result |
|---|---|
| Main dashboard opens | PASS |
| Data Intelligence page opens | PASS |
| Assistant page opens | PASS |
| Navigation between all three pages | PASS |
| Gemini-powered Assistant explanations | PASS |

The public deployment was manually checked after the frontend navigation update. Navigation between the Map, Data Intelligence, and Assistant pages was confirmed working. The public Assistant successfully returned Gemini-powered explanations.

### Preview and production Data Intelligence verification — 4 November 2026

| Verification item | Result |
|---|---|
| Preview Data Intelligence page opens | PASS |
| Production Data Intelligence page opens | PASS |
| NO2 chart displays eight cities | PASS |
| O3 chart displays eight cities | PASS |
| PM10 chart displays eight cities | PASS |
| PM2.5 chart displays eight cities | PASS |
| Pollutant filter | PASS |
| City filter | PASS |
| Result-specific Assistant handoff | PASS |
| Preview backend CORS preflight | PASS — HTTP 200 |
| Backend Python compilation | PASS |
| Backend automated test suite | PASS — 77 tests |
| Dedicated preview and production Selenium E2E | PASS — 26/26 checks |

The preview and production pages were manually checked and subsequently verified using a dedicated Selenium end-to-end test, which passed all 26 checks. All four pollutant charts displayed eight cities each, the pollutant and city filters worked, and the result-specific Assistant handoff navigation passed.

The backend compilation and 77-test results were verified separately. The preview CORS preflight returned HTTP 200 with the expected preview frontend origin.

## 5. Changes Verified

- Added shared primary navigation for the Map, Data Intelligence, and Assistant pages.
- Updated the Assistant page styling to align with the project's dark dashboard theme.
- Added approved city-comparison charts for the four supported pollutants.
- Preserved the existing Data Intelligence filters and result-specific Assistant handoff.
- Merged the approved feature branch into `phase3-release-candidate` without rewriting the original certification commit.

## 6. Scope and Limitations

This verification includes manual browser checks and a dedicated 26/26 Selenium end-to-end run for the preview and production Data Intelligence deployments. It is a scoped deployment verification, not a full application regression, security, performance, or real-world data-quality certification.

The project continues to use the approved controlled synthetic Phase 3 dataset and analytical scope. No new analytical track, prediction model, or dataset expansion is claimed. The deployment checks do not establish real-world measurement accuracy, regulatory compliance, health-risk assessment, or causal conclusions.

Dedicated Selenium screenshots are saved under `selenium-test/selenium_artifacts/data_intelligence/`.

## 7. Certification Preservation

The original Phase 3 certification remains associated with:

- **Certified tag:** `phase3-v1.0.0`
- **Certified commit:** `0a051fef8ecb2636261b1e951b22c793d3f91500`

This post-certification verification is documented separately. The original certified commit and tag have not been rewritten or replaced.

## 8. Conclusion

The preview and production Data Intelligence deployments were manually verified and passed all 26 dedicated Selenium end-to-end checks on 4 November 2026. The four pollutant charts, filters, and result-specific Assistant handoff worked as expected. The original Phase 3 certification remains preserved, with the deployment updates documented separately and known limitations retained.
