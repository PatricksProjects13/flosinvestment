import pandas as pd

from backend.portfolio import Portfolio
from backend.simulation import AbstractSimulationModel
from backend.utils import convert_yearly_interest_to_monthly


class SavingPlanInvestmentStrategy:
    def __init__(self,
                 monthly_savings: int,
                 initial_savings: int,
                 reserves: float,
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
        self.reserves = reserves
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
                                     "Ausgezahlter (kumulativ)": [0],
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
            # Update reserve
            monthly_interest_rate_on_reserves = convert_yearly_interest_to_monthly(
                self.yearly_interest_rate_on_reserves)
            self.reserves *= 1 + (monthly_interest_rate_on_reserves / 100) * (
                    1 - self.capital_yields_tax_percentage / 100)  # Increase by interest rate minus tax
            # Update portfolio
            if month_idx <= self.duration_accumulation_phase_in_years * 12:
                # Sparphase
                returned_money = 0
                payed_money = self.monthly_savings
                if month_idx == 1:
                    self.portfolio.buy(money=self.initial_savings, cost_buy=self.costs_buy_absolute)
                    payed_money += self.initial_savings
                self.portfolio.buy(money=self.monthly_savings, cost_buy=self.costs_buy_absolute)
            else:
                # Auszahlphase
                payed_money = 0
                if self.portfolio.current_total_value > 0:
                    returned_money = self.portfolio.sell(target_money_sell=self.monthly_payoff,
                                                         transaction_costs=self.costs_sell_absolute)
                else:
                    returned_money = min(self.reserves, self.monthly_payoff)
                    self.reserves -= returned_money
            self.portfolio.next_month()
            self._add_entry_in_history(value=self.reserves + self.portfolio.current_total_value,
                                       payed=payed_money,
                                       payoff=returned_money,
                                       tax=0,
                                       costs=0)  # TODO
