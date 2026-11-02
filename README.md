# Aether Pulse — Air Quality Heatmap

## Real-Time Air Intelligence Dashboard

Aether Pulse is a production-style demonstration for the **Real Rails Intelligence Library**, focused on the **Data & Intelligence** rail.

It combines air-quality observations, population context, spatial visualization, exposure scoring, and city comparison into an interactive intelligence dashboard.

---

## Project

| Item | Details |
|---|---|
| PoC | 32 |
| Project | Air Quality Heatmap |
| Dashboard | Aether Pulse |
| Rail | Data & Intelligence |
| Primary Air Quality Source | OpenAQ |
| Population Source | WorldPop |
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Backend | Python FastAPI + Pandas |
| Map | Leaflet / React Leaflet |
| Charts | Recharts |
| Containerization | Docker + Docker Compose |

---

## What Aether Pulse Does

Aether Pulse turns air-quality data into understandable intelligence.

### Core capabilities

- Interactive city air-quality map
- Pollutant selection
- City search
- City comparison
- Time-series visualization
- Exposure scoring
- Population context
- Intelligence insights
- Live-data status
- Fallback-data handling
- Downloadable sample data

The dashboard is designed for three audiences:

- **Everyday viewers** — understand what the data means
- **Builders** — understand how the data and application work
- **Allocators** — understand where environmental intelligence and exposure matter

---

# Architecture

The application follows a three-layer architecture.

```text
OpenAQ ───────────────┐
                      │
WorldPop ─────────────┤
                      ▼
               Data Adapters
                      │
                      ▼
              FastAPI Backend
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Air Quality     Exposure     Comparison
     Service        Scoring       Service
        │             │             │
        └─────────────┼─────────────┘
                      │
                JSON / GeoJSON
                      │
                      ▼
              Next.js Frontend
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
       Map          Charts      Intelligence
                                  Sidebar

---

## Phase 3 — Data Intelligence

Aether Pulse Phase 3 extends the Operational View with a canonical synthetic dataset, analytical processing, comparative intelligence, and an evidence-grounded Assistant.

- Dataset version: `phase3-v1.1`
- Canonical records: 96 across 8 cities and 4 pollutants.
- Approved method: `track-a-comparative-v1.0.0`.
- Comparative intelligence results: 32.
- Predictive Intelligence is not approved for the current dataset.

### Local services

- Operational frontend: `http://localhost:3002`
- Data Intelligence: `http://localhost:3002/data-intelligence`
- Assistant: `http://localhost:3002/assistant`
- Operational backend: port `8003`
- Data Intelligence API: port `8000`

Start services with `docker compose up -d --build` and inspect them with `docker compose ps`.

### Validation

See `docs/` and `final-evidence/` for data, analytical, API contract, operational, Assistant, automated test, Selenium, UAT, and deployment reports.

### Known limitations

- All Phase 3 published observations are controlled synthetic data, not verified real-world measurements.
- WorldPop population lookup currently returns HTTP 502 due to an upstream response-format issue.
- Public Data Intelligence deployment is suspended; local validation passed, but public validation was not performed.
- The latest local Assistant Python tests used deterministic fallback with Gemini disabled. Live Gemini generation was verified separately.
- No fresh Render redeployment is claimed.

**Release status: PHASE 3 FINAL CHANGES REQUIRED — certification pending.**
