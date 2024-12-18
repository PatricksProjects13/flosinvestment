import pandas as pd

from backend.portfolio import Portfolio
from backend.simulation import AbstractSimulationModel, DeterministicSimulationModel, \
    SimpleNormalDistributionSimulationModel
from backend.utils import convert_yearly_interest_to_monthly
from backend.constants import Strategy, SimulationModel

from ui.data_interface import SidebarResults
from abc import ABC, abstractmethod

from ui.sidebar import sidebar


class AbstractStrategy(ABC):
    @abstractmethod
    def simulate(self):
        pass

    @property
    def payed_money_total(self) -> float:
        return self.history.iloc[-1]["Eingezahlt (kumulativ)"]

    @property
    def returned_money_total(self) -> float:
        return self.history.iloc[-1]["Ausgezahlt (kumulativ)"]

    @property
    def payed_tax_total(self) -> float:
        return self.history.iloc[-1]["Steuern (kumulativ)"]

    @property
    def payed_costs_total(self) -> float:
        return self.history.iloc[-1]["Kosten (kumulativ)"]


class StrategyFactory:
    def __init__(self, sidebar_results: SidebarResults):
        self.sidebar_results = sidebar_results

    def _get_simulation_model(self) -> AbstractSimulationModel:
        if self.sidebar_results.simulation_model == SimulationModel.DETERMINISTIC:
            return DeterministicSimulationModel(
                yearly_interest_rate=self.sidebar_results.deterministic_simulation_parameters.yearly_interest_rate)
        elif self.sidebar_results.simulation_model == SimulationModel.SIMPLE_NORMAL_DISTRIBUTION:
            return SimpleNormalDistributionSimulationModel(
                average_yearly_interest_rate=self.sidebar_results.simple_normal_distribution_simulation_parameters.average_yearly_interest_rate,
                sigma=self.sidebar_results.simple_normal_distribution_simulation_parameters.sigma)
        else:
            raise NotImplementedError(f"Unknown simulation model: {self.sidebar_results.simulation_model}")

    def get_strategy(self) -> AbstractStrategy:
        sidebar_results = self.sidebar_results
        if sidebar_results.strategy == Strategy.SAVINGS_PLAN:
            strategy = SavingPlanInvestmentStrategy(monthly_savings=sidebar_results.monthly_savings,
                                                    initial_savings=sidebar_results.initial_savings,
                                                    reserves=sidebar_results.reserves,
                                                    monthly_savings_reserves=sidebar_results.monthly_savings_reserves,
                                                    yearly_interest_rate_on_reserves=sidebar_results.yearly_interest_rate_on_reserves,
                                                    yearly_tax_free_allowance=sidebar_results.yearly_tax_free_allowance,
                                                    capital_yields_tax_percentage=sidebar_results.capital_yields_tax_percentage,
                                                    duration_simulation=sidebar_results.duration_simulation,
                                                    simulation_model=self._get_simulation_model(),
                                                    costs_buy_absolute=sidebar_results.costs_buy_absolute,
                                                    costs_sell_absolute=sidebar_results.costs_sell_absolute,
                                                    duration_accumulation_phase_in_years=sidebar_results.duration_accumulation_phase_in_years,
                                                    extract_all_at_once=sidebar_results.extract_all_at_once,
                                                    monthly_payoff=sidebar_results.monthly_payoff)
        else:
            raise NotImplementedError(f"Strategy {sidebar_results.strategy} not implemented")
        return strategy


class SavingPlanInvestmentStrategy(AbstractStrategy):
    def __init__(self,
                 monthly_savings: int,
                 initial_savings: int,
                 reserves: float,
                 monthly_savings_reserves: int,
                 yearly_interest_rate_on_reserves: float,
                 yearly_tax_free_allowance: int,
                 capital_yields_tax_percentage: int,
                 duration_accumulation_phase_in_years: int,
                 extract_all_at_once: bool,
                 monthly_payoff: float,
                 duration_simulation: int,
                 simulation_model: AbstractSimulationModel,
                 costs_buy_absolute: float,
                 costs_sell_absolute: float
                 ):
        # Store input parameters
        self.monthly_savings = monthly_savings
        self.initial_savings = initial_savings
        self.monthly_savings_reserves = monthly_savings_reserves
        self.capital_yields_tax_percentage = capital_yields_tax_percentage
        self.yearly_interest_rate_on_reserves = yearly_interest_rate_on_reserves
        self.yearly_tax_free_allowance = yearly_tax_free_allowance
        self.duration_accumulation_phase_in_years = duration_accumulation_phase_in_years
        self.extract_all_at_once = extract_all_at_once
        self.monthly_payoff = monthly_payoff
        self.duration_simulation = duration_simulation
        self.simulation_model = simulation_model
        self.costs_buy_absolute = costs_buy_absolute
        self.costs_sell_absolute = costs_sell_absolute

        # These are the two targets
        self.reserves: float = reserves
        self.portfolio: Portfolio = Portfolio(updater=simulation_model,
                                              yearly_tax_free_allowance=yearly_tax_free_allowance,
                                              capital_yields_tax_percentage=capital_yields_tax_percentage,
                                              init_month=1,
                                              init_year=2024
                                              )
        self.history = pd.DataFrame({"Wert Tagesgeld + ETF": [self.reserves],
                                     "Eingezahlt (kumulativ)": [0],
                                     "Ausgezahlt (kumulativ)": [0],
                                     "Steuern (kumulativ)": [0],
                                     "Kosten (kumulativ)": [0],
                                     }, index=[0])  # Monthly current_value of the total wealth.
        # Convention: 1: (savings after 1 month + rate)
        # Order of actions in month m: Measure current_value, (extract all at once), add savings/ subtract payoff, add interest rate

    def _add_entry_in_history(self, value: float, payed: float, payoff: float, tax: float, costs: float):
        last_row = self.history.iloc[-1].to_list()
        last_value, last_payed, last_payoff, last_tax, last_costs = last_row
        self.history.loc[self.history.index.max() + 1] = [value,
                                                          payed + last_payed,
                                                          payoff + last_payoff,
                                                          tax + last_tax,
                                                          costs + last_costs]

    def simulate(self):
        for month_idx in range(1, self.duration_simulation * 12 + 1):
            returned_money = 0.0
            tax = 0.0
            transaction_costs = 0.0
            initial_reserves = self.reserves
            # Update reserve
            monthly_interest_rate_on_reserves = convert_yearly_interest_to_monthly(
                self.yearly_interest_rate_on_reserves)
            tax += self.reserves * monthly_interest_rate_on_reserves / 100 * self.capital_yields_tax_percentage / 100
            self.reserves *= 1 + (monthly_interest_rate_on_reserves / 100) * (
                    1 - self.capital_yields_tax_percentage / 100)  # Increase by interest rate minus tax
            # Update portfolio
            if month_idx <= self.duration_accumulation_phase_in_years * 12:
                # Sparphase
                payed_money = 0.0
                if month_idx == 1:
                    payed_money += initial_reserves
                    self.portfolio.buy(money=self.initial_savings, cost_buy=self.costs_buy_absolute)
                    transaction_costs += self.costs_buy_absolute
                    payed_money += self.initial_savings
                # Tagesgeld
                self.reserves += self.monthly_savings_reserves
                # Aktien / ETFs
                payed_money += self.monthly_savings + self.monthly_savings_reserves
                self.portfolio.buy(money=self.monthly_savings, cost_buy=self.costs_buy_absolute)
                transaction_costs += self.costs_buy_absolute
            else:
                # Auszahlphase
                payed_money = 0
                if self.portfolio.current_total_value > 0:
                    returned_money, tax_sell, costs_sell = self.portfolio.sell(target_money_sell=self.monthly_payoff,
                                                                               transaction_costs=self.costs_sell_absolute)
                    tax += tax_sell
                    transaction_costs += costs_sell
                else:
                    returned_money = min(self.reserves, self.monthly_payoff)
                    self.reserves -= returned_money
            self.portfolio.next_month()
            self._add_entry_in_history(value=self.reserves + self.portfolio.current_total_value,
                                       payed=payed_money,
                                       payoff=returned_money,
                                       tax=tax,
                                       costs=transaction_costs)
