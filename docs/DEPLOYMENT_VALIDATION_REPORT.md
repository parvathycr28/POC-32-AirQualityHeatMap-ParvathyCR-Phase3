# Phase 3 Deployment Validation Report

## Deployment targets

- Production frontend: https://poc32-phase3-frontend.onrender.com/data-intelligence
- Backend API: https://poc32-phase3-intelligence-api.onrender.com
- Preview frontend: https://poc32-phase3-frontend-preview.onrender.com/data-intelligence
- Hosting platform: Render

## Deployment scope

The Operational View and Assistant retain their public Render deployment targets. The public Assistant Selenium validation run on 2 November 2026 passed 4/4 checks. It covered page loading, supported comparison evidence, rejection of unsupported prediction requests, and responsive layouts at 1440, 768, 390, and 320 pixels.

Data Intelligence was initially validated locally and its public deployment was suspended during the earlier validation stage. Following the approved feature-branch merge, the preview and production Data Intelligence pages were deployed and verified on 4 November 2026 through manual browser checks and a dedicated Selenium end-to-end test, which passed all 26 checks.

The production frontend is deployed from `phase3-release-candidate` at commit `ba37b75406b50ab92f62c5d5ad1f87fab13c0deb`. The backend service is deployed from `feature/data-intelligence-page` at commit `f401c625db9d75d61591cf0ffff2af1e978231c6`. The preview frontend is deployed from `feature/data-intelligence-page` at commit `28b9ac796a84304ed8dfd183090bd39035d31461`.

Preview and production browser checks confirmed that the Data Intelligence page opened, all four pollutant charts displayed eight cities each, pollutant and city filters worked, and the result-specific Assistant handoff returned supporting evidence.

The preview backend CORS preflight returned HTTP 200 with the expected preview frontend origin. Backend compilation completed successfully, and the backend test suite passed 77 tests.

## Environment and security

Runtime configuration is supplied through environment variables. Secret values are not recorded in this report or evidence pack. The exposed Gemini key was revoked and replaced privately; the local environment file is excluded from Git.

## Known deployment limitations

- The WorldPop population endpoint has previously returned HTTP 502 because of an upstream response-format issue; this deployment verification does not establish that the issue is resolved.
- The latest Assistant Python test run used deterministic fallback with Gemini disabled; live Gemini generation was verified in an earlier separate test.
- The clean-clone environment did not have `OPENAQ_API_KEY` configured; the air-quality endpoint used its fallback path, so live OpenAQ connectivity was not verified there.
- The final frontend npm audit reported 16 moderate vulnerabilities, zero high, and zero critical findings. The remaining findings are documented in the clean-clone evidence.
- The Data Intelligence dataset is controlled synthetic data. The deployment checks do not establish real-world measurement accuracy, regulatory compliance, health-risk assessment, causal conclusions, or predictive capability.
- Dedicated Selenium end-to-end verification of the preview and production Data Intelligence deployments passed all 26 checks. Screenshots are saved under `selenium-test/selenium_artifacts/data_intelligence/`.

## Deployment assessment

- Public Assistant validation: PASS for the recorded Selenium scope.
- Local Data Intelligence validation: PASS for the recorded local scope.
- Preview Data Intelligence deployment: PASS for the recorded deployment and functional checks.
- Production Data Intelligence deployment: PASS for the recorded deployment and functional checks.
- Overall deployment assessment: PASS for the recorded deployment scope, WITH DOCUMENTED LIMITATIONS. This does not constitute full security, performance, or real-world data-quality certification.

The original certification tag `phase3-v1.0.0` remains unchanged and continues to identify the original certified commit. The deployment updates are recorded separately from that certification baseline.
