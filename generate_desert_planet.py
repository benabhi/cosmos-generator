#!/usr/bin/env python3
"""
Script para generar un planeta desierto con diferentes características.
"""
import os
import random
from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.viewport import Viewport

# Crear directorio de salida si no existe
os.makedirs("output", exist_ok=True)

# Crear generador de planetas
generator = PlanetGenerator()

# Generar semilla aleatoria para reproducibilidad
seed = random.randint(0, 2**32 - 1)
print(f"Generando planeta desierto con semilla: {seed}")

# Configuraciones para diferentes variantes del planeta
configurations = [
    {
        "name": "basic",
        "params": {
            "size": 512,
            "seed": seed,
            "light_angle": 45,
            "light_intensity": 1.0
        }
    },
    {
        "name": "with_rings",
        "params": {
            "size": 512,
            "seed": seed,
            "rings": True,
            "light_angle": 45,
            "light_intensity": 1.0
        }
    },
    {
        "name": "with_atmosphere",
        "params": {
            "size": 512,
            "seed": seed,
            "atmosphere": True,
            "atmosphere_intensity": 0.8,
            "light_angle": 45,
            "light_intensity": 1.0
        }
    },
    {
        "name": "complete",
        "params": {
            "size": 512,
            "seed": seed,
            "rings": True,
            "atmosphere": True,
            "atmosphere_intensity": 0.8,
            "light_angle": 30,
            "light_intensity": 1.2
        }
    }
]

# Generar cada variante del planeta
for config in configurations:
    print(f"Generando variante: {config['name']}")
    
    # Crear el planeta
    planet = generator.create("Desert", config["params"])
    
    # Guardar la imagen directamente
    output_path = f"output/desert_planet_{config['name']}_{seed}.png"
    planet.save(output_path)
    print(f"Guardado en: {output_path}")
    
    # Para la variante completa, también crear una vista con zoom y rotación
    if config["name"] == "complete":
        viewport = Viewport(width=800, height=600, initial_zoom=1.0)
        viewport.set_content(planet)
        viewport.zoom_in(1.5)
        viewport.rotate(45)
        viewport.pan(50, -30)
        
        viewport_path = f"output/desert_planet_viewport_{seed}.png"
        viewport.export(viewport_path)
        print(f"Vista con zoom guardada en: {viewport_path}")

print("¡Generación de planetas completada!")
