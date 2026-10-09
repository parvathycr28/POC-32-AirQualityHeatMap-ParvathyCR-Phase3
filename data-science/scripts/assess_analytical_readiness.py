
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "canonical" / "intelligence_data.csv"
PROFILE_FILE = ROOT / "data-science" / "outputs" / "canonical_profile.json"
QUALITY_FILE = ROOT / "data-science" / "outputs" / "quality_assessment.json"
REPRESENTATIVENESS_FILE = (
    ROOT / "data-science" / "outputs" / "representativeness_assessment.json"
)
OUTPUT_FILE = ROOT / "data-science" / "outputs" / "analytical_readiness.json"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required assessment is missing: {path}\n"
            "Run the profile, quality, and representativeness scripts first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {DATA_FILE}")

    profile = load_json(PROFILE_FILE)
    quality = load_json(QUALITY_FILE)
    representativeness = load_json(REPRESENTATIVENESS_FILE)
    df = pd.read_csv(DATA_FILE, low_memory=False)

    dates = pd.to_datetime(df["observed_at"], errors="coerce", utc=True)
    unique_timestamps = int(dates.nunique(dropna=True))
    unique_dates = int(dates.dropna().dt.strftime("%Y-%m-%d").nunique())
    unique_cities = int(df["entity_name"].nunique(dropna=True))
    unique_pollutants = int(df["subcategory"].nunique(dropna=True))
    record_types = sorted(df["record_type"].dropna().astype(str).unique().tolist())
    metric_names = sorted(df["metric_name"].dropna().astype(str).unique().tolist())
    text_non_null = int(df["text_value"].notna().sum())
    numeric_values = pd.to_numeric(df["metric_value"], errors="coerce")
    numeric_count = int(numeric_values.notna().sum())

    synthetic = (
        df["is_synthetic"].astype("string").str.strip().str.lower()
    )
    all_synthetic = bool(
        len(synthetic) > 0
        and synthetic.notna().all()
        and synthetic.isin(["true", "1", "yes"]).all()
    )

    # Track judgements are based on observed schema and coverage.
    # They are readiness judgements, not model-performance claims.
    tracks = {
        "A Comparative Intelligence": {
            "status": "Conditionally supported",
            "evidence": [
                f"{unique_cities} distinct city/entity names and {unique_pollutants} pollutant categories are present.",
                "The canonical records contain metric values that can support descriptive comparisons after unit and record-grain checks.",
            ],
            "limitations": [
                "Confirm that compared metrics use compatible units and equivalent meanings.",
                "Synthetic values do not establish real-world city rankings.",
            ],
        },
        "B Trend Intelligence": {
            "status": (
                "Conditionally supported"
                if unique_timestamps >= 2
                else "Not supported"
            ),
            "evidence": [
                f"{unique_timestamps} unique timestamps across {unique_dates} calendar date(s).",
            ],
            "limitations": [
                "Only one calendar date is represented; long-term, seasonal, and year-over-year trends are not supported.",
                "Three timestamps alone do not establish a reliable temporal pattern.",
            ],
        },
        "C Risk & Priority": {
            "status": "Conditionally supported",
            "evidence": [
                "Pollutant labels and numeric metric values are available for descriptive threshold-based exploration.",
            ],
            "limitations": [
                "A risk framework requires documented, domain-appropriate thresholds and units.",
                "Do not present an unvalidated ranking as a real-world health-risk assessment.",
            ],
        },
        "D Anomaly Intelligence": {
            "status": "Conditionally supported",
            "evidence": [
                "Numeric measurements exist and can be checked for unusual values descriptively.",
            ],
            "limitations": [
                "The dataset has limited temporal depth and is synthetic.",
                "No anomaly model or claim of statistically validated anomalies is justified by this assessment alone.",
            ],
        },
        "E Segmentation Intelligence": {
            "status": (
                "Conditionally supported"
                if unique_cities > 1 and unique_pollutants > 1
                else "Not supported"
            ),
            "evidence": [
                f"{unique_cities} city/entity names and {unique_pollutants} pollutant categories allow descriptive grouping.",
            ],
            "limitations": [
                "Grouping by existing categories is not the same as validated clustering.",
                "Further segmentation needs a defined analytical question and suitable comparable features.",
            ],
        },
        "F Predictive Intelligence": {
            "status": "Not supported",
            "evidence": [
                f"Only {unique_timestamps} unique timestamps and {unique_dates} calendar date(s) are available.",
                f"All records marked synthetic: {all_synthetic}.",
                "No validated target/outcome, decision-time feature specification, leakage assessment, or predictive validation plan has been established by these scripts.",
            ],
            "limitations": [
                "Do not build forecasting, classification, regression, clustering-as-prediction, or risk-score models under this readiness assessment.",
                "Reconsider only if every required target, history, input availability, leakage, distribution, validation, and business-need criterion is documented.",
            ],
        },
        "G Simulation & Scenario Intelligence": {
            "status": "Conditionally supported",
            "evidence": [
                "Descriptive what-if calculations may be possible if assumptions and parameters are explicitly defined.",
            ],
            "limitations": [
                "The canonical dataset alone does not establish causal relationships or validated scenario parameters.",
                "Do not claim simulated results predict real-world outcomes.",
            ],
        },
        "H Text & Theme Intelligence": {
            "status": (
                "Conditionally supported"
                if text_non_null > 0
                else "Not supported"
            ),
            "evidence": [
                f"{text_non_null} rows contain a non-null text_value.",
            ],
            "limitations": [
                "Inspect the actual content and meaning of text_value before claiming useful themes.",
                "A non-null text field alone does not establish that meaningful natural-language analysis is supported.",
            ],
        },
    }

    quality_checks = quality.get("checks", {})
    quality_structural_status = quality.get("overall_structural_status", "UNKNOWN")
    coverage_checks = representativeness.get("structural_checks", {})

    archetype = {
        "primary": "Cross-sectional synthetic multi-entity, multi-metric dataset",
        "temporal_component": "Sparse repeated measurements",
        "classification_reason": (
            "The data contains city/entity and pollutant categories, with three "
            "unique timestamps but only one calendar date. It is not sufficient "
            "evidence for a conventional long-horizon time-series archetype."
        ),
        "record_types": record_types,
        "metric_names": metric_names,
        "numeric_metric_value_count": numeric_count,
        "non_null_text_value_count": text_non_null,
        "all_records_marked_synthetic": all_synthetic,
    }

    # Readiness refers to proceeding with bounded analytical-track work,
    # not authorization to develop predictive models or claim real-world accuracy.
    if quality_structural_status != "PASS":
        final_conclusion = "CANONICAL DATA CHANGES REQUIRED"
        conclusion_reason = (
            "The current structural quality assessment requires review before "
            "analytical-track development."
        )
    elif not all(coverage_checks.values()):
        final_conclusion = "CANONICAL DATA CHANGES REQUIRED"
        conclusion_reason = (
            "The intended canonical sampling design did not pass all structural "
            "representativeness checks."
        )
    else:
        final_conclusion = "DATA READY FOR ANALYTICAL TRACK DEVELOPMENT"
        conclusion_reason = (
            "The canonical dataset passes the current structural quality checks "
            "and matches its intended coverage design. Development must remain "
            "bounded by the track limitations and synthetic-data caveats."
        )

    result = {
        "assessment_name": "Infocreon Analytical Readiness Assessment",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": "data/canonical/intelligence_data.csv",
        "data_version_distribution": profile.get("data_version_distribution", {}),
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "data_archetype": archetype,
        "quality_gate": {
            "overall_structural_status": quality_structural_status,
            "checks": quality_checks,
            "note": (
                "Structural checks do not independently prove accuracy, "
                "provenance, safety, or real-world representativeness."
            ),
        },
        "representativeness_gate": {
            "structural_checks": coverage_checks,
            "note": (
                "Balanced synthetic coverage is not evidence of real-world "
                "population or environmental representativeness."
            ),
        },
        "analytical_tracks": tracks,
        "predictive_intelligence_gate": {
            "decision": "REJECT FOR CURRENT PHASE",
            "target_or_outcome_defined_and_validated": False,
            "sufficient_temporal_history_established": False,
            "decision_time_input_availability_documented": False,
            "leakage_risk_assessed": False,
            "target_distribution_assessed": False,
            "validation_plan_documented": False,
            "business_need_documented": False,
            "reason": (
                "The required evidence has not been established. Do not begin "
                "predictive modelling as part of this post."
            ),
        },
        "final_conclusion": final_conclusion,
        "conclusion_reason": conclusion_reason,
        "scope_guardrails": [
            "Use only data/canonical/intelligence_data.csv as the analytical source.",
            "Do not create another cleaned or model-specific dataset.",
            "Do not modify the operational frontend or dashboard.",
            "Do not develop predictive models under this assessment.",
            "Do not describe synthetic observations as real-world measurements.",
        ],
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print("INFOCREON PHASE 3 — ANALYTICAL READINESS")
    print("=" * 60)
    print(f"Archetype: {archetype['primary']}")
    print(f"Temporal component: {archetype['temporal_component']}")
    print(f"Unique timestamps: {unique_timestamps}")
    print(f"Unique calendar dates: {unique_dates}")
    print(f"Quality gate: {quality_structural_status}")
    print("Predictive Intelligence: REJECT FOR CURRENT PHASE")
    print(f"Final conclusion: {final_conclusion}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()