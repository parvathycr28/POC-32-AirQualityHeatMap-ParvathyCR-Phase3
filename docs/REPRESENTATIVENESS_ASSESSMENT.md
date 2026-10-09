# Representativeness Assessment

## 1. Purpose

This report evaluates whether the canonical dataset matches its intended structural sampling design. It does not claim that synthetic records represent actual city populations or environmental conditions.

## 2. Observed Coverage

The assessment found 96 records, eight distinct city names, four pollutant categories, and three unique timestamps. All 32 city–pollutant groups have the expected timestamp coverage.

The intended design is eight cities × four pollutants × three timestamps, yielding 96 canonical records.

## 3. Interpretation

The observed counts match the intended structural design. This supports consistent coverage across the designed city–pollutant groups.

However, balanced counts do not establish geographic, demographic, seasonal, or environmental representativeness. The observations are synthetic, and the three timestamps fall on one calendar date.

## 4. Implications

* Descriptive comparisons across existing city and pollutant groups may be considered with appropriate caveats.
* Long-term trend and seasonal claims are not supported by the current temporal coverage.
* The dataset must not be used to claim verified real-world city rankings or pollution conditions.
* No additional sampling or dataset expansion is implied by this assessment alone.

## 5. Reproduction

```bash
python data-science/scripts/assess_representativeness.py
```

Output: `data-science/outputs/representativeness_assessment.json`.
