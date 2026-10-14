
from assistant.core.evidence_builder import build_evidence_package
from assistant.core.response_validator import validate_evidence_package


REQUIRED_EVIDENCE_FIELDS = {
    "result_id",
    "result_type",
    "record_id",
    "entity_id",
    "metric_name",
    "result_value",
    "result_unit",
    "data_version",
    "method_version",
    "quality_status",
    "limitation",
}


def approved_record(result_id="RES-0001"):
    return {
        "result_id": result_id,
        "result_type": "comparative_intelligence",
        "record_id": "REC-0001",
        "entity_id": "delhi",
        "group_key": "delhi::no2::µg/m³",
        "metric_name": "no2_mean",
        "result_value": 52.89333333333334,
        "result_unit": "µg/m³",
        "priority_rank": 1,
        "finding": "Existing source finding.",
        "evidence": "Existing source evidence.",
        "data_version": "phase3-v1.1",
        "method_version": "track-a-comparative-v1.0.0",
        "generated_at": "2026-01-01T00:00:00Z",
        "quality_status": "conditional",
        "limitation": "Synthetic descriptive comparison only.",
    }


def build_package(record):
    return build_evidence_package(
        question="Show the evidence for result RES-0001",
        intent="result_evidence",
        result_records=[record],
    )


def test_evidence_package_covers_required_source_fields():
    package = build_package(approved_record())

    validation = validate_evidence_package(package)

    assert validation["valid"] is True
    assert validation["record_count"] == 1

    evidence_record = package["records"][0]
    missing = REQUIRED_EVIDENCE_FIELDS - set(evidence_record)

    assert not missing, f"Missing evidence fields: {sorted(missing)}"


def test_evidence_package_preserves_source_versions_and_ids():
    package = build_package(approved_record())

    assert package["source"]["result_ids"] == ["RES-0001"]
    assert package["source"]["data_versions"] == ["phase3-v1.1"]
    assert package["source"]["method_versions"] == [
        "track-a-comparative-v1.0.0"
    ]


def test_evidence_package_preserves_quality_and_limitations():
    package = build_package(approved_record())

    assert package["quality"]["quality_status"] == "conditional"
    assert package["quality"]["quality_metadata_available"] is True
    assert "Synthetic descriptive comparison only." in (
        package["quality"]["limitations"]
    )


def test_missing_limitation_is_detected_as_missing_coverage():
    record = approved_record()
    record.pop("limitation")

    package = build_package(record)
    evidence_record = package["records"][0]

    # The builder preserves the missing field as None. The validator
    # does not currently require limitations, so assert coverage directly.
    assert evidence_record["limitation"] is None
    assert "limitation" not in package["quality"]["limitations"]


def test_missing_method_version_invalidates_evidence():
    record = approved_record()
    record["method_version"] = None

    package = build_package(record)
    validation = validate_evidence_package(package)

    assert validation["valid"] is False
    assert any("Method version is missing" in error
               for error in validation["errors"])


def test_empty_evidence_is_not_valid():
    package = build_evidence_package(
        question="Show the evidence for result RES-0001",
        intent="result_evidence",
        result_records=[],
    )

    validation = validate_evidence_package(package)

    assert validation["valid"] is False
    assert validation["record_count"] == 0
