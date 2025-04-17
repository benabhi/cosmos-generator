"""
Generate subcommand for the Planet CLI.
Handles the generation of planets with various features.
"""
import argparse
import os
import sys
import random
import time
from typing import Any

import config
from cosmos_generator.utils.logger import logger
from cosmos_generator.utils.directory_utils import (
    ensure_output_directories,
    get_planet_result_directory,
    ensure_directory_exists
)

# Try to import the required modules
try:
    from cosmos_generator.core.planet_generator import PlanetGenerator
    from cosmos_generator.utils.container import Container
except ImportError:
    # Try with direct imports if the package structure import fails
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from core.planet_generator import PlanetGenerator
    from utils.container import Container


def register_subcommand(subparsers: Any) -> None:
    """
    Register the 'generate' subcommand with its arguments.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "generate",
        help="Generate a planet",
        description="Generate a procedural planet with various features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument("--type", type=str, required=False, default="Desert",
                       help="Planet type (Desert, Furnace, etc.)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file path (default: output/planets/result/[type]/[seed].png, donde se crean las carpetas automáticamente)")

    # Optional arguments
    parser.add_argument("--seed", type=int, default=None,
                       help="Seed for reproducible generation")

    # Features
    parser.add_argument("--rings", action="store_true",
                       help="Add rings")
    parser.add_argument("--atmosphere", action="store_true",
                       help="Add atmosphere")
    parser.add_argument("--clouds", type=float, default=None,
                       help="Cloud coverage (0.0-1.0)")
    parser.add_argument("--variation", type=str, default=None,
                       help="Texture variation (depends on planet type)")

    # Lighting
    parser.add_argument("--light-intensity", type=float, default=1.0,
                       help="Light intensity (0.0-2.0)")
    parser.add_argument("--light-angle", type=float, default=45.0,
                       help="Light source angle (0-359)")

    # Container
    parser.add_argument("--rotation", type=float, default=0.0,
                       help="Rotation in degrees")
    parser.add_argument("--zoom", type=float, default=None,
                       help="Zoom level (0.0-1.0, where 0.0=far away/small, 1.0=very close/large)")

    # List available planet types and variations
    parser.add_argument("--list-types", action="store_true",
                       help="List available planet types")
    parser.add_argument("--list-variations", action="store_true",
                       help="List available variations for each planet type")


def main(args: argparse.Namespace) -> int:
    """
    Main function for the 'generate' subcommand.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Create planet generator
    generator = PlanetGenerator()

    # List available planet types if requested
    if args.list_types:
        print("Available planet types:")
        for planet_type in generator.get_celestial_types():
            print(f"  - {planet_type}")
        return 0

    # List available variations if requested
    if args.list_variations:
        print("Available variations for each planet type:")
        for planet_type, variations in config.PLANET_VARIATIONS.items():
            default_variation = config.DEFAULT_PLANET_VARIATIONS.get(planet_type, "")
            print(f"  {planet_type.title()}:")
            for variation in variations:
                if variation == default_variation:
                    print(f"    - {variation} (default)")
                else:
                    print(f"    - {variation}")
        return 0

    # Convert planet type to title case for case-insensitive matching
    input_type = args.type.title()

    # Get available types and create a case-insensitive mapping
    available_types = generator.get_celestial_types()
    type_mapping = {t.lower(): t for t in available_types}

    # Validate planet type (case-insensitive)
    if input_type.lower() not in type_mapping:
        print(f"Error: Unknown planet type '{args.type}'")
        print("Available types:")
        for planet_type in available_types:
            print(f"  - {planet_type}")
        return 1

    # Get the correct case for the planet type
    planet_type = type_mapping[input_type.lower()]

    # Generate random seed if not provided
    seed = args.seed if args.seed is not None else random.randint(0, 2**32 - 1)

    # Prepare parameters
    params = {
        "seed": seed,
        "size": config.PLANET_SIZE,  # Fixed size, not configurable by users
        "light_intensity": args.light_intensity,
        "light_angle": args.light_angle,
    }

    # Add optional features
    if args.rings:
        params["rings"] = True

    if args.atmosphere:
        params["atmosphere"] = True

    if args.clouds is not None:
        params["clouds"] = True
        params["cloud_coverage"] = max(0.0, min(1.0, args.clouds))

    # Handle variation parameter
    planet_type_lower = planet_type.lower()
    if args.variation is not None:
        # Check if the variation is valid for this planet type
        available_variations = config.PLANET_VARIATIONS.get(planet_type_lower, [])

        if args.variation in available_variations:
            params["variation"] = args.variation
            print(f"Using {args.variation} variation for {planet_type} planet")
        else:
            print(f"Warning: '{args.variation}' is not a valid variation for {planet_type} planets.")
            print(f"Available variations: {', '.join(available_variations)}")
            print(f"Using default variation: {config.DEFAULT_PLANET_VARIATIONS[planet_type_lower]}")
    else:
        # Use default variation from config
        default_variation = config.DEFAULT_PLANET_VARIATIONS.get(planet_type_lower)
        if default_variation:
            params["variation"] = default_variation
            print(f"Using default variation: {default_variation}")

    # Create the planet instance
    start_time = time.time()
    try:
        # Log only to file, not to console
        logger.info(f"Generating {planet_type} planet with seed {seed}", "cli", console=False)
        planet = generator.create(planet_type, params)
        print(f"Starting generation of {planet_type} planet with seed {seed}...")
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Error generating planet: {e}", "cli", exc_info=True)
        print(f"Error generating planet: {e}")
        return 1

    # Ensure all output directories exist
    ensure_output_directories()

    # Determine output path
    output_path = args.output
    if output_path is None:
        # Use default output path: output/planets/result/[planet_type]/[seed].png
        output_dir = get_planet_result_directory(planet_type.lower())
        output_path = os.path.join(output_dir, f"{seed}.png")
        logger.debug(f"Using default output path: {output_path}", "cli")
    else:
        # Ensure the directory exists for the specified output path
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_directory_exists(output_dir)
        logger.debug(f"Using custom output path: {output_path}", "cli")

    # Always use container for consistent display
    zoom_level = args.zoom
    logger.info(f"Using zoom level: {zoom_level}", "cli")

    # Ensure zoom_level is a float if provided
    if zoom_level is not None:
        try:
            zoom_level = float(zoom_level)
            logger.info(f"Converted zoom level to float: {zoom_level}", "cli")
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting zoom level to float: {e}", "cli")
            zoom_level = None

    container = Container(zoom_level=zoom_level)
    container.set_content(planet)

    if args.rotation != 0.0:
        logger.info(f"Setting rotation to {args.rotation} degrees", "cli")
        container.set_rotation(args.rotation)

    try:
        print(f"Generating planet... (this may take a while)")
        container.export(output_path)

        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        print(f"Planet generated and saved to {output_path} in {duration_ms:.2f}ms")

        # Only log to file, not to console
        logger.info(f"Planet generation completed in {duration_ms:.2f}ms", "cli", console=False)
        logger.end_generation(True, output_path)
    except Exception as e:
        logger.error(f"Error saving image: {e}", "cli", exc_info=True)
        print(f"Error saving image: {e}")

        # Log failure
        logger.end_generation(False, error=str(e))
        return 1

    return 0
