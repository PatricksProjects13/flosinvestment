import streamlit as st
from dataclasses import dataclass

from backend.constants import SimulationModel, Strategy
from backend.strategy import SavingPlanInvestmentStrategy
from backend.simulation import DeterministicSimulationModel, SimpleNormalDistributionSimulationModel


@dataclass
class DeterministicSimulationParameters:
    yearly_interest_rate: float  # Jährlicher Zinssatz


@dataclass
class SimpleNormalDistributionSimulationParameters:
    average_yearly_interest_rate: float  # Durchschnittlicher jährlicher Zinssatz
    sigma: float  # Volatilität


@dataclass
class SidebarResults:
    strategy: Strategy  # Nach welchem Modell soll Geld gespart werden, Sparer, Flo,...
    monthly_savings: int  # Monatliche Sparrate in Aktien/ETFs
    initial_savings: int  # Anfänglicher, einmaliger Sparbetrag in Aktien/ETFs
    reserves: int  # Sonstiger gesparter, aber verfügbarer Betrag (festverzinslichtes Tagesgeld)
    monthly_savings_reserves: int  # Sparbetrag auf das Tagesgeld
    yearly_interest_rate_on_reserves: float  # Jährlicher Zinssatz auf festverzinslichtes Tagesgeld
    costs_buy_absolute: float  # Kosten für den Kauf einer Aktie in Euro
    costs_sell_absolute: float  # Kosten für den Verkauf einer Aktie in Euro
    duration_accumulation_phase_in_years: int  # Dauer Ansparphase in Jahren. Danach beginnt die Auszahlphase
    include_inflation: bool  # Inflationsbereinigung
    simulation_model: SimulationModel  # Welches Modell für die Simulation genutzt wird
    extract_all_at_once: bool  # Soll nach der Ansparphase alles auf einmal ausgezahlt werden
    monthly_payoff: float  # Monatlicher Betrag, der in der Auszahlphase aus dem gesparten Vermögen herausgenommen wird.
    yearly_inflation_rate: float = 0.0  # Inflationsrate in
    yearly_tax_free_allowance: int = 1000  # Steuerfreibetrag
    capital_yields_tax_percentage: int = 25  # Kapitalertragssteuer
    duration_simulation: int = 40  # Maximale Dauer der Simulation in Jahren
    deterministic_simulation_parameters: DeterministicSimulationParameters | None = None  # Simulationsspezifische Parameter
    simple_normal_distribution_simulation_parameters: SimpleNormalDistributionSimulationParameters | None = None  # Simulationsspezifische Parameter


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
                                                               value=20)
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
            deterministic_simulation_parameters = None
            simple_normal_distribution_simulation_parameters = SimpleNormalDistributionSimulationParameters(
                average_yearly_interest_rate=average_yearly_interest_rate, sigma=sigma)

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


def main_bar(sidebar_results: SidebarResults):
    if sidebar_results.simulation_model == SimulationModel.DETERMINISTIC:
        simulation_model = DeterministicSimulationModel(
            yearly_interest_rate=sidebar_results.deterministic_simulation_parameters.yearly_interest_rate)
    elif sidebar_results.simulation_model == SimulationModel.SIMPLE_NORMAL_DISTRIBUTION:
        simulation_model = SimpleNormalDistributionSimulationModel(
            average_yearly_interest_rate=sidebar_results.simple_normal_distribution_simulation_parameters.average_yearly_interest_rate,
            sigma=sidebar_results.simple_normal_distribution_simulation_parameters.sigma)
    if sidebar_results.strategy == Strategy.SAVINGS_PLAN:
        strategy = SavingPlanInvestmentStrategy(monthly_savings=sidebar_results.monthly_savings,
                                                initial_savings=sidebar_results.initial_savings,
                                                reserves=sidebar_results.reserves,
                                                monthly_savings_reserves=sidebar_results.monthly_savings_reserves,
                                                yearly_interest_rate_on_reserves=sidebar_results.yearly_interest_rate_on_reserves,
                                                yearly_tax_free_allowance=sidebar_results.yearly_tax_free_allowance,
                                                capital_yields_tax_percentage=sidebar_results.capital_yields_tax_percentage,
                                                duration_simulation=sidebar_results.duration_simulation,
                                                simulation_model=simulation_model,
                                                costs_buy_absolute=sidebar_results.costs_buy_absolute,
                                                costs_sell_absolute=sidebar_results.costs_sell_absolute,
                                                duration_accumulation_phase_in_years=sidebar_results.duration_accumulation_phase_in_years,
                                                extract_all_at_once=sidebar_results.extract_all_at_once,
                                                monthly_payoff=sidebar_results.monthly_payoff)
        strategy.simulate()
        #
        payed_total = strategy.history.iloc[-1]["Eingezahlt (kumulativ)"]
        return_total = strategy.history.iloc[-1]["Ausgezahlt (kumulativ)"]
        tax_total = strategy.history.iloc[-1]["Steuern (kumulativ)"]
        costs_total = strategy.history.iloc[-1]["Kosten (kumulativ)"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Eingezahlter Betrag", value=f'{payed_total:.2f} €')
            st.metric("Bezahlte Steuern", value=f'{tax_total:.2f} €')
        with col2:
            st.metric("Ausgezahlter Betrag", value=f'{return_total:.2f} €',
                      delta=f"{(return_total - payed_total) / payed_total * 100:.0f}%")
            st.metric("Kosten", value=f'{costs_total:.2f} €')

        st.line_chart(strategy.history, use_container_width=True, x_label="Monate", y_label="Wert (€)")
        st.dataframe(strategy.history, use_container_width=True)
    else:
        st.error(f"Der Spartyp '{sidebar_results.strategy}' ist noch nicht implementiert!")


def main():
    st.title("Investment Simulator")
    sidebar_results = sidebar()
    main_bar(sidebar_results)


if __name__ == '__main__':
    main()
