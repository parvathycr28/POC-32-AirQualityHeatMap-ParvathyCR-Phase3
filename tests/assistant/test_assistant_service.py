
from assistant.core import assistant_service


def sample_record():
    return {
        "result_id": "RES-0001",
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
        "quality_status": "reviewed",
        "limitation": "Synthetic data with limited temporal coverage.",
    }


def test_result_evidence_question_returns_source_record(monkeypatch):
    record = sample_record()

    monkeypatch.setattr(assistant_service, "check_question", lambda question: True)
    monkeypatch.setattr(
        assistant_service,
        "classify_question",
        lambda question: {
            "intent": "result_evidence",
            "parameters": {"result_id": "RES-0001"},
        },
    )
    monkeypatch.setattr(
        assistant_service,
        "load_results",
        lambda path: [record],
    )
    monkeypatch.setattr(
        assistant_service,
        "load_summary",
        lambda path: {},
    )
    monkeypatch.setattr(
        assistant_service,
        "get_result_evidence",
        lambda results, result_id: (
            record if result_id == "RES-0001" else None
        ),
    )

    response = assistant_service.answer_question("Show evidence RES-0001")

    assert response["status"] == "ok"
    assert response["grounding"]["llm_used"] is False
    assert response["evidence"][0]["result_id"] == "RES-0001"
    assert response["evidence"][0]["result_value"] == record["result_value"]


def test_unsupported_question_is_not_answered(monkeypatch):
    monkeypatch.setattr(assistant_service, "check_question", lambda question: True)
    monkeypatch.setattr(
        assistant_service,
        "classify_question",
        lambda question: None,
    )

    response = assistant_service.answer_question(
        "Predict next month's pollution and its health impact"
    )

    assert response["status"] == "unsupported"
    assert response["evidence"] == []
    assert response["validation"]["valid"] is False


def test_empty_question_is_rejected():
    response = assistant_service.answer_question("   ")

    assert response["status"] == "refused"
    assert response["evidence"] == []


def test_overlong_question_is_rejected():
    response = assistant_service.answer_question("x" * 501)

    assert response["status"] == "refused"
    assert response["evidence"] == []


def test_evidence_question_with_the_and_result_is_supported():
    from assistant.core.intent_router import classify_question

    response = classify_question(
        "Show the evidence for result RES-0001"
    )

    assert response["intent"] == "result_evidence"
    assert response["parameters"]["result_id"] == "RES-0001"

