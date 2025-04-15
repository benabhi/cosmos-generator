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

from cosmos_generator.utils.logger import logger

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
    parser.add_argument("--size", type=int, default=512,
                       help="Image size in pixels")
    parser.add_argument("--seed", type=int, default=None,
                       help="Seed for reproducible generation")

    # Features
    parser.add_argument("--rings", action="store_true",
                       help="Add rings")
    parser.add_argument("--atmosphere", action="store_true",
                       help="Add atmosphere")
    parser.add_argument("--clouds", type=float, default=None,
                       help="Cloud coverage (0.0-1.0)")

    # Lighting
    parser.add_argument("--light-intensity", type=float, default=1.0,
                       help="Light intensity (0.0-2.0)")
    parser.add_argument("--light-angle", type=float, default=45.0,
                       help="Light source angle (0-359)")

    # Container
    parser.add_argument("--rotation", type=float, default=0.0,
                       help="Rotation in degrees")

    # List available planet types
    parser.add_argument("--list-types", action="store_true",
                       help="List available planet types")


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
        "size": args.size,
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

    # For Ocean planets, randomly choose between archipelago and water_world styles
    if planet_type.lower() == "ocean":
        ocean_styles = ["archipelago", "water_world"]
        chosen_style = random.choice(ocean_styles)
        params["ocean_style"] = chosen_style
        print(f"Randomly selected Ocean style: {chosen_style}")

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

    # Determine output path
    output_path = args.output
    if output_path is None:
        # Create default output directory structure
        output_dir = os.path.join("output", "planets", "result", planet_type.lower())
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{seed}.png")
        logger.debug(f"Using default output path: {output_path}", "cli")
    else:
        # Ensure the directory exists for the specified output path
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Using custom output path: {output_path}", "cli")

    # Always use container for consistent display
    container = Container()
    container.set_content(planet)

    if args.rotation != 0.0:
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
