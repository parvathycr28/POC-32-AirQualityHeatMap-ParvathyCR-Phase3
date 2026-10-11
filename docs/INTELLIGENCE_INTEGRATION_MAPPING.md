# Intelligence Integration Mapping

## 1. Purpose

Documents how the Phase 3 Data Intelligence page connects to the existing frontend, API configuration, backend endpoint, and analytical output.

## 2. Integration map

| Component                      | File or endpoint                                 | Responsibility                                         |
| ------------------------------ | ------------------------------------------------ | ------------------------------------------------------ |
| Data Intelligence page         | `frontend/app/data-intelligence/page.tsx`        | Fetches and displays comparative intelligence results  |
| Intelligence API configuration | `NEXT_PUBLIC_DATA_INTELLIGENCE_API_URL`          | Configures the Data Intelligence backend base URL      |
| Data Intelligence endpoint     | `/api/intelligence/results`                      | Returns the approved intelligence results              |
| Data Intelligence backend      | Port `8000` locally                              | Serves the intelligence API                            |
| Intelligence output            | `data-science/outputs/intelligence_results.json` | Supplies the comparative results to the backend        |
| Air Quality API configuration  | `NEXT_PUBLIC_API_URL`                            | Configures the existing Air Quality backend connection |
| Air Quality backend            | Port `8001` inside the container                 | Serves the existing Air Quality API                    |
| Data Intelligence page route   | `/data-intelligence`                             | Provides access to the Data Intelligence interface     |

## 3. Request and response flow

1. The user opens `/data-intelligence`.
2. The frontend requests `GET /api/intelligence/results` from the configured Data Intelligence API.
3. The backend loads and returns the intelligence output.
4. The frontend validates the response and displays the results.
5. The user can filter results by pollutant, city, and search text.

## 4. Separation of existing functionality

The Data Intelligence page uses its own API configuration. The existing Air Quality dashboard continues to use the separate Air Quality API helper in `frontend/app/lib/api.ts`.

The Data Intelligence integration should not replace or unnecessarily modify the existing map, population lookup, air-quality requests, or dashboard filters.

## 5. Local configuration

* Frontend: `http://localhost:3002`
* Data Intelligence backend: `http://localhost:8000`
* Air Quality backend: `http://localhost:8003` from the host when using the Phase 3 Compose configuration.
* Data Intelligence endpoint: `http://localhost:8000/api/intelligence/results`

## 6. Integration verification

The Data Intelligence endpoint returned HTTP 200 with 32 results during local testing. The backend CORS configuration was updated to allow the Phase 3 frontend origin.

Recheck the endpoint and both frontend pages after any relevant integration changes.

## 7. Known limitations

The current intelligence results are based on synthetic data and have conditional quality status. They should not be presented as verified real-world measurements, regulatory assessments, health-risk assessments, or predictions.
