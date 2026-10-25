# Aether Pulse — Architecture

## Project

- **PoC:** 32
- **Name:** Air Quality Heatmap
- **Dashboard:** Aether Pulse
- **Rail:** Data & Intelligence
- **Assistant Mode:** Mode B — Deterministic Retrieval + LLM Explanation

---

## 1. Architecture Overview

Aether Pulse is a production-style air-quality intelligence dashboard that transforms environmental data into spatial, analytical, and human-readable intelligence.

The system follows a layered architecture:

1. Data & Intelligence Layer
2. FastAPI Backend Layer
3. Grounded Data Assistant Layer
4. Next.js Visualization Layer

The Grounded Data Assistant operates within the backend. It uses deterministic retrieval to identify supported evidence and an LLM to explain that evidence in natural language.

The LLM does not replace the deterministic retrieval system, calculate authoritative results, or independently determine which evidence is valid.

### High-Level Architecture

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
   Air Quality    Exposure     Comparison
    Service       Scoring       Service
        │             │             │
        └─────────────┼─────────────┘
                      │
             Processed Data
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
  Dashboard APIs             Grounded Assistant
                                    │
                            Deterministic Retrieval
                                    │
                                    ▼
                             Evidence Package
                                    │
                                    ▼
                            Gemini Explanation
                                    │
                                    ▼
                          Grounding Validation
                                    │
                                    ▼
                          Validated Explanation
                                    │
                                    ▼
                              JSON Response
                                    │
                                    ▼
                              Next.js UI
                                    │
                      ┌─────────────┼─────────────┐
                      │             │             │
                      ▼             ▼             ▼
                     Map          Charts     Intelligence
                                                Panel
```

The dashboard's primary data-processing and evidence-retrieval responsibilities remain in the backend.

---

## 2. Frontend Architecture

### Technology

- Next.js 14+
- App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Leaflet / React Leaflet
- Recharts

### Responsibilities

The frontend is responsible for:

- Dashboard presentation
- Interactive map
- Pollutant selection
- City comparison
- Search and filtering
- Time-series visualization
- Exposure-score presentation
- Intelligence explanations
- Grounded Data Assistant interaction
- Displaying evidence and explanation status
- Downloading sample data
- Loading, error, and fallback states

The frontend does not perform primary data processing, deterministic evidence retrieval, or LLM grounding validation.

### Assistant Presentation

The frontend submits user questions to the FastAPI assistant endpoint.

It displays:

- The assistant's response
- Relevant evidence
- Explanation availability
- Grounding or validation status
- Appropriate unavailable or error states

The frontend must not treat an LLM-generated explanation as validated merely because the API returned a successful HTTP response.

---

## 3. Backend Architecture

### Technology

- Python
- FastAPI
- Pandas
- GeoPandas where required

### Responsibilities

The backend is responsible for:

- Data ingestion
- Data normalization
- Air-quality processing
- Exposure scoring
- City comparison
- GeoJSON generation
- API responses
- Fallback handling
- Deterministic assistant retrieval
- Evidence package generation
- LLM explanation generation
- Grounding validation
- Assistant response construction

### Primary APIs

```text
GET  /health

GET  /api/air-quality?pollutant=pm25

POST /api/assistant/ask
```

The assistant endpoint accepts a user question and returns a structured response containing the deterministic result, supporting evidence, validation information, and explanation status.

---

## 4. Data Sources

### OpenAQ

Primary source for air-quality observations.

Used for:

- Pollutant measurements
- Monitoring locations
- Time-series observations
- Location metadata

### WorldPop

Population data source.

Used for:

- Population context
- Exposure estimation
- Population-weighted intelligence

External data must be normalized before being used by the backend services.

---

## 5. Data Adapter Pattern

External sources are accessed through dedicated adapters.

```text
backend/
└── app/
    └── adapters/
        ├── openaq.py
        └── worldpop.py
```

Adapters isolate external API logic from business logic.

This allows the dashboard to continue operating if an external provider changes its API.

The assistant must use approved backend evidence rather than independently retrieving information from external sources.

---

## 6. Backend Services

Business logic is separated from external data access.

```text
backend/app/services/

air_quality.py
comparison.py
exposure.py
```

### Air Quality Service

Responsible for:

- Pollutant processing
- Observation normalization
- Map-ready records

### Exposure Service

Responsible for:

- Population context
- Exposure scoring
- Risk-oriented insights

### Comparison Service

Responsible for:

- City comparison
- Regional averages
- Relative differences

### Grounded Assistant Service

The assistant service is responsible for:

- Supported intent identification
- Deterministic retrieval
- Evidence validation
- Evidence package construction
- Gemini explanation generation
- Generated explanation validation
- Structured response construction
- Graceful handling of unavailable explanations

The assistant service must preserve the separation between deterministic results and generated explanations.

---

## 7. Mode B — Deterministic Retrieval + LLM Explanation

### 7.1 Purpose

Mode B combines deterministic data retrieval with natural-language explanation.

The deterministic system determines what the application can support.

Gemini explains the supported evidence in a readable format.

The LLM is an explanatory component, not the source of truth.

### 7.2 Processing Flow

```text
User Question
      │
      ▼
Intent Identification
      │
      ▼
Supported Intent?
      │
      ├── No ──► Unsupported Response
      │
      ▼
Deterministic Retrieval
      │
      ▼
Evidence Validation
      │
      ▼
Evidence Package
      │
      ▼
Gemini Explanation
      │
      ▼
Generated Output Validation
      │
      ├── Invalid ──► Explanation Unavailable
      │
      ▼
Validated Explanation
      │
      ▼
Structured API Response
```

### 7.3 Deterministic Retrieval

The deterministic retrieval system:

- Identifies supported question categories
- Extracts supported parameters
- Retrieves approved records
- Produces deterministic results
- Validates the retrieved evidence
- Constructs a structured evidence package

The retrieval system must not depend on Gemini to determine whether a result exists or whether the evidence is valid.

### 7.4 Evidence Package

The evidence package is the authoritative input to the explanation stage.

Conceptually:

```json
{
  "version": "grounded-evidence-v1.0.0",
  "intent": "compare_cities",
  "parameters": {
    "city_a": "delhi",
    "city_b": "mumbai",
    "pollutant": "no2"
  },
  "records": [],
  "limitations": []
}
```

The actual package must follow the backend's defined schema.

The evidence package must contain only retrieved and validated information.

### 7.5 Gemini Explanation

Gemini receives the validated evidence package and generates a concise natural-language explanation.

The model is configured through environment variables.

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
```

The model name may be changed through configuration without changing the deterministic retrieval architecture.

The LLM must:

- Use only information contained in the evidence package
- Preserve the exact supported result values
- Preserve supported ranks and categories
- Avoid unsupported calculations
- Avoid introducing new measurements
- Avoid unsupported causal or predictive claims
- Avoid presenting synthetic data as verified real-world observations
- Respect the limitations contained in the evidence package

The LLM must not independently calculate authoritative exposure scores, pollutant measurements, or comparative results.

### 7.6 Grounding Validation

Generated explanations are validated before being returned as available explanations.

Validation must check that:

- Required response fields are present
- Generated numerical values are supported by evidence
- Unsupported numerical claims are rejected
- Generated content follows the supported response contract
- Invalid explanations are not represented as validated output

A successful Gemini generation does not automatically imply a valid grounded explanation.

### 7.7 Failure Handling

The deterministic result remains authoritative when Gemini is unavailable.

Possible explanation states include:

- `AVAILABLE` — a generated explanation passed validation
- `UNAVAILABLE` — an explanation could not be generated or validated

Unavailable conditions may include:

- Missing Gemini API key
- Gemini API failure
- Empty or incomplete evidence
- Invalid generated output
- Grounding validation failure

The application must not fabricate an explanation when generation fails.

The API should preserve the deterministic response and communicate that the explanation is unavailable.

---

## 8. Grounded Assistant Response Contract

The assistant endpoint is:

```text
POST /api/assistant/ask
```

The response is a structured JSON object.

Conceptually:

```json
{
  "status": "ok",
  "answer": "Grounded explanation",
  "evidence": [],
  "validation": {
    "valid": true,
    "errors": []
  },
  "details": {},
  "evidence_package": {},
  "grounding": {
    "mode": "deterministic_retrieval_llm_explanation",
    "llm_used": true,
    "generated_findings": [],
    "source": "gemini"
  }
}
```

This example illustrates the response structure. The implementation's Pydantic response model remains authoritative for exact field names, types, and allowed values.

### Contract Principles

1. Deterministic retrieval produces the authoritative result.
2. The evidence package records the information supporting that result.
3. Gemini generates an explanation from the evidence package.
4. Generated content is validated before being marked available.
5. Unsupported claims must not be presented as grounded findings.
6. LLM failure must not invalidate an otherwise valid deterministic result.
7. The response must communicate explanation availability and validation status.
8. Synthetic evidence must retain its synthetic-data designation and limitations.

---

## 9. Dashboard API Response

The map uses GeoJSON-compatible data.

Each feature represents an air-quality observation or location.

Conceptually:

```json
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
```

The example represents the dashboard data contract and is not a guarantee that these values are currently available from a live provider.

---

## 10. Fallback Architecture

The application must remain usable when a live data source fails.

```text
             Live API
                │
          ┌─────┴─────┐
          │           │
        Success      Error
          │           │
          ▼           ▼
       Live Data   mock_data.json
          │           │
          └─────┬─────┘
                ▼
          FastAPI Response
                │
                ▼
            Next.js UI
```

Fallback data must be clearly identified in the interface.

The user should never mistake synthetic fallback data for live observations.

### Assistant Fallback

The assistant has a separate explanation fallback path.

```text
Validated Evidence
       │
       ▼
Gemini Available?
       │
  ┌────┴─────┐
  │          │
 Yes         No
  │          │
  ▼          ▼
Generate   Preserve
Explanation Deterministic
  │        Result
  ▼          │
Validate    ▼
  │      Explanation
  ▼      Unavailable
Return       │
Response     ▼
          Return Response
```

The assistant must not replace a failed LLM explanation with fabricated content.

The deterministic result and evidence remain available when possible.

---

## 11. Frontend Layout

The primary dashboard layout follows the Real Rails requirement.

```text
┌──────────────────────────────────────────────────────────────┐
│                       AETHER PULSE                           │
├───────────────────────────────────────┬──────────────────────┤
│                                       │                      │
│                                       │  Intelligence        │
│                                       │  Panel               │
│                                       │                      │
│                                       │  • Key Metric        │
│                                       │  • Why It Matters    │
│                                       │  • Who Controls Rail │
│                                       │  • Filters           │
│                                       │  • Download Data     │
│                                       │  • Grounded Assistant│
│                                       │                      │
│            AIR QUALITY MAP            │                      │
│                                       │                      │
│               70%                     │        30%           │
│                                       │                      │
├───────────────────────────────────────┴──────────────────────┤
│                    Supporting Analytics                      │
└──────────────────────────────────────────────────────────────┘
```

The main visualization area occupies approximately 70% of the dashboard.

The intelligence panel occupies approximately 30%.

The panel must communicate meaning rather than simply displaying raw data.

---

## 12. Intelligence Panel

### A — Primary Intelligence

Examples:

- Current PM2.5 level
- Exposure score
- Locations monitored
- Population affected

### B — Why This Matters

Explains the public-interest significance of the data.

### C — Who Controls the Rail

Explains the institutions and infrastructure involved in collecting and operating air-quality intelligence.

### D — Controls

Includes:

- Pollutant selector
- City search
- City comparison
- Relevant filters
- Interactive tooltips

### E — Sample Data

Allows users to download representative data.

### F — Grounded Data Assistant

Provides evidence-based answers to supported questions.

The assistant:

- Accepts supported natural-language questions
- Displays deterministic evidence
- Displays a generated explanation when available
- Communicates explanation validation status
- Handles unsupported questions
- Communicates unavailable explanations
- Preserves synthetic-data limitations

---

## 13. Visual System

Aether Pulse follows the Real Rails visual identity.

### Colors

- Background: `#030712`
- Surface: `#0B1117`
- Primary Accent: `#38BDF8`
- Secondary Accent: `#818CF8`
- Border: `#1F2937`

### Typography

Preferred:

- Inter
- Geist Sans

### Visual Style

- High-end fintech terminal
- Real-time intelligence aesthetic
- Dark interface
- Subtle glassmorphism
- Minimal borders
- Cyan active-state glow
- Dense but readable information hierarchy

Assistant response status and evidence should follow the same visual system.

---

## 14. Geospatial Rules

Geographical coordinates must not be manually calculated with custom SVG or mathematical projection logic.

Use professional geospatial/map libraries.

Preferred implementation:

- Leaflet / React Leaflet
- GeoJSON
- GeoPandas
- Turf.js where spatial calculations are required

---

## 15. Interaction Flow

### Dashboard

```text
User Selects Pollutant
        │
        ▼
Next.js Requests API
        │
        ▼
FastAPI Processes Data
        │
        ▼
GeoJSON + Intelligence Data
        │
        ▼
Map Updates
        │
        ├──► Charts Update
        ├──► Exposure Score Updates
        └──► Sidebar Insights Update
```

### Grounded Assistant

```text
User Enters Question
        │
        ▼
Next.js Submits Request
        │
        ▼
FastAPI Assistant Endpoint
        │
        ▼
Deterministic Retrieval
        │
        ▼
Evidence Package
        │
        ▼
Gemini Explanation
        │
        ▼
Grounding Validation
        │
        ▼
Structured Response
        │
        ▼
Assistant UI Updates
```

The page should not require a full refresh when filters change or when a question is submitted.

---

## 16. Error Handling

The dashboard supports three primary states.

### Loading

Clearly communicate that data is being retrieved.

### Live Data

Indicate that the dashboard is using live source data.

### Fallback Data

Indicate that live data was unavailable and local fallback data is being displayed.

Users should also have a retry mechanism when live data fails.

### Assistant States

The assistant must distinguish between:

- Supported question
- Unsupported question
- Evidence available
- Evidence unavailable
- Explanation available
- Explanation unavailable
- Explanation validated
- Explanation rejected by validation

The UI must not display an unavailable or invalid explanation as a successful grounded finding.

---

## 17. Security

API credentials must never be hardcoded.

Use environment variables:

```text
.env
.env.example
```

External API keys belong only in environment configuration.

The Gemini API key must remain in the backend environment and must never be exposed to the Next.js client.

The assistant must not accept arbitrary model instructions that override evidence-grounding requirements.

---

## 18. Repository Structure

The repository includes the dashboard, backend services, assistant implementation, tests, and supporting documentation.

```text
POC-32-AirQualityHeatmap/
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
│   │   │   ├── exposure.py
│   │   │   └── assistant/
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
├── tests/
│   └── assistant/
│
├── selenium-test/
│
└── README.md
```

The assistant directory is illustrative. The actual repository structure and implementation paths remain authoritative.

---

## 19. Validation and Acceptance

Mode B must be validated at multiple levels.

### Backend Tests

Automated tests verify:

- Supported intent identification
- Deterministic retrieval
- Evidence validation
- Evidence package structure
- Gemini explanation behavior
- Unsupported numerical claim rejection
- Missing API key behavior
- Gemini failure handling
- Invalid explanation handling
- Response contract compliance

### API Validation

The assistant endpoint must be verified using a supported question.

The response must preserve:

- Deterministic evidence
- Evidence package
- Validation result
- Explanation status
- Synthetic-data limitations

### Selenium / UAT

Browser tests verify:

- Assistant UI loads
- User can enter and submit a question
- Loading state is visible
- Response is displayed
- Evidence is accessible
- Explanation status is represented correctly
- Unsupported questions are handled
- Error and unavailable states are usable

Test results must be recorded with their actual execution status. A passing backend test suite must not be represented as a passing Selenium test.

---

## 20. Architecture Principle

Aether Pulse follows one core principle:

**Turn environmental data into actionable intelligence.**

The map shows where.

The charts show how conditions change.

The exposure score explains who may be affected.

The intelligence panel explains why the information matters.

The Grounded Data Assistant explains what the validated evidence supports.

Deterministic retrieval establishes what the system knows.

The LLM explains that evidence without replacing or expanding it.

The architecture therefore connects raw data, spatial visualization, analytics, and grounded human-readable intelligence into one coherent Data & Intelligence experience.