from zone import Zone


class Connection:
    """Represents a bidirectional connection between two zones"""
    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        """Initialize the Connection with its two zones and capacity"""
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.name = f"{zone1.name}-{zone2.name}"
