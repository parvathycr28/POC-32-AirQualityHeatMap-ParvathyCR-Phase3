# Phase 3 Final Architecture

## Project overview

Aether Pulse is an air-quality intelligence application within the Real Rails Data & Intelligence rail. Phase 3 adds a controlled canonical data foundation, analytical processing, validated comparative intelligence outputs, and an Assistant interface.

## Architecture layers

1. **Frontend:** Next.js, TypeScript, and Tailwind CSS provide the Operational View, Data Intelligence page, and Assistant interface.
2. **Operational backend:** Python FastAPI serves air-quality and population-related endpoints.
3. **Data Intelligence backend:** Python FastAPI exposes validated analytical results and summary responses.
4. **Data foundation:** Canonical CSV and published JSON provide a controlled synthetic dataset, with schema, sampling, and validation evidence.
5. **Analytical pipeline:** Python scripts generate Track A comparative intelligence outputs and validation metrics.
6. **Assistant:** The Assistant uses approved intelligence evidence and a Gemini explanation provider when configured, with deterministic fallback behavior.
7. **Deployment:** Docker Compose supports local multi-service validation. Render hosts the public Operational View and Assistant; public Data Intelligence deployment is suspended.

## Data and intelligence contract

- Dataset version: `phase3-v1.1`.
- Approved analytical method: `track-a-comparative-v1.0.0`.
- Canonical dataset: 96 records, 8 cities, 4 pollutants, and 3 timestamps per city-pollutant group.
- Generated intelligence: 32 comparative results.
- API and frontend validation enforce versions, counts, required metadata, result fields, unique identifiers, evidence, and freshness before display.

## Trust boundaries and limitations

The dataset is controlled synthetic data, not verified real-world observations. The current dataset supports descriptive comparative analysis only; predictive intelligence is not approved. The WorldPop upstream response-format issue currently causes HTTP 502. Public Data Intelligence is not deployed or publicly validated.

## Local service topology

- Frontend: port 3002.
- Operational backend: host port 8003 mapped to container port 8001.
- Data Intelligence backend: port 8000.

## Architecture status

The architecture was validated through local Docker Compose startup, API checks, frontend build and route checks, analytical validation, and recorded Assistant tests. See the release validation and evidence documents for the exact test scope and known limitations.
