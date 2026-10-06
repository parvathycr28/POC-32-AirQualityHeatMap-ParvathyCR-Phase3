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