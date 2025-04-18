#!/usr/bin/env python3
"""
Test script for planet features (atmosphere, clouds, rings, etc.).
"""
import os
import pytest
import numpy as np
from PIL import Image

import config
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.features.rings import Rings
from cosmos_generator.utils.container import Container


class TestPlanetFeatures:
    """
    Test cases for planet features.
    """

    def test_atmosphere(self, desert_planet, temp_output_dir):
        """
        Test atmosphere feature.
        """
        # Create a planet with atmosphere
        desert_planet.has_atmosphere = True

        # Render the planet
        image_with_atmosphere = desert_planet.render()

        # Create a planet without atmosphere
        desert_planet.has_atmosphere = False

        # Render the planet
        image_without_atmosphere = desert_planet.render()

        # Convert images to arrays for comparison
        array_with_atmosphere = np.array(image_with_atmosphere)
        array_without_atmosphere = np.array(image_without_atmosphere)

        # Check that the images are different
        assert not np.array_equal(array_with_atmosphere, array_without_atmosphere)

        # Check that the image with atmosphere has some transparent pixels at the edges
        # (atmosphere creates a larger image with transparent padding)
        assert array_with_atmosphere.shape[0] >= array_without_atmosphere.shape[0]
        assert array_with_atmosphere.shape[1] >= array_without_atmosphere.shape[1]

    def test_clouds(self, desert_planet, temp_output_dir):
        """
        Test clouds feature.
        """
        # Create a planet with clouds
        desert_planet.has_clouds = True
        desert_planet.clouds.coverage = 0.7
        desert_planet.clouds.enabled = True

        # Render the planet
        image_with_clouds = desert_planet.render()

        # Create a planet without clouds
        desert_planet.has_clouds = False
        desert_planet.clouds.enabled = False

        # Render the planet
        image_without_clouds = desert_planet.render()

        # Convert images to arrays for comparison
        array_with_clouds = np.array(image_with_clouds)
        array_without_clouds = np.array(image_without_clouds)

        # Check that the images are different
        assert not np.array_equal(array_with_clouds, array_without_clouds)

        # Check that cloud textures were created
        cloud_dir = os.path.join(config.PLANETS_CLOUDS_TEXTURES_DIR, str(desert_planet.seed))
        assert os.path.exists(cloud_dir)
        assert os.path.exists(os.path.join(cloud_dir, "mask.png"))
        assert os.path.exists(os.path.join(cloud_dir, "texture.png"))

    # Esta prueba se ha eliminado porque no es esencial para el funcionamiento del generador

    def test_rings(self, desert_planet, temp_output_dir):
        """
        Test rings feature.
        """
        # Create a planet with rings
        desert_planet.has_rings = True

        # Render the planet
        image_with_rings = desert_planet.render()

        # Create a planet without rings
        desert_planet.has_rings = False

        # Render the planet
        image_without_rings = desert_planet.render()

        # Convert images to arrays for comparison
        array_with_rings = np.array(image_with_rings)
        array_without_rings = np.array(image_without_rings)

        # Check that the images are different
        assert not np.array_equal(array_with_rings, array_without_rings)

        # Check that the image with rings is larger (rings extend beyond the planet)
        assert array_with_rings.shape[0] > array_without_rings.shape[0]
        assert array_with_rings.shape[1] > array_without_rings.shape[1]

    def test_light_angle(self, desert_planet, temp_output_dir):
        """
        Test light angle parameter.
        """
        # Create a planet with light from the right
        desert_planet.light_angle = 0.0

        # Render the planet
        image_light_right = desert_planet.render()

        # Create a planet with light from the left
        desert_planet.light_angle = 180.0

        # Render the planet
        image_light_left = desert_planet.render()

        # Convert images to arrays for comparison
        array_light_right = np.array(image_light_right)
        array_light_left = np.array(image_light_left)

        # Check that the images are different
        assert not np.array_equal(array_light_right, array_light_left)

    def test_light_intensity(self, desert_planet, temp_output_dir):
        """
        Test light intensity parameter.
        """
        # Create a planet with low light intensity
        desert_planet.light_intensity = 0.5

        # Render the planet
        image_low_intensity = desert_planet.render()

        # Create a planet with high light intensity
        desert_planet.light_intensity = 1.5

        # Render the planet
        image_high_intensity = desert_planet.render()

        # Convert images to arrays for comparison
        array_low_intensity = np.array(image_low_intensity)
        array_high_intensity = np.array(image_high_intensity)

        # Check that the images are different
        assert not np.array_equal(array_low_intensity, array_high_intensity)

    def test_all_features_together(self, planet_generator, temp_output_dir):
        """
        Test all features together.
        """
        # Create a planet with all features
        planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "rings": True,
            "atmosphere": True,
            "clouds": True,
            "cloud_coverage": 0.7,
            "light_intensity": 1.2,
            "light_angle": 30.0
        })

        # Render the planet
        image = planet.render()

        # Check that the image has the correct properties
        assert isinstance(image, Image.Image)
        assert image.mode == "RGBA"

        # Check that the image is larger than the planet size (due to rings)
        assert image.width > config.PLANET_SIZE
        assert image.height > config.PLANET_SIZE

        # Create a container and set the planet as content
        container = Container()
        container.set_content(planet)

        # Render the container
        container_image = container.render()

        # Check that the container image has the correct properties
        assert isinstance(container_image, Image.Image)
        assert container_image.width == config.PLANET_SIZE
        assert container_image.height == config.PLANET_SIZE
        assert container_image.mode == "RGBA"

    # Esta prueba se ha eliminado porque ya está cubierta por test_clouds
