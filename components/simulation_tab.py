"""
Flurry: Streamlit interface for a one-street snow-depth simulation.

Purpose:
    Collect a hypothetical snowfall and clearing scenario, call the existing
    simulation engine, and display its hourly results with model assumptions.

Inputs:
    Hourly snowfall entered as comma-separated centimetre values, street length
    in kilometres, and assumed clearing capacity in centimetre-kilometres/hour.
    These inputs are entered manually and are independent of map selections.

Outputs:
    Render a remaining-snow graph and hourly results table after a valid
    submission, or a helpful error message when input validation fails.

State and side effects:
    Save the latest successful results and their length/capacity assumptions in
    Streamlit session state so they remain available across app reruns. A new
    submission removes previous results before validation. This module does not
    write files or make network requests.

Assumptions and limitations:
    The calculation rules belong to services/simulation.py. Results are simulated
    estimates using assumed clearing capacity, not observed conditions or
    road-safety assessments. The interface displays the current model limits.
"""

import streamlit as st

from services.simulation import simulate_street


def render():
    """
    Collect a street scenario and show simulated snow remaining after each hour.

    Side effects:
        Render Streamlit inputs, assumptions, validation messages, and results.
        Replace street_simulation_results in the current session on submission;
        retain successful results across reruns until another submission.

    Returns:
        None. Output is displayed directly in the Simulation tab.
    """
    form_col, results_col = st.columns([1, 2], gap="medium")

    with form_col:
        # Batch the three inputs so calculations run only when the form is submitted
        with st.form("street_simulation"):
            st.subheader("Snow-depth simulation")
            st.write(
                "Explore one hypothetical street using manually entered assumptions. "
                "Map selections do not set these inputs."
            )

            # Each comma-separated value describes snowfall during one full hour
            # The default scenario leaves 2, 4, and 6 cm after hourly clearing
            profile = st.text_area(
                "Hourly snowfall (cm)",
                value="5, 5, 5",
                help="Enter one nonnegative number per hour, separated by commas. "
                "Add zero-snowfall hours to model clearing after the storm.",
            )

            # A positive length is required because the engine divides capacity by it
            length = st.number_input(
                "Street length (km)", min_value=0.01, value=1.0, step=0.1,
            )

            # Capacity represents depth multiplied by distance, rather than plow count
            # Allow zero capacity so users can explore snowfall without any clearing
            capacity = st.number_input(
                "Assumed clearing capacity (cm-km/hour)",
                min_value=0.0, value=3.0, step=0.5,
                help="A capacity of 6 can remove 3 cm from a 2 km street each hour.",
            )
            submitted = st.form_submit_button("Run simulation", type="primary")

        # Keep model limits visible before running a scenario and alongside its results
        with st.container(border=True, key="card-assumptions"):
            st.markdown("**Current known assumptions**")
            st.write(
                "The simulation starts with zero snow and assumes snow is uniform along "
                "the street and clearing capacity stays constant. Snowfall is added "
                "before clearing each hour, and unused clearing capacity does not carry "
                "forward. The model does not account for individual plows, routing, "
                "traffic, melting, drifting, compaction, or equipment failures. Results "
                "represent simulated snow depth and do not assess road safety."
            )
            st.caption(
                "Each value represents one full operating hour. The simulation ends "
                "after the last supplied hour."
            )

    with results_col, st.container(border=True, key="card-results"):
        st.subheader("Simulated results")

        if submitted:

            # Discard earlier results so invalid submissions cannot show stale output
            st.session_state.pop("street_simulation_results", None)

            # Convert text tokens to numbers while preserving their hourly order
            # Empty input, missing values between commas, and words fail conversion
            try:
                snowfall = [float(value.strip()) for value in profile.split(",")]
            except ValueError:
                st.error("Enter snowfall as comma-separated numbers, for example: 5, 5, 5, 0.")
                return

            # Delegate calculation and numeric range checks to the shared engine
            # This also rejects negative snowfall, infinity, and NaN after conversion
            try:
                results = simulate_street(snowfall, length, capacity)
            except ValueError as exc:
                st.error(f"Check your simulation inputs: {exc}")
                return

            # Save the submitted assumptions with results so later reruns label them
            # accurately instead of implying that they use newly edited form values
            st.session_state["street_simulation_results"] = (results, length, capacity)

        # Streamlit reruns this function during other app interactions, such as map
        # selection changes; session state keeps the last successful scenario visible
        saved = st.session_state.get("street_simulation_results")
        if saved is None:
            st.info("Enter a scenario and select Run simulation to see results.")
            return

        # Read results and labels from the same saved run to keep them consistent
        results, used_length, used_capacity = saved
        st.markdown("**Simulated results based on assumed clearing capacity.**")
        st.caption(
            f"Last run: {used_length:g} km street; "
            f"{used_capacity:g} cm-km/hour clearing capacity."
        )

        # Plot end-of-hour remaining depth using the engine's hour and remaining keys
        # Explicit axis labels and alternative text describe the units and timing
        st.line_chart(
            results, x="hour", y="remaining_cm",
            x_label="Hour", y_label="Remaining snow (cm)",
            alt="Simulated snow remaining at the end of each operating hour.",
        )

        # Show every hourly quantity so users can inspect the graph's supporting data
        # Friendly column labels leave the engine's original result keys unchanged
        st.dataframe(
            results, hide_index=True,
            column_config={
                "hour": "Hour",
                "snowfall_cm": "Snowfall (cm)",
                "cleared_cm": "Snow cleared (cm)",
                "remaining_cm": "Snow remaining (cm)",
            },
            alt="Hourly simulated snowfall, snow cleared, and snow remaining in centimetres.",
        )
