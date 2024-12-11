from enum import StrEnum


class SimulationModel(StrEnum):
    DETERMINISTIC = "Deterministisch"


class Strategy(StrEnum):
    SAVINGS_PLAN = "Sparplan"
    FLO = "Flo"
