
import re


def classify_question(question: str):
    """
    Classify a question into an explicitly supported assistant intent.

    This router only identifies supported question patterns.
    It does not calculate metrics or generate findings.
    """
    if not isinstance(question, str):
        return None

    text = " ".join(question.strip().split())

    if not text:
        return None

    # 1. Evidence for an existing result ID
    evidence_match = re.fullmatch(
        r"(show|get|explain|retrieve)?\s*"
        r"(the\s+)?evidence\s+"
        r"(for\s+)?(result\s+)?"
        r"(RES-[A-Za-z0-9_-]+)",
        text,
        flags=re.IGNORECASE,
    )

    if evidence_match:
        return {
            "intent": "result_evidence",
            "parameters": {
                "result_id": evidence_match.group(5).upper()
            },
        }

    # 2. Methodology and limitations
    methodology_patterns = [
        r"(explain|describe|summarize|outline)\s+"
        r"(the\s+)?(method|methodology)\s+"
        r"(and\s+)?(the\s+)?limitations",
        r"(explain|describe|summarize|outline)\s+"
        r"(the\s+)?limitations",
        r"(explain|describe|summarize|outline)\s+"
        r"(the\s+)?(method|methodology)",
        r"what\s+are\s+(the\s+)?"
        r"(methodological\s+)?limitations",
        r"what\s+(is|are)\s+the\s+"
        r"(method|methodology|limitations)",
        r"tell\s+me\s+about\s+(the\s+)?"
        r"(method|methodology|limitations)",
    ]

    if any(
        re.fullmatch(pattern, text, flags=re.IGNORECASE)
        for pattern in methodology_patterns
    ):
        return {
            "intent": "methodology",
            "parameters": {},
        }

    # 3. Summarize existing Track A findings
    summary_patterns = [
        r"summarize\s+(the\s+)?track\s+a\s+findings",
        r"(summarize|summary\s+of)\s+"
        r"(the\s+)?(track\s+a\s+)?findings",
        r"give\s+me\s+(a\s+)?summary\s+"
        r"(of\s+)?(the\s+)?(track\s+a\s+)?findings",
    ]

    if any(
        re.fullmatch(pattern, text, flags=re.IGNORECASE)
        for pattern in summary_patterns
    ):
        return {
            "intent": "summary",
            "parameters": {},
        }

    # 4. Highest sampled mean for a specified pollutant
    highest_match = re.fullmatch(
        r"(which\s+city\s+has\s+)?"
        r"(the\s+)?(highest|maximum|max)\s+"
        r"(sampled\s+)?mean\s+"
        r"(for\s+)?"
        r"(the\s+)?"
        r"(NO2|O3|PM10|PM2\.5)"
        r"(\s+pollutant)?"
        r"(\s+pollution)?"
        r"(\s+mean)?"
        r"(\s+value)?"
        r"(\s+among\s+cities)?"
        r"\??",
        text,
        flags=re.IGNORECASE,
    )

    if highest_match:
        pollutant = next(
            (
                group
                for group in highest_match.groups()
                if group and group.upper() in {
                    "NO2", "O3", "PM10", "PM2.5"
                }
            ),
            None,
        )

        if pollutant:
            return {
                "intent": "highest_city_mean",
                "parameters": {
                    "pollutant": pollutant.lower(),
                },
            }

    # Also support: "Which city has the highest NO2 mean?"
    highest_match = re.fullmatch(
        r"which\s+city\s+has\s+the\s+highest\s+"
        r"(NO2|O3|PM10|PM2\.5)"
        r"\s+(sampled\s+)?mean\??",
        text,
        flags=re.IGNORECASE,
    )

    if highest_match:
        return {
            "intent": "highest_city_mean",
            "parameters": {
                "pollutant": highest_match.group(1).lower(),
            },
        }

    # 5. Compare two named cities for a specified pollutant
    comparison_match = re.fullmatch(
        r"compare\s+"
        r"([A-Za-z][A-Za-z .'-]*?)\s+and\s+"
        r"([A-Za-z][A-Za-z .'-]*?)\s+"
        r"for\s+(NO2|O3|PM10|PM2\.5)\??",
        text,
        flags=re.IGNORECASE,
    )

    if comparison_match:
        return {
            "intent": "city_comparison",
            "parameters": {
                "city_a": comparison_match.group(1).strip().lower(),
                "city_b": comparison_match.group(2).strip().lower(),
                "pollutant": comparison_match.group(3).lower(),
            },
        }

    return None

def check_question(question: str) -> bool:
    """
    Validate the basic question requirements before intent classification.
    """
    if not isinstance(question, str):
        return False

    text = question.strip()

    if not text:
        return False

    if len(text) > 500:
        return False

    return True
