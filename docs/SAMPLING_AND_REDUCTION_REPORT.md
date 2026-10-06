# Sampling and Reduction Report

## Purpose

Phase 3 Post #1 establishes a reproducible canonical data foundation before exploratory data analysis or feature engineering.

## Input

The current source dataset contains 3 available air-quality records from the Phase 2 fallback/mock dataset.

## Sampling Method

Sampling is coverage-aware rather than a simple `head()` operation.

The sampling implementation groups available records by city and pollutant and selects representative records while using a fixed random seed.

## Random Seed

`42`

Using the fixed seed makes the sampling process reproducible.

## Current Coverage

The resulting source sample contains:

- Delhi — PM2.5
- Mumbai — PM2.5
- Bengaluru — PM2.5

## Reduction

Current source size:

- 3 records

Current sampled size:

- 3 records

Because the available source contains only three records, no records are removed during the current sampling stage.

## Canonical Dataset

The resulting canonical dataset contains:

- 3 records
- 20 columns

The canonical data is written to:

`data/canonical/intelligence_data.csv`

## Reproducibility

The sampling logic is maintained in:

`scripts/data_pipeline/sample_data.py`

The fixed random seed is:

`RANDOM_SEED = 42`

The sampling stage can therefore be rerun deterministically against the same source input.

## Phase 3 Boundary

This sampling stage does not perform exploratory analysis, feature engineering, predictive modeling, or analytical transformations.
