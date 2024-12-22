from dataclasses import dataclass

from backend.constants import Strategy, SimulationModel


@dataclass
class DeterministicSimulationParameters:
    yearly_interest_rate: float  # Jährlicher Zinssatz


@dataclass
class SimpleNormalDistributionSimulationParameters:
    average_yearly_interest_rate: float  # Durchschnittlicher jährlicher Zinssatz
    sigma: float  # Volatilität
    number_of_simulations: int


@dataclass
class FloStrategyParameters:
    initial_stock_prize: float  # Anfänglicher Aktienpreis
    target_number_of_stocks: int  # Zielgröße, wie viele Aktien (bei mittlerem Preis besessen werden sollen)
    duration_months_for_rolling_average_stock_prize: int  # Anzahl an Monate, über die der Aktienpreis gemittelt werden soll
    step_size: int  # Sogenannter Stufenschritt in Flos Modell. Im Grund ein Multiplikator. um aus Kursabweichungen Aktienmengen zu berechnen
    prize_step_size: int  # Diskretisierung von Kursschwankungen
    average_yearly_interest_rate: float  # Durchschnittlicher jährlicher Zinssatz
    sigma: float  # Vola


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
    flo_strategy_parameters: FloStrategyParameters | None = None
