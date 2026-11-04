# Phase 3 Release Manifest

## 1\. Project identity

|Field|Value|
|-|-|
|Project|Aether Pulse — Air Quality Heatmap|
|Project ID|PoC 32|
|Repository|https://github.com/parvathycr28/POC-32-AirQualityHeatMap-ParvathyCR-Phase3|
|Release branch|phase3-release-candidate|
|Application version|0.1.0|
|Current baseline commit|ba37b75406b50ab92f62c5d5ad1f87fab13c0deb|
|Certified commit|0a051fef8ecb2636261b1e951b22c793d3f91500|
|Certified tag|phase3-v1.0.0|

## 2\. Data and analytical versions

|Field|Approved value|
|-|-|
|Canonical dataset|Infocreon Aether Pulse Canonical Intelligence Dataset|
|Data version|phase3-v1.1|
|Dataset type|Controlled synthetic OpenAQ-shaped sample|
|Source records|192|
|Canonical records|96|
|City coverage|8 cities|
|Pollutant coverage|4 pollutants|
|Retained timestamps|3 per city/pollutant|
|Approved analytical track|Track A — Comparative|
|Method version|track-a-comparative-v1.0.0|
|Expected intelligence results|32|
|Output contract version|No separate version declared; governed by data\_version phase3-v1.1 and method\_version track-a-comparative-v1.0.0|

## 3\. Application routes and deployment

|Component|Route / target|
|-|-|
|Operational dashboard|/|
|Data Intelligence page|/data-intelligence|
|Assistant page|/assistant|
|Intelligence API|/api/intelligence/results|
|Assistant API|/api/assistant/ask|
|Assistant health|/api/assistant/health|
|Production frontend|https://poc32-phase3-frontend.onrender.com|
|Production backend|https://poc32-phase3-intelligence-api.onrender.com|
|Preview frontend|https://poc32-phase3-frontend-preview.onrender.com|
|Production frontend branch|phase3-release-candidate|
|Production frontend commit|ba37b75406b50ab92f62c5d5ad1f87fab13c0deb|
|Preview frontend branch|feature/data-intelligence-page|
|Preview frontend commit|28b9ac796a84304ed8dfd183090bd39035d31461|
|Backend deployment branch|feature/data-intelligence-page|
|Backend deployed commit|f401c625db9d75d61591cf0ffff2af1e978231c6|
|Data Intelligence validation mode|Local, preview, and production verification completed|

## 4\. Assistant configuration

|Field|Value|
|-|-|
|Assistant mode|Deterministic evidence grounding with optional Gemini explanation|
|Gemini model|gemini-3.5-flash-lite|
|Public Assistant validation|Previously validated on Render|
|Latest local Assistant Selenium result|4/4 PASS|
|Recorded public Assistant Selenium result|4/4 PASS — separate Render run|
|Latest local Python suite|62 passed|
|Local Gemini mode during latest suite|Disabled; deterministic fallback tested|
|Credential handling|Replacement key stored privately; never include credentials in release artifacts|

## 5\. Validation and certification

|Field|Status|
|-|-|
|Canonical data validation|PASS — 96 rows, 20 columns|
|Analytical validation|PASS — 24 checks|
|Data Intelligence local UAT|PASS — 7/7; separate fresh-clone browser validation PASS — 5/5|
|Operational regression|PASS — 4/4|
|Assistant Python tests|PASS — 62 tests|
|Assistant Selenium|PASS — 4/4|
|Clean-clone validation|PASS WITH DOCUMENTED LIMITATIONS|
|Full application build|PASS — frontend build and Docker Compose image builds verified|
|Assistant automated test report|PASS — 62 Assistant Python tests; see report for test scope|
|Deployment validation report|PASS WITH DOCUMENTED LIMITATIONS — public Assistant, preview Data Intelligence, and production Data Intelligence verified for their recorded scopes|
|Data Intelligence deployment Selenium|PASS — 26/26 preview and production checks|
|Evidence pack|REVIEWED — deployment reports, Selenium script, and preview/production screenshots checked; historical evidence and documented limitations preserved|
|Final Repomix|GENERATED AND VERIFIED — `repomix-phase3-final.md`, 4 November 2026|
|Certified release tag|phase3-v1.0.0|

## 6\. Limitations and release boundaries

* The canonical dataset is controlled synthetic data, not live air-quality measurements.
* Results are descriptive and comparative; they are not predictions, regulatory assessments, or health-risk determinations.
* Preview and production Data Intelligence deployments passed 26/26 dedicated Selenium end-to-end checks on 4 November 2026; screenshots are saved under `selenium-test/selenium_artifacts/data_intelligence/`.
* Deployment verification does not constitute full security, performance, or real-world data-quality certification.
* Public Assistant validation and local deterministic-fallback validation are separate test contexts.
* Gemini availability depends on private runtime configuration and external service availability.
* The clean-clone OpenAQ integration used its fallback path because no OPENAQ\_API\_KEY was configured in that environment; live OpenAQ connectivity was not verified there.
* The WorldPop population endpoint returned HTTP 502 during the latest operational regression because of an upstream response-format issue.
* The final npm audit reports 16 moderate vulnerabilities, with zero high or critical findings. The remaining dependency-tree findings are documented; the forced breaking downgrade was not applied.

## 7. Original certification record

* Original certification date: Not restated in this deployment update
* Certified commit: 0a051fef8ecb2636261b1e951b22c793d3f91500
* Certified tag: phase3-v1.0.0
* Tag status: Preserved; not rewritten or replaced
* Post-certification deployment merge: ba37b75406b50ab92f62c5d5ad1f87fab13c0deb

This manifest records the original certification baseline separately from subsequent deployment updates. The post-certification merge does not replace the original certified commit or tag.
