# Canonical Data Mapping

## Purpose

This document describes how the existing air-quality source fields are mapped into the required Infocreon Phase 3 canonical schema.

## Source-to-Canonical Mapping

| Source Field | Canonical Field | Mapping |
|---|---|---|
| city | entity_name | City name |
| city | entity_id | Normalized city identifier |
| pollutant | subcategory | Pollutant identifier |
| pollutant | metric_name | Pollutant metric |
| value | metric_value | Numeric air-quality measurement |
| unit | metric_unit | Measurement unit |
| timestamp | observed_at | Observation timestamp |
| country | text_value | Country context |
| latitude | latitude | Geographic latitude |
| longitude | longitude | Geographic longitude |
| source | source_name | Source identifier |
| synthetic status | is_synthetic | Boolean synthetic-data indicator |

## Generated Canonical Fields

The following fields are generated or standardized by the Phase 3 pipeline:

- `record_id`
- `record_type`
- `entity_id`
- `related_entity_id`
- `category`
- `status`
- `stage`
- `source_record_id`
- `data_version`

## Canonical Record Design

Each air-quality observation is represented as one canonical `measurement` record.

Current records use:

- `record_type`: `measurement`
- `category`: `air_quality`
- `status`: `observed`
- `stage`: `observation`
- `subcategory`: `pm2.5`

## Version

The current canonical dataset version is:

`phase3-v1.1`

## Canonical Column Order

The canonical CSV uses the required 20-column order:

1. `record_id`
2. `record_type`
3. `observed_at`
4. `entity_id`
5. `related_entity_id`
6. `entity_name`
7. `category`
8. `subcategory`
9. `status`
10. `stage`
11. `metric_name`
12. `metric_value`
13. `metric_unit`
14. `text_value`
15. `latitude`
16. `longitude`
17. `source_name`
18. `source_record_id`
19. `is_synthetic`
20. `data_version`

## Transformation Boundary

The canonicalization process standardizes structure and metadata but does not introduce downstream analytical features.

EDA, feature engineering, modeling, and other analytical work remain outside this canonical foundation stage.
