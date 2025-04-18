#!/usr/bin/env python3
"""
Pytest configuration file for Cosmos Generator tests.
"""
import os
import sys
import pytest
from PIL import Image
import numpy as np
import tempfile
import shutil

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from cosmos_generator.core.planet_generator import PlanetGenerator
from cosmos_generator.utils.container import Container
from cosmos_generator.core.fast_noise_generator import FastNoiseGenerator


@pytest.fixture
def planet_generator():
    """
    Fixture that provides a PlanetGenerator instance with a fixed seed.
    """
    return PlanetGenerator(seed=12345)


@pytest.fixture
def noise_generator():
    """
    Fixture that provides a FastNoiseGenerator instance with a fixed seed.
    """
    return FastNoiseGenerator(seed=12345)


@pytest.fixture
def container():
    """
    Fixture that provides a Container instance.
    """
    return Container()


@pytest.fixture
def temp_output_dir():
    """
    Fixture that provides a temporary output directory for tests.
    Cleans up after the test is done.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Store the original output directory
    original_output_dir = config.OUTPUT_DIR

    # Override the output directory in the config
    config.OUTPUT_DIR = os.path.join(temp_dir, "output")

    # Update all dependent paths
    config.PLANETS_DIR = os.path.join(config.OUTPUT_DIR, "planets")
    config.PLANETS_DEBUG_DIR = os.path.join(config.PLANETS_DIR, "debug")
    config.PLANETS_EXAMPLES_DIR = os.path.join(config.PLANETS_DIR, "examples")
    config.PLANETS_RESULT_DIR = os.path.join(config.PLANETS_DIR, "result")
    config.PLANETS_LOG_FILE = os.path.join(config.PLANETS_DEBUG_DIR, "planets.log")
    config.PLANETS_TEXTURES_DIR = os.path.join(config.PLANETS_DEBUG_DIR, "textures")
    config.PLANETS_TERRAIN_TEXTURES_DIR = os.path.join(config.PLANETS_TEXTURES_DIR, "terrain")
    config.PLANETS_CLOUDS_TEXTURES_DIR = os.path.join(config.PLANETS_TEXTURES_DIR, "clouds")

    # Create the necessary directories
    os.makedirs(config.PLANETS_DEBUG_DIR, exist_ok=True)
    os.makedirs(config.PLANETS_EXAMPLES_DIR, exist_ok=True)
    os.makedirs(config.PLANETS_RESULT_DIR, exist_ok=True)
    os.makedirs(config.PLANETS_TERRAIN_TEXTURES_DIR, exist_ok=True)
    os.makedirs(config.PLANETS_CLOUDS_TEXTURES_DIR, exist_ok=True)

    # Create result directories for each planet type
    for planet_type in config.PLANET_TYPES:
        os.makedirs(os.path.join(config.PLANETS_RESULT_DIR, planet_type), exist_ok=True)

    yield config.OUTPUT_DIR

    # Restore the original output directory
    config.OUTPUT_DIR = original_output_dir
    config.PLANETS_DIR = os.path.join(config.OUTPUT_DIR, "planets")
    config.PLANETS_DEBUG_DIR = os.path.join(config.PLANETS_DIR, "debug")
    config.PLANETS_EXAMPLES_DIR = os.path.join(config.PLANETS_DIR, "examples")
    config.PLANETS_RESULT_DIR = os.path.join(config.PLANETS_DIR, "result")
    config.PLANETS_LOG_FILE = os.path.join(config.PLANETS_DEBUG_DIR, "planets.log")
    config.PLANETS_TEXTURES_DIR = os.path.join(config.PLANETS_DEBUG_DIR, "textures")
    config.PLANETS_TERRAIN_TEXTURES_DIR = os.path.join(config.PLANETS_TEXTURES_DIR, "terrain")
    config.PLANETS_CLOUDS_TEXTURES_DIR = os.path.join(config.PLANETS_TEXTURES_DIR, "clouds")

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)


@pytest.fixture
def desert_planet(planet_generator):
    """
    Fixture that provides a Desert planet instance.
    """
    return planet_generator.create("Desert", {
        "size": config.PLANET_SIZE,
        "seed": 12345
    })


@pytest.fixture
def ocean_planet(planet_generator):
    """
    Fixture that provides an Ocean planet instance.
    """
    return planet_generator.create("Ocean", {
        "size": config.PLANET_SIZE,
        "seed": 12345
    })


@pytest.fixture
def desert_planet_with_features(planet_generator):
    """
    Fixture that provides a Desert planet with all features enabled.
    """
    return planet_generator.create("Desert", {
        "size": config.PLANET_SIZE,
        "seed": 12345,
        "rings": True,
        "atmosphere": True,
        "clouds": True,
        "cloud_coverage": 0.7,
        "light_intensity": 1.2,
        "light_angle": 30.0
    })


@pytest.fixture
def ocean_planet_with_features(planet_generator):
    """
    Fixture that provides an Ocean planet with all features enabled.
    """
    return planet_generator.create("Ocean", {
        "size": config.PLANET_SIZE,
        "seed": 12345,
        "rings": True,
        "atmosphere": True,
        "clouds": True,
        "cloud_coverage": 0.7,
        "light_intensity": 1.2,
        "light_angle": 30.0,
        "variation": "water_world"
    })


@pytest.fixture
def ocean_planet_archipelago(planet_generator):
    """
    Fixture that provides an Ocean planet with archipelago variation.
    """
    return planet_generator.create("Ocean", {
        "size": config.PLANET_SIZE,
        "seed": 12345,
        "variation": "archipelago"
    })


@pytest.fixture
def ocean_planet_water_world(planet_generator):
    """
    Fixture that provides an Ocean planet with water_world variation.
    """
    return planet_generator.create("Ocean", {
        "size": config.PLANET_SIZE,
        "seed": 12345,
        "variation": "water_world"
    })


def assert_image_properties(image, width, height, mode="RGBA"):
    """
    Helper function to assert common image properties.
    """
    assert isinstance(image, Image.Image)
    assert image.width == width
    assert image.height == height
    assert image.mode == mode
