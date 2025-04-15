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

    # Crear viewports con diferentes niveles de zoom para demostrar el comportamiento
    zoom_levels = [0.3, 0.5, 0.7, 1.0]

    for zoom in zoom_levels:
        # Crear viewport con el nivel de zoom actual
        viewport = Viewport(initial_zoom=zoom)
        viewport.set_content(planet)

        # Guardar la imagen con el nivel de zoom en el nombre del archivo
        filename = f"planet_zoom_{zoom:.1f}.png"
        viewport.export(os.path.join(output_dir, filename))
        print(f"Saved viewport with zoom {zoom:.1f} to output/{filename}")

    # Viewport con rotación para demostrar que también funciona con rotación
    viewport_rotated = Viewport(initial_zoom=0.7)
    viewport_rotated.set_content(planet)
    viewport_rotated.rotate(45)
    viewport_rotated.export(os.path.join(output_dir, "planet_rotated.png"))
    print(f"Saved rotated viewport to output/planet_rotated.png")


if __name__ == "__main__":
    main()
