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
        self.wealth_history = {0: reserves}  # Monthly current_value of the total wealth.
        # Convention: 1: (savings after 1 month + rate)
        # Order of actions in month m: Measure current_value, (extract all at once), add savings/ subtract payoff, add interest rate

    def simulate(self):
        for month_idx in range(1, self.duration_simulation * 12 + 1):
            if month_idx <= self.duration_accumulation_phase_in_years * 12:
                # Update reserve
                monthly_interest_rate_on_reserves = convert_yearly_interest_to_monthly(
                    self.yearly_interest_rate_on_reserves)
                self.reserves *= 1 + (monthly_interest_rate_on_reserves / 100) * (
                        1 - self.capital_yields_tax_percentage / 100)  # Increase by interest rate minus tax
                # Update portfolio
                if month_idx == 1:
                    self.portfolio.buy(money=self.initial_savings, cost_buy=self.costs_buy_absolute)
                self.portfolio.buy(money=self.monthly_savings, cost_buy=self.costs_buy_absolute)
                self.portfolio.next_month()
            self.wealth_history[month_idx] = self.reserves + self.portfolio.current_total_value
