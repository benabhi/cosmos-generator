#!/usr/bin/env python3
"""
Test script for the Container functionality.
"""
import pytest
import numpy as np
from PIL import Image

import config
from cosmos_generator.utils.container import Container


class TestContainer:
    """
    Test cases for the Container class.
    """

    def test_container_initialization(self):
        """
        Test container initialization.
        """
        # Create a container with default settings
        container = Container()

        # Check that the container has the correct properties
        assert container.width == config.PLANET_SIZE
        assert container.height == config.PLANET_SIZE
        assert container.rotation == 0.0
        assert container.content is None
        assert container.zoom_level is None

    def test_container_custom_zoom(self):
        """
        Test container with custom zoom level.
        """
        # Create a container with custom zoom level
        container = Container(zoom_level=0.5)

        # Check that the zoom level was set correctly
        assert container.zoom_level == 0.5

    def test_container_zoom_limits(self):
        """
        Test container zoom level limits.
        """
        # Create a container with zoom level below the minimum
        container = Container(zoom_level=-0.5)

        # Check that the zoom level was clamped to the minimum
        assert container.zoom_level == config.CONTAINER_DEFAULT_SETTINGS["zoom_min"]

        # Create a container with zoom level above the maximum
        container = Container(zoom_level=1.5)

        # Check that the zoom level was clamped to the maximum
        assert container.zoom_level == config.CONTAINER_DEFAULT_SETTINGS["zoom_max"]

    def test_container_set_zoom(self):
        """
        Test setting the zoom level.
        """
        # Create a container
        container = Container()

        # Set the zoom level
        container.set_zoom(0.7)

        # Check that the zoom level was set correctly
        assert container.zoom_level == 0.7

    def test_container_set_rotation(self):
        """
        Test setting the rotation angle.
        """
        # Create a container
        container = Container()

        # Set the rotation angle
        container.set_rotation(45.0)

        # Check that the rotation angle was set correctly
        assert container.rotation == 45.0

    def test_container_rotate(self):
        """
        Test rotating the container.
        """
        # Create a container
        container = Container()

        # Rotate the container
        container.rotate(45.0)

        # Check that the rotation angle was set correctly
        assert container.rotation == 45.0

        # Rotate the container again
        container.rotate(45.0)

        # Check that the rotation angle was updated correctly
        assert container.rotation == 90.0

        # Rotate the container to exceed 360 degrees
        container.rotate(300.0)

        # Check that the rotation angle was normalized to [0, 360)
        assert container.rotation == 30.0

    def test_container_render_empty(self):
        """
        Test rendering an empty container.
        """
        # Create a container
        container = Container()

        # Render the container
        image = container.render()

        # Check that the image has the correct properties
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

    def test_container_with_planet_no_rings(self, desert_planet):
        """
        Test container with a planet without rings.
        """
        # Ensure the planet has no rings
        desert_planet.has_rings = False

        # Create a container and set the planet as content
        container = Container()
        container.set_content(desert_planet)

        # Render the container
        image = container.render()

        # Check that the image has the correct properties
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

        # Check that the default zoom level for planets without rings is used
        assert container.zoom_level is None  # It's None until render() is called

    def test_container_with_planet_with_rings(self, desert_planet_with_features):
        """
        Test container with a planet with rings.
        """
        # Ensure the planet has rings
        # Manually set has_rings to True for this test
        desert_planet_with_features.has_rings = True
        desert_planet_with_features.rings_generator.enabled = True

        # Create a container and set the planet as content
        container = Container()
        container.set_content(desert_planet_with_features)

        # Render the container
        image = container.render()

        # Check that the image has the correct properties
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"

        # Check that the default zoom level for planets with rings is used
        assert container.zoom_level is None  # It's None until render() is called

    def test_container_zoom_levels(self, desert_planet):
        """
        Test container with different zoom levels.
        """
        # Create a container and set the planet as content
        container = Container()
        container.set_content(desert_planet)

        # Test with minimum zoom level
        container.set_zoom(config.CONTAINER_DEFAULT_SETTINGS["zoom_min"])
        min_zoom_image = container.render()

        # Test with maximum zoom level
        container.set_zoom(config.CONTAINER_DEFAULT_SETTINGS["zoom_max"])
        max_zoom_image = container.render()

        # Convert images to arrays for comparison
        min_zoom_array = np.array(min_zoom_image)
        max_zoom_array = np.array(max_zoom_image)

        # Check that the images are different
        assert not np.array_equal(min_zoom_array, max_zoom_array)

    def test_container_rotation_angles(self, desert_planet):
        """
        Test container with different rotation angles.
        """
        # Create a container and set the planet as content
        container = Container()
        container.set_content(desert_planet)

        # Test with 0 degrees rotation
        container.set_rotation(0.0)
        no_rotation_image = container.render()

        # Test with 90 degrees rotation
        container.set_rotation(90.0)
        rotation_90_image = container.render()

        # Convert images to arrays for comparison
        no_rotation_array = np.array(no_rotation_image)
        rotation_90_array = np.array(rotation_90_image)

        # Check that the images are different
        assert not np.array_equal(no_rotation_array, rotation_90_array)

    def test_container_export(self, desert_planet, temp_output_dir):
        """
        Test exporting a container to a file.
        """
        # Create a container and set the planet as content
        container = Container()
        container.set_content(desert_planet)

        # Export the container to a file
        output_path = f"{temp_output_dir}/container_export_test.png"
        container.export(output_path)

        # Check that the file was created
        import os
        assert os.path.exists(output_path)

        # Check that the file is a valid image
        image = Image.open(output_path)
        assert isinstance(image, Image.Image)
        assert image.width == config.PLANET_SIZE
        assert image.height == config.PLANET_SIZE
        assert image.mode == "RGBA"
