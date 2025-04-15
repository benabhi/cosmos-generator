#!/usr/bin/env python3
"""
Example script to generate a planet using the Cosmos Generator library.
"""
import os
import sys
import random

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.viewport import Viewport


def main():
    """
    Generate a desert planet with rings and atmosphere.
    """
    # Create a planet generator
    generator = PlanetGenerator()
    
    # Print available planet types
    print("Available planet types:")
    for planet_type in generator.get_celestial_types():
        print(f"  - {planet_type}")
    
    # Generate a random seed
    seed = random.randint(0, 2**32 - 1)
    
    # Create a desert planet with rings and atmosphere
    planet = generator.create("Desert", {
        "size": 1024,
        "seed": seed,
        "rings": True,
        "atmosphere": True,
        "atmosphere_intensity": 0.8,
        "lighting": {
            "intensity": 1.0,
            "angle": 45,
            "falloff": 0.7
        }
    })
    
    print(f"Generated Desert planet with seed {seed}")
    
    # Save the planet image
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    planet.save(os.path.join(output_dir, f"desert_planet_{seed}.png"))
    print(f"Saved to output/desert_planet_{seed}.png")
    
    # Create a viewport for more control
    viewport = Viewport(width=800, height=600, initial_zoom=1.0)
    viewport.set_content(planet)
    viewport.zoom_in(1.5)
    viewport.rotate(45)
    viewport.pan(50, -30)
    
    # Export the viewport image
    viewport.export(os.path.join(output_dir, f"desert_planet_{seed}_viewport.png"))
    print(f"Saved viewport to output/desert_planet_{seed}_viewport.png")


if __name__ == "__main__":
    main()
