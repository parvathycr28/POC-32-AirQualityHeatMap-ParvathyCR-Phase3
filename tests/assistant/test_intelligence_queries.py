from assistant.queries.intelligence_queries import compare_cities


def test_compare_cities_preserves_requested_city_order():
    mumbai = {
        "entity_id": "mumbai",
        "group_key": "no2",
        "metric_name": "no2_mean",
        "result_unit": "µg/m³",
        "result_value": 35.0,
    }

    delhi = {
        "entity_id": "delhi",
        "group_key": "no2",
        "metric_name": "no2_mean",
        "result_unit": "µg/m³",
        "result_value": 52.0,
    }

    selected = compare_cities(
        [mumbai, delhi],
        "no2",
        "delhi",
        "mumbai",
    )
    assert [record["entity_id"] for record in selected] == [
        "delhi",
        "mumbai",
    ]
    assert [record["result_value"] for record in selected] == [
        52.0,
        35.0,
    ]