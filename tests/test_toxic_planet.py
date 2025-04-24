"""
Tests for the Toxic planet type.
"""
import pytest
from PIL import Image

from cosmos_generator.celestial_bodies.planets.toxic import ToxicPlanet
from cosmos_generator.features.atmosphere import Atmosphere
from cosmos_generator.features.rings import Rings
from cosmos_generator.utils.container import Container
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator


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
def rings(noise_gen, color_palette):
    """Create rings for testing."""
    return Rings(noise_gen=noise_gen, color_palette=color_palette)


def test_toxic_planet_creation(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be created."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_variation_toxic_veins(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be created with the toxic_veins variation."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        variation="toxic_veins"
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_variation_acid_lakes(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be created with the acid_lakes variation."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        variation="acid_lakes"
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_variation_corrosive_storms(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be created with the corrosive_storms variation."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        variation="corrosive_storms"
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_atmosphere(noise_gen, color_palette, texture_gen, atmosphere):
    """Test that a Toxic planet can be created with an atmosphere."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        atmosphere=atmosphere,
        has_atmosphere=True
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_clouds(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be created with clouds."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        has_clouds=True,
        cloud_coverage=0.7
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_with_rings(noise_gen, color_palette, texture_gen, rings):
    """Test that a Toxic planet can be created with rings."""
    planet = ToxicPlanet(
        seed=12345,
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen,
        rings=rings,
        has_rings=True
    )
    result = planet.render()
    assert isinstance(result, Image.Image)


def test_toxic_planet_in_container(noise_gen, color_palette, texture_gen):
    """Test that a Toxic planet can be placed in a container."""
    planet = ToxicPlanet(
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


def test_toxic_planet_with_all_features(noise_gen, color_palette, texture_gen, atmosphere, rings):
    """Test that a Toxic planet can be created with all features."""
    planet = ToxicPlanet(
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
