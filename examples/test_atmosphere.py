#!/usr/bin/env python3
"""
Example script to test the simplified atmosphere implementation.
"""
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate planets with and without atmosphere to test the simplified implementation.
    """
    # Create output directory
    output_dir = "output/test_atmosphere"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create generator
    generator = PlanetGenerator()
    
    # Print available planet types
    print("Available planet types:")
    for planet_type in generator.get_celestial_types():
        print(f"  - {planet_type}")
    
    # Generate planets with and without atmosphere
    planet_type = "Desert"
    seed = 12345
    
    # Generate planet without atmosphere
    planet_no_atmo = generator.create(planet_type, {
        "seed": seed,
        "size": 512,
        "atmosphere": False,
    })
    
    # Generate planet with atmosphere
    planet_with_atmo = generator.create(planet_type, {
        "seed": seed,
        "size": 512,
        "atmosphere": True,
    })
    
    # Generate planet with atmosphere and rings
    planet_with_atmo_rings = generator.create(planet_type, {
        "seed": seed,
        "size": 512,
        "atmosphere": True,
        "rings": True,
    })
    
    # Save the planets using Container
    container = Container()
    
    # Save planet without atmosphere
    container.set_content(planet_no_atmo)
    no_atmo_path = os.path.join(output_dir, f"{planet_type.lower()}_no_atmosphere.png")
    container.export(no_atmo_path)
    print(f"Saved planet without atmosphere to {no_atmo_path}")
    
    # Save planet with atmosphere
    container.set_content(planet_with_atmo)
    with_atmo_path = os.path.join(output_dir, f"{planet_type.lower()}_with_atmosphere.png")
    container.export(with_atmo_path)
    print(f"Saved planet with atmosphere to {with_atmo_path}")
    
    # Save planet with atmosphere and rings
    container.set_content(planet_with_atmo_rings)
    with_atmo_rings_path = os.path.join(output_dir, f"{planet_type.lower()}_with_atmosphere_rings.png")
    container.export(with_atmo_rings_path)
    print(f"Saved planet with atmosphere and rings to {with_atmo_rings_path}")


if __name__ == "__main__":
    main()
