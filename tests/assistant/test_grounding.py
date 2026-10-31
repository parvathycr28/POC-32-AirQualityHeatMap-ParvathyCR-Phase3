from assistant.core.evidence_builder import build_evidence_package
from assistant.core.response_validator import (
    validate_answer_records,
    validate_evidence_package,
)


def sample_record():
    return {
        "result_id": "RES-0001",
        "result_type": "comparative_intelligence",
        "entity_id": "delhi",
        "group_key": "delhi::no2::µg/m³",
        "metric_name": "no2_mean",
        "result_value": 52.89333333333334,
        "result_unit": "µg/m³",
        "priority_rank": 1,
        "finding": "Example finding from an existing approved result.",
        "evidence": "Example source evidence.",
        "data_version": "phase3-v1.1",
        "method_version": "track-a-comparative-v1.0.0",
        "generated_at": "2026-01-01T00:00:00Z",
        "quality_status": "reviewed",
        "limitation": "Synthetic data; limited temporal coverage.",
    }


def test_valid_record_produces_valid_evidence_package():
    package = build_evidence_package(
        question="Show evidence RES-0001",
        intent="result_evidence",
        result_records=[sample_record()],
    )

    result = validate_evidence_package(package)

    assert result["valid"] is True
    assert result["record_count"] == 1
    assert package["source"]["result_ids"] == ["RES-0001"]
    assert package["source"]["data_versions"] == ["phase3-v1.1"]
    assert package["source"]["method_versions"] == [
        "track-a-comparative-v1.0.0"
    ]


def test_empty_evidence_is_rejected():
    package = build_evidence_package(
        question="Show evidence RES-9999",
        intent="result_evidence",
        result_records=[],
    )

    result = validate_evidence_package(package)

    assert result["valid"] is False
    assert any("No approved evidence" in error for error in result["errors"])


def test_mixed_data_versions_are_rejected():
    first = sample_record()
    second = sample_record()
    second["result_id"] = "RES-0002"
    second["data_version"] = "different-version"

    package = build_evidence_package(
        question="Compare records",
        intent="summary",
        result_records=[first, second],
    )

    result = validate_evidence_package(package)

    assert result["valid"] is False
    assert any("inconsistent data versions" in error for error in result["errors"])


def test_missing_method_version_is_rejected():
    record = sample_record()
    record["method_version"] = None

    package = build_evidence_package(
        question="Show evidence RES-0001",
        intent="result_evidence",
        result_records=[record],
    )

    result = validate_evidence_package(package)

    assert result["valid"] is False
    assert any("Method version is missing" in error for error in result["errors"])


def test_answer_record_must_belong_to_evidence_package():
    package = build_evidence_package(
        question="Show evidence RES-0001",
        intent="result_evidence",
        result_records=[sample_record()],
    )

    good = validate_answer_records(
        [{"result_id": "RES-0001"}],
        package,
    )
    bad = validate_answer_records(
        [{"result_id": "RES-9999"}],
        package,
    )

    assert good["valid"] is True
    assert bad["valid"] is False
    assert any("not backed" in error for error in bad["errors"])


def test_boolean_is_not_accepted_as_a_metric_value():
    record = sample_record()
    record["result_value"] = True

    package = build_evidence_package(
        question="Show evidence RES-0001",
        intent="result_evidence",
        result_records=[record],
    )

    result = validate_evidence_package(package)

    assert result["valid"] is False
    assert any("non-numeric metric value" in error for error in result["errors"])


def test_quality_metadata_can_be_required():
    record = sample_record()
    record.pop("quality_status")

    package = build_evidence_package(
        question="Show evidence RES-0001",
        intent="result_evidence",
        result_records=[record],
    )

    result = validate_evidence_package(
        package,
        require_quality_metadata=True,
    )

    assert result["valid"] is False
    assert any("quality metadata is unavailable" in error for error in result["errors"])

