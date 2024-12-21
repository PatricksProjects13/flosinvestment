import pandas as pd
import streamlit as st

from backend.constants import SimulationModel
from backend.strategy import StrategyFactory
from frontend.computations import get_simulated_strategies, get_percentile_strategy, get_average_strategy, \
    get_median_strategy
from frontend.data_interface import SidebarResults
from frontend.sidebar import sidebar


def tab_overview(tab, strategy: StrategyFactory):
    # Plot results
    with tab:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Eingezahlter Betrag", value=f'{strategy.payed_money_total:.2f} €')
            st.metric("Bezahlte Steuern", value=f'{strategy.payed_tax_total:.2f} €')
        with col2:
            st.metric("Ausgezahlter Betrag", value=f'{strategy.returned_money_total:.2f} €',
                      delta=f"{(strategy.returned_money_total - strategy.payed_money_total) / strategy.payed_money_total * 100:.0f}%")
            st.metric("Kosten", value=f'{strategy.payed_costs_total:.2f} €')
        st.line_chart(strategy.history, use_container_width=True, x_label="Monate", y_label="Wert (€)")


def tab_simulation_results(tab, strategies: list[StrategyFactory]):
    with tab:
        all_total_value_histories = pd.DataFrame(
            {i: strategy.history["Wert Tagesgeld + ETF"] for i, strategy in enumerate(strategies)})
        st.line_chart(all_total_value_histories, use_container_width=True)


def tab_data(tab, strategy: StrategyFactory):
    with tab:
        st.dataframe(strategy.history, use_container_width=True)


def deterministic_main_bar(sidebar_results: SidebarResults):
    strategy = StrategyFactory(sidebar_results=sidebar_results).get_strategy()
    strategy.simulate()
    tab1, tab2 = st.tabs(["Übersicht", "Daten"])
    tab_overview(tab1, strategy)
    tab_data(tab2, strategy)


def simple_normal_distribution_main_bar(sidebar_results: SidebarResults):
    strategies = get_simulated_strategies(sidebar_results)
    result_type = st.selectbox("Wähle eine Realisierung", options=["Durchschnitt", "Median", "Percentil"])
    weight_return_value = st.slider("Gewichtung Ausgezahlter Betrag (vs. Restwert Portfolio)", min_value=0.0, max_value=1.0, step=0.1,
                                    value=0.9)
    if result_type == "Percentil":
        percentile = st.number_input("Percentil (%)", min_value=0, max_value=100, value=50, step=5)
    if result_type == "Durchschnitt":
        strategy = get_average_strategy(sidebar_results, strategies)
    elif result_type == "Median":
        strategy = get_median_strategy(strategies, weight_return_value)
    elif result_type == "Percentil":
        strategy = get_percentile_strategy(percentile, weight_return_value, strategies)
    tab1, tab2, tab3 = st.tabs(["Übersicht", "Simulationsergebnisse", "Daten"])
    tab_overview(tab1, strategy)
    tab_simulation_results(tab2, strategies)
    tab_data(tab3, strategy)


def main_bar(sidebar_results: SidebarResults):
    if sidebar_results.simulation_model == SimulationModel.DETERMINISTIC:
        deterministic_main_bar(sidebar_results)
    elif sidebar_results.simulation_model == SimulationModel.SIMPLE_NORMAL_DISTRIBUTION:
        simple_normal_distribution_main_bar(sidebar_results)
    else:
        st.error(f"Das Simulationsmodell {sidebar_results.simulation_model} ist noch nicht implementiert")


def main():
    st.title("Investment Simulator")
    sidebar_results = sidebar()
    main_bar(sidebar_results)


if __name__ == '__main__':
    main()
