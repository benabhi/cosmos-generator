#!/usr/bin/env python3
"""
Example script to test the cloud feature on different planet types.
"""
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate planets with different cloud coverages and planet types.
    """
    # Create output directory
    output_dir = "output/examples/test_clouds"
    os.makedirs(output_dir, exist_ok=True)

    # Create generator
    generator = PlanetGenerator()

    # Base seed for reproducibility
    base_seed = 12345

    # Planet types to test
    planet_types = ["Desert", "Ocean", "Ice", "Jovian"]

    # Cloud coverages to test
    cloud_coverages = [0.3, 0.5, 0.7, 0.9]

    # Create a container for all planets
    container = Container()

    # Generate planets with clouds for each planet type
    for planet_type in planet_types:
        print(f"Generating {planet_type} planets with clouds...")

        # Generate planets with different cloud coverages
        for coverage in cloud_coverages:
            clouds = generator.create(planet_type, {
                "seed": base_seed,
                "size": 512,
                "clouds": True,
                "cloud_coverage": coverage,
            })
            container.set_content(clouds)
            clouds_path = os.path.join(output_dir, f"{planet_type.lower()}_clouds_{int(coverage*100)}.png")
            container.export(clouds_path)
            print(f"  - Saved {planet_type} planet with {int(coverage*100)}% cloud coverage to {clouds_path}")

        # For Ocean planets, test both styles with clouds
        if planet_type == "Ocean":
            # Test water_world style with clouds
            water_clouds = generator.create(planet_type, {
                "seed": base_seed,
                "size": 512,
                "clouds": True,
                "cloud_coverage": 0.6,
                "ocean_style": "water_world",
            })
            container.set_content(water_clouds)
            water_clouds_path = os.path.join(output_dir, f"{planet_type.lower()}_water_world_clouds.png")
            container.export(water_clouds_path)
            print(f"  - Saved {planet_type} planet (water_world style) with clouds to {water_clouds_path}")

            # Test archipelago style with clouds
            archipelago_clouds = generator.create(planet_type, {
                "seed": base_seed,
                "size": 512,
                "clouds": True,
                "cloud_coverage": 0.6,
                "ocean_style": "archipelago",
            })
            container.set_content(archipelago_clouds)
            archipelago_clouds_path = os.path.join(output_dir, f"{planet_type.lower()}_archipelago_clouds.png")
            container.export(archipelago_clouds_path)
            print(f"  - Saved {planet_type} planet (archipelago style) with clouds to {archipelago_clouds_path}")

        print()

    print("All cloud test planets generated successfully!")


if __name__ == "__main__":
    main()
