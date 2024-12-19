import pandas as pd
import streamlit as st

from backend.constants import SimulationModel
from backend.strategy import StrategyFactory
from frontend.caching import get_simulated_strategies, get_quantil_strategy, get_average_strategy, get_median_strategy
from frontend.data_interface import SidebarResults
from frontend.sidebar import sidebar


def main_bar(sidebar_results: SidebarResults):
    if sidebar_results.simulation_model == SimulationModel.DETERMINISTIC:
        strategy = StrategyFactory(sidebar_results=sidebar_results).get_strategy()
        strategy.simulate()
    elif sidebar_results.simulation_model == SimulationModel.SIMPLE_NORMAL_DISTRIBUTION:
        strategies = get_simulated_strategies(sidebar_results)
        all_total_value_histories = pd.DataFrame(
            {i: strategy.history["Wert Tagesgeld + ETF"] for i, strategy in enumerate(strategies)})
        st.line_chart(all_total_value_histories, use_container_width=True)
        result_type = st.selectbox("Wähle eine Realisierung", options=["Durchschnitt", "Median", "Quantil"])
        if result_type == "Quantil":
            quantil = st.number_input("Quantil (%)", min_value=0, max_value=100, value=50, step=5)
        if result_type == "Durchschnitt":
            strategy = get_average_strategy(sidebar_results, strategies)
        elif result_type == "Median":
            strategy = get_median_strategy(strategies)
        elif result_type == "Quantil":
            strategy = get_quantil_strategy(quantil, strategies)
    else:
        st.error(f"Das Simulationsmodell {sidebar_results.simulation_model} ist noch nicht implementiert")
    #
    # Plot results
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Eingezahlter Betrag", value=f'{strategy.payed_money_total:.2f} €')
        st.metric("Bezahlte Steuern", value=f'{strategy.payed_tax_total:.2f} €')
    with col2:
        st.metric("Ausgezahlter Betrag", value=f'{strategy.returned_money_total:.2f} €',
                  delta=f"{(strategy.returned_money_total - strategy.payed_money_total) / strategy.payed_money_total * 100:.0f}%")
        st.metric("Kosten", value=f'{strategy.payed_costs_total:.2f} €')
    #
    st.line_chart(strategy.history, use_container_width=True, x_label="Monate", y_label="Wert (€)")
    st.dataframe(strategy.history, use_container_width=True)


def main():
    st.title("Investment Simulator")
    sidebar_results = sidebar()
    main_bar(sidebar_results)


if __name__ == '__main__':
    main()
