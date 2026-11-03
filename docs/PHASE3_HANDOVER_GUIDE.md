# Phase 3 Handover Guide

## 1. Project

Aether Pulse — Air Quality Heatmap (PoC 32), Real Rails Data & Intelligence rail.

## 2. Local prerequisites

- Git and Git Bash.
- Python environment and project dependencies.
- Node.js and npm for the frontend.
- Docker and Docker Compose for the multi-service environment.
- Environment variables configured locally. Never commit `.env` files or expose API keys.

## 3. Start the application

From the repository root, start the local services:

```bash
docker compose up -d --build
```

Check service status:

```bash
docker compose ps
```

Local URLs:

- Operational frontend: `http://localhost:3002`
- Data Intelligence page: `http://localhost:3002/data-intelligence`
- Assistant page: `http://localhost:3002/assistant`
- Operational backend host port: `8003`
- Data Intelligence API: `http://localhost:8000`

## 4. Data and analytical validation

Run canonical data validation:

```bash
./.venv/Scripts/python.exe scripts/data_pipeline/validate_data.py
```

Regenerate analytical outputs:

```bash
./.venv/Scripts/python.exe data-science/scripts/run_analytical_track.py
```

Validate analytical outputs:

```bash
./.venv/Scripts/python.exe data-science/scripts/validate_analytical_track.py
```

## 5. Automated Assistant tests

```bash
./.venv/Scripts/python.exe -m pytest tests/assistant -v --tb=short
```

The recorded latest run passed 62 tests with Gemini disabled locally. Live Gemini generation was verified separately in an earlier test.

## 6. Important data and product limitations

- Dataset version: `phase3-v1.1`; all published observations are controlled synthetic data.
- Approved method: `track-a-comparative-v1.0.0`; 32 comparative results.
- Predictive Intelligence is not approved for this dataset.
- WorldPop population lookup currently returns HTTP 502 due to an upstream response-format issue.
- Public Data Intelligence deployment is suspended; use the locally validated page for demonstrations.
- Do not describe synthetic values as live measurements or use them for health, regulatory, or operational decisions.

## 7. Deployment and release status

The Operational View and Assistant have public Render targets. Public Assistant Selenium passed 4/4 recorded checks. No fresh Render redeployment is claimed. Public Data Intelligence deployment is suspended; its validation is local only. Fresh-clone validation has been completed with documented limitations. Final evidence review, final Repomix generation, release commit, and certified tag creation remain outstanding.

## 8. Evidence and reports

See `docs/` for release, architecture, data, analytical, operational, Assistant, UAT, and deployment reports. See `final-evidence/` for supporting test outputs, API responses, and handover evidence.
