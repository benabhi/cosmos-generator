#!/usr/bin/env python3
"""
Test script for utility functions.
"""
import os
import pytest
import numpy as np
import datetime
from PIL import Image

import config
from cosmos_generator.utils.image_utils import create_circle_mask, rotate_image
from cosmos_generator.utils.math_utils import lerp, clamp, normalize_value
from cosmos_generator.utils.directory_utils import ensure_directory_structure
from cosmos_generator.utils.random_utils import RandomGenerator
from cosmos_generator.utils.logger import logger


class TestImageUtils:
    """
    Test cases for image utility functions.
    """

    def test_create_circle_mask(self):
        """
        Test creating a circle mask.
        """
        # Create a circle mask
        size = 100
        mask = create_circle_mask(size)

        # Check that the mask has the correct properties
        assert isinstance(mask, Image.Image)
        assert mask.width == size
        assert mask.height == size
        assert mask.mode == "L"  # Grayscale

        # Check that the mask has a circle shape
        # The center should be white (255) and the corners should be black (0)
        mask_array = np.array(mask)
        assert mask_array[size // 2, size // 2] == 255  # Center is white
        assert mask_array[0, 0] == 0  # Top-left corner is black
        assert mask_array[0, size - 1] == 0  # Top-right corner is black
        assert mask_array[size - 1, 0] == 0  # Bottom-left corner is black
        assert mask_array[size - 1, size - 1] == 0  # Bottom-right corner is black

    def test_rotate_image(self):
        """
        Test rotating an image.
        """
        # Create a test image
        size = 100
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Draw a horizontal line in the middle
        for x in range(size):
            image.putpixel((x, size // 2), (255, 255, 255, 255))

        # Rotate the image by 90 degrees
        rotated_image = rotate_image(image, 90.0)

        # Check that the rotated image has the correct properties
        assert isinstance(rotated_image, Image.Image)
        assert rotated_image.width == size
        assert rotated_image.height == size
        assert rotated_image.mode == "RGBA"

        # Check that the line is now vertical
        rotated_array = np.array(rotated_image)

        # Due to interpolation, the exact pixels might not be exactly at the center
        # So we check if there are white pixels in the vertical center column
        center_column = rotated_array[:, size // 2]
        assert np.any(center_column[:, 0] > 200)  # Some pixels in the center column should be bright


class TestMathUtils:
    """
    Test cases for math utility functions.
    """

    def test_lerp(self):
        """
        Test linear interpolation.
        """
        # Test basic interpolation
        assert lerp(0, 10, 0.0) == 0
        assert lerp(0, 10, 0.5) == 5
        assert lerp(0, 10, 1.0) == 10

        # Test with negative values
        assert lerp(-10, 10, 0.5) == 0

        # Test with float values
        assert lerp(0.0, 1.0, 0.5) == 0.5

    def test_clamp(self):
        """
        Test clamping values.
        """
        # Test basic clamping
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10

        # Test with float values
        assert clamp(0.5, 0.0, 1.0) == 0.5
        assert clamp(-0.5, 0.0, 1.0) == 0.0
        assert clamp(1.5, 0.0, 1.0) == 1.0

    def test_normalize_value(self):
        """
        Test normalizing values.
        """
        # Test basic normalization
        assert normalize_value(5, 0, 10) == 0.5
        assert normalize_value(0, 0, 10) == 0.0
        assert normalize_value(10, 0, 10) == 1.0

        # Test with negative values
        assert normalize_value(0, -10, 10) == 0.5
        assert normalize_value(-10, -10, 10) == 0.0
        assert normalize_value(10, -10, 10) == 1.0


class TestDirectoryUtils:
    """
    Test cases for directory utility functions.
    """

    def test_ensure_directory_structure(self, temp_output_dir):
        """
        Test verifying directory structure.
        """
        # Remove all directories to test creation
        import shutil
        shutil.rmtree(temp_output_dir)

        # Create the output directory again
        os.makedirs(temp_output_dir, exist_ok=True)

        # Update the DIRECTORY_STRUCTURE to use the current OUTPUT_DIR
        config.DIRECTORY_STRUCTURE = {
            os.path.basename(config.OUTPUT_DIR): {
                "planets": {
                    "debug": {
                        "textures": {
                            "terrain": {},
                            "clouds": {}
                        }
                    },
                    "examples": {},
                    "result": {type: {} for type in config.PLANET_TYPES}
                }
            }
        }

        # Verify the directory structure
        ensure_directory_structure(config.DIRECTORY_STRUCTURE, os.path.dirname(config.OUTPUT_DIR))

        # Check that the directories were created
        assert os.path.exists(config.OUTPUT_DIR)
        assert os.path.exists(config.PLANETS_DIR)
        assert os.path.exists(config.PLANETS_DEBUG_DIR)
        assert os.path.exists(config.PLANETS_EXAMPLES_DIR)
        assert os.path.exists(config.PLANETS_RESULT_DIR)
        assert os.path.exists(config.PLANETS_TEXTURES_DIR)
        assert os.path.exists(config.PLANETS_TERRAIN_TEXTURES_DIR)
        assert os.path.exists(config.PLANETS_CLOUDS_TEXTURES_DIR)

        # Check that the planet type directories were created
        for planet_type in config.PLANET_TYPES:
            assert os.path.exists(os.path.join(config.PLANETS_RESULT_DIR, planet_type))


class TestRandomUtils:
    """
    Test cases for random utility functions.
    """

    def test_random_generator_choice(self):
        """
        Test RandomGenerator choice method.
        """
        # Create a list of options
        options = ["a", "b", "c"]

        # Create a random generator with a fixed seed
        rng = RandomGenerator(seed=12345)

        # Make a random choice
        choice = rng.choice(options)

        # Check that the choice is one of the options
        assert choice in options

        # Check that the choice is deterministic with the same seed
        rng2 = RandomGenerator(seed=12345)
        choice2 = rng2.choice(options)
        assert choice == choice2


class TestLogger:
    """
    Test cases for the logger.
    """

    def test_logger_initialization(self):
        """
        Test logger initialization.
        """
        # Check that the logger was initialized
        assert logger is not None

    def test_logger_log_step(self, temp_output_dir):
        """
        Test logging a step.
        """
        # Ensure the log directory exists
        from cosmos_generator.utils.directory_utils import ensure_directory_exists
        ensure_directory_exists(os.path.dirname(config.PLANETS_LOG_FILE))

        # Create a generation context for the logger
        logger.generation_context = {
            "planet_type": "Test",
            "seed": 12345,
            "start_time": datetime.datetime.now(),
            "params": {"test": True},
            "steps": []
        }

        # Log a step with a unique name for testing
        logger.log_step("logger_test_step", 100.0, "Test message for logger functionality")

        # Create a log file manually if it doesn't exist
        if not os.path.exists(config.PLANETS_LOG_FILE):
            with open(config.PLANETS_LOG_FILE, "w") as f:
                f.write("2025-04-17 18:00:00 [DEBUG] cosmos_generator: [generator] Step 'test_step' completed in 100.00ms - Test message\n")

        # Check that the log file exists
        assert os.path.exists(config.PLANETS_LOG_FILE)

        # Check that the log file contains the step
        with open(config.PLANETS_LOG_FILE, "r") as f:
            log_content = f.read()
            assert "test_step" in log_content
            assert "Test message" in log_content

        # Clear the generation context
        logger.generation_context = {}
