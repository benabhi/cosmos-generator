#!/usr/bin/env python3
"""
Example script to test the improved ring opacity and solid rings.
"""
import os
import sys

# Add the project root directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from cosmos_generator import PlanetGenerator


def main():
    """
    Generate planets with rings to test the improved ring opacity and solid rings.
    """
    # Create output directory
    output_dir = "output/planets/examples/test_ring_opacity"
    os.makedirs(output_dir, exist_ok=True)

    # Create generator
    generator = PlanetGenerator()

    # Print available planet types
    print("Available planet types:")
    for planet_type in generator.get_celestial_types():
        print(f"  - {planet_type}")

    # Generate planets with rings for different types
    # Use only types that are actually implemented
    planet_types = ["Desert"]

    for i, planet_type in enumerate(planet_types):
        # Use a different seed for each planet type
        seed = 12345 + i

        # Generate planet with rings
        planet = generator.create(planet_type, {
            "seed": seed,
            "size": 512,
            "rings": True,
            "atmosphere": True,
            "atmosphere_intensity": 0.8,
        })

        # Save the planet
        output_path = os.path.join(output_dir, f"{planet_type.lower()}_rings_{seed}.png")
        planet.save(output_path)
        print(f"Saved {planet_type} planet with rings to {output_path}")

        # Save the planet with container
        from cosmos_generator.utils.container import Container

        container = Container()
        container.set_content(planet)

        container_path = os.path.join(output_dir, f"{planet_type.lower()}_rings_{seed}_container.png")
        container.export(container_path)
        print(f"Saved {planet_type} planet with rings in container to {container_path}")


if __name__ == "__main__":
    main()
