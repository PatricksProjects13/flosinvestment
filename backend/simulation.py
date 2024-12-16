from abc import ABC, abstractmethod

from backend.utils import convert_yearly_interest_to_monthly


class AbstractSimulationModel(ABC):
    @abstractmethod
    def __call__(self, current_price: float) -> float:
        pass


class DeterministicSimulationModel(AbstractSimulationModel):
    def __init__(self, yearly_interest_rate: float):
        self.monthly_interest_rate = convert_yearly_interest_to_monthly(yearly_interest_rate)

    def __call__(self, current_price: float) -> float:
        return current_price * (1 + self.monthly_interest_rate / 100)
