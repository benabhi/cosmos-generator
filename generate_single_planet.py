#!/usr/bin/env python3
"""
Script para generar un solo planeta con anillos mejorados.
"""
import os
from cosmos_generator.core.planet_generator import PlanetGenerator

# Crear directorio de salida si no existe
os.makedirs("output", exist_ok=True)

# Crear generador de planetas con una semilla fija para reproducibilidad
seed = 12345
generator = PlanetGenerator(seed=seed)

# Crear un planeta con anillos
planet_type = "Desert"
planet = generator.create(planet_type, {
    "size": 512,
    "seed": seed,
    "rings": True,
    "light_angle": 45,
    "light_intensity": 1.2
})

# Guardar la imagen
output_path = f"output/{planet_type.lower()}_rings_final.png"
planet.save(output_path)
print(f"Planeta con anillos mejorados guardado en: {output_path}")
