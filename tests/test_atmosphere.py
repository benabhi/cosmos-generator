"""
Tests for the Atmosphere class.
"""
import pytest
import numpy as np
from PIL import Image

from cosmos_generator.features.atmosphere import Atmosphere


@pytest.fixture
def atmosphere():
    """
    Fixture that provides an Atmosphere instance with default parameters.
    """
    return Atmosphere(seed=12345)


@pytest.fixture
def test_image():
    """
    Fixture that provides a simple test image.
    """
    # Create a simple planet image (black circle on transparent background)
    size = 100
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    
    # Draw a black circle in the center
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, size-1, size-1), fill=(0, 0, 0, 255))
    
    return image


def test_atmosphere_creation():
    """
    Test that an Atmosphere instance can be created with various parameters.
    """
    # Create with default parameters
    atmo1 = Atmosphere()
    assert atmo1.enabled is True
    assert atmo1.glow_intensity == 0.5
    assert atmo1.halo_intensity == 0.7
    assert atmo1.halo_thickness == 3
    assert atmo1.blur_amount == 0.5
    
    # Create with custom parameters
    atmo2 = Atmosphere(
        enabled=False,
        glow_intensity=0.8,
        halo_intensity=0.2,
        halo_thickness=5,
        blur_amount=0.3
    )
    assert atmo2.enabled is False
    assert atmo2.glow_intensity == 0.8
    assert atmo2.halo_intensity == 0.2
    assert atmo2.halo_thickness == 5
    assert atmo2.blur_amount == 0.3
    
    # Test parameter clamping
    atmo3 = Atmosphere(
        glow_intensity=1.5,  # Should be clamped to 1.0
        halo_intensity=-0.5,  # Should be clamped to 0.0
        halo_thickness=15,  # Should be clamped to 10
        blur_amount=2.0  # Should be clamped to 1.0
    )
    assert atmo3.glow_intensity == 1.0
    assert atmo3.halo_intensity == 0.0
    assert atmo3.halo_thickness == 10
    assert atmo3.blur_amount == 1.0


def test_atmosphere_disabled(atmosphere, test_image):
    """
    Test that a disabled atmosphere returns the original image.
    """
    # Disable the atmosphere
    atmosphere.enabled = False
    
    # Apply to the test image
    result = atmosphere.apply_to_planet(test_image, "Desert")
    
    # Check that the result is the same as the input
    assert result.size == test_image.size
    assert np.array_equal(np.array(result), np.array(test_image))


def test_atmosphere_glow(atmosphere, test_image):
    """
    Test that atmosphere glow is applied correctly.
    """
    # Set parameters for testing glow only
    atmosphere.glow_intensity = 1.0
    atmosphere.halo_intensity = 0.0  # Disable halo
    
    # Apply to the test image
    result = atmosphere.apply_to_planet(test_image, "Desert")
    
    # Check that the result is larger than the input (due to glow padding)
    assert result.width > test_image.width
    assert result.height > test_image.height
    
    # Check that the result has some semi-transparent pixels (the glow)
    result_array = np.array(result)
    # Count pixels with alpha > 0 but < 255
    semi_transparent_pixels = np.sum((result_array[:, :, 3] > 0) & (result_array[:, :, 3] < 255))
    assert semi_transparent_pixels > 0


def test_atmosphere_halo(atmosphere, test_image):
    """
    Test that atmosphere halo is applied correctly.
    """
    # Set parameters for testing halo only
    atmosphere.glow_intensity = 0.0  # Minimal glow
    atmosphere.halo_intensity = 1.0  # Maximum halo
    atmosphere.halo_thickness = 5    # Thick halo
    
    # Apply to the test image
    result = atmosphere.apply_to_planet(test_image, "Desert")
    
    # The result should still be larger than the input due to minimal glow
    assert result.width > test_image.width
    assert result.height > test_image.height
    
    # Check that the result has some semi-transparent pixels (the halo)
    result_array = np.array(result)
    # Count pixels with alpha > 0 but < 255
    semi_transparent_pixels = np.sum((result_array[:, :, 3] > 0) & (result_array[:, :, 3] < 255))
    assert semi_transparent_pixels > 0


def test_atmosphere_with_rings(atmosphere, test_image):
    """
    Test that atmosphere is applied correctly with rings.
    """
    # Apply to the test image with rings=True
    result = atmosphere.apply_to_planet(test_image, "Desert", has_rings=True)
    
    # The result should be larger than the input but with smaller padding
    assert result.width > test_image.width
    assert result.height > test_image.height
    
    # Apply to the test image with rings=False
    result_no_rings = atmosphere.apply_to_planet(test_image, "Desert", has_rings=False)
    
    # The result without rings should be larger than the result with rings
    # because we use smaller padding for planets with rings
    assert result_no_rings.width >= result.width
    assert result_no_rings.height >= result.height


def test_atmosphere_blur(atmosphere, test_image):
    """
    Test that atmosphere blur is applied correctly.
    """
    # Test with different blur amounts
    atmosphere.glow_intensity = 0.5
    atmosphere.halo_intensity = 0.0  # Disable halo for this test
    
    # Low blur
    atmosphere.blur_amount = 0.2
    result_low_blur = atmosphere.apply_to_planet(test_image, "Desert")
    
    # High blur
    atmosphere.blur_amount = 0.8
    result_high_blur = atmosphere.apply_to_planet(test_image, "Desert")
    
    # Both results should be the same size
    assert result_low_blur.size == result_high_blur.size
    
    # But the pixel values should be different due to different blur amounts
    assert not np.array_equal(np.array(result_low_blur), np.array(result_high_blur))


def test_legacy_methods(test_image):
    """
    Test that legacy methods still work for backward compatibility.
    """
    atmosphere = Atmosphere(seed=12345)
    
    # Test apply_atmosphere
    result1 = atmosphere.apply_atmosphere(test_image, "Desert", intensity=0.6)
    assert result1.width > test_image.width
    assert result1.height > test_image.height
    
    # Test apply_simple_atmosphere
    result2 = atmosphere.apply_simple_atmosphere(test_image, "Desert", intensity=0.6)
    assert result2.width > test_image.width
    assert result2.height > test_image.height
    
    # The results should be different because apply_simple_atmosphere doesn't add a halo
    assert not np.array_equal(np.array(result1), np.array(result2))
