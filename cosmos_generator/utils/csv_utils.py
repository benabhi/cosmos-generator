"""
CSV utilities for Cosmos Generator.

This module provides functions for working with CSV files.
"""
import os
import csv
from typing import Dict, Any, List, Optional

import config
from cosmos_generator.utils.directory_utils import ensure_file_directory


def ensure_planets_csv_exists() -> None:
    """
    Ensure that the planets CSV file exists with the correct header.
    If the file doesn't exist, create it with the header.
    If the file exists but doesn't have a header, add the header.
    """
    # Get the path for the planets CSV file
    planets_path = config.PLANETS_CSV

    # Ensure the directory exists
    ensure_file_directory(planets_path)

    # Check if the file exists
    file_exists = os.path.exists(planets_path)

    if not file_exists:
        # Create the file with the header
        with open(planets_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['seed', 'planet_type', 'variation', 'atmosphere', 'rings', 'clouds'])
    else:
        # Check if the file has a header
        try:
            with open(planets_path, 'r', newline='') as csvfile:
                # Read the first line
                first_line = csvfile.readline().strip()

                # If the file is empty or doesn't have the expected header
                if not first_line or 'seed' not in first_line:
                    # Read the existing content
                    csvfile.seek(0)
                    content = csvfile.read()

                    # Write the header and the existing content
                    with open(planets_path, 'w', newline='') as f:
                        f.write('seed,planet_type,variation,atmosphere,rings,clouds\n')
                        f.write(content)
        except Exception:
            # If there's an error reading the file, create a new one with the header
            with open(planets_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['seed', 'planet_type', 'variation', 'atmosphere', 'rings', 'clouds'])


# The create_planet_details_csv function has been removed because we now use planets.csv


def append_to_planets_csv(planet_type: str, variation: str, seed: str, atmosphere: int, rings: int, clouds: int) -> bool:
    """
    Append a new planet to the planets CSV file.

    Args:
        planet_type: Type of planet
        variation: Variation of the planet
        seed: Seed used for generation (as string)
        atmosphere: Whether the planet has an atmosphere (0 or 1)
        rings: Whether the planet has rings (0 or 1)
        clouds: Whether the planet has clouds (0 or 1)

    Returns:
        True if the planet was added, False if it already exists
    """
    # Ensure the planets CSV file exists with the correct header
    ensure_planets_csv_exists()

    # Get the path for the planets CSV file
    planets_path = config.PLANETS_CSV

    # Check if a planet with this seed already exists
    with open(planets_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['seed'] == seed:
                return False  # Planet with this seed already exists

    # Open the file in append mode
    with open(planets_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write data
        writer.writerow([seed, planet_type.lower(), variation, atmosphere, rings, clouds])

    return True  # Planet was added successfully


def get_all_seeds() -> List[str]:
    """
    Get a list of all seeds from the planets CSV file.

    Returns:
        List of seeds
    """
    # Ensure the planets CSV file exists with the correct header
    ensure_planets_csv_exists()

    # Get the path for the planets CSV file
    planets_path = config.PLANETS_CSV

    # Read the seeds from the CSV file
    seeds = []
    with open(planets_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            seeds.append(row['seed'])

    return seeds


def is_seed_used(seed: str) -> bool:
    """
    Check if a seed has already been used.

    Args:
        seed: Seed to check

    Returns:
        True if the seed has been used, False otherwise
    """
    return seed in get_all_seeds()


def get_planet_details(seed: str) -> Optional[Dict[str, Any]]:
    """
    Get details about a generated planet from the planets CSV file.

    Args:
        seed: Seed used for generation (as string)

    Returns:
        Dictionary with planet details, or None if the planet doesn't exist
    """
    # Ensure the planets CSV file exists with the correct header
    ensure_planets_csv_exists()

    # Get the path for the planets CSV file
    planets_path = config.PLANETS_CSV

    # Read the details from the CSV file
    with open(planets_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if this is the planet we're looking for
            if row['seed'] == seed:
                # Convert string values to appropriate types
                details = {
                    'type': row['planet_type'],
                    'variation': row['variation'],
                    'atmosphere': row['atmosphere'] == '1',
                    'rings': row['rings'] == '1',
                    'clouds': row['clouds'] == '1'
                }
                return details

    # If we get here, the planet wasn't found
    return None
