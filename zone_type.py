from enum import Enum


class ZoneType(Enum):
    """Represents the existing type zone we are going to work with"""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
