from zone import Zone
from connection import Connection
from zone_role import ZoneRole
from zone_type import ZoneType
import sys


class MapParser:
    """Class to parse the input text"""
    def __init__(self) -> None:
        """Initializing to save the read values in the input text"""
        self.zones: dict[str, Zone] = {}
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.nb_drones: int = 0
        self.connections: list[Connection] = []

    def parse_drone_num(self, line: str) -> None:
        """Parse the number of drones"""
        if line.startswith("nb_drones:"):
            try:
                self.nb_drones = int(line.split(":", 1)[1].strip())
                if self.nb_drones <= 0:
                    raise ValueError(f"Number of drones has to "
                                     f"be higher than 0: {line}")
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid nb_drones format: {e}") from e

    def parse_zone_line(self, line: str, role: ZoneRole) -> Zone:
        """Parses the zone type, returns the Zone with its attributes"""
        try:
            rest = line.split(":", 1)[1]
            parts = rest.strip().split()
            name = parts[0]
            x = int(parts[1])
            y = int(parts[2])

            metadata = self.parse_metadata(line)

            zone_type_text = metadata.get("zone", "normal")
            zone_type = ZoneType(zone_type_text)

            color = metadata.get("color", None)

            if role == ZoneRole.HUB:
                max_drones = int(metadata.get("max_drones", "1"))
                if max_drones <= 0:
                    raise ValueError(f"Max drones has to be "
                                     f"higher than 0: {line}")
            else:
                max_drones = sys.maxsize

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid zones format: {e}") from e
        return Zone(name, x, y, zone_type=zone_type,
                    color=color, max_drones=max_drones, role=role)

    def parse_metadata(self, line: str) -> dict[str, str]:
        """Parses the metadata. Is going to be used in other parse functions"""
        metadata: dict[str, str] = {}
        if "[" in line and "]" in line:
            start = line.index("[") + 1
            end = line.index("]")
            content = line[start:end]
            for pair in content.split():
                key, value = pair.split("=", 1)
                metadata[key] = value
        return metadata

    def parse_connection(self, line: str) -> Connection:
        """Parses the connections and its metadata (max_link_capacity)"""
        try:
            rest = line.split(":", 1)[1].strip()
            names_part = rest.split()[0]
            zone_name1, zone_name2 = names_part.split("-", 1)

            zone1 = self.zones[zone_name1]
            zone2 = self.zones[zone_name2]

            metadata = self.parse_metadata(line)
            max_link_capacity = int(metadata.get("max_link_capacity", "1"))
            if max_link_capacity <= 0:
                raise ValueError(f"Max link capacity has to be "
                                 f"higher than 0: {line}")
        except (KeyError, ValueError, IndexError) as e:
            raise ValueError(f"Invalid connection format: {e}") from e
        return Connection(zone1, zone2, max_link_capacity=max_link_capacity)

    def read_file(self, path: str) -> None:
        """Open, read and parser the file"""
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    if line.startswith("nb_drones:"):
                        self.parse_drone_num(line)

                    elif line.startswith("start_hub:"):
                        if self.start_zone is not None:
                            raise ValueError(f"Start hub "
                                             f"already exists: {line}")
                        zone = self.parse_zone_line(
                            line, ZoneRole.START_HUB
                        )
                        if zone.name in self.zones:
                            raise ValueError(f"Start hub is duplicate: {line}")
                        self.zones[zone.name] = zone
                        self.start_zone = zone

                    elif line.startswith("end_hub:"):
                        if self.end_zone is not None:
                            raise ValueError(f"End hub "
                                             f"already exists: {line}")
                        zone = self.parse_zone_line(line, ZoneRole.END_HUB)

                        if zone.name in self.zones:
                            raise ValueError(f"End hub is duplicate: {line}")
                        self.zones[zone.name] = zone
                        self.end_zone = zone

                    elif line.startswith("hub:"):
                        zone = self.parse_zone_line(line, ZoneRole.HUB)
                        if zone.name in self.zones:
                            raise ValueError(f"Hub is duplicate: {line}")
                        self.zones[zone.name] = zone

                    elif line.startswith("connection:"):
                        conn = self.parse_connection(line)
                        for existing in self.connections:
                            same_conn = (existing.zone1 == conn.zone1
                                         and existing.zone2 == conn.zone2)
                            reversed_conn = (existing.zone1 == conn.zone2
                                             and existing.zone2 == conn.zone1)
                            if same_conn or reversed_conn:
                                raise ValueError(f"Duplicate "
                                                 f"connection: {line}")

                        self.connections.append(conn)
                        conn.zone1.neighbors.append(conn)
                        conn.zone2.neighbors.append(conn)

                    else:
                        raise ValueError(f"Unknown line format: {line}")

                except ValueError as e:
                    raise ValueError(f"Error at line "
                                     f"{line_number}: {e}") from e
