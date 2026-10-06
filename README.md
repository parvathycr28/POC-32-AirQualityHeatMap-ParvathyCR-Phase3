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