"""
Tests for the FastNoiseGenerator class.
"""
import pytest
import numpy as np

from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator


@pytest.fixture
def noise_gen():
    """
    Fixture that provides a FastNoiseGenerator instance with a fixed seed.
    """
    return FastNoiseGenerator(seed=12345)


def test_simplex_noise(noise_gen):
    """
    Test that simplex_noise returns values in the expected range.
    """
    # Generate a noise value
    value = noise_gen.simplex_noise(0.5, 0.5)
    
    # Check that the value is in the expected range [-1, 1]
    assert -1.0 <= value <= 1.0


def test_fractal_simplex(noise_gen):
    """
    Test that fractal_simplex returns values in the expected range.
    """
    # Generate a noise value
    value = noise_gen.fractal_simplex(0.5, 0.5, octaves=3, persistence=0.5, lacunarity=2.0, scale=1.0)
    
    # Check that the value is in the expected range [-1, 1]
    assert -1.0 <= value <= 1.0


def test_ridged_simplex(noise_gen):
    """
    Test that ridged_simplex returns values in the expected range.
    """
    # Generate a noise value
    value = noise_gen.ridged_simplex(0.5, 0.5, octaves=3, persistence=0.5, lacunarity=2.0, scale=1.0)
    
    # Check that the value is in the expected range [0, 1]
    assert 0.0 <= value <= 1.0


def test_worley_noise(noise_gen):
    """
    Test that worley_noise returns values in the expected range.
    """
    # Generate a noise value
    value = noise_gen.worley_noise(0.5, 0.5, cell_count=10, distance_function="euclidean")
    
    # Check that the value is in the expected range [0, 1]
    assert 0.0 <= value <= 1.0


def test_domain_warp(noise_gen):
    """
    Test that domain_warp correctly applies the warp function.
    """
    # Define a simple warp function
    def warp_func(x, y):
        return x + 0.1, y + 0.1
    
    # Define a simple noise function
    def noise_func(x, y):
        return (x + y) / 2
    
    # Generate a warped noise value
    value = noise_gen.domain_warp(0.5, 0.5, warp_func, noise_func)
    
    # Check that the value is the expected result
    expected = noise_func(warp_func(0.5, 0.5)[0], warp_func(0.5, 0.5)[1])
    assert value == expected


def test_simplex_warp(noise_gen):
    """
    Test that simplex_warp returns a tuple of warped coordinates.
    """
    # Generate warped coordinates
    x, y = noise_gen.simplex_warp(0.5, 0.5, warp_scale=0.1, warp_strength=0.5)
    
    # Check that the values are different from the input
    assert x != 0.5 or y != 0.5


def test_generate_noise_map(noise_gen):
    """
    Test that generate_noise_map returns a numpy array of the expected shape.
    """
    # Generate a noise map
    width, height = 10, 10
    noise_map = noise_gen.generate_noise_map(width, height, lambda x, y: noise_gen.simplex_noise(x, y))
    
    # Check that the noise map has the expected shape
    assert noise_map.shape == (height, width)
    
    # Check that the values are in the expected range [-1, 1]
    assert np.all(noise_map >= -1.0) and np.all(noise_map <= 1.0)


def test_normalize_noise_map(noise_gen):
    """
    Test that normalize_noise_map correctly normalizes a noise map to [0, 1].
    """
    # Create a test noise map with values in [-1, 1]
    noise_map = np.array([[-1.0, -0.5], [0.0, 1.0]])
    
    # Normalize the noise map
    normalized = noise_gen.normalize_noise_map(noise_map)
    
    # Check that the normalized map has values in [0, 1]
    assert np.all(normalized >= 0.0) and np.all(normalized <= 1.0)
    
    # Check that the minimum value is mapped to 0 and the maximum to 1
    assert normalized[0, 0] == 0.0  # -1.0 -> 0.0
    assert normalized[1, 1] == 1.0  # 1.0 -> 1.0


def test_combine_noise_maps(noise_gen):
    """
    Test that combine_noise_maps correctly combines multiple noise maps.
    """
    # Create test noise maps
    map1 = np.array([[0.0, 0.5], [0.5, 1.0]])
    map2 = np.array([[1.0, 0.5], [0.5, 0.0]])
    
    # Combine the noise maps with equal weights
    combined = noise_gen.combine_noise_maps([map1, map2])
    
    # Check that the combined map has the expected shape
    assert combined.shape == map1.shape
    
    # Check that the values are in [0, 1]
    assert np.all(combined >= 0.0) and np.all(combined <= 1.0)


def test_seed_reproducibility():
    """
    Test that using the same seed produces the same noise values.
    """
    # Create two noise generators with the same seed
    noise_gen1 = FastNoiseGenerator(seed=12345)
    noise_gen2 = FastNoiseGenerator(seed=12345)
    
    # Generate noise values from both generators
    value1 = noise_gen1.simplex_noise(0.5, 0.5)
    value2 = noise_gen2.simplex_noise(0.5, 0.5)
    
    # Check that the values are the same
    assert value1 == value2


def test_different_seeds():
    """
    Test that using different seeds produces different noise values.
    """
    # Create two noise generators with different seeds
    noise_gen1 = FastNoiseGenerator(seed=12345)
    noise_gen2 = FastNoiseGenerator(seed=54321)
    
    # Generate noise values from both generators
    value1 = noise_gen1.simplex_noise(0.5, 0.5)
    value2 = noise_gen2.simplex_noise(0.5, 0.5)
    
    # Check that the values are different
    assert value1 != value2
