from math import floor

import numpy as np
import pandas as pd
import streamlit as st

from backend.strategy import AbstractStrategy, StrategyFactory
from frontend.data_interface import SidebarResults

CACHE_TTL_SECONDS = 60 * 60


@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def get_simulated_strategies(sidebar_results: SidebarResults) -> list[AbstractStrategy]:
    """
    Fetches a list of simulated strategies based on user-defined parameters. Simulates
    each strategy using parameters provided through the `sidebar_results` object. The
    simulation process includes updating a progress bar to indicate progress. The
    returned list contains the simulated strategies.
    The results are cached for performance reasons.

    :param sidebar_results: User-defined parameters for the simulation process.
    :type sidebar_results: SidebarResults
    :return: A list of simulated strategies derived from the given parameters.
    :rtype: list[AbstractStrategy]
    """
    strategies = [StrategyFactory(sidebar_results=sidebar_results).get_strategy() for _ in
                  range(sidebar_results.simple_normal_distribution_simulation_parameters.number_of_simulations)]
    progressbar = st.progress(0)
    for i, strategy in enumerate(strategies):
        strategy.simulate()
        progressbar.progress((i + 1) / len(strategies), text=f"Simuliere. Simulation Nummer {i + 1}")
    progressbar.empty()
    return strategies


def get_percentile_strategy(percentile: int,
                            weight_return_value: int,
                            strategies: list[AbstractStrategy]) -> AbstractStrategy:
    index_percentile = floor(percentile / 100 * len(strategies))

    sorted_strategies = list(sorted(strategies, key=lambda
        strategy: strategy.returned_money_total * weight_return_value + strategy.remaining_value * (
            1 - weight_return_value)))
    return sorted_strategies[index_percentile]


def get_average_strategy(sidebar_results: SidebarResults, strategies: list[AbstractStrategy]) -> AbstractStrategy:
    histories = [strategy.history for strategy in strategies]
    history = pd.DataFrame(columns=histories[0].columns,
                           data=np.mean([h.to_numpy() for h in histories], axis=0))
    strategy = StrategyFactory(sidebar_results=sidebar_results).get_strategy()
    strategy.history = history
    return strategy


def get_median_strategy(strategies: list[AbstractStrategy], weight_return_value: int) -> AbstractStrategy:
    return get_percentile_strategy(50, weight_return_value, strategies)
