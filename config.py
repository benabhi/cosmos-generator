"""
Configuration module for Cosmos Generator.

This module contains centralized configuration settings for the application,
including output directory structure, default parameters, and other settings.
"""
import os

# Base output directory
OUTPUT_DIR = "output"

# Planet-specific directories
PLANETS_DIR = os.path.join(OUTPUT_DIR, "planets")

# Main log file for all planet generations
PLANETS_LOG_FILE = os.path.join(PLANETS_DIR, "planets.log")

# Planets CSV file to track all generated planets
PLANETS_CSV = os.path.join(PLANETS_DIR, "planets.csv")

# Planet types (used for creating result subdirectories)
PLANET_TYPES = [
    "desert",
    "ocean",
    "furnace",
    "jovian",
    "vital",
    "toxic",
    "ice",
    "rocky",
    "jungle"
]

# Directory structure definition
# This dictionary defines the complete directory structure
# It can be used to verify and create all necessary directories
DIRECTORY_STRUCTURE = {
    OUTPUT_DIR: {
        "planets": {
            type: {} for type in PLANET_TYPES
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
    "furnace": "magma_rivers",  # Default variation for Furnace planets
    "jovian": "bands",  # Default variation for Jovian planets
    "vital": "earthlike",  # Default variation for Vital planets
    "toxic": "toxic_veins",  # Default variation for Toxic planets
    "ice": "glacier",  # Default variation for Ice planets
    "rocky": "cratered",  # Default variation for Rocky planets
    "jungle": "overgrown"  # Default variation for Jungle planets
}

# Available variations for each planet type
PLANET_VARIATIONS = {
    "desert": ["arid", "dunes", "mesa"],  # Available variations for Desert planets
    "ocean": ["water_world", "archipelago", "reef"],  # Available variations for Ocean planets
    "furnace": ["magma_rivers", "ember_wastes", "volcanic_hellscape"],  # Available variations for Furnace planets
    "jovian": ["bands", "storm", "nebulous"],  # Available variations for Jovian planets
    "vital": ["earthlike", "archipelago", "pangaea"],  # Available variations for Vital planets
    "toxic": ["toxic_veins", "acid_lakes", "corrosive_storms"],  # Available variations for Toxic planets
    "ice": ["glacier", "tundra", "frozen_ocean"],  # Available variations for Ice planets
    "rocky": ["cratered", "fractured", "mountainous"],  # Available variations for Rocky planets
    "jungle": ["overgrown", "canopy", "bioluminescent"]  # Available variations for Jungle planets
}

# Container default settings
CONTAINER_DEFAULT_SETTINGS = {
    "width": PLANET_SIZE,
    "height": PLANET_SIZE,
    "default_zoom_with_rings": 0.25,  # 0.0=far/small, 1.0=close/large
    "default_zoom_without_rings": 0.95,  # 0.0=far/small, 1.0=close/large
    "zoom_min": 0.0,  # Minimum zoom value (farther/smaller)
    "zoom_max": 1.0   # Maximum zoom value (closer/larger)
}

# Logging configuration
LOGGING_CONFIG = {
    "default_level": "INFO",
    "file_level": "DEBUG",
    "console_level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# Web interface configuration
WEB_CONFIG = {
    "host": "0.0.0.0",  # Listen on all interfaces
    "port": 4000,       # Default port
    "debug": False,     # Debug mode (set to False in production)
    "log_dir": "web/logs",  # Directory for web interface logs
    "log_file": "web/logs/web.log",  # Log file for web interface
    "secret_key": "cosmos-generator-secret-key",  # Secret key for session
    "max_content_length": 16 * 1024 * 1024  # 16 MB max upload size
}

def get_planet_seed_dir(planet_type: str, seed: str) -> str:
    """
    Get the directory for a specific planet seed.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)

    Returns:
        Path to the seed directory
    """
    return os.path.join(PLANETS_DIR, planet_type.lower(), seed)


def get_planet_result_path(planet_type: str, seed: str) -> str:
    """
    Get the standard output path for a planet result.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)

    Returns:
        Standard output path
    """
    seed_dir = get_planet_seed_dir(planet_type, seed)
    return os.path.join(seed_dir, "planet.png")


def get_planet_log_path(planet_type: str, seed: str) -> str:
    """
    Get the path for an individual planet's log file.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)

    Returns:
        Path to the planet's log file
    """
    seed_dir = get_planet_seed_dir(planet_type, seed)
    return os.path.join(seed_dir, "planet.log")


def get_planet_details_path(planet_type: str, seed: str) -> str:
    """
    Get the path for a planet's details CSV file.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)

    Returns:
        Path to the planet's details CSV file
    """
    seed_dir = get_planet_seed_dir(planet_type, seed)
    return os.path.join(seed_dir, "details.csv")


def get_planet_texture_path(planet_type: str, seed: str, texture_type: str) -> str:
    """
    Get the path for a planet's texture file.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)
        texture_type: Type of texture (terrain, cloud_texture, cloud_mask)

    Returns:
        Path to the texture file
    """
    seed_dir = get_planet_seed_dir(planet_type, seed)

    if texture_type == "terrain":
        return os.path.join(seed_dir, "terrain_texture.png")
    elif texture_type == "cloud_texture":
        return os.path.join(seed_dir, "cloud_texture.png")
    elif texture_type == "cloud_mask":
        return os.path.join(seed_dir, "cloud_mask.png")
    else:
        # For other texture types, use a generic approach
        return os.path.join(seed_dir, f"{texture_type}.png")
