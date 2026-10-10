# Canonical Data Profile

## 1. Purpose

This report documents the structure and observed characteristics of the Phase 3 canonical dataset. The sole analytical source is `data/canonical/intelligence_data.csv`.

## 2. Dataset Overview

| Attribute                        | Observed result                           |
| -------------------------------- | ----------------------------------------- |
| Canonical records                | 96                                        |
| Columns                          | 20                                        |
| Canonical CSV size               | 19,614 bytes (approximately 0.018705 MiB) |
| Data version                     | `phase3-v1.1`                             |
| Unique city/entity names         | 8                                         |
| Pollutant categories             | 4                                         |
| Unique timestamps                | 3                                         |
| Unique calendar dates            | 1                                         |
| Rows with valid coordinate pairs | 96                                        |

The canonical dataset contains 96 records across eight cities, four pollutant categories, and three unique timestamps. All records belong to the `phase3-v1.1` data version according to the generated profile.

## 3. Schema and Record Structure

The dataset contains 20 columns covering record identity, record type, observation time, entity relationships, descriptive categories, metric values and units, optional text, geographic coordinates, source information, synthetic-data flags, and data version.

The profiling script confirmed that all expected columns are present and that the column order matches the expected canonical schema. Detailed field-level null counts, distinct-value counts, examples, and numeric summaries are available in `data-science/outputs/canonical_profile.json`.

## 4. Temporal Coverage

The dataset contains three unique timestamps but only one unique calendar date. It therefore provides sparse repeated measurements rather than substantial historical coverage.

This temporal structure does not support claims of long-term trends, seasonality, or year-over-year change. The existence of an observation-time field alone does not establish suitability for conventional time-series analysis.

## 5. Geographic Coverage

All 96 records have valid latitude and longitude values within the accepted coordinate ranges. This establishes structural coordinate validity, not independent verification of the real-world locations or the representativeness of the observations.

## 6. Data Nature and Limitations

The dataset is a controlled synthetic dataset. Its structure is designed to support reproducible analytical-readiness assessment, but synthetic values must not be presented as verified real-world air-quality observations.

The dataset's limited temporal depth, synthetic nature, and finite geographic coverage must be considered when choosing analytical tracks.

## 7. Reproducibility

Regenerate the profile from the repository root using:

```bash
python data-science/scripts/profile_canonical_data.py
```

The generated output is `data-science/outputs/canonical_profile.json`.

## 8. Conclusion

The canonical dataset has the expected 96-row, 20-column structure and includes multiple entities, pollutant categories, and repeated timestamps. It is suitable for assessing bounded descriptive analytical work, subject to the quality, representativeness, and track-specific limitations documented in the accompanying reports.
s