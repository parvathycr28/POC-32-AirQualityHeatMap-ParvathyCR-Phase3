# Build and Environment Validation — Phase 3

## 1. Runtime environment

| Component | Version |
|---|---|
| Local Python | 3.10.11 |
| Docker Python image | python:3.12-slim |
| Local Node.js | 24.21.0 |
| Local npm | 11.19.0 |
| Docker Node.js image | node:22-alpine |
| Next.js | 16.3.2 |
| Docker | 29.8.1 |
| Docker Compose | 5.5.1 |

## 2. Frontend production build

Command: `cd frontend && npm run build`

Result: PASS

TypeScript compilation passed. Static page generation completed (6/6). Routes generated: `/`, `/assistant`, `/data-intelligence`, and `/_not-found`.

## 3. Docker validation

Commands:
- `docker compose config --quiet`
- `docker compose build`
- `docker compose up -d`
- `docker compose up -d --no-deps --force-recreate frontend`

Result: All three service images built successfully. All three containers started. The frontend was recreated from the newly built image.

## 4. Container and route validation

Frontend:
- `/` — HTTP 200
- `/data-intelligence` — HTTP 200
- `/assistant` — HTTP 200
- Next.js 16.3.2 startup completed; ready in 346 ms.

Operational backend:
- `/` — HTTP 200
- `/api/air-quality?pollutant=pm25` — HTTP 200; GeoJSON returned.
- `/api/assistant/health` — HTTP 200.
- `/health` — HTTP 404; this route is not registered.

Data Intelligence backend:
- `/api/assistant/health` — HTTP 200.
- `/api/intelligence/results` — 32 results; metadata count 32; data version `phase3-v1.1`; method version `track-a-comparative-v1.0.0`.

## 5. External data limitation

The operational population endpoint returned HTTP 502. Backend logs show that the external WorldPop service returned PHP deprecation output instead of valid JSON, causing a JSON decoding error. This is recorded as an upstream dependency limitation and not as a successful population API check.

## 6. Environment and security

Docker Compose configuration validation completed. Environment files are used for runtime configuration. Secret values are intentionally excluded from this report and evidence package.

## 7. Runtime consistency

Local Python and Node.js versions differ from the Python and Node.js versions used in the Docker images. Container builds and startup succeeded; clean-clone and runtime compatibility checks remain part of the release process.

## 8. Conclusion

Frontend production build, Docker image builds, container startup, frontend routes, and the tested backend routes passed. The WorldPop population endpoint remains an unresolved external-data limitation. This report does not certify overall Phase 3 release completion.
