#!/usr/bin/env python3
"""
Example script to test various Ocean planet combinations.
"""
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate Ocean planets with various combinations of features.
    """
    # Create output directory
    output_dir = "output/examples/test_ocean_combinations"
    os.makedirs(output_dir, exist_ok=True)

    # Create generator
    generator = PlanetGenerator()

    # Base seed for reproducibility
    base_seed = 12345

    # Create a container for all planets
    container = Container()

    # 1. Normal Ocean planet without any features (water_world style)
    print("Generating normal Ocean planet without any features (water_world style)...")
    ocean_normal = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "ocean_style": "water_world",
    })
    container.set_content(ocean_normal)
    normal_path = os.path.join(output_dir, "ocean_normal.png")
    container.export(normal_path)
    print(f"Saved to {normal_path}")
    print()

    # 2. Ocean planet with atmosphere and water_world style (no rings)
    print("Generating Ocean planet with atmosphere and water_world style (no rings)...")
    ocean_atmo_water = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "ocean_style": "water_world",
    })
    container.set_content(ocean_atmo_water)
    atmo_water_path = os.path.join(output_dir, "ocean_atmo_water.png")
    container.export(atmo_water_path)
    print(f"Saved to {atmo_water_path}")
    print()

    # 3. Ocean planet with atmosphere and archipelago style (no rings)
    print("Generating Ocean planet with atmosphere and archipelago style (no rings)...")
    ocean_atmo_archipelago = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "ocean_style": "archipelago",
    })
    container.set_content(ocean_atmo_archipelago)
    atmo_archipelago_path = os.path.join(output_dir, "ocean_atmo_archipelago.png")
    container.export(atmo_archipelago_path)
    print(f"Saved to {atmo_archipelago_path}")
    print()

    # 4. Ocean planet with atmosphere, archipelago style, and rings
    print("Generating Ocean planet with atmosphere, archipelago style, and rings...")
    ocean_atmo_archipelago_rings = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "ocean_style": "archipelago",
        "rings": True,
    })
    container.set_content(ocean_atmo_archipelago_rings)
    atmo_archipelago_rings_path = os.path.join(output_dir, "ocean_atmo_archipelago_rings.png")
    container.export(atmo_archipelago_rings_path)
    print(f"Saved to {atmo_archipelago_rings_path}")
    print()

    # 5. Ocean planet with atmosphere, water_world style, and rings
    print("Generating Ocean planet with atmosphere, water_world style, and rings...")
    ocean_atmo_water_rings = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "ocean_style": "water_world",
        "rings": True,
    })
    container.set_content(ocean_atmo_water_rings)
    atmo_water_rings_path = os.path.join(output_dir, "ocean_atmo_water_rings.png")
    container.export(atmo_water_rings_path)
    print(f"Saved to {atmo_water_rings_path}")
    print()

    # 6. Ocean planet with atmosphere, archipelago style, rings, and rotation
    print("Generating Ocean planet with atmosphere, archipelago style, rings, and rotation...")
    ocean_atmo_archipelago_rings_rotated = generator.create("Ocean", {
        "seed": base_seed,
        "size": 512,
        "atmosphere": True,
        "ocean_style": "archipelago",
        "rings": True,
    })
    container.set_content(ocean_atmo_archipelago_rings_rotated)
    container.set_rotation(45.0)  # Rotate 45 degrees
    atmo_archipelago_rings_rotated_path = os.path.join(output_dir, "ocean_atmo_archipelago_rings_rotated.png")
    container.export(atmo_archipelago_rings_rotated_path)
    print(f"Saved to {atmo_archipelago_rings_rotated_path}")
    print()

    print("All Ocean planet combinations generated successfully!")


if __name__ == "__main__":
    main()
