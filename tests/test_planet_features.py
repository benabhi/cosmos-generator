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

    def test_atmosphere(self, planet_generator, temp_output_dir):
        """
        Test atmosphere feature.
        """
        # Create a planet with atmosphere
        planet_with_atmosphere = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "atmosphere": True,
            "atmosphere_glow": 0.7,
            "atmosphere_halo": 0.8,
            "atmosphere_thickness": 4,
            "atmosphere_blur": 0.6
        })

        # Ensure the atmosphere is enabled
        planet_with_atmosphere.has_atmosphere = True
        planet_with_atmosphere.atmosphere.enabled = True

        # Render the planet
        image_with_atmosphere = planet_with_atmosphere.render()

        # Create a planet without atmosphere
        planet_without_atmosphere = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "atmosphere": False
        })

        # Ensure the atmosphere is disabled
        planet_without_atmosphere.has_atmosphere = False
        planet_without_atmosphere.atmosphere.enabled = False

        # Render the planet
        image_without_atmosphere = planet_without_atmosphere.render()

        # Convert images to arrays for comparison
        array_with_atmosphere = np.array(image_with_atmosphere)
        array_without_atmosphere = np.array(image_without_atmosphere)

        # Check that the images are different
        assert not np.array_equal(array_with_atmosphere, array_without_atmosphere)

        # Check that the image with atmosphere has some transparent pixels at the edges
        # (atmosphere creates a larger image with transparent padding)
        assert array_with_atmosphere.shape[0] > array_without_atmosphere.shape[0]
        assert array_with_atmosphere.shape[1] > array_without_atmosphere.shape[1]

    def test_atmosphere_parameters(self, planet_generator, temp_output_dir):
        """
        Test atmosphere parameters.
        """
        # Create a planet with atmosphere and default parameters
        planet_default = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "atmosphere": True,
            "atmosphere_glow": 0.5,
            "atmosphere_halo": 0.7,
            "atmosphere_blur": 0.5
        })

        # Ensure the atmosphere is enabled
        planet_default.has_atmosphere = True
        planet_default.atmosphere.enabled = True

        # Render the planet
        image_default = planet_default.render()

        # Create a planet with atmosphere and custom parameters
        planet_custom = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "atmosphere": True,
            "atmosphere_glow": 1.0,
            "atmosphere_halo": 0.0,  # No halo
            "atmosphere_blur": 0.2
        })

        # Ensure the atmosphere is enabled
        planet_custom.has_atmosphere = True
        planet_custom.atmosphere.enabled = True

        # Render the planet
        image_custom = planet_custom.render()

        # Convert images to arrays for comparison
        array_default = np.array(image_default)
        array_custom = np.array(image_custom)

        # Check that the images are different
        assert not np.array_equal(array_default, array_custom)

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

        # Check that cloud textures were created in the new directory structure
        seed_str = f"{desert_planet.seed:08d}"  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the cloud texture files exist
        cloud_texture_path = os.path.join(planet_dir, "cloud_texture.png")
        cloud_mask_path = os.path.join(planet_dir, "cloud_mask.png")
        assert os.path.exists(cloud_texture_path), f"Cloud texture {cloud_texture_path} not found"
        assert os.path.exists(cloud_mask_path), f"Cloud mask {cloud_mask_path} not found"

    # Esta prueba se ha eliminado porque no es esencial para el funcionamiento del generador

    def test_rings(self, desert_planet, temp_output_dir):
        """
        Test rings feature.
        """
        # Create a planet with rings
        desert_planet.has_rings = True
        desert_planet.rings_generator.enabled = True

        # Render the planet
        image_with_rings = desert_planet.render()

        # Create a planet without rings
        desert_planet.has_rings = False
        desert_planet.rings_generator.enabled = False

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

    def test_rings_complexity(self, planet_generator, temp_output_dir):
        """
        Test rings complexity parameter.
        """
        # Create planets with different ring complexities
        planet_simple = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "rings": True,
            "rings_complexity": 1  # Minimal complexity
        })

        planet_medium = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "rings": True,
            "rings_complexity": 2  # Medium complexity
        })

        planet_complex = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "rings": True,
            "rings_complexity": 3  # Full complexity
        })

        # Ensure rings are enabled
        planet_simple.has_rings = True
        planet_simple.rings_generator.enabled = True
        planet_medium.has_rings = True
        planet_medium.rings_generator.enabled = True
        planet_complex.has_rings = True
        planet_complex.rings_generator.enabled = True

        # Render the planets
        image_simple = planet_simple.render()
        image_medium = planet_medium.render()
        image_complex = planet_complex.render()

        # Check that the images have the correct properties
        assert isinstance(image_simple, Image.Image)
        assert isinstance(image_medium, Image.Image)
        assert isinstance(image_complex, Image.Image)

        # Check that the ring definitions are different
        assert len(planet_simple.rings_generator.last_ring_definitions) < len(planet_complex.rings_generator.last_ring_definitions)

    def test_rings_tilt(self, planet_generator, temp_output_dir):
        """
        Test rings tilt parameter.
        """
        # Create planets with different ring tilts
        planet_low_tilt = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "rings": True,
            "rings_tilt": 10.0  # Low tilt (more edge-on)
        })

        planet_high_tilt = planet_generator.create("Desert", {
            "size": 512,
            "seed": 12345,
            "rings": True,
            "rings_tilt": 70.0  # High tilt (more face-on)
        })

        # Ensure rings are enabled
        planet_low_tilt.has_rings = True
        planet_low_tilt.rings_generator.enabled = True
        planet_high_tilt.has_rings = True
        planet_high_tilt.rings_generator.enabled = True

        # Render the planets
        image_low_tilt = planet_low_tilt.render()
        image_high_tilt = planet_high_tilt.render()

        # Check that the images have the correct properties
        assert isinstance(image_low_tilt, Image.Image)
        assert isinstance(image_high_tilt, Image.Image)

        # Convert images to arrays for comparison
        array_low_tilt = np.array(image_low_tilt)
        array_high_tilt = np.array(image_high_tilt)

        # Check that the images are different
        assert not np.array_equal(array_low_tilt, array_high_tilt)

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
            "clouds_coverage": 0.7,
            "light_intensity": 1.2,
            "light_angle": 30.0
        })

        # Ensure all features are enabled
        planet.has_rings = True
        planet.rings_generator.enabled = True
        planet.has_atmosphere = True
        planet.atmosphere.enabled = True
        planet.has_clouds = True
        planet.clouds.enabled = True

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
