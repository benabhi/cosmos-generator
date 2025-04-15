#!/usr/bin/env python3
"""
Example script to generate a planet without rings using the Cosmos Generator library.
"""
import os
import sys
import random

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.container import Container


def main():
    """
    Generate a desert planet without rings and test different zoom levels.
    """
    # Create a planet generator
    generator = PlanetGenerator()

    # Usar una semilla fija para asegurar que el color sea consistente
    seed = 12345

    # Create a desert planet without rings
    planet = generator.create("Desert", {
        "size": 512,  # Tamaño fijo de 512x512
        "seed": seed,
        "rings": False,  # Sin anillos
        "atmosphere": True,
        "atmosphere_intensity": 0.8,
        "lighting": {
            "intensity": 1.0,
            "angle": 45,
            "falloff": 0.7
        }
    })

    print(f"Generated Desert planet without rings with seed {seed}")

    # Save the planet image
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    planet.save(os.path.join(output_dir, f"desert_planet_no_rings_{seed}.png"))
    print(f"Saved to output/desert_planet_no_rings_{seed}.png")

    # Usar Container para mostrar el planeta sin anillos
    container = Container()
    container.set_content(planet)
    container.export(os.path.join(output_dir, "planet_no_rings_container.png"))
    print(f"Saved to output/planet_no_rings_container.png using container")

    # Probar rotación con Container
    container_rotated = Container()
    container_rotated.set_content(planet)
    container_rotated.rotate(45)
    container_rotated.export(os.path.join(output_dir, "planet_no_rings_container_rotated.png"))
    print(f"Saved to output/planet_no_rings_container_rotated.png using container with rotation")


if __name__ == "__main__":
    main()
