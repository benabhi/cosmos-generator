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
    ensure_planet_seed_structure,
    ensure_directory_exists
)
from cosmos_generator.utils.csv_utils import append_to_planets_csv, ensure_planets_csv_exists

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
    parser.add_argument("--rings-complexity", type=int, default=None, choices=[1, 2, 3],
                       help="Ring system complexity (1=minimal, 2=medium, 3=full)")
    parser.add_argument("--rings-tilt", type=float, default=None,
                       help="Tilt angle of the rings in degrees (0-90, where 0=edge-on, 90=face-on)")
    parser.add_argument("--atmosphere", action="store_true",
                       help="Add atmosphere")
    parser.add_argument("--atmosphere-glow", type=float, default=0.5,
                       help="Atmosphere glow intensity (0.0-1.0)")
    parser.add_argument("--atmosphere-halo", type=float, default=0.7,
                       help="Atmosphere halo intensity (0.0-1.0)")
    parser.add_argument("--atmosphere-thickness", type=int, default=3,
                       help="Atmosphere halo thickness in pixels (1-10)")
    parser.add_argument("--atmosphere-blur", type=float, default=0.5,
                       help="Atmosphere blur amount (0.0-1.0)")
    parser.add_argument("--clouds", action="store_true",
                       help="Add clouds")
    parser.add_argument("--clouds-coverage", type=float, default=None,
                       help="Cloud coverage (0.0-1.0)")
    parser.add_argument("--variation", type=str, default=None,
                       help="Texture variation (depends on planet type)")
    parser.add_argument("--color-palette-id", type=int, default=None, choices=[1, 2, 3, 4, 5],
                       help="Color palette ID (1-5, default: random, note: only Jovian planets support values 4-5)")

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

    # Note: --list-types and --list-variations have been moved to the planet level


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

    # Note: --list-types and --list-variations are now handled at the planet level

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

    # Standardize seed to 8 characters (pad with zeros if needed)
    # If seed is longer than 8 characters, use the first 8
    seed_str = str(seed)
    if len(seed_str) > 8:
        seed_str = seed_str[:8]
    else:
        seed_str = seed_str.zfill(8)

    # Convert seed_str back to integer for use in generation
    seed_int = int(seed_str)

    # Prepare parameters
    params = {
        "seed": seed_int,  # Use the standardized integer seed
        "size": config.PLANET_SIZE,  # Fixed size, not configurable by users
        "light_intensity": args.light_intensity,
        "light_angle": args.light_angle,
    }

    # Add optional features
    if args.rings:
        params["rings"] = True
        # Add rings parameters if provided, otherwise use random values
        if args.rings_complexity is not None:
            params["rings_complexity"] = args.rings_complexity
            print(f"Using rings complexity: {args.rings_complexity}")
        else:
            # Random complexity between 1 and 3
            complexity = random.randint(1, 3)
            params["rings_complexity"] = complexity
            print(f"Using random rings complexity: {complexity}")

        if args.rings_tilt is not None:
            # Ensure tilt is between 0 and 90 degrees
            tilt = max(0.0, min(90.0, args.rings_tilt))
            params["rings_tilt"] = tilt
            print(f"Using rings tilt: {tilt} degrees")
        else:
            # Random tilt between 10 and 45 degrees
            tilt = random.uniform(10.0, 45.0)
            params["rings_tilt"] = tilt
            print(f"Using random rings tilt: {tilt:.1f} degrees")

    if args.atmosphere:
        params["atmosphere"] = True
        # Add atmosphere parameters
        params["atmosphere_glow"] = max(0.0, min(1.0, args.atmosphere_glow))
        params["atmosphere_halo"] = max(0.0, min(1.0, args.atmosphere_halo))
        params["atmosphere_thickness"] = max(1, min(10, args.atmosphere_thickness))
        params["atmosphere_blur"] = max(0.0, min(1.0, args.atmosphere_blur))

    if args.clouds or args.clouds_coverage is not None:
        params["clouds"] = True

        # If clouds-coverage is provided, use that value
        if args.clouds_coverage is not None:
            params["cloud_coverage"] = max(0.0, min(1.0, args.clouds_coverage))
            print(f"Using cloud coverage: {params['cloud_coverage']:.1f}")
        else:
            # Generate random cloud coverage between 0.3 and 0.8 for better visibility
            coverage = random.uniform(0.3, 0.8)
            params["cloud_coverage"] = coverage
            print(f"Using random cloud coverage: {coverage:.1f}")

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

    # Handle color palette ID parameter
    if args.color_palette_id is not None:
        params["color_palette_id"] = args.color_palette_id
        print(f"Using color palette ID: {args.color_palette_id}")
    else:
        print(f"Using random color palette ID")

    # Create the planet instance
    start_time = time.time()
    try:
        # Log only to file, not to console
        logger.info(f"Generating {planet_type} planet with seed {seed_int}", "cli", console=False)
        planet = generator.create(planet_type, params)
        print(f"Starting generation of {planet_type} planet with seed {seed_int}...")
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Error generating planet: {e}", "cli", exc_info=True)
        print(f"Error generating planet: {e}")
        return 1

    # Ensure all output directories exist
    ensure_output_directories()

    # Ensure planets.csv exists with the correct header
    ensure_planets_csv_exists()

    # We already standardized the seed earlier, no need to do it again
    # The seed_str variable already contains the standardized seed

    # Determine feature flags (0 or 1)
    has_atmosphere = 1 if args.atmosphere else 0
    has_clouds = 1 if args.clouds or args.clouds_coverage is not None else 0
    has_rings = 1 if args.rings else 0

    # Get variation (use default if not specified)
    variation = params.get('variation', config.DEFAULT_PLANET_VARIATIONS.get(planet_type.lower(), 'standard'))

    # Ensure the seed directory structure exists
    ensure_planet_seed_structure(planet_type.lower(), seed_str)

    # Determine output path
    output_path = args.output
    if output_path is None:
        # Use default output path with new structure: output/planets/[planet_type]/[seed]/planet.png
        output_path = config.get_planet_result_path(planet_type.lower(), seed_str)
        logger.debug(f"Using default output path: {output_path}", "cli")
    else:
        # Ensure the directory exists for the specified output path
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_directory_exists(output_dir)
        logger.debug(f"Using custom output path: {output_path}", "cli")

    # Append to planets CSV file
    planet_added = append_to_planets_csv(
        planet_type.lower(),
        variation,
        seed_str,
        has_atmosphere,
        has_rings,
        has_clouds
    )

    # Check if the planet already exists
    if not planet_added:
        logger.error(f"A planet with seed {seed_str} already exists", "cli")
        print(f"Error: A planet with seed {seed_str} already exists. Please use a different seed.")
        return 1

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
