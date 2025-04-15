#!/usr/bin/env python3
"""
Example script to generate a planet with rings using the Cosmos Generator library.

Este ejemplo muestra cómo:
1. Crear un planeta con anillos y atmósfera
2. Guardar la imagen original del planeta
3. Usar la clase Container para mostrar el planeta con un tamaño fijo de 512x512
4. Aplicar rotación al planeta dentro del Container
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
    Generate a desert planet with rings and atmosphere.

    Este ejemplo demuestra la generación de un planeta tipo desierto con anillos
    y atmósfera, y cómo usar la clase Container para mostrar el planeta con
    un tamaño fijo de 512x512 píxeles.
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
        "size": 512,  # Tamaño fijo de 512x512
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

    # Usar Container para mostrar el planeta
    container = Container()
    container.set_content(planet)
    container.export(os.path.join(output_dir, "planet_container.png"))
    print(f"Saved to output/planet_container.png using container")

    # Probar rotación con Container
    container_rotated = Container()
    container_rotated.set_content(planet)
    container_rotated.rotate(45)
    container_rotated.export(os.path.join(output_dir, "planet_container_rotated.png"))
    print(f"Saved to output/planet_container_rotated.png using container with rotation")


if __name__ == "__main__":
    main()
