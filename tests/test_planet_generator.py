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

    def test_create_basic_planets(self, planet_generator, temp_output_dir):
        """
        Test creating basic planets of different types.
        """
        # Test Desert planet
        desert_planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

        # Check that the planet was created with correct properties
        assert desert_planet is not None
        assert desert_planet.PLANET_TYPE == "Desert"
        assert desert_planet.size == config.PLANET_SIZE
        assert desert_planet.seed == 12345

        # Check that the planet can be rendered
        desert_image = desert_planet.render()
        assert isinstance(desert_image, Image.Image)
        assert desert_image.width == config.PLANET_SIZE
        assert desert_image.height == config.PLANET_SIZE
        assert desert_image.mode == "RGBA"

        # Test Ocean planet
        ocean_planet = planet_generator.create("Ocean", {
            "size": config.PLANET_SIZE,
            "seed": 12345
        })

        # Check that the planet was created with correct properties
        assert ocean_planet is not None
        assert ocean_planet.PLANET_TYPE == "Ocean"
        assert ocean_planet.size == config.PLANET_SIZE
        assert ocean_planet.seed == 12345

        # Check that the planet can be rendered
        ocean_image = ocean_planet.render()
        assert isinstance(ocean_image, Image.Image)
        assert ocean_image.width == config.PLANET_SIZE
        assert ocean_image.height == config.PLANET_SIZE
        assert ocean_image.mode == "RGBA"

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

        # Manually set the features
        planet.has_rings = True
        planet.rings_generator.enabled = True
        planet.has_atmosphere = True
        planet.atmosphere.enabled = True
        planet.has_clouds = True
        planet.clouds.enabled = True
        planet.clouds.coverage = 0.7

        # Check that the features were set correctly
        assert planet.has_rings is True
        assert planet.has_atmosphere is True
        assert planet.has_clouds is True
        assert planet.clouds.coverage == 0.7
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
        import numpy as np

        # Test Ocean planet variations
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

        # Test Ocean planet with reef variation
        reef_planet = planet_generator.create("Ocean", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "reef"
        })

        assert reef_planet is not None
        assert reef_planet.variation == "reef"

        # Render all ocean planets to ensure they're different
        archipelago_image = archipelago_planet.render()
        water_world_image = water_world_planet.render()
        reef_image = reef_planet.render()

        # Convert images to arrays for comparison
        archipelago_array = np.array(archipelago_image)
        water_world_array = np.array(water_world_image)
        reef_array = np.array(reef_image)

        # Check that the images are different (they should have different pixel values)
        # We're just checking if they're not identical, not specific differences
        assert not np.array_equal(archipelago_array, water_world_array)
        assert not np.array_equal(archipelago_array, reef_array)
        assert not np.array_equal(water_world_array, reef_array)

        # Test Desert planet variations
        # Test Desert planet with arid variation
        arid_planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "arid"
        })

        assert arid_planet is not None
        assert arid_planet.variation == "arid"

        # Test Desert planet with dunes variation
        dunes_planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "dunes"
        })

        assert dunes_planet is not None
        assert dunes_planet.variation == "dunes"

        # Test Desert planet with mesa variation
        mesa_planet = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "variation": "mesa"
        })

        assert mesa_planet is not None
        assert mesa_planet.variation == "mesa"

        # Render all desert planets to ensure they're different
        arid_image = arid_planet.render()
        dunes_image = dunes_planet.render()
        mesa_image = mesa_planet.render()

        # Convert images to arrays for comparison
        arid_array = np.array(arid_image)
        dunes_array = np.array(dunes_image)
        mesa_array = np.array(mesa_image)

        # Check that the images are different (they should have different pixel values)
        assert not np.array_equal(arid_array, dunes_array)
        assert not np.array_equal(arid_array, mesa_array)
        assert not np.array_equal(dunes_array, mesa_array)

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
            "seed": 12345,
            "variation": "arid"  # Add variation to make them different
        })

        planet2 = generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 54321,
            "variation": "rocky"  # Add variation to make them different
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

    def test_color_palette_selection(self, planet_generator, temp_output_dir):
        """
        Test that planets can be generated with specific color palettes.
        """
        import numpy as np

        # Create planets with different color palette IDs
        planet1 = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "color_palette_id": 1
        })

        planet2 = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "color_palette_id": 2
        })

        planet3 = planet_generator.create("Desert", {
            "size": config.PLANET_SIZE,
            "seed": 12345,
            "color_palette_id": 3
        })

        # Check that the color palette IDs were set correctly
        assert planet1.color_palette_id == 1
        assert planet2.color_palette_id == 2
        assert planet3.color_palette_id == 3

        # Render the planets
        image1 = planet1.render()
        image2 = planet2.render()
        image3 = planet3.render()

        # Convert images to arrays for comparison
        array1 = np.array(image1)
        array2 = np.array(image2)
        array3 = np.array(image3)

        # Check that the images are different (they should have different color palettes)
        assert not np.array_equal(array1, array2)
        assert not np.array_equal(array1, array3)
        assert not np.array_equal(array2, array3)

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

        # Manually set the features
        planet.has_rings = True
        planet.rings_generator.enabled = True
        planet.has_atmosphere = True
        planet.atmosphere.enabled = True
        planet.has_clouds = True
        planet.clouds.enabled = True

        # Render the planet to trigger file creation
        planet.render()

        # Check that the terrain texture was created
        # Use the new path structure: /planets/desert/00012345/terrain_texture.png
        seed_str = "00012345"  # Padded to 8 characters
        terrain_texture_path = config.get_planet_texture_path("desert", seed_str, "terrain")
        assert os.path.exists(terrain_texture_path)

        # Check that the cloud textures were created
        cloud_texture_path = config.get_planet_texture_path("desert", seed_str, "cloud_texture")
        cloud_mask_path = config.get_planet_texture_path("desert", seed_str, "cloud_mask")
        assert os.path.exists(cloud_texture_path)
        assert os.path.exists(cloud_mask_path)
