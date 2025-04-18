#!/usr/bin/env python3
"""
Test script for the Planet Generator functionality.
"""
import os
import pytest
from PIL import Image

from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.container import Container
import config


class TestPlanetGenerator:
    """
    Test cases for the PlanetGenerator class.
    """

    def test_create_desert_planet(self, planet_generator, temp_output_dir):
        """
        Test creating a desert planet.
        """
        planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

        # Check that the planet was created
        assert planet is not None

        # Check that the planet has the correct type
        assert planet.PLANET_TYPE == "Desert"

        # Check that the planet has the correct size
        assert planet.size == config.PLANET_SIZE

        # Check that the planet has the correct seed
        assert planet.seed == 12345

        # Check that the planet can be rendered
        image = planet.render()
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_create_ocean_planet(self, planet_generator, temp_output_dir):
        """
        Test creating an ocean planet.
        """
        planet = planet_generator.create("Ocean", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

        # Check that the planet was created
        assert planet is not None

        # Check that the planet has the correct type
        assert planet.PLANET_TYPE == "Ocean"

        # Check that the planet has the correct size
        assert planet.size == config.PLANET_SIZE

        # Check that the planet has the correct seed
        assert planet.seed == 12345

        # Check that the planet can be rendered
        image = planet.render()
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_create_planet_with_features(self, planet_generator, temp_output_dir):
        """
        Test creating a planet with various features.
        """
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

        # Check that the planet was created
        assert planet is not None

        # Check that the features were set correctly
        assert planet.has_rings is True
        assert planet.has_atmosphere is True
        assert planet.has_clouds is True
        assert planet.cloud_coverage == 0.7
        assert planet.light_intensity == 1.2
        assert planet.light_angle == 30.0

        # Check that the planet can be rendered
        image = planet.render()
        assert isinstance(image, Image.Image)
        assert image.width > config.PLANET_SIZE  # With rings, the image is larger
        assert image.height > config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_planet_variations(self, planet_generator, temp_output_dir):
        """
        Test creating planets with different variations.
        """
        # Test Ocean planet with archipelago variation
        archipelago_planet = planet_generator.create("Ocean", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "archipelago"
        })

        assert archipelago_planet is not None
        assert archipelago_planet.variation == "archipelago"

        # Test Ocean planet with water_world variation
        water_world_planet = planet_generator.create("Ocean", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "water_world"
        })

        assert water_world_planet is not None
        assert water_world_planet.variation == "water_world"

        # Render both planets to ensure they're different
        archipelago_image = archipelago_planet.render()
        water_world_image = water_world_planet.render()

        # Convert images to arrays for comparison
        import numpy as np
        archipelago_array = np.array(archipelago_image)
        water_world_array = np.array(water_world_image)

        # Check that the images are different (they should have different pixel values)
        # We're just checking if they're not identical, not specific differences
        assert not np.array_equal(archipelago_array, water_world_array)

    def test_reproducibility(self, temp_output_dir):
        """
        Test that planets generated with the same seed are identical.
        """
        # Create two generators with the same seed
        generator1 = PlanetGenerator(seed=54321)
        generator2 = PlanetGenerator(seed=54321)

        # Create two planets with the same parameters
        planet1 = generator1.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 54321
        })

        planet2 = generator2.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 54321
        })

        # Render both planets
        image1 = planet1.render()
        image2 = planet2.render()

        # Convert images to arrays for comparison
        import numpy as np
        array1 = np.array(image1)
        array2 = np.array(image2)

        # Check that the images are identical
        assert np.array_equal(array1, array2)

    def test_different_seeds(self, temp_output_dir):
        """
        Test that planets generated with different seeds are different.
        """
        # Create a generator
        generator = PlanetGenerator()

        # Create two planets with different seeds
        planet1 = generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

        planet2 = generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 54321
        })

        # Render both planets
        image1 = planet1.render()
        image2 = planet2.render()

        # Convert images to arrays for comparison
        import numpy as np
        array1 = np.array(image1)
        array2 = np.array(image2)

        # Check that the images are different
        assert not np.array_equal(array1, array2)

    def test_container_integration(self, planet_generator, temp_output_dir):
        """
        Test integration between PlanetGenerator and Container.
        """
        # Create a planet
        planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

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

    def test_debug_output_files(self, planet_generator, temp_output_dir):
        """
        Test that debug output files are created correctly.
        """
        # Create a planet with all features
        planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "rings": True,
            "atmosphere": True,
            "clouds": True
        })

        # Render the planet to trigger file creation
        planet.render()

        # Check that the terrain texture was created
        terrain_texture_path = os.path.join(config.PLANETS_TERRAIN_TEXTURES_DIR, "12345.png")
        assert os.path.exists(terrain_texture_path)

        # Check that the cloud textures were created
        cloud_dir = os.path.join(config.PLANETS_CLOUDS_TEXTURES_DIR, "12345")
        assert os.path.exists(cloud_dir)
        assert os.path.exists(os.path.join(cloud_dir, "mask.png"))
        assert os.path.exists(os.path.join(cloud_dir, "texture.png"))
        assert os.path.exists(os.path.join(cloud_dir, "adjusted_mask.png"))  # New file from cloud visibility enhancement
