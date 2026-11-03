# Clean Clone Validation Report

## Repository and Release

- Project: Aether Pulse — Air Quality Heatmap (PoC 32).
- Repository: https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3
- Release branch in the current working copy: `phase3-release-candidate`.
- Current working-copy commit: `225639eba5f53214765edd849efa9e8660bbbc67`.
- Fresh-clone validation was performed separately from the current working copy.

## Validation Environment

- Node.js: 24.21.0
- npm: 11.19.0
- Python: 3.11.9
- Docker: 29.8.1
- Docker Compose: 5.5.1
- Operating environment: Windows with Git Bash.

## Clone Command

The repository was cloned into a separate directory for clean-clone validation.

```bash
git clone https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3.git
cd POC-32-AirQualityHeatMap-ParvathyCR-Phase3
git rev-parse HEAD

## Checked-Out Commit / Tag

- Fresh-clone starting commit: `d2192f48ab08f1074d99faee4f060adf0cec09a0`.
- Current release working-copy commit: `225639eba5f53214765edd849efa9e8660bbbc67`.
- These are separate commits. The fresh-clone starting commit must not be represented as the current release commit.
- Certified release tag: pending.

## Dependency Installation

- Frontend dependency installation using `npm ci` completed successfully.
- Next.js 16.4.4, eslint-config-next 16.4.4, and ESLint 9.39.5 were used in the validated frontend environment.
- The required `unrs-resolver` install script was explicitly approved after review.
- Python dependency consistency check using `pip check` passed with no broken requirements.
- Frontend npm audit reported 16 moderate vulnerabilities, zero high vulnerabilities, and zero critical vulnerabilities. No forced breaking dependency downgrade was applied.

## Environment Configuration

- Runtime configuration was supplied through local environment settings.
- No API credentials or secret values are included in this report.
- The fresh-clone environment did not have `OPENAQ_API_KEY` configured; the fallback data path was used.
- Gemini was disabled during the latest Assistant Python test run, which exercised deterministic fallback behaviour.

## Data Validation / Regeneration

- Canonical dataset validation passed.
- Dataset version: `phase3-v1.1`.
- Canonical dataset: 96 records, 8 cities, 4 pollutants, and 3 retained timestamps per city/pollutant.
- Validated dataset dimensions: 96 rows and 20 columns.
- Reported dataset size: approximately 0.137 MB.

## Analytical Output Regeneration

- Analytical outputs were regenerated successfully.
- Approved method version: `track-a-comparative-v1.0.0`.
- Regenerated output: 32 comparative intelligence results.
- Analytical validation passed: 24 checks, zero failures.
- Recorded maximum mean error and baseline gap error: 0.0.
- Timestamp sensitivity validation covered 12 cases.

## Frontend Build

- Frontend production build completed successfully using Next.js 16.4.4.
- Compilation and TypeScript checks passed.
- Static page generation completed: 6/6.
- Validated routes included `/`, `/assistant`, and `/data-intelligence`.
- Build log: `final-evidence/02-clean-clone/frontend-build.log`.

## Backend Startup

- Operational backend started successfully in the isolated Docker Compose environment.
- Operational air-quality API returned HTTP 200.
- Assistant health endpoint returned HTTP 200.
- Data Intelligence API returned HTTP 200 with 32 results and the expected data and method versions.
- Data Intelligence response contract validation passed.
- The WorldPop population endpoint returned HTTP 502 because of an upstream response-format issue.

## Container Build

- Docker Compose configuration validation passed.
- All three application images built successfully.
- The isolated fresh-clone services started successfully.
- The frontend was exposed at port 3003, the operational backend at port 8004, and the Data Intelligence API at port 8005 for this isolated validation run.
- These isolated validation ports are distinct from the normal handover Compose ports.

## Test Execution

- Assistant Python tests: 62 passed, zero failed.
- Python dependency consistency check: passed.
- Analytical validation: 24 checks passed, zero failures.
- Assistant Selenium validation: 4/4 passed.
- Assistant Selenium covered page loading, supported evidence comparison, rejection of unsupported prediction requests, and responsive layouts.

## Route Validation

- `http://localhost:3003/`: HTTP 200.
- `http://localhost:3003/assistant`: HTTP 200.
- `http://localhost:3003/data-intelligence`: HTTP 200.
- Operational air-quality API: HTTP 200.
- Assistant health API: HTTP 200.
- Data Intelligence results API: HTTP 200.
- Fresh-clone local Data Intelligence browser validation: 5/5 checks passed.

## Assistant or Skip Validation

- Assistant validation was performed; no skip was used.
- Python test suite: 62/62 passed.
- Fresh-clone Selenium suite: 4/4 passed.
- The latest Python suite used deterministic fallback with Gemini disabled.
- Live Gemini generation was verified separately in an earlier test; it is not claimed as part of the latest fresh-clone test run.

## Undocumented Dependency Check

- Frontend dependencies were installed from the lockfile using `npm ci`.
- The required install script was reviewed and explicitly approved.
- Python dependency consistency was checked using `pip check`.
- No broken Python requirements were reported.
- The frontend audit findings are documented under Dependency Installation.

## Issues and Corrections

- Assistant browser requests initially encountered a CORS issue on the isolated frontend port. The backend CORS configuration was updated to allow the isolated frontend origin, and the backend was rebuilt and revalidated.
- The fresh-clone OpenAQ integration used its fallback path because no API key was configured.
- The WorldPop endpoint returned HTTP 502 due to an upstream response-format issue.
- Public Data Intelligence deployment remained suspended; validation was performed locally only.

## Final Result

**PASS WITH DOCUMENTED LIMITATIONS**

The fresh-clone frontend build, Docker Compose startup, canonical data validation, analytical regeneration and validation, intelligence contract validation, Assistant tests, route checks, and local Data Intelligence browser validation passed for their recorded scopes.

This report does not claim a fresh Render redeployment, public Data Intelligence deployment validation, or live OpenAQ connectivity. The documented limitations remain applicable. Final release certification is pending final documentation and evidence review, final Repomix generation, release commit, and certified tag creation.
