#!/usr/bin/env python3
"""
Example script to generate planets using the Container class.
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
    Generate planets with and without rings using the Container class.
    """
    # Create a planet generator
    generator = PlanetGenerator()
    
    # Usar una semilla fija para asegurar que el color sea consistente
    seed = 12345
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Generar un planeta con anillos
    planet_with_rings = generator.create("Desert", {
        "size": 512,
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
    
    print(f"Generated Desert planet with rings (seed {seed})")
    
    # Guardar la imagen original del planeta
    planet_with_rings.save(os.path.join(output_dir, "planet_with_rings_original.png"))
    print(f"Saved to output/planet_with_rings_original.png")
    
    # Usar Container para mostrar el planeta con anillos
    container_rings = Container()
    container_rings.set_content(planet_with_rings)
    container_rings.export(os.path.join(output_dir, "planet_with_rings_container.png"))
    print(f"Saved to output/planet_with_rings_container.png")
    
    # Probar rotación
    container_rings_rotated = Container()
    container_rings_rotated.set_content(planet_with_rings)
    container_rings_rotated.rotate(45)
    container_rings_rotated.export(os.path.join(output_dir, "planet_with_rings_rotated.png"))
    print(f"Saved to output/planet_with_rings_rotated.png")
    
    # 2. Generar un planeta sin anillos
    planet_without_rings = generator.create("Desert", {
        "size": 512,
        "seed": seed,
        "rings": False,
        "atmosphere": True,
        "atmosphere_intensity": 0.8,
        "lighting": {
            "intensity": 1.0,
            "angle": 45,
            "falloff": 0.7
        }
    })
    
    print(f"Generated Desert planet without rings (seed {seed})")
    
    # Guardar la imagen original del planeta
    planet_without_rings.save(os.path.join(output_dir, "planet_without_rings_original.png"))
    print(f"Saved to output/planet_without_rings_original.png")
    
    # Usar Container para mostrar el planeta sin anillos
    container_no_rings = Container()
    container_no_rings.set_content(planet_without_rings)
    container_no_rings.export(os.path.join(output_dir, "planet_without_rings_container.png"))
    print(f"Saved to output/planet_without_rings_container.png")
    
    # Probar rotación
    container_no_rings_rotated = Container()
    container_no_rings_rotated.set_content(planet_without_rings)
    container_no_rings_rotated.rotate(45)
    container_no_rings_rotated.export(os.path.join(output_dir, "planet_without_rings_rotated.png"))
    print(f"Saved to output/planet_without_rings_rotated.png")


if __name__ == "__main__":
    main()
