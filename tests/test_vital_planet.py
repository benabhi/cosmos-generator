"""
Tests for the Vital planet type.
"""
import pytest
from PIL import Image

from cosmos_generator.celestial_bodies.planets.vital import VitalPlanet
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.features.clouds import Clouds
from cosmos_generator.features.rings import Rings
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
def texture_gen(noise_gen):
    """Create a texture generator for testing."""
    return TextureGenerator(noise_gen=noise_gen)


@pytest.fixture
def atmosphere(color_palette):
    """Create an atmosphere for testing."""
    return Atmosphere(color_palette=color_palette)


@pytest.fixture
def clouds(noise_gen):
    """Create clouds for testing."""
    return Clouds(noise_gen=noise_gen)


@pytest.fixture
def rings(noise_gen, color_palette):
    """Create rings for testing."""
    return Rings(noise_gen=noise_gen, color_palette=color_palette)


def test_vital_planet_init():
    """Test that a Vital planet can be initialized."""
    planet = VitalPlanet(seed=12345)
    assert planet.PLANET_TYPE == "Vital"
    assert planet.size == 512


def test_vital_planet_variations():
    """Test that a Vital planet can be created with different variations."""
    # Test earthlike variation
    planet1 = VitalPlanet(seed=12345, variation="earthlike")
    assert planet1.variation == "earthlike"

    # Test archipelago variation
    planet2 = VitalPlanet(seed=12345, variation="archipelago")
    assert planet2.variation == "archipelago"

    # Test pangaea variation
    planet3 = VitalPlanet(seed=12345, variation="pangaea")
    assert planet3.variation == "pangaea"


def test_vital_planet_generate_texture(noise_gen, color_palette, texture_gen):
    """Test that a Vital planet can generate a texture."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen
    )
    texture = planet.generate_texture()
    assert isinstance(texture, Image.Image)
    assert texture.size == (512, 512)


def test_vital_planet_with_atmosphere(noise_gen, color_palette, texture_gen, atmosphere):
    """Test that a Vital planet can be created with an atmosphere."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        atmosphere=atmosphere,
        has_atmosphere=True
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_vital_planet_with_clouds(noise_gen, color_palette, texture_gen):
    """Test that a Vital planet can be created with clouds."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        has_clouds=True,
        cloud_coverage=0.7
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_vital_planet_with_rings(noise_gen, color_palette, texture_gen, rings):
    """Test that a Vital planet can be created with rings."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        rings=rings,
        has_rings=True
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_vital_planet_in_container(noise_gen, color_palette, texture_gen):
    """Test that a Vital planet can be placed in a container."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen
    )
    container = Container(zoom_level=0.5)
    container.set_content(planet)
    result = container.render()
    assert isinstance(result, Image.Image)
    assert result.size == (512, 512)


def test_vital_planet_with_all_features(noise_gen, color_palette, texture_gen, atmosphere, rings):
    """Test that a Vital planet can be created with all features."""
    planet = VitalPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        atmosphere=atmosphere,
        rings=rings,
        has_atmosphere=True,
        has_clouds=True,
        has_rings=True,
        cloud_coverage=0.6
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_vital_planet_color_palettes():
    """Test that a Vital planet can use different color palettes."""
    # Test color palette 1
    planet1 = VitalPlanet(seed=12345, color_palette_id=1)
    assert planet1.color_palette_id == 1

    # Test color palette 2
    planet2 = VitalPlanet(seed=12345, color_palette_id=2)
    assert planet2.color_palette_id == 2

    # Test color palette 3
    planet3 = VitalPlanet(seed=12345, color_palette_id=3)
    assert planet3.color_palette_id == 3
