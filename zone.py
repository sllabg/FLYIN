from typing import TYPE_CHECKING
from zone_type import ZoneType
from zone_role import ZoneRole

if TYPE_CHECKING:
    from connection import Connection


class Zone:
    """Represents a single zone (node) in the drone network"""
    def __init__(self, name: str, x: int, y: int,
                 zone_type: ZoneType = ZoneType.NORMAL,
                 color: str | None = None,
                 max_drones: int = 1,
                 role: ZoneRole = ZoneRole.HUB) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.role = role
        self.neighbors: list["Connection"] = []
        """Initialize a Zone withits position, type and metadata"""

    def get_neighboring_zones(self) -> list["Zone"]:
        """Return the list of zones directly reachable from this zone"""
        zones: list["Zone"] = []
        for connection in self.neighbors:
            if connection.zone1 == self:
                zones.append(connection.zone2)
            else:
                zones.append(connection.zone1)
        return zones

    def get_connection_to(self, other: "Zone") -> "Connection":
        """Return the connection linking this zone to the given neighbor."""
        for connection in self.neighbors:
            if connection.zone1 == other or connection.zone2 == other:
                return connection
        raise ValueError(f"No connection between {self.name} and {other.name}")
