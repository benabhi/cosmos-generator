"""
Tests for the Jovian planet implementation.
"""
import pytest
from PIL import Image

from cosmos_generator.celestial_bodies.planets.jovian import JovianPlanet
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator
from cosmos_generator.core.color_palette import ColorPalette
from cosmos_generator.core.texture_generator import TextureGenerator


@pytest.fixture
def jovian_planet():
    """Create a basic Jovian planet for testing."""
    seed = 12345
    noise_gen = FastNoiseGenerator(seed=seed)
    color_palette = ColorPalette(seed=seed)
    texture_gen = TextureGenerator(seed=seed, noise_gen=noise_gen, color_palette=color_palette)
    
    return JovianPlanet(
        seed=seed,
        size=256,  # Smaller size for faster tests
        noise_gen=noise_gen,
        color_palette=color_palette,
        texture_gen=texture_gen
    )


def test_jovian_planet_init(jovian_planet):
    """Test that a Jovian planet can be initialized correctly."""
    assert jovian_planet.PLANET_TYPE == "Jovian"
    assert jovian_planet.size == 256
    assert jovian_planet.variation == "bands"  # Default variation


def test_jovian_planet_generate_texture(jovian_planet):
    """Test that a Jovian planet can generate a texture."""
    texture = jovian_planet.generate_texture()
    
    # Check that the texture is a PIL Image
    assert isinstance(texture, Image.Image)
    
    # Check that the texture has the correct size
    assert texture.width == jovian_planet.size
    assert texture.height == jovian_planet.size
    
    # Check that the texture has an alpha channel (RGBA)
    assert texture.mode == "RGBA"


def test_jovian_planet_variations():
    """Test that all Jovian planet variations can be generated."""
    seed = 12345
    size = 256  # Smaller size for faster tests
    
    # Test each variation
    for variation in ["bands", "storm", "nebulous"]:
        planet = JovianPlanet(
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


def test_jovian_planet_with_features():
    """Test that a Jovian planet can be generated with various features."""
    seed = 12345
    size = 256  # Smaller size for faster tests
    
    # Create a planet with rings and atmosphere
    planet = JovianPlanet(
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
