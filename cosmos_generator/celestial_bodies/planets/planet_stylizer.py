"""
Module to configure cloud generation for planets.
"""
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.celestial_bodies.planets.abstract_planet import AbstractPlanet
from cosmos_generator.utils.logger import logger


def apply_stylized_clouds_to_planet_class():
    """
    Monkey patch the AbstractPlanet class to use the stylized cloud generation.
    This function should be called before creating any planet instances.
    """
    # Store the original __init__ method
    original_init = AbstractPlanet.__init__

    # Define a new __init__ method that uses stylized clouds
    def new_init(self, *args, **kwargs):
        # Call the original __init__ method
        original_init(self, *args, **kwargs)

        # Configure the clouds instance with stylized settings
        # Only if clouds are enabled and clouds instance exists
        if self.has_clouds and hasattr(self, 'clouds') and self.clouds is not None:
            # The clouds class now has the stylized cloud generation built-in
            # No need to replace the instance, just ensure it's properly configured
            pass

            # Log the configuration
            logger.debug(f"Using stylized clouds for {self.PLANET_TYPE} planet", "planet")

    # Replace the __init__ method
    AbstractPlanet.__init__ = new_init

    # Log the monkey patching
    logger.info("Applied stylized clouds to AbstractPlanet class", "planet")


def enable_stylized_clouds():
    """
    Enable stylized clouds for all planets.
    This function should be called before creating any planet instances.
    """
    apply_stylized_clouds_to_planet_class()
    logger.info("Enabled stylized clouds for all planets", "planet")
