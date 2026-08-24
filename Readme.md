*This project has been created as part of the 42 curriculum by <sllabres>.*

## Description

Flyin is a Python simulation of a fleet of autonomous drones routing from a
start zone to an end zone across a network of connected zones. The program
parses a text-based map description (zones, connection topology, capacity
constraints and zone types), computes a reference shortest-cost path with a
custom Dijkstra implementation, and then runs a turn-by-turn simulation in
which every drone attempts to advance one step per turn while respecting
zone occupancy limits, connection capacity limits, and the two-turn transit
rule for `restricted` zones.

The goal is to move every drone from the start zone to the end zone in as
few simulation turns as possible, while never violating any capacity or
movement-cost constraint defined by the input map.

## Instructions

Requires **Python 3.10+** (the project uses the `X | None` union type syntax
introduced in that version).

```bash
make install     # installs flake8 and mypy for linting
make run MAP=maps/hard/01_maze_nightmare.txt   # runs on a specific map
make debug        # runs the simulation under pdb
make lint         # runs flake8 + mypy (standard mode)
make lint-strict   # runs flake8 + mypy --strict
make clean        # removes __pycache__ / .mypy_cache
```

You can also run it directly:
```bash
python3 main.py <path_to_map_file>
```

## Algorithm Explanation

**Graph representation.** No graph library is used. Each `Zone` is a node
that keeps a list of the `Connection` objects it participates in
(`zone.neighbors`); each `Connection` stores references to the two `Zone`
objects it links (not just their names), which lets any zone list its
reachable neighbors without a central lookup structure.

**Pathfinding (`Pathfinder`).** A custom Dijkstra implementation computes
the minimum-cost path from the start zone to the end zone, where the cost
of entering a zone depends on its type (`normal`/`priority` = 1 turn,
`restricted` = 2 turns, `blocked` = never enterable). The current
implementation selects the next zone to visit with a linear scan
(`min()` over the unvisited zones) rather than a priority queue, giving a
time complexity of roughly O(V² + E) instead of the O((V + E) log V) that a
binary-heap-based Dijkstra would achieve. For the map sizes in this project
this trade-off keeps the code considerably simpler without a measurable
performance cost, though swapping in Python's `heapq` would be the natural
next optimization.

**All drones currently share the same reference path**, computed once
(since Dijkstra ignores capacity and all drones share the same start/end
zones, the ideal path is identical for all of them). Divergence between
drones' actual behaviour comes entirely from the simulation layer below,
not from the pathfinding layer.

**Turn-based simulation (`Simulation`).** Rather than pre-planning all
turns in advance, the simulation tracks *live* occupancy: `zone_occupancy`
and `connection_occupancy` dictionaries record how many drones currently
occupy each zone/connection. Every turn, each non-delivered drone attempts
to advance to the next zone in its path; the move is only committed if both
the destination zone and the connection have free capacity, otherwise the
drone waits and retries next turn. `restricted` zones are handled as a
special two-turn move: capacity in the destination zone is reserved
immediately (so no drone can "lose" a promised slot mid-transit), while the
drone's actual position only updates on the following turn, at which point
it can no longer be redirected — matching the rule that a drone cannot wait
mid-connection for a free slot to open up.

Connections are released via a small "release schedule"
(`connection_releases`, keyed by future turn number) rather than freed
synchronously, so a normal 1-turn move frees its connection at the start of
the following turn, while a 2-turn restricted move keeps it occupied for
both turns of the transit.

## Visual Representation

The simulation output is printed to the terminal with ANSI color codes
(`TerminalColors`), colouring each zone name in the movement log according
to the `color` metadata defined for that zone in the input map file. Colors
that are `None` or not recognised fall back to plain, uncoloured text
instead of raising an error, since the map format allows arbitrary color
strings. This makes it easier to visually track, at a glance, which type of
zone each drone is moving through turn by turn, without needing to cross
reference the raw map file.

A short summary is also printed after the simulation output: total number
of turns, drones delivered, and the minimum/maximum/average number of turns
taken per individual drone.

## Example Input and Output

Example input (`example_map.txt`):
```
nb_drones: 3
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
connection: hub-roof1
connection: hub-corridorA
connection: corridorA-goal [max_link_capacity=2]
```

Example output shape (`python3 main.py example_map.txt`):
```
D1-hub-roof1 D2-corridorA
D1-roof1 D2-goal
...
Total turns: N
Drones delivered: 3/3
Turns per drone - min: X, max: Y, avg: Z
```

(Exact turn counts depend on the full map topology and capacity values.)

## Resources

- [42 Fly-in subject](https://cdn.intra.42.fr/pdf/pdf/204766/en.subject.pdf)
- Dijkstra's algorithm — general graph theory background.
- Python `typing` / `enum` / `dataclasses` documentation for type-safe OOP
  design.

**AI usage disclosure:** Claude (Anthropic) was used to sumarize and explain the subject as some bugs solving I couldn't fix by myself. Also for the visualization and structure of the Readme and examples of maps to prove each error requeriment.