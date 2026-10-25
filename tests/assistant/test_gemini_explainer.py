
import pytest
import assistant.core.gemini_explainer as gemini_explainer
from assistant.core.gemini_explainer import validate_gemini_explanation


@pytest.fixture
def evidence_package():
    return {
        "question": "Describe the supplied reading",
        "records": [
            {
                "result_value": 42.5,
                "finding": "Observed reading is 42.5",
                "result_id": "RES-0001",
            }
        ],
    }


def test_valid_evidence_supported_explanation_is_accepted(evidence_package):
    result = validate_gemini_explanation(
        "The observed reading is 42.5.",
        evidence_package,
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_unsupported_number_is_rejected(evidence_package):
    result = validate_gemini_explanation(
        "The observed reading is 42.5 and another reading is 999.",
        evidence_package,
    )

    assert result["valid"] is False
    assert any("numeric tokens" in error for error in result["errors"])


def test_forbidden_prediction_claim_is_rejected(evidence_package):
    result = validate_gemini_explanation(
        "This reading predicts future pollution.",
        evidence_package,
    )

    assert result["valid"] is False
    assert any("prohibited claim" in error for error in result["errors"])


def test_empty_explanation_is_rejected(evidence_package):
    result = validate_gemini_explanation("", evidence_package)

    assert result["valid"] is False
    assert any("empty explanation" in error for error in result["errors"])


def test_overlong_explanation_is_rejected(evidence_package):
    result = validate_gemini_explanation("A" * 1801, evidence_package)

    assert result["valid"] is False
    assert any("exceeds the permitted length" in error for error in result["errors"])

def test_provider_failure_returns_safe_unavailable_result(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        gemini_explainer.genai,
        "Client",
        lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("simulated provider failure")
        ),
    )

    result = gemini_explainer.generate_gemini_explanation(
        {
            "question": "Describe the supplied reading",
            "records": [{"result_value": 42.5}],
        }
    )

    assert result["status"] == "UNAVAILABLE"
    assert "deterministic answer" in result["text"]
    assert result["reason"] == "Gemini request failed or timed out."
    assert "simulated provider failure" not in str(result)

def test_prompt_does_not_include_record_keys_diagnostic(monkeypatch, evidence_package):
    captured = {}

    class FakeResponse:
        text = "The observed reading is 42.5."
        candidates = []
        usage_metadata = None

    class FakeModels:
        def generate_content(self, **kwargs):
            captured["prompt"] = kwargs["contents"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            self.models = FakeModels()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_explainer.genai, "Client", FakeClient)

    result = gemini_explainer.generate_gemini_explanation(evidence_package)

    assert "GEMINI_RECORD_KEYS:" not in captured["prompt"]
    assert "EVIDENCE_JSON:" in captured["prompt"]
    assert "42.5" in captured["prompt"]
    assert result["status"] == "AVAILABLE"