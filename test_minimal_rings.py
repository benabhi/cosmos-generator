#!/usr/bin/env python3
"""
Script para probar el sistema de anillos planetarios mejorado con la implementación minimal.
"""
import os
import random
from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.viewport import Viewport

# Crear directorio de salida si no existe
os.makedirs("output", exist_ok=True)

# Crear generador de planetas con una semilla fija para reproducibilidad
seed = 12345
generator = PlanetGenerator(seed=seed)

# Tipos de planetas para probar
planet_types = ["Desert", "Furnace", "Jovian"]

# Configuraciones para diferentes ángulos de visualización
angles = [0, 30, 45, 60, 90]

for planet_type in planet_types:
    print(f"Generando planeta tipo: {planet_type}")
    
    # Crear el planeta base con anillos
    planet = generator.create(planet_type, {
        "size": 512,
        "seed": seed,
        "rings": True,
        "light_angle": 45,
        "light_intensity": 1.2
    })
    
    # Guardar la imagen directamente
    output_path = f"output/{planet_type.lower()}_minimal_rings.png"
    planet.save(output_path)
    print(f"Guardado en: {output_path}")
    
    # Crear diferentes vistas con rotación
    for angle in angles:
        viewport = Viewport(width=800, height=600, initial_zoom=1.0)
        viewport.set_content(planet)
        viewport.set_rotation(angle)
        
        viewport_path = f"output/{planet_type.lower()}_minimal_rings_angle_{angle}.png"
        viewport.export(viewport_path)
        print(f"Vista con rotación {angle}° guardada en: {viewport_path}")

print("¡Generación de planetas con anillos mejorados completada!")
