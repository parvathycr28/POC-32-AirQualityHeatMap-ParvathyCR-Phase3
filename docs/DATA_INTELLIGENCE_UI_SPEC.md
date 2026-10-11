# Data Intelligence UI Specification

## 1. Purpose

Defines the required user-interface behavior for the Phase 3 Data Intelligence page.

## 2. Page identity

* **Route:** `/data-intelligence`
* **Implementation:** `frontend/app/data-intelligence/page.tsx`
* **Framework:** Next.js and TypeScript
* **Data source:** `/api/intelligence/results`

## 3. Required interface elements

The page should include:

* A clear page title and explanation of the comparative intelligence results.
* A visible notice identifying the dataset as synthetic and its quality status as conditional.
* Dataset and method version information when supplied by the API.
* A result count and the available intelligence records.
* Pollutant and city filters.
* A text-search field.
* A clear presentation of metric values, units, findings, evidence, priority ranks, and limitations when those fields are available.

## 4. Interaction behavior

### Loading

Display a loading indicator or message while the API request is in progress.

### Successful response

Display the returned results and update the visible records when filters or search terms change.

### Empty results

If no records match the current filters or search term, communicate that no matching results are available.

### API error

Display an understandable error message and provide a Retry action.

### Sorting

Keep the existing sorting behavior by pollutant and priority rank.

## 5. Data transparency and accessibility

* Keep synthetic-data and conditional-quality notices visible.
* Do not describe synthetic records as verified real-world observations.
* Do not imply that priority ranks establish regulatory compliance, health risk, or safety.
* Use understandable labels for filters and controls.
* Ensure important findings and limitations are available as text, not only through color.
* Handle optional or missing API fields without breaking the page.

## 6. Visual consistency

The Data Intelligence page should remain consistent with the existing project branding and dashboard styling. Any visual changes must preserve the page’s filters, result content, loading state, error state, and Retry behavior.

## 7. Acceptance criteria

* All required interface elements are present.
* Filters and search update the displayed records.
* Sorting remains functional.
* Loading, empty, and error states are understandable.
* Synthetic-data limitations are visible.
* The page remains usable without relying on color alone.
* The existing Air Quality dashboard is not disrupted.
