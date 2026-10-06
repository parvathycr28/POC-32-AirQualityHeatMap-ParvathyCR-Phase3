def calculate_exposure_score(
    value: float,
    population: float | None = None,
) -> float:
    """
    Demo intelligence score.

    The score combines pollution intensity and population exposure.
    This is an analytical demo score, not a medical risk model.
    """

    pollution_component = min(value / 100, 1) * 70

    if population:
        population_component = min(
            population / 50_000_000,
            1,
        ) * 30
    else:
        population_component = 0

    return round(
        min(pollution_component + population_component, 100),
        1,
    )


def percentage_above_average(
    value: float,
    regional_average: float,
) -> float:
    if regional_average == 0:
        return 0

    return round(
        ((value - regional_average) / regional_average) * 100,
        1,
    )