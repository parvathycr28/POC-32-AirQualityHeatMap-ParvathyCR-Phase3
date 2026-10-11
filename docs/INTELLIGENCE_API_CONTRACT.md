# Intelligence API Contract

## 1. Purpose

Defines the API connection between the Phase 3 Data Intelligence frontend and the FastAPI backend.

## 2. Endpoint

* **Method:** GET
* **Path:** `/api/intelligence/results`
* **Local URL:** `http://localhost:8000/api/intelligence/results`
* **Frontend page:** `/data-intelligence`
* **Frontend configuration:** `NEXT_PUBLIC_DATA_INTELLIGENCE_API_URL`
* **Cache behavior:** The frontend fetch uses `cache: "no-store"`.

## 3. Response structure

The response contains:

* `metadata`: data version, method version, result count, synthetic-data flag, quality status, and description.
* `count`: number of returned results.
* `results`: array of comparative intelligence records.

Each result can include an identifier, result type, group key, metric, value, unit, priority rank, finding, evidence, quality status, limitation, method and data versions, entity name, pollutant, synthetic-data flag, and optional period boundaries.

Evidence items contain a factor and a value that may be a string, number, boolean, or null.

## 4. Frontend behavior

The page validates that the response is an object containing a `results` array. It displays a loading state, an error state with a Retry button, and filtered results when data is available.

Filtering supports pollutant, city, and text search. Results are sorted by pollutant and priority rank.

## 5. CORS and local integration

The backend CORS configuration includes the configured `FRONTEND_URL` and the local origins `http://localhost:3002` and `http://127.0.0.1:3002`.

A CORS issue was resolved during local integration. The endpoint subsequently returned HTTP 200 and the frontend loaded the results.

## 6. Data limitations

The current dataset is synthetic, with `data_version` `phase3-v1.1`, `method_version` `track-a-comparative-v1.0.0`, and `quality_status` `conditional`. The results are descriptive comparisons, not verified real-world measurements, regulatory assessments, health-risk assessments, or predictions.

## 7. Verification

The endpoint was observed returning HTTP 200 and a response count of 32 during local testing. Re-run the endpoint and browser checks after relevant configuration or code changes.
