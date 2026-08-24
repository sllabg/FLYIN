from enum import Enum


class ZoneRole(Enum):
    """Created to diferenciate the START from the END mostly"""
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
