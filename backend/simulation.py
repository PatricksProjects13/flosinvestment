from abc import ABC, abstractmethod

from backend.utils import convert_yearly_interest_to_monthly

import numpy as np


class AbstractSimulationModel(ABC):
    @abstractmethod
    def __call__(self, current_price: float) -> float:
        pass


class DeterministicSimulationModel(AbstractSimulationModel):
    def __init__(self, yearly_interest_rate: float):
        self.monthly_interest_rate = convert_yearly_interest_to_monthly(yearly_interest_rate)

    def __call__(self, current_price: float) -> float:
        return current_price * (1 + self.monthly_interest_rate / 100)


class SimpleNormalDistributionSimulationModel(AbstractSimulationModel):
    def __init__(self, average_yearly_interest_rate: float, sigma: float):
        self.average_monthly_interest_rate = convert_yearly_interest_to_monthly(average_yearly_interest_rate)
        self.sigma = sigma

    def __call__(self, current_price: float) -> float:
        rate = np.random.normal(loc=self.average_monthly_interest_rate, scale=self.sigma)
        return current_price * (1 + rate / 100)
