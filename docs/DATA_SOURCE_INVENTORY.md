# Data Source Inventory

## Dataset

Infocreon Aether Pulse — Phase 3 Canonical Intelligence Dataset.

## Source Type

The Phase 3 canonical dataset is currently based on the existing Phase 2 fallback/mock air-quality dataset rather than a live API extraction.

## Source Location

Primary source used for the Phase 3 sample:

`backend/data/mock_data.json`

A source sample is preserved at:

`data/source-sample/source_sample.csv`

and:

`data/source-sample/source_sample.json`

## Source Characteristics

The source contains air-quality observations for three cities:

- Delhi
- Mumbai
- Bengaluru

The available observation fields include city, country, pollutant, value, unit, timestamp, population, exposure score, regional average, percentage above regional average, source, latitude and longitude.

## Source Status

The records are explicitly marked as synthetic in the canonical dataset.

`source_name` is `Fallback`.

This means the Phase 3 canonical package is reproducible using the existing local Phase 2 fallback data and does not require a live OpenAQ request for every analysis run.

## Source Count

The current source sample contains 3 records.

## Restrictions

No restricted or private source data is used in the current canonical package.

## Live API Status

The Phase 2 application retains its existing OpenAQ integration. Phase 3 canonicalization does not replace or modify that application integration.

The canonical dataset provides a stable versioned data foundation for downstream Phase 3 analysis.
