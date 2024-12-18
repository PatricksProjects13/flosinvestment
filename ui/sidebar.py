import streamlit as st

from backend.constants import Strategy, SimulationModel
from ui.data_interface import SidebarResults, DeterministicSimulationParameters, \
    SimpleNormalDistributionSimulationParameters


def sidebar() -> SidebarResults:
    with st.sidebar.expander("Sparphase"):
        strategy = st.selectbox("Spartyp", options=Strategy)
        initial_savings = st.number_input("Initialer Sparbetrag Aktie/ETF (€)", min_value=0, step=1000, value=0)
        monthly_savings = st.number_input("Monatlicher Sparbetrag Aktie/ETF (€)", min_value=0, step=50, value=100)
        reserves = st.number_input("Initialer Sparbetrag Tagesgeld (€)", min_value=0, step=1000, value=0)
        monthly_savings_reserves = st.number_input("Monatlicher Sparbetrag Tagesgeld (€)", min_value=0, step=50,
                                                   value=100)
        costs_buy_absolute = st.number_input("Kosten Kauf Aktie/ETF (€)", min_value=0.0, step=1.0, value=1.0)
        costs_sell_absolute = st.number_input("Kosten Verkauf Aktie/ETF (€)", min_value=0.0, step=1.0, value=1.0)
        yearly_interest_rate_on_reserves = st.number_input("Zinsen Tagesgeld (%)", step=1.0, value=2.0, min_value=0.0)
        duration_accumulation_phase_in_years = st.number_input("Dauer Ansparphase (Jahre)", min_value=1, step=10,
                                                               value=30)
    with st.sidebar.expander("Inflation und Steuern"):
        include_inflation = st.toggle("Inflation", value=False, disabled=True)
        if include_inflation:
            yearly_inflation_rate = st.number_input("Inflation (% pro Jahr)", min_value=0.0, max_value=100.0,
                                                    value=2.0,
                                                    step=0.1)
        else:
            yearly_inflation_rate = 0.0
        yearly_tax_free_allowance = st.number_input("Steuerfreibetrag (€ pro Jahr)", min_value=0, step=100, value=1000)
        capital_yields_tax_percentage = st.number_input("Kapitalertragssteuer (%)", min_value=0, max_value=100,
                                                        value=25, step=1)
    with st.sidebar.expander("Auszahlphase"):
        extract_all_at_once = st.toggle("Einmaliger Verkauf", value=False, disabled=True)
        monthly_payoff = st.number_input("Monatlicher Auszahlbetrag (€)", min_value=0, step=100, value=100)
    with st.sidebar.expander("Simulation"):
        duration_simulation = st.number_input("Maximale Simulationsdauer (Jahre)", min_value=1, step=10, value=60,
                                              max_value=100)
        simulation_model = st.selectbox("Simulationsmodell", options=SimulationModel)
        # Add parameters dependent on the simulation type
        if simulation_model == SimulationModel.DETERMINISTIC:
            yearly_interest_rate = st.number_input("Jährlicher Zinssatz Aktie (%)", min_value=0.0,
                                                   max_value=100.0,
                                                   value=5.0, step=1.0)
            deterministic_simulation_parameters = DeterministicSimulationParameters(
                yearly_interest_rate=yearly_interest_rate)
            simple_normal_distribution_simulation_parameters = None
        elif simulation_model == SimulationModel.SIMPLE_NORMAL_DISTRIBUTION:
            average_yearly_interest_rate = st.number_input("Durchschnittliche jährlicher Zinssatz Aktie (%)",
                                                           min_value=0.0,
                                                           max_value=100.0,
                                                           value=5.0, step=1.0)
            sigma = st.number_input("Volatilität", min_value=0.0, value=2.0, step=1.0)
            number_of_simulations = st.number_input("Anzahl der Simulationen", min_value=1, step=100, value=100,
                                                    max_value=10000)
            deterministic_simulation_parameters = None
            simple_normal_distribution_simulation_parameters = SimpleNormalDistributionSimulationParameters(
                average_yearly_interest_rate=average_yearly_interest_rate, sigma=sigma,
                number_of_simulations=number_of_simulations)

        else:
            deterministic_simulation_parameters = None
            simple_normal_distribution_simulation_parameters = None

    # Collect the input parameters
    sidebar_results = SidebarResults(strategy=strategy,
                                     monthly_savings=monthly_savings,
                                     initial_savings=initial_savings,
                                     reserves=reserves,
                                     monthly_savings_reserves=monthly_savings_reserves,
                                     costs_buy_absolute=costs_buy_absolute,
                                     costs_sell_absolute=costs_sell_absolute,
                                     yearly_interest_rate_on_reserves=yearly_interest_rate_on_reserves,
                                     duration_accumulation_phase_in_years=duration_accumulation_phase_in_years,
                                     include_inflation=include_inflation,
                                     yearly_inflation_rate=yearly_inflation_rate,
                                     yearly_tax_free_allowance=yearly_tax_free_allowance,
                                     capital_yields_tax_percentage=capital_yields_tax_percentage,
                                     extract_all_at_once=extract_all_at_once,
                                     monthly_payoff=monthly_payoff,
                                     duration_simulation=duration_simulation,
                                     simulation_model=simulation_model,
                                     deterministic_simulation_parameters=deterministic_simulation_parameters,
                                     simple_normal_distribution_simulation_parameters=simple_normal_distribution_simulation_parameters
                                     )
    return sidebar_results
