"""
Tests for the Rocky planet type.
"""
import pytest
from PIL import Image
import numpy as np

from cosmos_generator.celestial_bodies.planets.rocky import RockyPlanet
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator
from cosmos_generator.utils.container import Container


@pytest.fixture
def noise_gen():
    """Create a noise generator for testing."""
    return FastNoiseGenerator(seed=12345)


@pytest.fixture
def color_palette():
    """Create a color palette for testing."""
    return ColorPalette(seed=12345)


@pytest.fixture
def texture_gen(noise_gen, color_palette):
    """Create a texture generator for testing."""
    return TextureGenerator(seed=12345, noise_gen=noise_gen, color_palette=color_palette)


class TestRockyPlanet:
    """Test suite for the Rocky planet type."""

    def test_rocky_planet_creation(self):
        """Test that a Rocky planet can be created with default parameters."""
        planet = RockyPlanet(seed=12345)
        assert planet is not None
        assert planet.PLANET_TYPE == "Rocky"
        assert planet.variation == "cratered"  # Default variation

    def test_rocky_planet_variations(self):
        """Test that all Rocky planet variations can be created."""
        variations = ["cratered", "fractured", "mountainous"]
        for variation in variations:
            planet = RockyPlanet(seed=12345, variation=variation)
            assert planet.variation == variation

    def test_rocky_planet_texture_generation(self):
        """Test that Rocky planet textures can be generated for all variations."""
        variations = ["cratered", "fractured", "mountainous"]
        for variation in variations:
            planet = RockyPlanet(seed=12345, variation=variation)
            texture = planet.generate_texture()
            assert isinstance(texture, Image.Image)
            assert texture.size == (512, 512)

    def test_rocky_planet_with_container(self):
        """Test that a Rocky planet can be rendered in a container."""
        planet = RockyPlanet(seed=12345)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_rocky_planet_with_atmosphere(self):
        """Test that a Rocky planet can be rendered with atmosphere."""
        planet = RockyPlanet(seed=12345, atmosphere=True)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_rocky_planet_with_rings(self):
        """Test that a Rocky planet can be rendered with rings."""
        planet = RockyPlanet(seed=12345, rings=True)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_rocky_planet_with_clouds(self):
        """Test that a Rocky planet can be rendered with clouds."""
        planet = RockyPlanet(seed=12345, cloud_coverage=0.5)
        container = Container()
        container.set_content(planet)
        image = container.render()
        assert isinstance(image, Image.Image)
        assert image.size == (512, 512)

    def test_rocky_planet_with_all_features(self):
        """Test that a Rocky planet can be rendered with all features."""
        planet = RockyPlanet(
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

    def test_rocky_planet_different_variations_with_features(self):
        """Test that all Rocky planet variations can be rendered with features."""
        variations = ["cratered", "fractured", "mountainous"]
        for variation in variations:
            planet = RockyPlanet(
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

    def test_rocky_planet_different_seeds(self):
        """Test that Rocky planets with different seeds look different."""
        planet1 = RockyPlanet(seed=12345)
        planet2 = RockyPlanet(seed=54321)

        # Render both planets
        container1 = Container()
        container1.set_content(planet1)
        image1 = container1.render()

        container2 = Container()
        container2.set_content(planet2)
        image2 = container2.render()

        # Convert to numpy arrays for comparison
        array1 = np.array(image1)
        array2 = np.array(image2)

        # Get the pixels
        pixels1 = array1.reshape(-1, 4)  # RGBA
        pixels2 = array2.reshape(-1, 4)  # RGBA

        # Check that at least 30% of pixels are different
        different_pixels = sum(1 for p1, p2 in zip(pixels1, pixels2) if not np.array_equal(p1, p2))
        assert different_pixels > (512 * 512 * 0.3)  # 30% of total pixels

    def test_rocky_planet_zoom_levels(self):
        """Test that Rocky planets can be rendered at different zoom levels."""
        planet = RockyPlanet(seed=12345)

        # Test with no rings at default zoom
        container1 = Container()
        container1.set_content(planet)
        image1 = container1.render()

        # Test with no rings at zoom 0.5
        container2 = Container(0.5)
        container2.set_content(planet)
        image2 = container2.render()

        # Test with rings at default zoom
        planet_with_rings = RockyPlanet(seed=12345, rings=True)
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

    def test_rocky_planet_color_palettes(self):
        """Test that a Rocky planet can use different color palettes."""
        # Test color palette 1
        planet1 = RockyPlanet(seed=12345, color_palette_id=1)
        assert planet1.color_palette_id == 1

        # Test color palette 2
        planet2 = RockyPlanet(seed=12345, color_palette_id=2)
        assert planet2.color_palette_id == 2

        # Test color palette 3
        planet3 = RockyPlanet(seed=12345, color_palette_id=3)
        assert planet3.color_palette_id == 3

        # Generate textures for each palette
        texture1 = planet1.generate_texture()
        texture2 = planet2.generate_texture()
        texture3 = planet3.generate_texture()

        # Convert to numpy arrays for comparison
        array1 = np.array(texture1)
        array2 = np.array(texture2)
        array3 = np.array(texture3)

        # Check that the textures are different
        assert not np.array_equal(array1, array2)
        assert not np.array_equal(array1, array3)
        assert not np.array_equal(array2, array3)
