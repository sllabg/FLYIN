from drone import Drone
from parser import MapParser
from zone import Zone
from connection import Connection
from pathfinding import Pathfinder
from zone_type import ZoneType
from visualization import TerminalColors


class Simulation:
    """Simulates drone movement turn by turn across the network."""
    def __init__(self, map_parser: MapParser) -> None:
        """Initialize the simulation with drones and empty tracking state."""
        if map_parser.start_zone is None or map_parser.end_zone is None:
            raise ValueError("Map must have a start and "
                             "end zone before simulating")

        self.map_parser = map_parser
        self.start_zone: Zone = map_parser.start_zone
        self.end_zone: Zone = map_parser.end_zone

        self.drones: list[Drone] = []
        for drone_id in range(1, map_parser.nb_drones + 1):
            self.drones.append(Drone(drone_id, map_parser.start_zone))

        self.movement_log: dict[int, list[str]] = {}
        self.current_turn: int = 0
        self.delivered: set[Drone] = set()
        self.zone_occupancy: dict[Zone, int] = {}
        self.connection_occupancy: dict[Connection, int] = {}
        self.connection_releases: dict[int, list[Connection]] = {}
        self.in_transit: dict[Drone, int] = {}
        self.arrival_turns: dict[Drone, int] = {}
        self.movement_colors: dict[int, list[str | None]] = {}

    def has_zone_capacity(self, zone: Zone) -> bool:
        """Return True if the zone can currently accept another drone."""
        occupancy = self.zone_occupancy.get(zone, 0)
        return occupancy < zone.max_drones

    def has_connection_capacity(self, connection: Connection) -> bool:
        """Return True if the connection can currently accept another drone."""
        occ = self.connection_occupancy.get(connection, 0)
        return occ < connection.max_link_capacity

    def enter_zone(self, zone: Zone) -> None:
        """Register a drone entering this zone."""
        self.zone_occupancy[zone] = self.zone_occupancy.get(zone, 0) + 1

    def leave_zone(self, zone: Zone) -> None:
        """Register a drone leaving this zone."""
        self.zone_occupancy[zone] = self.zone_occupancy.get(zone, 0) - 1

    def enter_connection(self, connection: Connection) -> None:
        """Register a drone entering this connection."""
        occ = self.connection_occupancy.get(connection, 0)
        self.connection_occupancy[connection] = occ + 1

    def leave_connection(self, connection: Connection) -> None:
        """Register a drone leaving this connection."""
        occ = self.connection_occupancy.get(connection, 0)
        self.connection_occupancy[connection] = occ - 1

    def calculate_paths(self, pathfinder: Pathfinder) -> None:
        """Calculate the ideal reference path for all drones."""
        reference_path = pathfinder.find_path(self.start_zone, self.end_zone)
        for drone in self.drones:
            drone.path = list(reference_path)

    def try_move_drone(self, drone: Drone) -> None:
        """Attempt to move a single drone one step along its path."""
        if drone in self.delivered:
            return
        if drone in self.in_transit:
            return

        next_zone = drone.path[drone.path_index + 1]
        connection = drone.current_zone.get_connection_to(next_zone)

        if not self.has_zone_capacity(next_zone):
            return
        if not self.has_connection_capacity(connection):
            return

        if next_zone.zone_type == ZoneType.RESTRICTED:
            self._start_restricted_move(drone, next_zone, connection)
        else:
            self._complete_normal_move(drone, next_zone, connection)

    def _complete_normal_move(self, drone: Drone, next_zone: Zone,
                              connection: Connection) -> None:
        self.leave_zone(drone.current_zone)
        self.enter_zone(next_zone)
        self.enter_connection(connection)
        self.schedule_connection_release(connection, self.current_turn + 1)

        drone.current_zone = next_zone
        drone.path_index += 1

        self.movement_log.setdefault(self.current_turn, []).append(
            f"D{drone.drone_id}-{next_zone.name}"
        )
        self.movement_colors.setdefault(self.current_turn, []).append(
            next_zone.color
        )

        if next_zone == self.end_zone:
            self.delivered.add(drone)
            self.arrival_turns[drone] = self.current_turn

    def _start_restricted_move(self, drone: Drone, next_zone: Zone,
                               connection: Connection) -> None:
        """Begin a 2-turn move into a restricted zone."""
        self.leave_zone(drone.current_zone)
        self.enter_zone(next_zone)
        self.enter_connection(connection)
        self.schedule_connection_release(connection, self.current_turn + 2)

        self.in_transit[drone] = self.current_turn + 1

        self.movement_log.setdefault(self.current_turn, []).append(
            f"D{drone.drone_id}-{connection.name}"
        )
        self.movement_colors.setdefault(self.current_turn, []).append(
            next_zone.color
        )

    def run_turn(self) -> None:
        """Attempt to move every non-delivered drone by one step."""
        for drone in self.drones:
            self.try_move_drone(drone)

    def schedule_connection_release(self, connection: Connection,
                                    turn: int) -> None:
        """Schedule a connection to be freed at the start of the given turn."""
        self.connection_releases.setdefault(turn, []).append(connection)

    def release_connections(self) -> None:
        """Free connections whose transit time ends at the current turn."""
        connections_to_release = self.connection_releases.get(
            self.current_turn, [])
        for connection in connections_to_release:
            self.leave_connection(connection)

    def run(self) -> None:
        """Run the simulation turn by turn untili all drones are delivered"""
        while len(self.delivered) < len(self.drones):
            self.current_turn += 1
            if self.current_turn > 1000:
                raise ValueError("Simulation did not converge "
                                 "within 1000 turns")
            self.release_connections()
            self.run_turn()
            self.complete_transits()

    def complete_transits(self) -> None:
        """Land any drones whose 2-turn transit ends this turn"""
        arrived_drones = []

        for drone, arrival_turn in self.in_transit.items():
            if self.current_turn != arrival_turn:
                continue

            next_zone = drone.path[drone.path_index + 1]
            drone.current_zone = next_zone
            drone.path_index += 1

            self.movement_log.setdefault(self.current_turn, []).append(
                f"D{drone.drone_id}-{next_zone.name}"
            )
            self.movement_colors.setdefault(self.current_turn, []).append(
                next_zone.color
            )

            if next_zone == self.end_zone:
                self.delivered.add(drone)
                self.arrival_turns[drone] = self.current_turn

            arrived_drones.append(drone)

        for drone in arrived_drones:
            del self.in_transit[drone]

    def generate_colored_output(self, colors: TerminalColors) -> list[str]:
        """Return the simulation output as one colored
        formatted line per turn."""
        output_lines: list[str] = []
        sorted_turns = sorted(self.movement_log.keys())
        for turn in sorted_turns:
            texts = self.movement_log[turn]
            turn_colors = self.movement_colors[turn]
            colored_texts = [
                colors.colorize(text, color)
                for text, color in zip(texts, turn_colors)
            ]
            output_lines.append(" ".join(colored_texts))
        return output_lines

    def generate_summary(self) -> str:
        """Return a short summary of the simulation results."""
        total_turns = self.current_turn
        drones_delivered = len(self.delivered)
        total_drones = len(self.drones)

        turns_per_drone = list(self.arrival_turns.values())
        min_turns = min(turns_per_drone)
        max_turns = max(turns_per_drone)
        avg_turns = sum(turns_per_drone) / len(turns_per_drone)

        return (
            f"Total turns: {total_turns}\n"
            f"Drones delivered: {drones_delivered}/{total_drones}\n"
            f"Turns per drone - min: {min_turns}, "
            f"max: {max_turns}, avg: {avg_turns:.1f}"
        )
