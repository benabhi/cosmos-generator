#!/usr/bin/env python3
"""
Test script for the Furnace Planet functionality.
"""
import pytest
from PIL import Image
import numpy as np

from cosmos_generator.celestial_bodies.planets.furnace import FurnacePlanet
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator


@pytest.fixture
def furnace_planet():
    """Create a basic Furnace planet for testing."""
    seed = 12345
    noise_gen = FastNoiseGenerator(seed=seed)
    color_palette = ColorPalette(seed=seed)
    texture_gen = TextureGenerator(seed=seed, noise_gen=noise_gen, color_palette=color_palette)

    return FurnacePlanet(
        seed=seed,
        size=256,  # Smaller size for faster tests
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen
    )


def test_furnace_planet_init(furnace_planet):
    """Test that a Furnace planet can be initialized correctly."""
    assert furnace_planet.PLANET_TYPE == "Furnace"
    assert furnace_planet.size == 256
    assert furnace_planet.variation == "magma_rivers"  # Default variation


def test_furnace_planet_generate_texture(furnace_planet):
    """Test that a Furnace planet can generate a texture."""
    texture = furnace_planet.generate_texture()

    # Check that the texture is a PIL Image
    assert isinstance(texture, Image.Image)

    # Check that the texture has the correct size
    assert texture.width == furnace_planet.size
    assert texture.height == furnace_planet.size

    # Check that the texture has an alpha channel (RGBA)
    assert texture.mode == "RGBA"


def test_furnace_planet_variations():
    """Test that all Furnace planet variations can be generated."""
    seed = 12345
    size = 256  # Smaller size for faster tests

    # Test each variation
    for variation in ["magma_rivers", "ember_wastes", "volcanic_hellscape"]:
        planet = FurnacePlanet(
            seed=seed,
            size=size,
            variation=variation
        )

        # Check that the variation was set correctly
        assert planet.variation == variation

        # Generate the texture
        texture = planet.generate_texture()

        # Check that the texture is a PIL Image with the correct size
        assert isinstance(texture, Image.Image)
        assert texture.width == size
        assert texture.height == size


def test_furnace_planet_with_features():
    """Test that a Furnace planet can be generated with various features."""
    seed = 12345
    size = 256  # Smaller size for faster tests

    # Create a planet with rings and atmosphere
    planet = FurnacePlanet(
        seed=seed,
        size=size,
        rings=True,
        atmosphere=True
    )

    # Check that the features were set correctly
    assert planet.has_rings
    assert planet.has_atmosphere

    # Render the planet
    image = planet.render()

    # Check that the image is a PIL Image
    assert isinstance(image, Image.Image)


def test_furnace_planet_color_palettes():
    """Test that a Furnace planet can be generated with different color palettes."""
    seed = 12345
    size = 256  # Smaller size for faster tests

    # Test each color palette
    for palette_id in range(1, 4):  # 1, 2, 3
        planet = FurnacePlanet(
            seed=seed,
            size=size,
            color_palette_id=palette_id
        )

        # Check that the color palette was set correctly
        assert planet.color_palette_id == palette_id

        # Generate the texture
        texture = planet.generate_texture()

        # Check that the texture is a PIL Image with the correct size
        assert isinstance(texture, Image.Image)
        assert texture.width == size
        assert texture.height == size


def test_furnace_planet_different_seeds():
    """Test that Furnace planets with different seeds are different."""
    size = 256  # Smaller size for faster tests

    # Create two planets with different seeds
    planet1 = FurnacePlanet(
        seed=12345,
        size=size,
        variation="magma_rivers"
    )

    planet2 = FurnacePlanet(
        seed=54321,
        size=size,
        variation="magma_rivers"
    )

    # Generate textures
    texture1 = planet1.generate_texture()
    texture2 = planet2.generate_texture()

    # Convert to numpy arrays for comparison
    array1 = np.array(texture1)
    array2 = np.array(texture2)

    # Check that the textures are different
    assert not np.array_equal(array1, array2)


def test_furnace_planet_reproducibility():
    """Test that Furnace planets with the same seed are identical."""
    size = 256  # Smaller size for faster tests

    # Create two planets with the same seed
    planet1 = FurnacePlanet(
        seed=12345,
        size=size,
        variation="magma_rivers"
    )

    planet2 = FurnacePlanet(
        seed=12345,
        size=size,
        variation="magma_rivers"
    )

    # Generate textures
    texture1 = planet1.generate_texture()
    texture2 = planet2.generate_texture()

    # Convert to numpy arrays for comparison
    array1 = np.array(texture1)
    array2 = np.array(texture2)

    # Check that the textures are identical
    assert np.array_equal(array1, array2)
