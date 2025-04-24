"""
Tests for the Ice planet type.

This module contains tests for the Ice planet type and its variations.
"""
import os
import pytest
from PIL import Image

from cosmos_generator.celestial_bodies.planets.ice import IcePlanet
from cosmos_generator.utils.container import Container


class TestIcePlanet:
    """Test suite for the Ice planet type."""

    def test_ice_planet_creation(self):
        """Test that an Ice planet can be created with default parameters."""
        planet = IcePlanet(seed=12345)
        assert planet is not None
        assert planet.PLANET_TYPE == "Ice"
        assert planet.variation == "glacier"  # Default variation

    def test_ice_planet_variations(self):
        """Test that all Ice planet variations can be created."""
        variations = ["glacier", "tundra", "frozen_ocean"]
        for variation in variations:
            planet = IcePlanet(seed=12345, variation=variation)
            assert planet.variation == variation

    def test_ice_planet_texture_generation(self):
        """Test that Ice planet textures can be generated for all variations."""
        variations = ["glacier", "tundra", "frozen_ocean"]
        for variation in variations:
            planet = IcePlanet(seed=12345, variation=variation)
            texture = planet.generate_texture()
            assert isinstance(texture, Image.Image)
            assert texture.size == (512, 512)

    def test_ice_planet_with_container(self):
        """Test that an Ice planet can be rendered in a container."""
        planet = IcePlanet(seed=12345)
        container = Container(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_ice_planet_with_atmosphere(self):
        """Test that an Ice planet can be rendered with atmosphere."""
        planet = IcePlanet(seed=12345, atmosphere=True)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_ice_planet_with_rings(self):
        """Test that an Ice planet can be rendered with rings."""
        planet = IcePlanet(seed=12345, rings=True)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_ice_planet_with_clouds(self):
        """Test that an Ice planet can be rendered with clouds."""
        planet = IcePlanet(seed=12345, cloud_coverage=0.5)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_ice_planet_with_all_features(self):
        """Test that an Ice planet can be rendered with all features."""
        planet = IcePlanet(
            seed=12345,
            atmosphere=True,
            rings=True,
            cloud_coverage=0.5
        )
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_ice_planet_different_variations_with_features(self):
        """Test that all Ice planet variations can be rendered with features."""
        variations = ["glacier", "tundra", "frozen_ocean"]
        for variation in variations:
            planet = IcePlanet(
                seed=12345,
                variation=variation,
                atmosphere=True,
                rings=True,
                cloud_coverage=0.5
            )
            container = Container()
            container.set_content(planet)
            image = container.render()
            assert isinstance(image, Image.Image)
            assert image.size == (512, 512)

    def test_ice_planet_different_seeds(self):
        """Test that Ice planets with different seeds look different."""
        planet1 = IcePlanet(seed=12345)
        planet2 = IcePlanet(seed=54321)

        texture1 = planet1.generate_texture()
        texture2 = planet2.generate_texture()

        # Convert to RGB mode for comparison if they're not already
        if texture1.mode != 'RGB':
            texture1 = texture1.convert('RGB')
        if texture2.mode != 'RGB':
            texture2 = texture2.convert('RGB')

        # Get the pixel data
        pixels1 = list(texture1.getdata())
        pixels2 = list(texture2.getdata())

        # Check that at least 30% of pixels are different
        different_pixels = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 != p2)
        assert different_pixels > (512 * 512 * 0.3)  # 30% of total pixels

    def test_ice_planet_zoom_levels(self):
        """Test that Ice planets can be rendered at different zoom levels."""
        planet = IcePlanet(seed=12345)

        # Test with no rings at default zoom
        container1 = Container()
        container1.set_content(planet)
        image1 = container1.render()

        # Test with no rings at zoom 0.5
        container2 = Container(0.5)
        container2.set_content(planet)
        image2 = container2.render()

        # Test with rings at default zoom
        planet_with_rings = IcePlanet(seed=12345, rings=True)
        container3 = Container()
        container3.set_content(planet_with_rings)
        image3 = container3.render()

        # Test with rings at zoom 0.5
        container4 = Container(0.5)
        container4.set_content(planet_with_rings)
        image4 = container4.render()

        assert isinstance(image1, Image.Image)
        assert isinstance(image2, Image.Image)
        assert isinstance(image3, Image.Image)
        assert isinstance(image4, Image.Image)
