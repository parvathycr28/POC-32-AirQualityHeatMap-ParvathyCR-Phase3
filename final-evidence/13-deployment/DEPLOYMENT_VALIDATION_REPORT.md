# Phase 3 Deployment Validation Report

## Deployment targets

- Frontend: https://poc32-phase3-frontend.onrender.com
- Backend: https://poc32-phase3-intelligence-api.onrender.com
- Hosting platform: Render

## Deployment scope

The Operational View and Assistant have public Render deployment targets. The public Assistant Selenium validation was run on 2 November 2026 and passed 4/4 checks. It covered page loading, supported comparison evidence, rejection of unsupported prediction requests, and responsive layouts at 1440, 768, 390, and 320 pixels.

The public Data Intelligence deployment is intentionally suspended. Its latest validation was performed locally using Docker Compose, with API HTTP 200, 32 results, correct data and method versions, frontend HTTP 200, and browser checks 7/7 passed. No public Data Intelligence UAT or deployment PASS is claimed.

## Environment and security

Runtime configuration is supplied through environment variables. Secret values are not recorded in this report or evidence pack. The exposed Gemini key was revoked and replaced privately; the local environment file is excluded from Git.

## Known deployment limitations

- The WorldPop population endpoint currently returns HTTP 502 because of an upstream response-format issue.
- Public Data Intelligence deployment remains suspended.
- The latest Assistant Python test run used deterministic fallback with Gemini disabled; live Gemini generation was verified in an earlier separate test.
- No fresh Render redeployment is claimed by this report.

## Deployment assessment

Public Assistant validation: PASS for the recorded Selenium scope. Local Data Intelligence validation: PASS for the recorded local scope. Public Data Intelligence: NOT DEPLOYED / NOT TESTED. Overall deployment status: PARTIAL, WITH DOCUMENTED LIMITATIONS; final release certification remains pending.
