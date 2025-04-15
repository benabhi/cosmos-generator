"""
Command-line interface for Cosmos Generator.
"""
import argparse
import sys
import os
import random
from typing import Dict, Any, Optional, List

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Now we can import our modules
try:
    from cosmos_generator.core.planet_generator import PlanetGenerator
    from cosmos_generator.utils.viewport import Viewport
except ImportError:
    # Try with direct imports if the package structure import fails
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from core.planet_generator import PlanetGenerator
    from utils.viewport import Viewport


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate procedural celestial bodies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument("--type", type=str, required=True,
                       help="Planet type (Desert, Furnace, etc.)")
    parser.add_argument("--output", type=str, required=True,
                       help="Output file path")

    # Optional arguments
    parser.add_argument("--size", type=int, default=512,
                       help="Image size in pixels")
    parser.add_argument("--seed", type=int, default=None,
                       help="Seed for reproducible generation")

    # Features
    parser.add_argument("--rings", action="store_true",
                       help="Add rings")
    parser.add_argument("--atmosphere", type=float, default=None,
                       help="Atmosphere intensity (0.0-1.0)")
    parser.add_argument("--clouds", type=float, default=None,
                       help="Cloud coverage (0.0-1.0)")

    # Lighting
    parser.add_argument("--light-intensity", type=float, default=1.0,
                       help="Light intensity (0.0-2.0)")
    parser.add_argument("--light-angle", type=float, default=45.0,
                       help="Light source angle (0-359)")

    # Viewport
    parser.add_argument("--viewport-width", type=int, default=None,
                       help="Viewport width")
    parser.add_argument("--viewport-height", type=int, default=None,
                       help="Viewport height")
    parser.add_argument("--zoom", type=float, default=1.0,
                       help="Zoom factor (0.1-5.0)")
    parser.add_argument("--rotation", type=float, default=0.0,
                       help="Rotation in degrees")
    parser.add_argument("--pan-x", type=int, default=0,
                       help="Horizontal pan offset")
    parser.add_argument("--pan-y", type=int, default=0,
                       help="Vertical pan offset")

    # List available planet types
    parser.add_argument("--list-types", action="store_true",
                       help="List available planet types")

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the command-line interface.

    Returns:
        Exit code
    """
    args = parse_args()

    # Create planet generator
    generator = PlanetGenerator()

    # List available planet types if requested
    if args.list_types:
        print("Available planet types:")
        for planet_type in generator.get_celestial_types():
            print(f"  - {planet_type}")
        return 0

    # Validate planet type
    if args.type not in generator.get_celestial_types():
        print(f"Error: Unknown planet type '{args.type}'")
        print("Available types:")
        for planet_type in generator.get_celestial_types():
            print(f"  - {planet_type}")
        return 1

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

    if args.atmosphere is not None:
        params["atmosphere"] = True
        params["atmosphere_intensity"] = max(0.0, min(1.0, args.atmosphere))

    if args.clouds is not None:
        params["clouds"] = True
        params["cloud_coverage"] = max(0.0, min(1.0, args.clouds))

    # Create the planet
    try:
        planet = generator.create(args.type, params)
        print(f"Generated {args.type} planet with seed {seed}")
    except Exception as e:
        print(f"Error generating planet: {e}")
        return 1

    # Use viewport if specified
    if args.viewport_width or args.viewport_height or args.zoom != 1.0 or args.rotation != 0.0 or args.pan_x != 0 or args.pan_y != 0:
        viewport_width = args.viewport_width if args.viewport_width else args.size
        viewport_height = args.viewport_height if args.viewport_height else args.size

        viewport = Viewport(width=viewport_width, height=viewport_height, initial_zoom=args.zoom)
        viewport.set_content(planet)
        viewport.set_rotation(args.rotation)
        viewport.set_pan(args.pan_x, args.pan_y)

        try:
            viewport.export(args.output)
            print(f"Saved to {args.output}")
        except Exception as e:
            print(f"Error saving image: {e}")
            return 1
    else:
        # Save directly
        try:
            planet.save(args.output)
            print(f"Saved to {args.output}")
        except Exception as e:
            print(f"Error saving image: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())