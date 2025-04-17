"""
Configuration module for Cosmos Generator.

This module contains centralized configuration settings for the application,
including output directory structure, default parameters, and other settings.
"""
import os
from typing import Dict, List, Any

# Base output directory
OUTPUT_DIR = "output"

# Planet-specific directories
PLANETS_DIR = os.path.join(OUTPUT_DIR, "planets")
PLANETS_DEBUG_DIR = os.path.join(PLANETS_DIR, "debug")
PLANETS_EXAMPLES_DIR = os.path.join(PLANETS_DIR, "examples")
PLANETS_RESULT_DIR = os.path.join(PLANETS_DIR, "result")

# Debug subdirectories
PLANETS_LOG_FILE = os.path.join(PLANETS_DEBUG_DIR, "planets.log")
PLANETS_TEXTURES_DIR = os.path.join(PLANETS_DEBUG_DIR, "textures")
PLANETS_TERRAIN_TEXTURES_DIR = os.path.join(PLANETS_TEXTURES_DIR, "terrain")
PLANETS_CLOUDS_TEXTURES_DIR = os.path.join(PLANETS_TEXTURES_DIR, "clouds")

# Planet types (used for creating result subdirectories)
PLANET_TYPES = [
    "desert",
    "ocean",
    "furnace",
    "gas",
    "ice",
    "lava",
    "rocky",
    "terran",
    "toxic"
]

# Directory structure definition
# This dictionary defines the complete directory structure
# It can be used to verify and create all necessary directories
DIRECTORY_STRUCTURE = {
    OUTPUT_DIR: {
        "planets": {
            "debug": {
                "textures": {
                    "terrain": {},
                    "clouds": {}
                }
            },
            "examples": {},
            "result": {type: {} for type in PLANET_TYPES}
        }
    }
}

# Fixed size for all planets and containers (not configurable by users)
PLANET_SIZE = 512

# Default parameters for planet generation
DEFAULT_PLANET_PARAMS = {
    "light_intensity": 1.0,
    "light_angle": 45.0,
    "light_falloff": 0.7,
    "cloud_coverage": 0.5
}

# Default variations for each planet type
DEFAULT_PLANET_VARIATIONS = {
    "desert": "arid",  # Default variation for Desert planets
    "ocean": "water_world",  # Default variation for Ocean planets
    "furnace": "standard",  # Default variation for Furnace planets
    "gas": "standard",  # Default variation for Gas planets
    "ice": "standard",  # Default variation for Ice planets
    "lava": "standard",  # Default variation for Lava planets
    "rocky": "standard",  # Default variation for Rocky planets
    "terran": "standard",  # Default variation for Terran planets
    "toxic": "standard"  # Default variation for Toxic planets
}

# Available variations for each planet type
PLANET_VARIATIONS = {
    "desert": ["arid"],  # Available variations for Desert planets
    "ocean": ["water_world", "archipelago"],  # Available variations for Ocean planets
    "furnace": ["standard"],  # Available variations for Furnace planets
    "gas": ["standard"],  # Available variations for Gas planets
    "ice": ["standard"],  # Available variations for Ice planets
    "lava": ["standard"],  # Available variations for Lava planets
    "rocky": ["standard"],  # Available variations for Rocky planets
    "terran": ["standard"],  # Available variations for Terran planets
    "toxic": ["standard"]  # Available variations for Toxic planets
}

# Container default settings
CONTAINER_DEFAULT_SETTINGS = {
    "width": PLANET_SIZE,
    "height": PLANET_SIZE,
    "default_zoom_with_rings": 0.25,  # 0.0=lejos/pequeño, 1.0=cerca/grande
    "default_zoom_without_rings": 0.95,  # 0.0=lejos/pequeño, 1.0=cerca/grande
    "zoom_min": 0.0,  # Valor mínimo de zoom (más lejos/pequeño)
    "zoom_max": 1.0   # Valor máximo de zoom (más cerca/grande)
}

# Logging configuration
LOGGING_CONFIG = {
    "default_level": "INFO",
    "file_level": "DEBUG",
    "console_level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

def get_planet_result_path(planet_type: str, seed: int) -> str:
    """
    Get the standard output path for a planet result.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation

    Returns:
        Standard output path
    """
    return os.path.join(PLANETS_RESULT_DIR, planet_type.lower(), f"{seed}.png")

def get_planet_debug_texture_path(texture_type: str, seed: int, filename: str = None) -> str:
    """
    Get the standard path for a planet debug texture.

    Args:
        texture_type: Type of texture (terrain, clouds, etc.)
        seed: Seed used for generation
        filename: Optional specific filename (default: seed.png)

    Returns:
        Standard texture path
    """
    if texture_type == "terrain":
        base_dir = PLANETS_TERRAIN_TEXTURES_DIR
        return os.path.join(base_dir, f"{seed}.png")
    elif texture_type == "clouds":
        base_dir = os.path.join(PLANETS_CLOUDS_TEXTURES_DIR, str(seed))
        if filename:
            return os.path.join(base_dir, filename)
        else:
            return os.path.join(base_dir, "texture.png")
    else:
        # For other texture types, use a generic approach
        base_dir = os.path.join(PLANETS_TEXTURES_DIR, texture_type)
        if filename:
            return os.path.join(base_dir, str(seed), filename)
        else:
            return os.path.join(base_dir, f"{seed}.png")

def get_planet_example_path(example_name: str, filename: str) -> str:
    """
    Get the standard path for a planet example.

    Args:
        example_name: Name of the example
        filename: Filename for the example

    Returns:
        Standard example path
    """
    return os.path.join(PLANETS_EXAMPLES_DIR, example_name, filename)
