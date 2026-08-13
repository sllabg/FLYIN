import sys

from parser import MapParser
from pathfinding import Pathfinder
from simulation import Simulation
from visualization import TerminalColors


def main() -> None:
    """Entry point: parse a map, run the simulation, print the result."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        return

    map_path = sys.argv[1]

    try:
        map_parser = MapParser()
        map_parser.read_file(map_path)

        pathfinder = Pathfinder()
        simulation = Simulation(map_parser)
        simulation.calculate_paths(pathfinder)
        simulation.run()

        colors = TerminalColors()

        for line in simulation.generate_colored_output(colors):
            print(line)

        print()
        print(simulation.generate_summary())

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
