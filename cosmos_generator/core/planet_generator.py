"""
Planet-specific generator class.
"""
from typing import Dict, Any, Optional, List, Type
import importlib
import os
import pkgutil
import time

from cosmos_generator.utils.logger import logger

from cosmos_generator.core.celestial_generator import CelestialGenerator
from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet
from cosmos_generator.core.interfaces import NoiseGeneratorInterface, ColorPaletteInterface, TextureGeneratorInterface


class PlanetGenerator(CelestialGenerator):
    """
    Main entry point for creating planets.
    """

    def __init__(self, seed: Optional[int] = None,
                 noise_gen: Optional[NoiseGeneratorInterface] = None,
                 color_palette: Optional[ColorPaletteInterface] = None,
                 texture_gen: Optional[TextureGeneratorInterface] = None):
        """
        Initialize a planet generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation
            noise_gen: Optional noise generator instance (will create one if not provided)
            color_palette: Optional color palette instance (will create one if not provided)
            texture_gen: Optional texture generator instance (will create one if not provided)
        """
        super().__init__(seed=seed,
                        noise_gen=noise_gen,
                        color_palette=color_palette,
                        texture_gen=texture_gen)

        # Auto-discover and register planet types
        self._discover_planet_types()

    def _discover_planet_types(self) -> None:
        """
        Automatically discover and register planet types from the planets package.
        """
        from cosmos_generator.celestial_bodies import planets

        # Get the package path
        package_path = os.path.dirname(planets.__file__)

        # Iterate through all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
            # Skip __init__.py and abstract classes
            if module_name.startswith('_') or module_name == 'abstract_planet':
                continue

            # Import the module
            module = importlib.import_module(f"cosmos_generator.celestial_bodies.planets.{module_name}")

            # Look for planet classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if it's a class and a subclass of AbstractPlanet
                if (isinstance(attr, type) and
                    issubclass(attr, AbstractPlanet) and
                    attr != AbstractPlanet):

                    # Register the planet type
                    planet_type = attr.PLANET_TYPE if hasattr(attr, 'PLANET_TYPE') else attr_name
                    self.register_celestial_type(planet_type, attr)

    def create(self, planet_type: str, params: Optional[Dict[str, Any]] = None) -> AbstractPlanet:
        """
        Create a planet of the specified type.

        Args:
            planet_type: Type of planet to create
            params: Optional parameters for customization

        Returns:
            Created planet instance
        """
        start_time = time.time()
        try:
            # Log the planet instance creation request
            logger.info(f"Initializing {planet_type} planet instance", "generator")
            if params:
                logger.debug(f"Parameters: {params}", "generator")

            # Create the planet instance
            planet = super().create(planet_type, params)

            # Log success
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(f"Planet instance initialized in {duration_ms:.2f}ms (rendering will start next)", "generator")

            return planet
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed to create {planet_type} planet: {str(e)}", "generator", exc_info=True)
            raise
