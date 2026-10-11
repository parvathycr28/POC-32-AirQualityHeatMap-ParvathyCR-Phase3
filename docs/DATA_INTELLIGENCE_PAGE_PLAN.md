# Data Intelligence Page Plan

## 1. Objective

Provide a dedicated page for displaying the approved Phase 3 comparative intelligence results while preserving the existing Air Quality dashboard.

## 2. Page route

* **Route:** `/data-intelligence`
* **Frontend file:** `frontend/app/data-intelligence/page.tsx`
* **Frontend:** Next.js with TypeScript
* **Data source:** Data Intelligence API at `/api/intelligence/results`

## 3. Page content

The page should provide:

* A clear Data Intelligence page heading.
* A notice identifying the dataset as synthetic and its quality status as conditional.
* A result count and relevant dataset/method version information when available.
* Comparative intelligence results with their metric values and units.
* Evidence, findings, limitations, and priority ranks where supplied by the API.
* Filters for pollutant, city, and text search.
* Loading and error states, including a Retry action.

## 4. Data handling

The frontend fetches results using `NEXT_PUBLIC_DATA_INTELLIGENCE_API_URL` and validates that the response contains a `results` array.

The page should display the returned API data rather than inventing or hardcoding analytical findings. Optional fields should be handled safely when they are absent.

## 5. User experience

The page should make the synthetic-data status and analytical limitations easy to understand. Filtering should help users explore results without implying that a higher priority rank proves a city or pollutant is unsafe.

Loading, empty, and error states should be understandable, and the Retry action should allow the user to attempt the request again.

## 6. Existing dashboard protection

The existing Air Quality dashboard, map, population data, and API requests must remain functional. The Data Intelligence page should remain a separate route and use its own API configuration.

## 7. Acceptance criteria

* The `/data-intelligence` route loads.
* Results are fetched from the configured endpoint.
* The result count and returned records are displayed correctly.
* Pollutant, city, and text-search filters work.
* Loading and error states are handled.
* Synthetic-data and conditional-quality notices remain visible.
* The existing Air Quality dashboard continues to work.
