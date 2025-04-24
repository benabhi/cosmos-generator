"""
Test script to verify that duplicate planets cannot be created.
"""
import os
import pytest
from unittest.mock import patch

import config
from cosmos_generator.subcommands.planet.generate import main as generate_main


class TestDuplicatePlanets:
    """
    Test cases for duplicate planet prevention.
    """

    def test_duplicate_planet_prevention(self, temp_output_dir):
        """
        Test that a planet with the same seed cannot be created twice, regardless of type or variation.
        """
        # Clean up any existing planets.csv file
        planets_csv_path = config.PLANETS_CSV
        if os.path.exists(planets_csv_path):
            os.remove(planets_csv_path)
        # Create arguments for the first planet
        args = type('Args', (), {
            'type': 'Desert',
            'seed': 12345,
            'output': None,
            'rings': False,
            'rings_complexity': None,
            'rings_tilt': None,
            'atmosphere': False,
            'atmosphere_glow': 0.5,
            'atmosphere_halo': 0.7,
            'atmosphere_thickness': 3,
            'atmosphere_blur': 0.5,
            'clouds': False,
            'clouds_coverage': 0.5,
            'light_intensity': 1.0,
            'light_angle': 45.0,
            'zoom': None,
            'rotation': 0.0,
            'variation': 'arid',  # Explicitly set variation
            'color_palette_id': None
        })

        # Run the generate command for the first planet
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0

        # Check that the output file was created
        seed_str = '00012345'  # Padded to 8 characters
        planet_dir = os.path.join(config.PLANETS_DIR, 'desert', seed_str)
        assert os.path.exists(planet_dir), f"Planet directory {planet_dir} not found"

        # Check that the planets.csv file exists and contains the planet
        planets_csv_path = config.PLANETS_CSV
        assert os.path.exists(planets_csv_path), f"Planets CSV {planets_csv_path} not found"

        with open(planets_csv_path, 'r') as f:
            csv_content = f.read()
            assert seed_str in csv_content, f"Seed {seed_str} not found in planets.csv"

        # Try to create the same planet again (same seed, type, and variation)
        result = generate_main(args)

        # Check that the command failed (returned non-zero)
        assert result != 0, "Command should have failed when trying to create a duplicate planet"

        # Try with a different variation but same seed - should fail
        args.variation = 'dunes'
        result = generate_main(args)

        # Check that the command failed (returned non-zero)
        assert result != 0, "Command should fail when trying to create a planet with the same seed"

        # Try with a different type but same seed - should fail
        args.type = 'Ocean'
        args.variation = 'water_world'  # Reset to default variation for Ocean
        result = generate_main(args)

        # Check that the command failed (returned non-zero)
        assert result != 0, "Command should fail when trying to create a planet with the same seed"

        # Try with a different seed but same type and variation
        args.seed = 54321
        args.type = 'Desert'
        args.variation = 'arid'
        result = generate_main(args)

        # Check that the command was successful
        assert result == 0, "Command should succeed with different seed"
