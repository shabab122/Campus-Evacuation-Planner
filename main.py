"""Small command-line demo using the same fallback policy as the dashboard."""

import argparse

from src.evaluation import ALGORITHMS, run_algorithm
from src.scenarios import build_grid, load_locations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="All exit corridors blocked (stairs fallback)")
    parser.add_argument("--algorithm", choices=list(ALGORITHMS), default="A*")
    parser.add_argument("--location", default="Room A")
    args = parser.parse_args()
    locations = load_locations()
    if args.location not in locations:
        parser.error(f"Unknown location: {args.location}. Choose from {', '.join(locations)}")
    try:
        grid = build_grid(args.scenario, locations[args.location])
    except ValueError as error:
        parser.error(str(error))
    result = run_algorithm(args.algorithm, grid)
    print(result["message"])
    print("Destination:", result["destination_type"], result["selected_destination"])
    print("Route risk:", result["risk_level"])
    print("Path:", result["path"])
    print("Route cost:", result["route_cost"])
    print("Expanded nodes (all stages):", result["nodes_explored"])


if __name__ == "__main__":
    main()
