from zone import Zone


class Drone:
    """Represents a drone identified by an id and its current zone."""
    def __init__(self, drone_id: int, current_zone: Zone) -> None:
        """Initialize the drone with its id and starting zone."""
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.path: list["Zone"] = []
        self.path_index: int = 0
