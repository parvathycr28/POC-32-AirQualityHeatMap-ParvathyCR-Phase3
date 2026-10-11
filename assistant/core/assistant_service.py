
"""Deterministic, evidence-grounded assistant service. No LLM is used."""

from __future__ import annotations

from typing import Any

from assistant.config.settings import RESULTS_FILE, SUMMARY_FILE
from assistant.core.evidence_builder import build_evidence_package
from assistant.core.intent_router import check_question, classify_question
from assistant.core.response_validator import validate_evidence_package
from assistant.queries.intelligence_queries import (
    compare_cities,
    get_highest_city,
    get_result_evidence,
    get_summary_results,
    load_results,
    load_summary,
)


SAFE_FALLBACK = (
    "I can't answer that from the currently supported intelligence queries. "
    "Try asking for a summary, the highest sampled mean for a pollutant, "
    "a comparison of two cities, evidence for a result ID, or the method "
    "and limitations."
)


def _normalise_router_result(
    routed: Any,
) -> tuple[str | None, dict[str, Any]]:
    """Accept common router return shapes without guessing an intent."""
    if isinstance(routed, str):
        return routed, {}

    if not isinstance(routed, dict):
        return None, {}

    intent = routed.get("intent") or routed.get("name")
    parameters = routed.get("parameters") or routed.get("entities") or {}

    if not isinstance(parameters, dict):
        parameters = {}

    return (str(intent) if intent else None), parameters


def _normalise_intent(intent: str | None) -> str | None:
    if not intent:
        return None

    value = intent.strip().lower().replace("-", "_").replace(" ", "_")

    aliases = {
        "summary": "summary",
        "summarize": "summary",
        "summarise": "summary",
        "methodology": "methodology",
        "method": "methodology",
        "limitations": "methodology",
        "result_evidence": "result_evidence",
        "evidence": "result_evidence",
        "highest_city": "highest_city",
	"highest_city_mean": "highest_city",
        "highest_sampled_mean": "highest_city",
        "compare_cities": "compare_cities",
        "city_comparison": "compare_cities",
    }
    return aliases.get(value)


def _extract_parameter(
    parameters: dict[str, Any],
    *names: str,
) -> Any:
    """Read a parameter by case-insensitive key."""
    lowered = {str(key).lower(): value for key, value in parameters.items()}

    for name in names:
        value = lowered.get(name.lower())
        if value is not None and value != "":
            return value

    return None


def _extract_result_id(
    question: str,
    parameters: dict[str, Any],
) -> str | None:
    value = _extract_parameter(parameters, "result_id", "id")
    if isinstance(value, str) and value.strip():
        return value.strip().upper()

    # Fallback only for the explicit, allowlisted RES-<digits> identifier form.
    import re

    match = re.search(r"\bRES-\d+\b", question, flags=re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_cities(
    question: str,
    parameters: dict[str, Any],
) -> tuple[str | None, str | None]:
    city_a = _extract_parameter(parameters, "city_a", "city1", "first_city")
    city_b = _extract_parameter(parameters, "city_b", "city2", "second_city")

    if city_a and city_b:
        return str(city_a).strip().lower(), str(city_b).strip().lower()

    # Conservative fallback for common natural-language comparisons.
    # City names must still match entity_id values in approved results.
    import re

    match = re.search(
        r"\bcompare\s+([a-z][a-z .'-]+?)\s+and\s+"
        r"([a-z][a-z .'-]+?)\s+for\s+([a-z0-9.]+)",
        question,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip().lower(), match.group(2).strip().lower()

    return None, None


def _extract_pollutant(
    question: str,
    parameters: dict[str, Any],
) -> str | None:
    value = _extract_parameter(parameters, "pollutant", "metric", "metric_name")

    if value:
        candidate = str(value).strip().lower()
    else:
        lowered_question = question.lower()
        candidate = next(
            (
                pollutant
                for pollutant in ("pm2.5", "pm25", "pm10", "no2", "o3")
                if pollutant in lowered_question
            ),
            "",
        )

    aliases = {
        "pm25": "pm2.5",
        "pm2_5": "pm2.5",
        "nitrogen dioxide": "no2",
        "ozone": "o3",
    }
    candidate = aliases.get(candidate, candidate)

    return candidate if candidate in {"no2", "o3", "pm10", "pm2.5"} else None


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return approved fields only; never expose arbitrary source fields."""
    allowed = (
        "result_id",
        "result_type",
        "record_id",
        "entity_id",
        "group_key",
        "period_start",
        "period_end",
        "metric_name",
        "result_value",
        "result_unit",
        "result_category",
        "priority_rank",
        "finding",
        "evidence",
        "quality_status",
        "limitation",
        "data_version",
        "method_version",
        "generated_at",
    )
    return {key: record.get(key) for key in allowed if key in record}


def _record_city(record: dict[str, Any]) -> str:
    """Extract a displayable city label from approved record identifiers."""
    entity = record.get("entity_id")

    if not isinstance(entity, str) or not entity.strip():
        return "Unknown city"

    value = entity.strip()

    # Support identifiers such as 'delhi' or 'delhi_no2'.
    # Only strip a suffix when it matches a known pollutant.
    lowered = value.lower()
    for pollutant in ("pm2.5", "pm25", "pm10", "no2", "o3"):
        suffix = f"_{pollutant}"
        if lowered.endswith(suffix):
            value = value[: -len(suffix)]
            break

    return value.replace("_", " ").replace("-", " ").title()


def _format_record_value(record: dict[str, Any]) -> str | None:
    """Format a stored numeric result without calculating a new metric."""
    value = record.get("result_value")

    if isinstance(value, bool) or value is None:
        return None

    if not isinstance(value, (int, float)):
        return None

    unit = record.get("result_unit")
    formatted = f"{value:g}"

    if isinstance(unit, str) and unit.strip():
        formatted = f"{formatted} {unit.strip()}"

    return formatted


def _methodology_response(
    results: list[dict[str, Any]],
    summary: dict[str, Any] | None,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Describe recorded method/version/limitations without inventing them."""
    data_versions = sorted({
        str(record["data_version"])
        for record in results
        if record.get("data_version") not in (None, "")
    })
    method_versions = sorted({
        str(record["method_version"])
        for record in results
        if record.get("method_version") not in (None, "")
    })

    limitations: list[str] = []
    quality_statuses = sorted({
        str(record["quality_status"])
        for record in results
        if record.get("quality_status") not in (None, "")
    })

    for record in results:
        limitation = record.get("limitation")
        if isinstance(limitation, list):
            limitations.extend(str(item) for item in limitation if item)
        elif limitation:
            limitations.append(str(limitation))

    if isinstance(summary, dict):
        for key in ("limitations", "limitation"):
            value = summary.get(key)
            if isinstance(value, list):
                limitations.extend(str(item) for item in value if item)
            elif value:
                limitations.append(str(value))

        metadata = summary.get("metadata")
        if isinstance(metadata, dict):
            for key in ("limitations", "limitation"):
                value = metadata.get(key)
                if isinstance(value, list):
                    limitations.extend(str(item) for item in value if item)
                elif value:
                    limitations.append(str(value))

    limitations = list(dict.fromkeys(limitations))

    details = {
        "data_versions": data_versions,
        "method_versions": method_versions,
        "quality_statuses": quality_statuses,
        "limitations": limitations,
    }

    parts = [
        "This assistant reads existing approved intelligence outputs. "
        "It does not recompute the analytical track or generate predictions.",
        "Recorded data version: "
        + (", ".join(data_versions) if data_versions else "unavailable")
        + ".",
        "Recorded method version: "
        + (", ".join(method_versions) if method_versions else "unavailable")
        + ".",
        "Recorded quality status: "
        + (", ".join(quality_statuses) if quality_statuses else "unavailable")
        + ".",
        "Recorded limitations: "
        + (
            "; ".join(limitations)
            if limitations
            else "not provided in the loaded outputs"
        )
        + ".",
    ]

    return " ".join(parts), [], details


def answer_question(
    question: str,
    *,
    results_path: str | None = None,
    summary_path: str | None = None,
) -> dict[str, Any]:
    """
    Answer a supported question using existing approved output files.

    Returns a JSON-serialisable response. Exceptions from malformed or
    unavailable data are converted into a safe service error.
    """
    question = question.strip() if isinstance(question, str) else ""

    if not question:
        return {
            "status": "refused",
            "answer": "Please enter a question.",
            "evidence": [],
            "validation": {"valid": False, "errors": ["Question is empty."]},
        }

    if len(question) > 500:
        return {
            "status": "refused",
            "answer": "Questions must be 500 characters or fewer.",
            "evidence": [],
            "validation": {"valid": False, "errors": ["Question is too long."]},
        }

    try:
        safety_result = check_question(question)

        if safety_result is False:
            return {
                "status": "refused",
                "answer": SAFE_FALLBACK,
                "evidence": [],
                "validation": {
                    "valid": False,
                    "errors": ["Question failed the safety check."],
                },
            }

        if isinstance(safety_result, dict) and not safety_result.get(
            "allowed", safety_result.get("safe", True)
        ):
            return {
                "status": "refused",
                "answer": SAFE_FALLBACK,
                "evidence": [],
                "validation": {
                    "valid": False,
                    "errors": ["Question failed the safety check."],
                },
            }

        routed = classify_question(question)
        intent_raw, parameters = _normalise_router_result(routed)
        intent = _normalise_intent(intent_raw)

        if isinstance(routed, dict) and routed.get("supported") is False:
            intent = None

        if intent is None:
            return {
                "status": "unsupported",
                "answer": SAFE_FALLBACK,
                "evidence": [],
                "validation": {
                    "valid": False,
                    "errors": ["Question did not match a supported intent."],
                },
            }

        results = load_results(results_path or str(RESULTS_FILE))
        summary = None

        try:
            summary = load_summary(summary_path or str(SUMMARY_FILE))
        except (FileNotFoundError, ValueError, TypeError):
            summary = None

        selected: list[dict[str, Any]] = []
        details: dict[str, Any] = {}
        answer = ""

        if intent == "summary":
            selected = get_summary_results(results, limit=10)
            answer = (
                f"Retrieved {len(selected)} approved Track A result record(s). "
                "The records below are existing outputs, not newly calculated findings."
            )

        elif intent == "highest_city":
            pollutant = _extract_pollutant(question, parameters)

            if not pollutant:
                return {
                    "status": "needs_clarification",
                    "answer": (
                        "Please specify one supported pollutant: NO2, O3, PM10, or PM2.5."
                    ),
                    "evidence": [],
                    "validation": {
                        "valid": False,
                        "errors": ["Pollutant is missing or invalid."],
                    },
                }

            result = get_highest_city(results, pollutant)

            if result:
                selected = [result]
                city = _record_city(result)
                value = _format_record_value(result)

                if value is not None:
                    answer = (
                        f"{city} has the highest recorded sampled mean for "
                        f"{pollutant.upper()} among the retrieved approved records: "
                        f"{value}. This is an existing result, not a new calculation."
                    )
                else:
                    answer = (
                        f"The approved results identify {city} as having the "
                        f"highest sampled mean for {pollutant.upper()} among the "
                        "retrieved records. A numeric result value is not available "
                        "in the approved record."
                    )
            else:
                answer = (
                    f"No approved result was found to identify the highest sampled "
                    f"mean for {pollutant.upper()}."
                )

        elif intent == "compare_cities":
            pollutant = _extract_pollutant(question, parameters)
            city_a, city_b = _extract_cities(question, parameters)

            if not pollutant or not city_a or not city_b:
                return {
                    "status": "needs_clarification",
                    "answer": (
                        "Please provide two city names and one pollutant "
                        "(NO2, O3, PM10, or PM2.5)."
                    ),
                    "evidence": [],
                    "validation": {
                        "valid": False,
                        "errors": ["Comparison parameters are incomplete."],
                    },
                }

            selected = compare_cities(results, pollutant, city_a, city_b)

            if len(selected) >= 2:
                comparison_lines: list[str] = []

                for record in selected:
                    city = _record_city(record)
                    value = _format_record_value(record)

                    if value is not None:
                        comparison_lines.append(f"{city}: {value}")
                    else:
                        comparison_lines.append(
                            f"{city}: the numeric value is not available"
                        )

                answer = (
                    f"Existing {pollutant.upper()} result records for "
                    f"{city_a.title()} and {city_b.title()}: "
                    + "; ".join(comparison_lines)
                    + ". These are retrieved values; no new metric was calculated."
                )
            else:
                answer = (
                    f"Found {len(selected)} matching approved record(s) for "
                    f"{city_a.title()} and {city_b.title()} for {pollutant.upper()}. "
                    "The available evidence is shown below; no new metric was calculated."
                )

        elif intent == "result_evidence":
            result_id = _extract_result_id(question, parameters)

            if not result_id:
                return {
                    "status": "needs_clarification",
                    "answer": "Please provide a result ID, such as RES-0001.",
                    "evidence": [],
                    "validation": {
                        "valid": False,
                        "errors": ["Result ID is missing."],
                    },
                }

            result = get_result_evidence(results, result_id)

            if result:
                selected = [result]

            answer = f"Retrieved the approved evidence record for {result_id}."

        elif intent == "methodology":
            answer, selected, details = _methodology_response(results, summary)

            # Keep a source record for traceable provenance when available.
            if not selected and results:
                selected = results[:1]

        else:
            return {
                "status": "unsupported",
                "answer": SAFE_FALLBACK,
                "evidence": [],
                "validation": {
                    "valid": False,
                    "errors": ["Intent is not allowlisted."],
                },
            }

        selected = [
            record for record in selected
            if isinstance(record, dict)
        ]

        if intent != "methodology" and not selected:
            return {
                "status": "not_found",
                "answer": (
                    "No matching approved result was found. I will not infer or "
                    "invent a replacement result."
                ),
                "evidence": [],
                "validation": {
                    "valid": False,
                    "errors": ["No matching records found."],
                },
            }

        package = build_evidence_package(
            question=question,
            intent=intent,
            result_records=selected,
            summary=summary,
            parameters=parameters,
        )

        validation = validate_evidence_package(package)

        if not validation["valid"]:
            return {
                "status": "blocked",
                "answer": (
                    "I couldn't safely answer because the retrieved evidence "
                    "did not pass grounding checks."
                ),
                "evidence": [],
                "evidence_package": package,
                "validation": validation,
            }

        if intent == "methodology" and not selected:
            if (
                not package["source"]["data_versions"]
                or not package["source"]["method_versions"]
            ):
                return {
                    "status": "blocked",
                    "answer": (
                        "I couldn't verify the recorded data and method versions, "
                        "so I can't provide a grounded methodology response."
                    ),
                    "evidence": [],
                    "evidence_package": package,
                    "validation": {
                        "valid": False,
                        "errors": ["Methodology response lacks version metadata."],
                    },
                }

        return {
            "status": "ok",
            "answer": answer,
            "details": details,
            "evidence": [_public_record(record) for record in selected],
            "evidence_package": package,
            "validation": validation,
            "grounding": {
                "mode": "deterministic",
                "llm_used": False,
                "generated_findings": False,
                "source": "approved_intelligence_results",
            },
        }

    except (FileNotFoundError, ValueError, TypeError, KeyError) as exc:
        # Do not return filesystem paths, file contents, or configuration data.
        return {
            "status": "service_error",
            "answer": (
                "The approved intelligence data could not be safely loaded "
                "or validated. Please check the configured output files and logs."
            ),
            "evidence": [],
            "validation": {
                "valid": False,
                "errors": [
                    f"Data loading or validation failed: {type(exc).__name__}"
                ],
            },
        }
