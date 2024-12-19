from enum import StrEnum


class SimulationModel(StrEnum):
    DETERMINISTIC = "Deterministisch"
    SIMPLE_NORMAL_DISTRIBUTION = "Einfache Normalverteilung"


class Strategy(StrEnum):
    SAVINGS_PLAN = "Sparplan"
    FLO = "Flo"

