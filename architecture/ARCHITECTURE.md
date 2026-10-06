# Aether Pulse — Architecture

## Project

**PoC:** 32  
**Name:** Air Quality Heatmap  
**Dashboard:** Aether Pulse  
**Rail:** Data & Intelligence

---

## 1. Architecture Overview

Aether Pulse is a production-style air-quality intelligence dashboard.

The system follows a three-layer architecture:

1. Data & Intelligence Layer
2. FastAPI Backend Layer
3. Next.js Visualization Layer

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
   Air Quality    Exposure      Comparison
     Service       Scoring        Service
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
      Map          Charts       Intelligence
                                  Sidebar
                        
2. Frontend
Technology
Next.js 14+
App Router
TypeScript
Tailwind CSS
shadcn/ui
Leaflet / React Leaflet
Recharts
Responsibilities

The frontend is responsible for:

Dashboard presentation
Interactive map
Pollutant selection
City comparison
Search and filtering
Time-series visualization
Exposure-score presentation
Intelligence explanations
Downloading sample data
Loading/error/fallback states

The frontend does not perform the primary data processing.

3. Backend
Technology
Python
FastAPI
Pandas
GeoPandas where required
Responsibilities

The backend is responsible for:

Data ingestion
Data normalization
Air-quality processing
Exposure scoring
City comparison
GeoJSON generation
API responses
Fallback handling

Primary API:

GET /health

GET /api/air-quality?pollutant=pm25
4. Data Sources
OpenAQ

Primary source for air-quality observations.

Used for:

Pollutant measurements
Monitoring locations
Time-series observations
Location metadata
WorldPop

Population data source.

Used for:

Population context
Exposure estimation
Population-weighted intelligence
5. Data Adapter Pattern

External sources are accessed through dedicated adapters.

backend/
└── app/
    └── adapters/
        ├── openaq.py
        └── worldpop.py

Adapters isolate external API logic from business logic.

This allows the dashboard to continue operating if an external provider changes its API.

6. Services

Business logic is separated from external data access.

backend/app/services/

air_quality.py
comparison.py
exposure.py
Air Quality Service

Responsible for:

Pollutant processing
Observation normalization
Map-ready records
Exposure Service

Responsible for:

Population context
Exposure scoring
Risk-oriented insights
Comparison Service

Responsible for:

City comparison
Regional averages
Relative differences
7. API Response

The map uses GeoJSON-compatible data.

Each feature represents an air-quality observation or location.

Conceptually:

{
  "type": "FeatureCollection",
  "data_source": "OpenAQ",
  "fallback": false,
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "city": "Example City",
        "pollutant": "pm25",
        "value": 42.5,
        "unit": "µg/m³",
        "population": 1000000,
        "exposure_score": 68.4,
        "source": "OpenAQ"
      }
    }
  ]
}
8. Fallback Architecture

The application must remain usable when a live data source fails.

             Live API
                │
          ┌─────┴─────┐
          │            │
        Success       Error
          │            │
          ▼            ▼
      Live Data    mock_data.json
          │            │
          └─────┬──────┘
                ▼
          FastAPI Response
                │
                ▼
           Next.js UI

Fallback data must be clearly identified in the interface.

The user should never mistake synthetic fallback data for live observations.

9. Frontend Layout

The primary dashboard layout follows the Real Rails requirement:

┌──────────────────────────────────────────────────────────────┐
│                         AETHER PULSE                         │
├───────────────────────────────────────┬──────────────────────┤
│                                       │                      │
│                                       │  Intelligence        │
│                                       │  Sidebar             │
│                                       │                      │
│              AIR QUALITY MAP           │  • Key Metric       │
│                                       │  • Why It Matters    │
│                                       │  • Who Controls Rail │
│                                       │  • Filters           │
│                                       │  • Download Data     │
│                                       │                      │
│               70%                     │       30%            │
│                                       │                      │
├───────────────────────────────────────┴──────────────────────┤
│                    Supporting Analytics                       │
└──────────────────────────────────────────────────────────────┘

The main visualization area occupies approximately 70% of the dashboard.

The intelligence sidebar occupies 30%.

10. Intelligence Sidebar

The sidebar communicates meaning rather than simply displaying raw data.

A — Primary Intelligence

Examples:

Current PM2.5 level
Exposure score
Locations monitored
Population affected
B — Why This Matters

Explains the public-interest significance of the data.

C — Who Controls the Rail

Explains the institutions and infrastructure involved in collecting and operating air-quality intelligence.

D — Controls

Includes:

Pollutant selector
City search
City comparison
Relevant filters
Interactive tooltips
E — Sample Data

Allows users to download representative data.

11. Visual System

Aether Pulse follows the Real Rails visual identity.

Colors
Background:       #030712
Surface:          #0B1117
Primary Accent:   #38BDF8
Secondary Accent: #818CF8
Border:           #1F2937
Typography

Preferred:

Inter
Geist Sans
Visual Style
High-end fintech terminal
Real-time intelligence aesthetic
Dark interface
Subtle glassmorphism
Minimal borders
Cyan active-state glow
Dense but readable information hierarchy
12. Geospatial Rules

Geographical coordinates must not be manually calculated with custom SVG or mathematical projection logic.

Use professional geospatial/map libraries.

Preferred implementation:

Leaflet / React Leaflet
GeoJSON
GeoPandas
Turf.js where spatial calculations are required
13. Interaction Flow
User selects pollutant
        │
        ▼
Next.js requests API
        │
        ▼
FastAPI processes data
        │
        ▼
GeoJSON + intelligence data
        │
        ▼
Map updates
        │
        ├──► Charts update
        │
        ├──► Exposure score updates
        │
        └──► Sidebar insights update

The page should not require a full refresh when filters change.

14. Error Handling

The UI supports three primary states:

Loading

Clearly communicate that data is being retrieved.

Live Data

Indicate that the dashboard is using live source data.

Fallback Data

Indicate that live data was unavailable and local fallback data is being displayed.

Users should also have a retry mechanism when live data fails.

15. Security

API credentials must never be hardcoded.

Use environment variables:

.env
.env.example

External API keys belong only in environment configuration.

16. Repository Structure
POC-32-AirQualityHeatmap-ParvathyCR/
│
├── architecture/
│   └── ARCHITECTURE.md
│
├── backend/
│   ├── app/
│   │   ├── adapters/
│   │   │   ├── openaq.py
│   │   │   └── worldpop.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   ├── air_quality.py
│   │   │   ├── comparison.py
│   │   │   └── exposure.py
│   │   │
│   │   ├── utils/
│   │   │   └── fallback.py
│   │   │
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── data/
│   │   └── mock_data.json
│   │
│   ├── .env
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── air-quality-dashboard.tsx
│   │   │   ├── city-search-select.tsx
│   │   │   ├── intelligence-sidebar.tsx
│   │   │   └── leaflet-map.tsx
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts
│   │   │
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   └── package.json
│
└── README.md
17. Architecture Principle

Aether Pulse follows one core principle:

Turn environmental data into actionable intelligence.

The map shows where.

The charts show how conditions change.

The exposure score explains who may be affected.

The intelligence sidebar explains why the information matters.

The architecture therefore connects raw data, spatial visualization, analytics, and human-readable intelligence into one coherent Data & Intelligence experience.

