from backend.strategy import SavingPlanInvestmentStrategy
from backend.simulation import DeterministicSimulationModel
from pyinstrument import Profiler
profiler = Profiler()
profiler.start()

strategy = SavingPlanInvestmentStrategy(monthly_savings=100,
                                        initial_savings=0,
                                        reserves=1000,
                                        monthly_savings_reserves=100,
                                        yearly_interest_rate_on_reserves=5,
                                        yearly_tax_free_allowance=1000,
                                        capital_yields_tax_percentage=25,
                                        duration_simulation=100,
                                        simulation_model=DeterministicSimulationModel(yearly_interest_rate=5),
                                        costs_buy_absolute=1,
                                        costs_sell_absolute=1,
                                        duration_accumulation_phase_in_years=20,
                                        extract_all_at_once=False,
                                        monthly_payoff=100)
strategy.simulate()
profiler.stop()
profiler.print()

