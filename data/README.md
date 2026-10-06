# Aether Pulse — Phase 3 Canonical Data Package

This directory contains the canonical data foundation for PoC 32 — Aether Pulse Air Quality Heatmap.

## Purpose

Phase 3 establishes a reproducible canonical dataset that can be used by downstream analysis and feature-engineering work without requiring a live API call for every analysis run.

## Current source

The current source package is derived from the application's fallback/mock air-quality dataset.

The records are therefore marked as synthetic:

```text
is_synthetic = true
source_name = Fallback
# Phase 3 Canonical Data Package

## Dataset Version

phase3-v1.1

## Source

Synthetic OpenAQ-shaped sample.

The dataset is deliberately reproducible and does not depend on a live API
during canonical package generation.

## Coverage

- 8 cities
- 4 pollutants
- 6 source time points
- 96 sampled records
- 20 canonical columns

## Synthetic Status

All canonical records are synthetic and are marked:

is_synthetic=true

## Pipeline

```text
extract_data.py
       ↓
source_sample_full.csv
       ↓
sample_data.py
       ↓
source_sample.csv
       ↓
standardize_data.py
       ↓
intelligence_data.csv
       ↓
validate_data.py
       ↓
publish_data.py
       ↓
intelligence_data.json