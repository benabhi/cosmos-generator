#!/usr/bin/env python3
"""
Example script to test the Ocean planet type.
"""
import os
import sys

# Add the project root directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from cosmos_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate Ocean planets with various features.
    """
    # Create output directory
    output_dir = "output/planets/examples/test_ocean"
    os.makedirs(output_dir, exist_ok=True)

    # Create generator
    generator = PlanetGenerator()

    # Print available planet types to verify Ocean is registered
    print("Available planet types:")
    for planet_type in generator.get_celestial_types():
        print(f"  - {planet_type}")

    # Base seed for reproducibility
    base_seed = 12345

    # Generate basic Ocean planet
    basic_ocean = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
    })

    # Generate Ocean planet with atmosphere
    ocean_with_atmosphere = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
    })

    # Generate Ocean planet with rings
    ocean_with_rings = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "rings": True,
    })

    # Generate Ocean planet with both atmosphere and rings
    ocean_with_both = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "rings": True,
    })

    # Generate Ocean planet with different island coverage
    ocean_more_islands = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "island_coverage": 0.3,  # More islands
    })

    ocean_less_islands = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "island_coverage": 0.05,  # Fewer islands
    })

    # Save all planets using Container
    container = Container()

    # Save basic Ocean planet
    container.set_content(basic_ocean)
    basic_path = os.path.join(output_dir, "ocean_basic.png")
    container.export(basic_path)
    print(f"Saved basic Ocean planet to {basic_path}")

    # Save Ocean planet with atmosphere
    container.set_content(ocean_with_atmosphere)
    atmosphere_path = os.path.join(output_dir, "ocean_with_atmosphere.png")
    container.export(atmosphere_path)
    print(f"Saved Ocean planet with atmosphere to {atmosphere_path}")

    # Save Ocean planet with rings
    container.set_content(ocean_with_rings)
    rings_path = os.path.join(output_dir, "ocean_with_rings.png")
    container.export(rings_path)
    print(f"Saved Ocean planet with rings to {rings_path}")

    # Save Ocean planet with both atmosphere and rings
    container.set_content(ocean_with_both)
    both_path = os.path.join(output_dir, "ocean_with_both.png")
    container.export(both_path)
    print(f"Saved Ocean planet with atmosphere and rings to {both_path}")

    # Save Ocean planets with different island coverage
    container.set_content(ocean_more_islands)
    more_islands_path = os.path.join(output_dir, "ocean_more_islands.png")
    container.export(more_islands_path)
    print(f"Saved Ocean planet with more islands to {more_islands_path}")

    container.set_content(ocean_less_islands)
    less_islands_path = os.path.join(output_dir, "ocean_less_islands.png")
    container.export(less_islands_path)
    print(f"Saved Ocean planet with fewer islands to {less_islands_path}")


if __name__ == "__main__":
    main()
