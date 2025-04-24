#!/usr/bin/env python3
"""
Script to generate 100 random planets with random parameters.
This script uses the CLI to generate planets with random types, variations, and features.

This script supports all planet types and variations available in the generator,
including Desert, Ocean, Furnace, Jovian, Vital, Toxic, Ice, Rocky, and Jungle planets
with all their respective variations.

Features supported:
- Random planet types and variations
- Random seeds
- Random lighting parameters (intensity and angle)
- Random features (rings, atmosphere, clouds)
- Random rings parameters (complexity and tilt)
- Random atmosphere parameters
- Random cloud coverage
- Random zoom and rotation
- Random color palette selection
"""
import os
import sys
import random
import subprocess
import re
from typing import Dict, List, Any, Optional

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Import config to get planet types and variations
import config


def get_planet_types() -> List[str]:
    """
    Get a list of available planet types using the CLI.

    Returns:
        List of planet types
    """
    print("Getting available planet types...")
    result = subprocess.run(
        ["python", "-m", "cosmos_generator", "planet", "--list-types"],
        capture_output=True,
        text=True
    )

    # Parse the output to extract planet types
    types = []
    for line in result.stdout.splitlines():
        if line.strip().startswith("-"):
            # Extract the planet type from the line (format: "  - PlanetType")
            planet_type = line.strip().split("-")[1].strip()
            types.append(planet_type)

    print(f"Found {len(types)} planet types: {', '.join(types)}")
    return types


def get_planet_variations() -> Dict[str, List[str]]:
    """
    Get a dictionary of available variations for each planet type using the CLI.

    Returns:
        Dictionary mapping planet types to lists of variations
    """
    print("Getting available planet variations...")
    result = subprocess.run(
        ["python", "-m", "cosmos_generator", "planet", "--list-variations"],
        capture_output=True,
        text=True
    )

    # Parse the output to extract variations for each planet type
    variations = {}
    current_type = None

    for line in result.stdout.splitlines():
        line = line.strip()

        # Check if this line defines a planet type
        if line.endswith(":") and not line.startswith("-"):
            # Extract the planet type from the line (format: "  PlanetType:")
            current_type = line.rstrip(":").strip().lower()
            variations[current_type] = []

        # Check if this line defines a variation
        elif line.startswith("-") and current_type is not None:
            # Extract the variation from the line (format: "    - variation")
            variation = line.split("-")[1].strip()
            # If there's a description in parentheses, remove it
            if "(" in variation:
                variation = variation.split("(")[0].strip()
            variations[current_type].append(variation)

    # Print the variations found for each type
    for planet_type, type_variations in variations.items():
        print(f"Found {len(type_variations)} variations for {planet_type}: {', '.join(type_variations)}")

    return variations


def generate_random_parameters() -> Dict[str, Any]:
    """
    Generate random parameters for planet generation.

    Returns:
        Dictionary of random parameters
    """
    params = {}

    # Random seed
    params["seed"] = random.randint(1, 1000000)

    # Random lighting
    params["light_intensity"] = round(random.uniform(0.5, 1.5), 1)
    params["light_angle"] = random.randint(0, 359)

    # Random color palette (33% chance of using a specific palette)
    if random.random() < 0.33:
        params["color_palette_id"] = random.randint(1, 3)

    # Random features with 50% probability each
    if random.random() < 0.5:
        params["rings"] = True
        # Random rings complexity with 33% probability for each level
        if random.random() < 0.33:
            params["rings_complexity"] = 1
        elif random.random() < 0.66:
            params["rings_complexity"] = 2
        else:
            params["rings_complexity"] = 3

        # Random rings tilt (0-75 degrees)
        params["rings_tilt"] = random.randint(0, 75)

    if random.random() < 0.5:
        params["atmosphere"] = True
        # Random atmosphere parameters
        params["atmosphere_glow"] = round(random.uniform(0.3, 1.0), 1)
        params["atmosphere_halo"] = round(random.uniform(0.3, 1.0), 1)
        params["atmosphere_thickness"] = random.randint(1, 10)
        params["atmosphere_blur"] = round(random.uniform(0.3, 1.0), 1)

    if random.random() < 0.5:
        # Enable clouds
        params["clouds"] = True
        # Random cloud coverage
        params["clouds_coverage"] = round(random.uniform(0.1, 1.0), 1)

    # Random zoom (en el rango 0.7-1.0) y rotation
    params["zoom"] = round(random.uniform(0.7, 1.0), 1)
    params["rotation"] = random.randint(0, 359)

    return params


def build_command(planet_type: str, variation: Optional[str], params: Dict[str, Any]) -> List[str]:
    """
    Build the command to generate a planet with the given parameters.

    Args:
        planet_type: Type of planet to generate
        variation: Variation to use (or None for default)
        params: Dictionary of parameters

    Returns:
        List of command arguments
    """
    cmd = ["python", "-m", "cosmos_generator", "planet", "generate", "--type", planet_type]

    # Add variation if specified
    if variation:
        cmd.extend(["--variation", variation])

    # Parameter name mapping (from our keys to CLI parameter names)
    param_mapping = {
        "light_intensity": "light-intensity",
        "light_angle": "light-angle",
        "rings_complexity": "rings-complexity",
        "rings_tilt": "rings-tilt",
        "atmosphere_glow": "atmosphere-glow",
        "atmosphere_halo": "atmosphere-halo",
        "atmosphere_thickness": "atmosphere-thickness",
        "atmosphere_blur": "atmosphere-blur",
        "color_palette_id": "color-palette-id",
        "clouds_coverage": "clouds-coverage"
    }

    # Add all other parameters
    for key, value in params.items():
        # Skip the 'type' parameter as it's already added
        if key == "type":
            continue

        # Convert parameter name if needed
        cli_param = param_mapping.get(key, key)

        if isinstance(value, bool) and value:
            # For boolean flags, just add the flag
            cmd.append(f"--{cli_param}")
        elif not isinstance(value, bool):
            # For value parameters, add the flag and value
            cmd.append(f"--{cli_param}")
            cmd.append(str(value))

    return cmd


def generate_random_planet(planet_types: List[str], variations: Dict[str, List[str]]) -> None:
    """
    Generate a random planet with random parameters.

    Args:
        planet_types: List of available planet types
        variations: Dictionary mapping planet types to lists of variations
    """
    # Select a random planet type
    planet_type = random.choice(planet_types)
    planet_type_lower = planet_type.lower()

    # Select a random variation for this planet type (50% chance of using default)
    variation = None
    if random.random() > 0.5 and planet_type_lower in variations and variations[planet_type_lower]:
        variation = random.choice(variations[planet_type_lower])

    # Generate random parameters
    params = generate_random_parameters()

    # Build the command
    cmd = build_command(planet_type, variation, params)

    # Print the command
    print(f"Generating planet: {' '.join(cmd)}")

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        # Extract the output path from the output
        match = re.search(r"Planet generated and saved to (.*) in", result.stdout)
        if match:
            output_path = match.group(1)
            print(f"Planet generated successfully: {output_path}")
        else:
            print("Planet generated successfully (output path not found in output)")
    else:
        print(f"Error generating planet: {result.stderr}")


def main() -> None:
    """
    Main function to generate random planets.
    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate random planets with random parameters.")
    parser.add_argument(
        "--count", "-n", type=int, default=100,
        help="Number of planets to generate (default: 100)"
    )
    args = parser.parse_args()

    count = args.count

    print(f"Starting random planet generation script to create {count} planets...")

    # Get available planet types and variations
    planet_types = get_planet_types()
    variations = get_planet_variations()

    # Generate random planets
    print(f"\nGenerating {count} random planets...")
    for i in range(1, count + 1):
        print(f"\n--- Generating planet {i}/{count} ---")
        generate_random_planet(planet_types, variations)

    print("\nAll planets generated successfully!")


if __name__ == "__main__":
    main()
