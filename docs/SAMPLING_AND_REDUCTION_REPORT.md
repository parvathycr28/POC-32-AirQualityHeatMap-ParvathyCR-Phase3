# Sampling and Reduction Report

## Purpose

This report documents the reproducible reduction of the controlled
synthetic air-quality source dataset into the Phase 3 canonical data
sample.

## Source Dataset

The controlled source dataset contains:

- 192 records
- 8 cities
- 4 pollutants
- Multiple observation timestamps
- PM2.5
- PM10
- NO2
- O3

The source data is synthetic and reproducible. It follows the
measurement structure used by the existing air-quality application and
is designed to provide stable input for Phase 3 data processing.

## Sampling Method

A coverage-aware sampling method is used instead of taking the first
rows of the source dataset.

Sampling is stratified by:

- City
- Pollutant

Each city/pollutant combination retains 3 observation timestamps.

There are:

- 8 cities
- 4 pollutants
- 32 city/pollutant combinations
- 3 retained observations per combination

Therefore:

`8 × 4 × 3 = 96 canonical records`

## Random Seed

The sampling process uses:

```text
Random seed: 42