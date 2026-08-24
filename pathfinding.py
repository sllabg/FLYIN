from zone import Zone
from zone_type import ZoneType


class Pathfinder:
    MOVEMENT_COST = {
        ZoneType.NORMAL: 1,
        ZoneType.PRIORITY: 1,
        ZoneType.RESTRICTED: 2,
    }

    """Calculates the shortest-cost path between two zones using Dijkstra"""
    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        """Return the ordered list of zones from start
        to end, minimizing total turn cost."""
        distances: dict[Zone, int] = {start: 0}
        visited: set[Zone] = set()
        previous: dict[Zone, Zone] = {}

        while len(distances) > len(visited):
            unvisited = [zone for zone in distances if zone not in visited]
            current = min(unvisited, key=lambda zone: distances[zone])
            visited.add(current)

            for neighbor in current.get_neighboring_zones():
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue

                cost = self.MOVEMENT_COST[neighbor.zone_type]
                new_distance = distances[current] + cost
                cond = (
                    neighbor not in distances
                    or new_distance < distances[neighbor]
                )
                if cond:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current

        if end not in distances:
            raise ValueError(f"No path found from {start.name} to {end.name}")

        path: list[Zone] = []
        current_end = end
        while current_end != start:
            path.append(current_end)
            current_end = previous[current_end]
        path.append(start)
        path.reverse()
        return path
