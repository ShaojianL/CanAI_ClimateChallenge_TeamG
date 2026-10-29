"""
Flurry: hourly snow accumulation and clearing for one pilot street.

Purpose:
    Provide a small, deterministic calculation engine that can be tested
    independently and later connected to the Streamlit interface. This module
    uses explicit rules; it does not train a model or call an AI service.

Inputs:
    hourly_snowfall_cm: Snowfall depth in centimetres for each one-hour interval.
    length_km: Positive length of the modelled street in kilometres.
    clearing_capacity_cm_km_per_hour: ASSUMED work available each hour, measured
        in centimetre-kilometres per hour. For example, a capacity of 6 can
        remove 3 cm of snow from a 2 km street in one hour.

Calculation rules:
    Start with zero snow and add each hour's snowfall before clearing. Divide
    work capacity by street length to obtain the maximum depth removable that
    hour. Remove only the snow present and carry the remaining depth into the
    next hour. Unused clearing capacity is not carried forward.

    remaining_cm = max(0, previous_remaining_cm + snowfall_cm - clearing_cm)

Outputs:
    simulate_street returns one dictionary per hour containing the hour number
    (starting at 1), snowfall_cm, cleared_cm, and remaining_cm. An empty snowfall
    profile returns an empty list. Invalid inputs or nonfinite calculated
    values raise ValueError.

Example:
    A 1 km street receiving [5, 5, 5] cm of hourly snowfall with an assumed
    capacity of 3 cm-km/hour has remaining depths of [2, 4, 6] cm.

Assumptions and limitations:
    Snow is uniform along the street, clearing capacity is constant, and every
    supplied interval represents one full operating hour. The simulation ends
    with the supplied profile; include zero-snowfall hours to model subsequent
    clearing. This version does not allocate individual plows, apply street
    priorities, model operating schedules, or determine a clearing target.
    Routing, road width, melting, drifting, compaction, traffic, and equipment
    failures are outside this model.

    All results are SIMULATED and clearing capacity is ASSUMED. Results are not
    observed road conditions, validated municipal recovery times, or road-safety
    assessments. The module performs no file access or network requests and
    does not render an interface.
"""

import math


def _validate_number(value, name, positive=False):
    """
    Reject nonnumeric, nonfinite, or out-of-range simulation inputs.

    Parameters:
        value: Input to check.
        name: Input name used in errors.
        positive: Whether zero is also invalid.
    Raises:
        ValueError: When the value is invalid.
    """
    if (
        type(value) not in (int, float)
        or not math.isfinite(value)
        or value < 0
        or (positive and value == 0)
    ):
        requirement = "positive" if positive else "nonnegative"
        raise ValueError(f"{name} must be a finite {requirement} number.")


def simulate_street(hourly_snowfall_cm, length_km, clearing_capacity_cm_km_per_hour):
    """
    Calculate hourly remaining snow for one street starting with no snow.

    Parameters:
        hourly_snowfall_cm: Iterable of nonnegative snowfall depths, one per hour.
        length_km: Positive length of the modelled street in kilometres.
        clearing_capacity_cm_km_per_hour: Assumed hourly work capacity. Removing
            3 cm from a 2 km street consumes 6 cm-km of work.
    Returns:
        List of hourly dictionaries with hour (starting at 1), snowfall_cm,
        cleared_cm, and remaining_cm. An empty profile returns an empty list.
    Raises:
        ValueError: When inputs are invalid or calculations exceed finite range.

    Snowfall is added before clearing each hour. Capacity is constant, unused
    capacity is not carried forward, and snow is uniform over the street.
    This simplified model excludes routing, melting, drifting, and compaction.
    Results are simulated estimates, not observations or safety assessments.
    """
    _validate_number(length_km, "length_km", positive=True)
    _validate_number(
        clearing_capacity_cm_km_per_hour, "clearing_capacity_cm_km_per_hour"
    )
    try:
        snowfall = list(hourly_snowfall_cm)
    except TypeError as exc:
        raise ValueError("hourly_snowfall_cm must be an iterable of numbers.") from exc
    for value in snowfall:
        _validate_number(value, "hourly snowfall")

    hourly_clearing_cm = clearing_capacity_cm_km_per_hour / length_km
    _validate_number(hourly_clearing_cm, "hourly clearing depth")
    remaining_cm = 0.0
    results = []
    for hour, snowfall_cm in enumerate(snowfall, start=1):
        accumulated_cm = remaining_cm + snowfall_cm
        _validate_number(accumulated_cm, "accumulated snow")

        # Clearing cannot remove more snow than is present
        cleared_cm = min(accumulated_cm, hourly_clearing_cm)
        remaining_cm = accumulated_cm - cleared_cm
        results.append({
            "hour": hour,
            "snowfall_cm": snowfall_cm,
            "cleared_cm": cleared_cm,
            "remaining_cm": remaining_cm,
        })
    return results
