# Canonical Data Package

This directory contains the reproducible canonical data foundation for
PoC 32 — Aether Pulse Air Quality Heatmap, Phase 3.

## Dataset Overview

The Phase 3 package uses a controlled, reproducible synthetic air-quality
dataset shaped around the existing OpenAQ-style measurement structure.

The source dataset contains:

- 192 source records
- 8 cities
- 4 pollutants
- Multiple observation timestamps
- PM2.5, PM10, NO2, and O3 measurements

The coverage-aware sampling stage reduces the source dataset to:

- 96 sampled records
- 8 cities
- 4 pollutants
- 3 retained timestamps per city/pollutant combination
- Random seed: 42

The canonical dataset contains 20 standardized columns and uses
data version `phase3-v1.1`.

## Directory Structure

```text
data/
├── README.md
├── manifest.json
├── schema.json
├── source-sample/
│   ├── source_sample_full.csv
│   └── source_sample.csv
├── canonical/
│   └── intelligence_data.csv
├── published/
│   └── intelligence_data.json
└── quality/
    ├── data_profile.json
    ├── sampling_report.md
    └── validation_report.json