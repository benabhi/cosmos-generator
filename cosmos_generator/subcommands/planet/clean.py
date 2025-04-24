"""
Clean subcommand for the Planet CLI.
Handles the deletion of planet-related output directories and files.
"""
import argparse
import os
import shutil
import csv

from typing import Any

import config


def register_subcommand(subparsers: Any) -> None:
    """
    Register the 'clean' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "clean",
        help="Clean planet output directories",
        description="Delete generated planet files and directories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Create a mutually exclusive group for the arguments
    group = parser.add_mutually_exclusive_group(required=True)

    # Add the mutually exclusive arguments
    group.add_argument("--all", action="store_true",
                      help="Clean all generated planets, empty planets.log and reset planets.csv")
    group.add_argument("--seeds", type=str,
                      help="Clean specific planets by seed (comma-separated list, e.g., 12345,67890)")


def main(args: argparse.Namespace) -> int:
    """
    Main function for the 'clean' subcommand.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Initialize counters
    planets_removed = 0

    if args.all:
        # Clean all planets
        print("Cleaning all generated planets...")

        # Clean all planet type directories
        for planet_type in config.PLANET_TYPES:
            planet_type_dir = os.path.join(config.PLANETS_DIR, planet_type.lower())

            if os.path.exists(planet_type_dir):
                # Get all seed directories
                seed_dirs = [d for d in os.listdir(planet_type_dir)
                            if os.path.isdir(os.path.join(planet_type_dir, d))]

                for seed_dir in seed_dirs:
                    seed_path = os.path.join(planet_type_dir, seed_dir)
                    try:
                        # Remove the seed directory and all its contents
                        shutil.rmtree(seed_path)
                        print(f"Removed planet {planet_type.lower()}/{seed_dir}")
                        planets_removed += 1
                    except Exception as e:
                        print(f"Error removing planet {planet_type.lower()}/{seed_dir}: {e}")

        # Clean planets.log
        if os.path.exists(config.PLANETS_LOG_FILE):
            try:
                # Empty the log file but keep it
                with open(config.PLANETS_LOG_FILE, 'w') as f:
                    pass
                print(f"Emptied log file: {config.PLANETS_LOG_FILE}")
            except Exception as e:
                print(f"Error emptying log file: {e}")

        # Clean planets.csv
        planets_csv_path = config.PLANETS_CSV
        if os.path.exists(planets_csv_path):
            try:
                # Write only the header to the CSV file
                with open(planets_csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['seed', 'planet_type', 'variation', 'atmosphere', 'rings', 'clouds'])
                print(f"Reset CSV file: {planets_csv_path}")
            except Exception as e:
                print(f"Error resetting CSV file: {e}")

        print(f"Removed {planets_removed} planets in total.")

    elif args.seeds:
        # Clean specific planets by seed
        seeds = [s.strip() for s in args.seeds.split(',')]
        print(f"Cleaning planets with seeds: {', '.join(seeds)}...")

        # Ensure seeds are in the correct format (8 digits)
        formatted_seeds = []
        for seed in seeds:
            # Convert to integer and back to string to remove any non-numeric characters
            try:
                seed_int = int(seed)
                # Format as 8-digit string
                formatted_seed = f"{seed_int:08d}"
                formatted_seeds.append(formatted_seed)
            except ValueError:
                print(f"Warning: Invalid seed '{seed}', must be a number.")

        # Find and remove the specified planets
        for planet_type in config.PLANET_TYPES:
            planet_type_dir = os.path.join(config.PLANETS_DIR, planet_type.lower())

            if os.path.exists(planet_type_dir):
                for formatted_seed in formatted_seeds:
                    seed_path = os.path.join(planet_type_dir, formatted_seed)

                    if os.path.exists(seed_path):
                        try:
                            # Remove the seed directory and all its contents
                            shutil.rmtree(seed_path)
                            print(f"Removed planet {planet_type.lower()}/{formatted_seed}")
                            planets_removed += 1
                        except Exception as e:
                            print(f"Error removing planet {planet_type.lower()}/{formatted_seed}: {e}")

        # Remove entries from planets.csv
        planets_csv_path = config.PLANETS_CSV
        if os.path.exists(planets_csv_path):
            try:
                # Read the current CSV file
                rows = []
                with open(planets_csv_path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    header = next(reader)  # Save the header
                    for row in reader:
                        if row and row[0] not in formatted_seeds:
                            rows.append(row)

                # Write back the CSV file without the removed planets
                with open(planets_csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(rows)

                print(f"Updated CSV file: {planets_csv_path}")
            except Exception as e:
                print(f"Error updating CSV file: {e}")

        print(f"Removed {planets_removed} planets in total.")

    return 0
