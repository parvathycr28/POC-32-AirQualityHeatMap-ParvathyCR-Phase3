
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
    assert result["provider_attempted"] is False


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
    assert result["provider_attempted"] is True
    assert result["validation"]["valid"] is True


def test_reversed_city_comparison_is_rejected(evidence_package):
    evidence_package["question"] = "Compare Delhi and Mumbai for NO2"
    evidence_package["intent"] = "compare_cities"
    evidence_package["records"] = [
        {
            "entity_id": "delhi",
            "metric_name": "no2_mean",
            "result_value": 52.0,
            "finding": "Delhi recorded 52.0 µg/m³ for NO2.",
        },
        {
            "entity_id": "mumbai",
            "metric_name": "no2_mean",
            "result_value": 35.0,
            "finding": "Mumbai recorded 35.0 µg/m³ for NO2.",
        },
    ]

    result = validate_gemini_explanation(
        "Mumbai had a higher NO2 value than Delhi: 52.0 versus 35.0.",
        evidence_package,
    )

    assert result["valid"] is False
    assert any(
        "comparison" in error.lower()
        for error in result["errors"]
    )


def test_gemini_reversed_comparison_uses_safe_fallback(
    monkeypatch, evidence_package
):
    evidence_package["question"] = "Compare Delhi and Mumbai for NO2"
    evidence_package["intent"] = "compare_cities"
    evidence_package["records"] = [
        {
            "entity_id": "delhi",
            "metric_name": "no2_mean",
            "result_value": 52.0,
            "finding": "Delhi recorded 52.0 µg/m³ for NO2.",
        },
        {
            "entity_id": "mumbai",
            "metric_name": "no2_mean",
            "result_value": 35.0,
            "finding": "Mumbai recorded 35.0 µg/m³ for NO2.",
        },
    ]

    class FakeResponse:
        # Both numbers occur in the approved evidence, but the comparison
        # incorrectly reverses which city has the higher value.
        text = "Mumbai had a higher NO2 value than Delhi: 52.0 versus 35.0."
        candidates = []
        usage_metadata = None

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            self.models = FakeModels()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_explainer.genai, "Client", FakeClient)

    result = gemini_explainer.generate_gemini_explanation(evidence_package)

    assert result["status"] == "UNAVAILABLE"
    assert result["reason"] == "Generated explanation did not pass validation."
    assert "deterministic answer" in result["text"]
    assert result["validation"]["valid"] is False
    assert any(
        "comparison" in error.lower()
        for error in result["validation"]["errors"]
    )
    assert result["provider_attempted"] is True


def test_missing_api_key_returns_safe_fallback(monkeypatch, evidence_package):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    def unexpected_client_call(**kwargs):
        raise AssertionError("Gemini client must not be created without an API key")

    monkeypatch.setattr(
        gemini_explainer.genai,
        "Client",
        unexpected_client_call,
    )

    result = gemini_explainer.generate_gemini_explanation(evidence_package)

    assert result["status"] == "UNAVAILABLE"
    assert "deterministic answer" in result["text"]
    assert result["reason"] == "Gemini API key is not configured."
    assert result["provider_attempted"] is False


@pytest.mark.parametrize(
    ("provider_error", "expected_attempts"),
    [
        ("429 RESOURCE_EXHAUSTED", 2),
        ("503 UNAVAILABLE", 2),
        ("504 Gateway Timeout", 1),
        ("request timed out", 1),
    ],
)


def test_provider_errors_return_safe_fallback(
    monkeypatch,
    evidence_package,
    provider_error,
    expected_attempts,
):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_explainer.time, "sleep", lambda seconds: None)

    calls = {"count": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls["count"] += 1
            raise RuntimeError(provider_error)

    class FakeClient:
        def __init__(self, **kwargs):
            self.models = FakeModels()

    monkeypatch.setattr(gemini_explainer.genai, "Client", FakeClient)

    result = gemini_explainer.generate_gemini_explanation(evidence_package)

    assert result["status"] == "UNAVAILABLE"
    assert "deterministic answer" in result["text"]
    assert calls["count"] == expected_attempts
    assert provider_error not in str(result)
    assert result["provider_attempted"] is True


def test_invalid_generated_explanation_returns_safe_fallback(
    monkeypatch,
    evidence_package,
):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeResponse:
        text = "The observed reading is 42.5 and another reading is 999."
        candidates = []
        usage_metadata = None

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            self.models = FakeModels()

    monkeypatch.setattr(gemini_explainer.genai, "Client", FakeClient)

    result = gemini_explainer.generate_gemini_explanation(evidence_package)

    assert result["status"] == "UNAVAILABLE"
    assert "deterministic answer" in result["text"]
    assert result["reason"] == "Generated explanation did not pass validation."
    assert result["validation"]["valid"] is False
    assert result["provider_attempted"] is True
