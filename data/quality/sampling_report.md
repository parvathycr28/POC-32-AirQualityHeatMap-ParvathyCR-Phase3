# Phase 3 Sampling and Reduction Report

## Dataset

Infocreon Aether Pulse Canonical Intelligence Dataset

## Source Strategy

The Phase 3 canonical package uses a controlled reproducible synthetic dataset
shaped around the public OpenAQ air-quality measurement structure.

The public OpenAQ API provides measurement timestamps, measurement values,
geographic coordinates and sensor/location identifiers. The controlled sample
uses the same analytical concepts while avoiding dependency on a live API during
canonical package generation.

## Original Dataset

- Source type: Synthetic
- Original records: 192
- Cities: 8
- Pollutants: 4
- Time points: 6 per city/pollutant
- Approximate source file size: less than 1 MB

## Sampling Method

Coverage-aware sampling was applied independently to each city/pollutant
combination.

Three time points were retained for every city/pollutant group.

This prevents a simple first-N-row sample from over-representing particular
cities or pollutants.

## Sampling Parameters

- Random seed: 42
- Input records: 192
- Output records: 96
- Cities retained: 8
- Pollutants retained: 4
- Time points retained per city/pollutant: 3

## Pollutant Coverage

The controlled dataset contains:

- PM2.5
- PM10
- NO2
- O3

## City Coverage

The controlled dataset contains:

- Delhi
- Mumbai
- Bengaluru
- Kolkata
- Chennai
- Hyderabad
- Pune
- Ahmedabad

## Reproducibility

The source dataset is generated deterministically by:

```text
scripts/data_pipeline/extract_data.py