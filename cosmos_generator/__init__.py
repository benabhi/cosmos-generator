"""
Cosmos Generator - A Python library for procedurally generating celestial bodies.
"""

__version__ = "1.0.0"

# Import main classes for easier access
from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.core.celestial_generator import CelestialGenerator
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator

# Import utility classes
from cosmos_generator.utils.container import Container

# Import feature classes
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.features.rings import Rings
from cosmos_generator.features.surface import Surface

# Import planet stylizer
from cosmos_generator.celestial_bodies.planets.planet_stylizer import enable_stylized_clouds

# Enable stylized clouds by default
enable_stylized_clouds()